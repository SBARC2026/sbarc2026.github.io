#!/usr/bin/env python3
"""Turn a Daily Progress Report workbook (MP + Villa Status + Building Status sheets) into the Executive Summary datasets.

Usage: python3 builder/tools/dpr_import.py <DPR.xlsx> --src builder/_data/exec/blobs --out <dir> --date 31-10-2026

--src is the folder of the current exec blobs (the previous figures give the row order, names and the landscape rows, which this
report does not carry). --out receives the rewritten blobs: villas, villa_activities, buildings, manpower, activities, layouts.
Landscape / infrastructure rows and the building rows of `activities` / `layouts` are kept as they were (the tracker structure differs).
Every count is cross-checked against the workbook's own summary sheets before anything is written.
"""
import argparse, glob, json, os, re, sys, warnings
import openpyxl
warnings.filterwarnings('ignore')

IDS = {  # activities dataset id -> (villa group, villa activity)
    'toilet': ('Finishes', 'Porcelain tiles'), 'paint': ('Finishes', 'Paint'), 'quartz': ('Finishes', 'Quartz'), 'floor': ('Finishes', 'Floor tiles'),
    'gyp': ('Gypsum board', 'Board'), 'gtj': ('Gypsum board', 'Tape & joint'), 'gpt': ('Gypsum board', 'Painting'),
    'bwp': ('Other', 'Balcony waterproofing'), 'wood': ('Other', 'Wooden handrail'), 'cage': ('Other', 'Cage ladder'),
    'idoor': ('Other', 'Internal doors'), 'edoor': ('Other', 'External doors'), 'kitchen': ('Other', 'Kitchen'),
    'aluw': ('Aluminium', 'Windows'), 'bp': ('Aluminium exterior', 'Balcony pergola'), 'wp': ('Aluminium exterior', 'Walkway pergola'),
    'cp': ('Aluminium exterior', 'Car shade pergola'), 'bh': ('Aluminium exterior', 'Balcony handrail'),
    'e1w': ('Electrical', '1st fix walls'), 'e1f': ('Electrical', '1st fix flooring'), 'e1c': ('Electrical', '1st fix ceiling EMT'),
    'e2c': ('Electrical', '2nd fix ceiling wires'), 'p1': ('Plumbing', '1st fix'), 'p2c': ('Plumbing', '2nd fix ceiling'),
    'h1': ('HVAC', '1st fix'), 'h2c': ('HVAC', '2nd fix ceiling'),
}
MARBLE = ['60×60 floor', '40×40 wet area', 'Stairs']

def jl(p): return json.load(open(p, encoding='utf-8'))
def find(src, key):  # blob by a field it holds
    for f in glob.glob(os.path.join(src, '*.json')):
        d = jl(f)
        if isinstance(d, list) and d and key(d[0]): return f, d
    sys.exit('blob not found in ' + src)

