#!/usr/bin/env python3
"""Import a weekly Primavera (P6) export into the portal.

Usage:
  SBARC_PASSWORD=... python3 builder/tools/p6_import.py <export.xlsx> --date 2026-10-26 [--week-end 2026-10-23]

The export is the P6 "This Week" layout: one sheet, columns
  Activity ID | Activity Name | Performance % Complete | Budgeted Total Cost | Earned Value Cost | Remaining Cost |
  Performance % Complete - Labor Units | Budgeted Labor Units | Earned Value Labor Units | Previous Week Cumm EV Units |
  This Week EV Unit | This Week EV Unit % | Remaining Units
with the hierarchy shown by indentation: Total > trade group > Buildings/Villas/No VILLA NO. > building or villa > activity.

It writes builder/p6/p6.bin: the processed figures, encrypted with the portal password (the repository is public, so the
readable figures never go in it). build.py decrypts it, applies the earned value to the Management Tracking dashboard and
adds the Primavera tab. Run it again each week with the new export; the last file replaces the previous one.

--week-end is the Management Tracking reporting week the figures belong to (a plan Friday). Default: the Friday on or before --date.
"""
import argparse, datetime, json, os, re, subprocess, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
OUT = os.path.join(B, 'p6')

# Dashboard activity -> P6 trade group. "X — Villas|Buildings" activities take the matching area row of the group.
GROUP_OF = {
    'Plaster': 'Wall rough in and Internal Plaster', 'Façade': 'Facade Finishes', 'MEP 1st Fix': 'MEP 1st Fix', 'MEP 2nd Fix': 'MEP 2nd Fix',
    'MEP 3rd Fix': 'MEP 3rd Fixand Termination', 'Floor and Wall Tiles': 'Floor and Wall Tiles', 'Ceiling': 'Ceiling', 'Paint': 'Internal Paint',
    'Sanitary Fixtures': 'Sanitary Fixtures', 'Doors, Windows, Woodwork & Handrails': 'Doors and Windows', 'External Works': 'External Works',
}

def num(v):
    return float(v) if isinstance(v, (int, float)) else 0.0

# Column headers (first match wins; the 30-Oct layout has a cost block then a man-hours block with repeated names)
COLS = {
    'bc': ['Budgeted Total Cost'], 'pvc': ['Planned Value Cost'], 'ec': ['Cumm This Week EV', 'Earned Value Cost'],
    'prevc': ['Previous Week Cumm EV', 'Previous Week Cumm EV Cost'], 'bu': ['Budgeted Labor Units'], 'pvu': ['Planned Value Labor Units'],
    'eu': ['This Week Cumm Earned Value Labor Units', 'Earned Value Labor Units'], 'prev': ['Previous Week Cumm EV Units'],
    'wk': ['This Week EV Unit'], 'rem': ['Remaining Units'],
}

