"""Import the latest payment certificate (IPA) BOQ breakdown workbook -> builder/ipa/ipa.bin (encrypted with the portal password).

Usage:  SBARC_PASSWORD=... python3 builder/tools/ipa_import.py "<IPA n B.O.Q. Break. Rxx>.xlsx"

Reads GENERAL SUMMARY (bills, discount, grand totals), SECTIONS (work types, external-works packages) and every bill sheet (B1, B2.x ... B5.b)
line by line. Item amounts are scaled by the contract discount so they add up to the certified totals. Asserts the reconciliation
(items vs GENERAL SUMMARY) and stops if it fails. The repository is public: the output is only ever written encrypted, never as readable JSON.
"""
import json, os, re, subprocess, sys, tempfile
from openpyxl import load_workbook

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
num = lambda x: x if isinstance(x, (int, float)) and not isinstance(x, bool) else 0


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    pw = os.environ.get('SBARC_PASSWORD') or sys.exit('set SBARC_PASSWORD')
    wb = load_workbook(src, read_only=True, data_only=True)
    gs = [list(r) + [None] * 25 for r in wb['GENERAL SUMMARY'].iter_rows(min_row=1, max_row=70, values_only=True)]
    head = ' '.join(str(c) for r in gs[:8] for c in r[:1] if c)
    ipa = re.search(r'IPA Ref:\s*([^\n]+?)\s*(?:Period|$)', head)
    period = re.search(r'Period Ending:\s*(.+?)\s*$', [str(r[0]) for r in gs[:10] if r[0] and 'Period Ending' in str(r[0])][0])
    bills = []
    for r in gs:
        if isinstance(r[0], str) and r[0].startswith('BILL') and isinstance(r[5], (int, float)) and r[5] > 1000:
            bills.append(dict(id=r[0].title(), name=str(r[1]).title(), contract=r[21], orig=r[19], claimed=r[7], prev=num(r[15]), remaining=r[13]))
    grand = next(r for r in gs if r[1] == 'GRAND TOTALS')
    G = dict(contract=grand[5], orig=grand[19], discount=grand[20], claimed=grand[7], prev=num(grand[15]), remaining=grand[13])
    f = G['contract'] / G['orig']  # discount factor applied to every item
    # work types and external packages from SECTIONS
    secs, ext = [], []
    for i, r in enumerate(wb['SECTIONS'].iter_rows(min_row=1, max_row=600, values_only=True), 1):
        d = r[0]
        if not isinstance(d, str): continue
        if d.startswith('SECTION') and i < 519:
            secs.append(dict(name=d.strip(), contract=r[3], claimed=num(r[6]), remaining=num(r[9])))
        elif re.match(r'BILL NO\. 5\.\d - ', d) and i > 519:
            ext.append(dict(name=d.strip().title().replace('Bill No. ', 'Bill '), contract=r[3], claimed=num(r[6]), remaining=num(r[9])))
    # items
    items = []
    for s in wb.sheetnames:
        if not (s.startswith('B') and len(s) > 1 and s[1].isdigit()) or s.endswith('Sum'): continue
        cur = ''
        for i, r in enumerate(wb[s].iter_rows(min_row=10, values_only=True), 10):
            r = list(r) + [None] * 20
            d, unit, tot, cl = r[1], r[2], num(r[5]), num(r[7])
            if isinstance(d, str) and d.upper().startswith(('SECTION', 'BILL NO')): cur = d.strip()
            has_unit = isinstance(unit, str) and unit.strip()
            if not (tot or cl): continue
            if has_unit and 'Summary' in unit: continue
            if not (has_unit or (r[0] and isinstance(d, str) and not d.upper().startswith('SECTION') and num(r[3]) and num(r[4]))): continue
            items.append([s, str(r[0] or ''), str(d or '').strip()[:110], (unit or '').strip(), round(num(r[3]), 3), round(tot * f, 2), round(num(r[6]), 4), round(cl * f, 2),
                          round(num(r[15]) / tot, 4) if tot else 0, cur[:60], str(r[11] or '')[:70]])
    t = sum(x[5] for x in items); c = sum(x[7] for x in items)
    assert abs(t - G['contract']) < 5, ('contract does not reconcile', t, G['contract'])
    assert abs(c - G['claimed']) < 500, ('claimed does not reconcile', c, G['claimed'])
    out = dict(ipa=(ipa.group(1).strip() if ipa else ''), period=period.group(1) if period else '', grand=G, bills=bills, sections=secs, ext=ext, items=items,
               cols=['sheet', 'code', 'description', 'unit', 'qty', 'total', 'pct', 'claimed', 'pct_prev', 'section', 'comment'])
    os.makedirs(os.path.join(B, 'ipa'), exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        j = os.path.join(d, 'ipa.json'); json.dump(out, open(j, 'w'), separators=(',', ':'))
        subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', j, pw, os.path.join(B, 'ipa', 'ipa.bin')], check=True)
    print('ok:', len(items), 'items,', len(bills), 'bills,', len(secs), 'work types')


if __name__ == '__main__':
    main()