def code_pct(v):  # sheet value -> (code, pct)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ('n/s', 'ns', '-', 'n\\a', 'n/a'): return 'X', None
        if s == 'done': return 'C', 100
        if s == 'ongoing': return 'P', 50
        return 'N', None
    if v is None or v <= 0: return 'N', None
    if v >= 0.9999: return 'C', 100
    return 'P', min(99, max(1, round(v * 100)))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xlsx'); ap.add_argument('--src', required=True); ap.add_argument('--out', required=True); ap.add_argument('--date', required=True); ap.add_argument('--override', help='JSON {villa:{v:{col idx:value}}} read from the report PDF; replaces the villa status cells of the workbook')
    a = ap.parse_args()
    wb = openpyxl.load_workbook(a.xlsx, data_only=True)
    os.makedirs(a.out, exist_ok=True)
    fv, villas0 = find(a.src, lambda r: 'villa' in r and 'finishes' in r and 'type' in r)
    fa, vacts0 = find(a.src, lambda r: 'villa' in r and 'activity' in r and 'group' in r)
    fb, blds0 = find(a.src, lambda r: 'acts' in r and 'zone' in r)
    fm, mp0 = find(a.src, lambda r: 'kind' in r and r['kind'] == 'kpi')
    fc, act0 = find(a.src, lambda r: 'scope' in r and 'pct_complete' in r)
    fl, lay0 = find(a.src, lambda r: 'kind' in r and r.get('id') == 'site')
    problems = []

    # ---------- villas ----------
    ws = wb['Villa Status']; hdr = None; rows = []
    for r in ws.iter_rows(min_row=1, values_only=True):
        if r and r[1] == 'Villa': hdr = list(r); continue
        if hdr and r[1] and r[2]: rows.append(r)
    assert len(rows) == len(villas0) == 104, (len(rows), len(villas0))
    col = {h: i for i, h in enumerate(hdr) if h}
    if a.override:  # the PDF is newer than the workbook: take the 29 activity cells from it and recompute the three % columns
        ov = json.load(open(a.override)); rows = [list(r) for r in rows]
        for k, (r, v0) in enumerate(zip(rows, villas0)):
            cells = ov[v0['villa']]['v']
            for j in range(29): r[3 + j] = cells[str(j)]
            n = [0 if x is None else x for x in r[3:32]]
            fin_l = [n[0], n[1], n[4], n[5], n[6], n[2], n[3], (2 * n[7] + n[8] + n[9]) / 4, n[10], n[11], n[12], n[13], n[14], n[15], n[16], sum(1 for x in n[17:21] if x >= 0.9999) / 4]
            r[col['Finishes %']] = sum(fin_l) / 16; r[col['MEP %']] = sum(n[21:29]) / 8; r[col['TOTAL %']] = (sum(fin_l) + sum(n[21:29])) / 24
    fin_i, mep_i, tot_i = col['Finishes %'], col['MEP %'], col['TOTAL %']
    acts0 = [(r['group'], r['activity']) for r in vacts0 if r['villa'] == villas0[0]['villa']]
    assert len(acts0) == 29
    villas, vacts, vm = [], [], {}
    for k, (r, v0) in enumerate(zip(rows, villas0)):
        code = v0['villa']
        if r[1] != code: problems.append(f'sheet row {k + 1} says villa {r[1]}, kept {code} (cluster {r[2]} = {v0["cluster"]})'); assert r[2] == v0['cluster']
        villas.append({'villa': code, 'cluster': v0['cluster'], 'type': v0['type'], 'finishes': round(r[fin_i], 4), 'mep': round(r[mep_i], 4), 'total': round(r[tot_i], 4)})
        vm[code] = {}
        for j, (g, act) in enumerate(acts0):
            v = r[3 + j]; v = 0 if v is None else v
            c, p = code_pct(v)
            if c == 'X': c, p = 'N', 0
            st = {'C': 'Done', 'P': 'In progress', 'N': 'Not started'}[c]
            vacts.append({'villa': code, 'cluster': v0['cluster'], 'group': g, 'activity': act, 'status': st, 'pct': 100 if c == 'C' else (p or 0)})
            vm[code][(g, act)] = (c, 100 if c == 'C' else (p or 0), v)
    # ---------- activity counts: Villas scope ----------
    def counts(vals): return (sum(1 for c in vals if c == 'C'), sum(1 for c in vals if c == 'P'), sum(1 for c in vals if c == 'N'))
    summ = {}
    for r in wb['Villa Activity Summary'].iter_rows(min_row=5, values_only=True):
        if r[1]: summ[(r[0].strip().lower(), r[1].strip().lower())] = r[2:6]
    act1 = []
    for r in act0:
        r = dict(r)
        if r['scope'] == 'Villas' and r['id'].rsplit('-', 1)[0] in IDS | {'marble-Villas': 0, 'marble': 0}:
            key = r['id'].rsplit('-', 1)[0]
            if key == 'marble':
                cs = []
                for code in vm:
                    x = [vm[code][('Marble', m)][2] for m in MARBLE]; avg = sum(x) / 3
                    cs.append('C' if avg >= 0.9999 else 'N' if avg <= 0 else 'P')
            else:
                g, name = IDS[key]; cs = [vm[code][(g, name)][0] for code in vm]
                s = summ.get((g.lower(), name.lower().replace(' floor', '').replace(' wet area', '')))
                if s and not a.override:
                    d, ip, ns = counts(cs)
                    if (d, ip, ns) != tuple(s[:3]): problems.append(f'{name}: computed {d}/{ip}/{ns}, workbook summary {tuple(s[:3])}')
            d, ip, ns = counts(cs); n = len(cs)
            r.update(done=d, in_progress=ip, not_started=ns, not_in_scope=0, pct_complete=round(d / n, 4))
        act1.append(r)

    # ---------- buildings ----------
    ws = wb['Building Status']; hdr = hdr2 = None; brows = []
    all_rows = list(ws.iter_rows(min_row=1, values_only=True))
    for i, r in enumerate(all_rows):
        if r[0] == '#' and r[1] == 'Building': hdr = list(r); hdr2 = all_rows[i + 1]; start = i + 2; break
    for r in all_rows[start:]:
        if r[1] and isinstance(r[0], (int, float)): brows.append(r)
    assert len(brows) == len(blds0) == 14
    fi, mi, ti = hdr.index('Finishes %'), hdr.index('MEP %'), hdr.index('TOTAL %')
    bm = {r[1]: r for r in brows}; blds = []; bstat = {}
    for b0 in blds0:
        r = bm[b0['code']]; old = [x.split('|') for x in b0['acts'].split(';')]
        assert len(old) == 36 and fi - 5 == 36, (len(old), fi)
        parts, rec = [], []
        for j, (g, act, _c, _p, mep) in enumerate(old):
            c, p = code_pct(r[5 + j])
            parts.append(f'{g}|{act}|{c}|{"" if p is None else p}|{mep}'); rec.append([g, act, c, p, ''])
        blds.append(dict(b0, zone=r[3], engineer=r[4], finishes=round(r[fi], 4), mep=round(r[mi], 4), total=round(r[ti], 4), acts=';'.join(parts)))
        bstat[b0['code']] = rec
    bsum = {}
    for r in wb['Bldg Activity Summary'].iter_rows(min_row=5, values_only=True):
        if r[1]: bsum[(r[0], r[1])] = tuple(r[2:6])
    for j in range(36):  # cross-check the building counts
        g, act = blds[0]['acts'].split(';')[j].split('|')[:2]
        cs = [code_pct(bm[b['code']][5 + j])[0] for b in blds0]
        d, ip, ns, x = counts(cs) + (sum(1 for c in cs if c == 'X'),)
        hit = [v for (gg, aa), v in bsum.items() if aa.lower().replace(' / ', '/') == act.lower().replace(' / ', '/') and gg.split(' ')[0].lower() == g.split(' ')[0].lower()]
        if len(hit) == 1 and tuple(hit[0]) != (d, ip, ns, x): problems.append(f'building {g}/{act}: computed {(d, ip, ns, x)}, workbook {tuple(hit[0])}')

    # ---------- manpower ----------
    ms = wb['MP Summary']; kv = {}; rep = {}
    for r in ms.iter_rows(min_row=1, max_row=24, values_only=True):
        if r[0] and r[1] is not None: kv[str(r[0]).strip()] = r[1]
    rep_no, rep_date = kv['Report no.'], kv['Report date']
    kp = lambda n, v, x=None: {'kind': 'kpi', 'name': n, 'value': v, 'extra': x}
    mp = [kp('Total workforce', kv['TOTAL WORKFORCE']), kp('Direct workforce', kv['Direct workforce']), kp('Main contractor (site support)', kv['Main contractor (site support)']),
          kp('Man-hours', kv['MAN-HOURS']), kp('Villas', kv['Villas']), kp('Buildings', kv['Buildings']), kp('Site / infra', kv['Site / infra']),
          {'kind': 'meta', 'name': 'Report', 'value': rep_no, 'extra': f'{rep_date:%d-%m-%Y} · {kv["Weather - high (°C)"]}°/{kv["Weather - low (°C)"]}°C'}]
    dsum = 0
    for r in wb['MP Tracker'].iter_rows(min_row=5, values_only=True):
        if r[0] and isinstance(r[0], (int, float)) and r[1]:
            mp.append({'kind': 'discipline', 'name': r[1], 'value': r[5], 'villas': r[2], 'buildings': r[3], 'site': r[4]}); dsum += r[5]
    if dsum != kv['Direct workforce']: problems.append(f'disciplines add to {dsum}, summary says {kv["Direct workforce"]}')
    mb = list(wb['MP Buildings'].iter_rows(min_row=1, values_only=True)); hi = next(i for i, r in enumerate(mb) if r[0] == 'NO.'); heads = mb[hi]; bsum_p = 0
    for r in mb[hi + 2:]:
        if not (isinstance(r[0], (int, float)) and r[1]): continue
        tr = [f'{heads[c]}|{int(r[c])}' for c in range(4, 19) if isinstance(r[c], (int, float)) and r[c] > 0]
        mp.append({'kind': 'building', 'name': r[1], 'value': r[3], 'extra': r[2], 'trades': ';'.join(tr)}); bsum_p += r[3]
    if bsum_p != kv['Buildings']: problems.append(f'building personnel add to {bsum_p}, summary says {kv["Buildings"]}')
    mc = list(wb['MP Main Contractor'].iter_rows(min_row=1, values_only=True)); hi = next(i for i, r in enumerate(mc) if r[0] == 'Category'); sup = 0
    for r in mc[hi + 1:]:
        if r[0] and r[1] and isinstance(r[2], (int, float)) and r[2] > 0:
            mp.append({'kind': 'role', 'name': r[1], 'value': int(r[2]), 'extra': r[0]}); sup += int(r[2]) if r[0] == 'Site support' else 0
    if sup != kv['Main contractor (site support)']: problems.append(f'site support adds to {sup}, summary says {kv["Main contractor (site support)"]}')

    # ---------- layouts ----------
    D = a.date; lay = []
    def ustr(codes, vals_label):
        return None
    vlist = [v['villa'] for v in villas]; allpct = sum(r[tot_i] for r in rows) / len(rows)
    def lab(c, p): return 'Done' if c == 'C' else f'{p}%' if c == 'P' else 'Not started'
    for r in lay0:
        r = dict(r)
        if r.get('id') == 'site': r['bstat'] = json.dumps(bstat, ensure_ascii=False, separators=(',', ':'))
        elif r.get('id') == 'all': r['pct'] = allpct; r['date'] = D
        elif r.get('kind') == 'units' and (r['scope'] == 'Villas' or r['id'] in ('e1w', 'e1f', 'e1c', 'e2c', 'p1', 'p2c', 'h1', 'h2c')):
            key = r['id']
            if key != 'marble' and key not in IDS: lay.append(r); continue
            ent = {}
            for u in r['units'].split(';'):
                code = u.split('|')[0]; ent[code] = u
            for code in vlist:
                if key == 'marble':
                    avg = sum(vm[code][('Marble', m)][2] for m in MARBLE) / 3; c, p = code_pct(avg)
                else: c, p, _ = vm[code][IDS[key]]
                ent[code] = f'{code}|{c}|{"" if c == "N" else (100 if c == "C" else p)}|{lab(c, p)}'
            r['units'] = ';'.join(ent.values())
            cs = [u.split('|')[1] for u in ent.values()]
            r['n_done'], r['n_prog'], r['n_not'] = cs.count('C'), cs.count('P'), cs.count('N'); r['n'] = len(cs)
            r['pct'] = r['n_done'] / r['n']; r['prog'] = r['n_prog'] / r['n']
            if r['scope'] == 'Villas': r['date'] = D
            else: r['sub'] = r['sub']; r['date'] = D + ' (villas) · 21-10-2026 (buildings)'
        lay.append(r)

    outs = {fv: villas, fa: vacts, fb: blds, fm: mp, fc: act1, fl: lay}
    for f, d in outs.items():
        with open(os.path.join(a.out, os.path.basename(f)), 'w', encoding='utf-8') as fh: json.dump(d, fh, ensure_ascii=False, separators=(',', ':'))
    for p in problems: print('CHECK', p)
    print(f'report {rep_no} {rep_date:%d-%m-%Y}: {len(villas)} villas ({sum(v["total"] for v in villas) / len(villas):.2%} avg total), {len(blds)} buildings, '
          f'workforce {kv["TOTAL WORKFORCE"]} (direct {kv["Direct workforce"]}), {len(problems)} checks flagged')

if __name__ == '__main__':
    main()