def sheet_rows(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    for ws in wb.worksheets:
        if ws.sheet_state != 'visible': continue
        it = ws.iter_rows(values_only=True); head = None
        for r in it:
            if r and r[0] == 'Activity ID': head = [str(x).strip() if x is not None else '' for x in r]; break
            if r and r[0] and str(r[0]).startswith('Data Date'): continue
        if head and 'Budgeted Labor Units' in head: return head, it
    sys.exit('No sheet with an "Activity ID" header and Budgeted Labor Units found.')

def parse(path):
    head, it = sheet_rows(path)
    ix = {k: next((head.index(n) for n in names if n in head), None) for k, names in COLS.items()}
    assert ix['bu'] is not None and ix['eu'] is not None, 'unexpected layout'
    total = None; groups = []; units = []; names = []; nidx = {}; acts = []
    g = a = u = None
    for r in it:
        if not r or not r[0]: continue
        raw = str(r[0]); ind = len(raw) - len(raw.lstrip()); n = raw.strip()
        v = {k: (num(r[i]) if i is not None and i < len(r) else 0.0) for k, i in ix.items()}
        if ind == 0:
            total = dict(v)
        elif ind == 2:
            g = {'n': n, 'areas': []}; groups.append(g); a = u = None
        elif ind == 4:
            a = {'n': n, **v}; g['areas'].append(a); u = None
        elif ind == 6:
            u = len(units); units.append([len(groups) - 1, len(g['areas']) - 1, n, v['bu'], v['eu'], v['prev'], v['wk'], v['rem'], v['bc'], v['ec'], v['prevc'], v['pvu'], v['pvc']])
        elif ind == 8:
            if u is None:  # activity straight under an area: give it a unit of its own
                u = len(units); units.append([len(groups) - 1, len(g['areas']) - 1, '(whole area)', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]); a['_pseudo'] = u
            nm = str(r[1] or '').strip()
            if nm not in nidx: nidx[nm] = len(names); names.append(nm)
            acts.append([u, n, nidx[nm], v['bu'], v['eu'], v['prev'], v['wk'], v['rem'], v['bc'], v['ec'], v['prevc'], v['pvu'], v['pvc']])
    return total, groups, units, names, acts

def r0(x):
    x = round(x); return 0 if x == 0 else x  # avoid -0

def unit_map(groups, dash_activities):
    """Dashboard activity -> [group index, area index] for the activities that sit on villas / buildings (their units are listed in the This week breakdown)."""
    gi = {g['n']: i for i, g in enumerate(groups)}; out = {}
    for act in dash_activities:
        base, _, area = act['activity'].partition(' — ')
        if area and base in GROUP_OF and GROUP_OF[base] in gi:
            names = [x['n'] for x in groups[gi[GROUP_OF[base]]]['areas']]
            if area in names: out[act['activity']] = [gi[GROUP_OF[base]], names.index(area)]
    return out

def cost_map(groups, dash_activities):
    """Dashboard activity -> [group index, area index or -1 for the whole group], for every activity with a P6 row (used for weekly cost)."""
    gi = {g['n']: i for i, g in enumerate(groups)}; out = {}
    for act in dash_activities:
        name = act['activity']; base, _, area = name.partition(' - ') if False else name.partition(' — ')
        if name in gi and not area: out[name] = [gi[name], -1]
        elif area and base in GROUP_OF and GROUP_OF[base] in gi:
            names = [x['n'] for x in groups[gi[GROUP_OF[base]]]['areas']]
            if area in names: out[name] = [gi[GROUP_OF[base]], names.index(area)]
    return out

def ev_rows(groups, dash_activities, week_end):
    """Exact earned labor units per dashboard activity from the P6 group / area rows."""
    byname = {g['n']: g for g in groups}
    rows, problems = [], []
    for act in dash_activities:
        name = act['activity']; ev = None; bud = None
        base, _, area = name.partition(' — ')
        if name in byname and not area:
            gg = byname[name]; ev = sum(x['eu'] for x in gg['areas']); bud = sum(x['bu'] for x in gg['areas'])
        elif area and base in GROUP_OF and GROUP_OF[base] in byname:
            hit = [x for x in byname[GROUP_OF[base]]['areas'] if x['n'] == area]
            if hit: ev, bud = hit[0]['eu'], hit[0]['bu']
        if ev is None: problems.append(f'{name}: no P6 row'); continue
        if abs(bud - act['budget']) > 3: problems.append(f'{name}: P6 budget {bud:.0f} vs dashboard {act["budget"]}')
        rows.append({'activity': name, 'week_end': week_end, 'earned_to_date': r0(ev)})
    return rows, problems

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xlsx'); ap.add_argument('--date', required=True); ap.add_argument('--week-end')
    ap.add_argument('--activities', default=os.path.join(B, '_data', 'p02b', 'blobs', '6f4dd1cc6a61e075b86d8ae1710386e2.json'),
                    help="dashboard 'activities' blob (builder/_data/p02b/...)")
    ap.add_argument('--name')
    args = ap.parse_args()
    pw = os.environ.get('SBARC_PASSWORD') or sys.exit('Set SBARC_PASSWORD.')
    d = datetime.date.fromisoformat(args.date)
    we = args.week_end or (d - datetime.timedelta(days=(d.weekday() - 4) % 7)).isoformat()
    total, groups, units, names, acts = parse(args.xlsx)
    assert total and groups and acts, 'unexpected layout'
    # the hierarchy must add up to the total
    for k in ('bu', 'eu', 'bc', 'ec'):
        s = sum(a[k] for g in groups for a in g['areas'])
        assert abs(s - total[k]) < (5 if k in ('bu', 'eu') else 50), f'{k}: groups add to {s:.0f}, total says {total[k]:.0f}'
    # Activity rows exist only for the building trades; infrastructure and "No Work Feature" are single lines. Where activities exist
    # they must agree with their group to within 0.5%.
    ga = {}
    for x in acts: gi = units[x[0]][0]; ga[gi] = ga.get(gi, 0) + x[4]
    for gi, s in ga.items():
        gt = sum(a['eu'] for a in groups[gi]['areas'])
        assert abs(s - gt) <= max(150, 0.005 * gt), f"{groups[gi]['n']}: activities add to {s:.0f} earned units, group says {gt:.0f}"
    dash = json.load(open(args.activities))
    rows, problems = ev_rows(groups, dash, we)
    for p in problems: print('WARNING', p)
    for g in groups:
        for a in g['areas']: a.pop('_pseudo', None)
    KEYS = ('bc', 'pvc', 'ec', 'prevc', 'bu', 'pvu', 'eu', 'prev', 'wk', 'rem')
    for x in [total] + [a for g in groups for a in g['areas']]:
        for k in KEYS: x[k] = r0(x[k])
        x['rc'] = x['bc'] - x['ec']; x['pc'] = round(x['ec'] / x['bc'], 4) if x['bc'] else 0
    # the last report's rows for earlier weeks stay (exact figures), this week's replace any with the same week end
    old = []
    prev_f = os.path.join(OUT, 'p6.bin')
    if os.path.exists(prev_f):
        tmp0 = os.path.join(OUT, '.old.json')
        if subprocess.run(['node', os.path.join(B, 'decrypt.js'), prev_f, pw, tmp0]).returncode == 0:
            old = [r for r in json.load(open(tmp0)).get('actuals', []) if r['week_end'] != we]; os.remove(tmp0)
    doc = {'date': args.date, 'week_end': we, 'file': args.name or os.path.basename(args.xlsx), 'total': total,
           'groups': groups, 'units': [[r0(x) if isinstance(x, float) else x for x in u] for u in units], 'names': names,
           'acts': [[u, i, n] + [r0(x) for x in rest] for u, i, n, *rest in acts], 'actuals': old + rows, 'amap': unit_map(groups, dash), 'cmap': cost_map(groups, dash)}
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '.p6.json')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', tmp, pw, os.path.join(OUT, 'p6.bin')], check=True)
    os.remove(tmp)
    print(f'{len(groups)} groups, {len(units)} units, {len(acts)} activities, {len(rows)} dashboard activities mapped; week end {we}; '
          f'man-hours earned {total["eu"]:,} of {total["bu"]:,} ({total["eu"] / total["bu"]:.2%}), planned {total["pvu"] / total["bu"]:.2%}; '
          f'cost earned {total["ec"]:,} of {total["bc"]:,} ({total["ec"] / total["bc"]:.2%}), planned {total["pvc"] / total["bc"]:.2%}')

if __name__ == '__main__':
    main()
