#!/usr/bin/env python3
"""Import the contract BOQ (items and amounts) into the portal.

Usage:  SBARC_PASSWORD=... python3 builder/tools/boq_import.py <SBARC Rules of Credit artifact .html | boq.json>

The source is the "SBARC Rules of Credit" artifact (BOQ 5.3 - IPA 24 B.O.Q. Break R00): its data block holds the work types with their
rules of credit (rules), every priced BOQ line (lines: bill, item, description, unit, amount, work-type code, section) and the bills.
The result goes to builder/boq/boq.bin, encrypted with the portal password (the repository is public, so the amounts never go in it).
build.py decrypts it and adds the BOQ tab.
"""
import json, os, subprocess, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    pw = os.environ.get('SBARC_PASSWORD') or sys.exit('Set SBARC_PASSWORD.')
    t = open(src, encoding='utf-8').read()
    if src.endswith('.json'): D = json.loads(t)
    else:
        i = t.index('const D = ') + len('const D = '); D, _ = json.JSONDecoder().raw_decode(t[i:])
    assert D['rules'] and D['lines'] and D['bills'], 'unexpected layout'
    tot = sum(r['v'] for r in D['rules']); ln = sum(l[4] for l in D['lines'])
    assert abs(tot - ln) < 50, (tot, ln)
    assert abs(sum(b[3] for b in D['bills']) - ln) < 50
    os.makedirs(os.path.join(B, 'boq'), exist_ok=True)
    tmp = os.path.join(B, 'boq', 'boq.json')
    json.dump(D, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', tmp, pw, os.path.join(B, 'boq', 'boq.bin')], check=True)
    os.remove(tmp)
    print(f'BOQ: {len(D["lines"])} lines, {len(D["rules"])} work types, {len(D["bills"])} bills, total {ln:,.0f}')

main()
