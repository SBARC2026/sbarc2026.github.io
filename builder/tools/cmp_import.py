"""Import the MAK-vs-PMC progress comparison workbook -> builder/cmp/cmp.bin (encrypted with the portal password).

Usage:  SBARC_PASSWORD=... python3 builder/tools/cmp_import.py "<Comp_Sheet>.xlsx" [--date YYYY-MM-DD]

Reads sheet "Main": MAK in columns A-F, PMC in columns G-L (Activity ID/name, Performance % Complete - Labor, Budgeted / Earned / Remaining labour units),
one row per WBS node or activity, hierarchy shown by the indentation of column A. Writes a flat depth-first list of nodes.
Rows: [level, activity id (activities only), name, budget, MAK %, MAK earned, PMC %, PMC earned].  Only ever written encrypted (public repository).
"""
import json, os, subprocess, sys, tempfile
from openpyxl import load_workbook

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
num = lambda x: float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else 0.0


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    src = a[0] if a else sys.exit(__doc__)
    date = sys.argv[sys.argv.index('--date') + 1] if '--date' in sys.argv else ''
    pw = os.environ.get('SBARC_PASSWORD') or sys.exit('set SBARC_PASSWORD')
    ws = load_workbook(src, read_only=True, data_only=True)['Main']
    rows, head = [], ''
    for i, r in enumerate(ws.iter_rows(min_row=1, values_only=True), 1):
        r = list(r) + [None] * 12
        if i == 1: head = ' '.join(str(c) for c in r[:12] if c); continue
        if i == 2 or (r[0] is None and r[6] is None): continue
        name = str(r[0] or '')
        lvl = (len(name) - len(name.lstrip())) // 2
        leaf = bool(r[1])
        rows.append([lvl, name.strip() if leaf else '', (str(r[1]).strip() if leaf else name.strip())[:120],
                     round(num(r[3]), 1), round(num(r[2]), 4), round(num(r[4]), 1), round(num(r[8]), 4), round(num(r[10]), 1)])
    top = rows[0]
    assert top[0] == 0 and top[3] > 1e6, ('first row is not the project total', top)
    leaves = [x for x in rows if x[1]]
    assert abs(sum(x[3] for x in leaves) - top[3]) / top[3] < 0.001, 'activity budgets do not add up to the project total'
    mak = sum(x[5] for x in leaves); pmc = sum(x[7] for x in leaves)
    assert abs(mak - top[5]) / top[5] < 0.002 and abs(pmc - top[7]) / top[7] < 0.002, ('earned units do not add up', mak, top[5], pmc, top[7])
    out = dict(date=date, head=head, total=dict(budget=top[3], mak=top[5], pmc=top[7], makp=top[4], pmcp=top[6]), rows=rows,
               cols=['level', 'id', 'name', 'budget', 'mak_pct', 'mak_earned', 'pmc_pct', 'pmc_earned'])
    os.makedirs(os.path.join(B, 'cmp'), exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        j = os.path.join(d, 'cmp.json'); json.dump(out, open(j, 'w'), separators=(',', ':'))
        subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', j, pw, os.path.join(B, 'cmp', 'cmp.bin')], check=True)
    print('ok:', len(rows), 'rows,', len(leaves), 'activities')


if __name__ == '__main__':
    main()
