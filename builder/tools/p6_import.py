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

def parse(path):
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True).active
    total = None; groups = []; units = []; names = []; nidx = {}; acts = []
    g = a = u = None
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or not r[0]: continue
        raw = str(r[0]); ind = len(raw) - len(raw.lstrip()); n = raw.strip()
        v = [num(x) for x in r[2:13]]  # pct, bud cost, ev cost, rem cost, lab pct, bud u, ev u, prev u, wk u, wk %, rem u
        if ind == 0:
            total = {'pc': v[0], 'bc': v[1], 'ec': v[2], 'rc': v[3], 'pu': v[4], 'bu': v[5], 'eu': v[6], 'prev': v[7], 'wk': v[8], 'rem': v[10]}
        elif ind == 2:
            g = {'n': n, 'areas': []}; groups.append(g); a = u = None
        elif ind == 4:
            a = {'n': n, 'pc': v[0], 'bc': v[1], 'ec': v[2], 'rc': v[3], 'bu': v[5], 'eu': v[6], 'prev': v[7], 'wk': v[8], 'rem': v[10]}; g['areas'].append(a); u = None
        elif ind == 6:
            u = len(units); units.append([len(groups) - 1, len(g['areas']) - 1, n, v[5], v[6], v[7], v[8], v[10]])
        elif ind == 8:
            if u is None:  # activity straight under an area: give it a unit of its own
                u = len(units); units.append([len(groups) - 1, len(g['areas']) - 1, '(whole area)', 0, 0, 0, 0, 0]); a['_pseudo'] = u
            nm = str(r[1] or '').strip()
            if nm not in nidx: nidx[nm] = len(names); names.append(nm)
            acts.append([u, n, nidx[nm], v[5], v[6], v[7], v[8], v[10]])
    return total, groups, units, names, acts

def r0(x):
    x = round(x); return 0 if x == 0 else x  # avoid -0

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
    for k in ('bu', 'eu', 'rem'):
        s = sum(a[k] for g in groups for a in g['areas'])
        assert abs(s - total[k]) < 5, f'{k}: groups add to {s:.0f}, total says {total[k]:.0f}'
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
    doc = {'date': args.date, 'week_end': we, 'file': args.name or os.path.basename(args.xlsx), 'total': total,
           'groups': groups, 'units': [[r0(x) if isinstance(x, float) else x for x in u] for u in units], 'names': names,
           'acts': [[u, i, n] + [r0(x) for x in rest] for u, i, n, *rest in acts], 'actuals': rows}
    for g in groups:
        for a in g['areas']:
            for k in ('bc', 'ec', 'rc', 'bu', 'eu', 'prev', 'wk', 'rem'): a[k] = r0(a[k])
            a['pc'] = round(a['pc'], 4)
    for k in ('bc', 'ec', 'rc', 'bu', 'eu', 'prev', 'wk', 'rem'): total[k] = r0(total[k])
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '.p6.json')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', tmp, pw, os.path.join(OUT, 'p6.bin')], check=True)
    os.remove(tmp)
    print(f'{len(groups)} groups, {len(units)} units, {len(acts)} activities, {len(rows)} dashboard activities mapped; week end {we}; '
          f'earned {total["eu"]:,} of {total["bu"]:,} units ({total["eu"] / total["bu"]:.2%})')

if __name__ == '__main__':
    main()
