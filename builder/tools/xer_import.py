#!/usr/bin/env python3
"""Import a Primavera P6 schedule (.xer) for the Gantt chart in the Primavera tab.

Usage:  SBARC_PASSWORD=... python3 builder/tools/xer_import.py <schedule.xer>

Reads the PROJECT, PROJWBS (hierarchy) and TASK tables and writes builder/p6/gantt.bin: compact figures encrypted with the portal
password (the repository is public). build.py copies it to docs/p6/gantt.bin; the browser fetches and decrypts it when the Gantt opens.
Bars: completed activities use actual start / finish, active ones actual start and forecast finish, not-started ones the early dates.
The baseline bar is the target (planned) start / finish. % complete is duration based here; the portal swaps in earned labour units
from the weekly export where the activity ID matches.
"""
import datetime, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); OUT = os.path.join(B, 'p6')
EPOCH = datetime.date(2020, 1, 1)

def tables(path):
    T, cur = {}, None
    with open(path, encoding='cp1252', errors='replace', newline='') as fh:
        for line in fh:
            p = line.rstrip('\r\n').split('\t')
            if p[0] == '%T': cur = p[1]; T[cur] = {'f': [], 'r': []}
            elif p[0] == '%F': T[cur]['f'] = p[1:]
            elif p[0] == '%R': T[cur]['r'].append(p[1:])
    return T

def rows(T, n):
    f = T[n]['f']; return [dict(zip(f, r)) for r in T[n]['r']]

def day(s):
    if not s: return None
    d = datetime.date.fromisoformat(s[:10]); return (d - EPOCH).days

def num(s, nd=1):
    try: return round(float(s), nd)
    except ValueError: return None

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    pw = os.environ.get('SBARC_PASSWORD') or sys.exit('Set SBARC_PASSWORD.')
    T = tables(path)
    proj = rows(T, 'PROJECT')[0]; W = rows(T, 'PROJWBS'); K = rows(T, 'TASK')
    byid = {w['wbs_id']: w for w in W}; kids = {}
    for w in W: kids.setdefault(w['parent_wbs_id'], []).append(w)
    for v in kids.values(): v.sort(key=lambda w: (int(w['seq_num'] or 0), w['wbs_short_name']))
    has = {k['wbs_id'] for k in K}
    root = [w for w in W if not w['parent_wbs_id'] or w['parent_wbs_id'] not in byid]
    keep = {}
    def mark(w):  # does this node or anything below it hold activities?
        ok = w['wbs_id'] in has
        for c in kids.get(w['wbs_id'], []): ok = mark(c) or ok
        keep[w['wbs_id']] = ok; return ok
    sys.setrecursionlimit(10000)
    for r in root: mark(r)
    wbs, idx = [], {}
    def walk(w, parent):
        if not keep[w['wbs_id']]: return
        idx[w['wbs_id']] = len(wbs); wbs.append([parent, w['wbs_short_name'], w['wbs_name']])
        for c in kids.get(w['wbs_id'], []): walk(c, idx[w['wbs_id']])
    for r in root: walk(r, -1)
    names, nidx, tasks = [], {}, []
    for k in sorted(K, key=lambda k: (idx.get(k['wbs_id'], 1 << 30), k['task_code'])):
        if k['wbs_id'] not in idx: continue
        st = {'TK_NotStart': 0, 'TK_Active': 1, 'TK_Complete': 2}[k['status_code']]
        ty = {'TT_Task': 0, 'TT_LOE': 1, 'TT_Mile': 2, 'TT_FinMile': 2, 'TT_WBS': 1, 'TT_Rsrc': 0}.get(k['task_type'], 0)
        if st == 2: s, e = day(k['act_start_date']), day(k['act_end_date'])
        elif st == 1: s, e = day(k['act_start_date']), day(k['early_end_date'])
        else: s, e = day(k['early_start_date']), day(k['early_end_date'])
        bs, be = day(k['target_start_date']), day(k['target_end_date'])
        s = s if s is not None else (bs if bs is not None else e); e = e if e is not None else (be if be is not None else s)
        if s is None: continue
        if e < s: e = s
        nm = k['task_name']
        if nm not in nidx: nidx[nm] = len(names); names.append(nm)
        fl = num(k['total_float_hr_cnt'], 0)
        tasks.append([idx[k['wbs_id']], k['task_code'], nidx[nm], st, ty, s, e, bs if bs is not None else s, be if be is not None else e,
                      num(k['target_drtn_hr_cnt']) or 0, num(k['remain_drtn_hr_cnt']) or 0, None if fl is None else round(fl / 8)])
    doc = {'epoch': EPOCH.isoformat(), 'name': proj['proj_short_name'], 'dd': (proj['last_recalc_date'] or '')[:10], 'start': (proj['plan_start_date'] or '')[:10],
           'end': (proj['scd_end_date'] or '')[:10], 'wbs': wbs, 'names': names, 'tasks': tasks}
    os.makedirs(OUT, exist_ok=True); tmp = os.path.join(OUT, '.gantt.json')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    subprocess.run(['node', os.path.join(B, 'encrypt.js'), '--bin', tmp, pw, os.path.join(OUT, 'gantt.bin')], check=True)
    sz = os.path.getsize(tmp); os.remove(tmp)
    print(f'{len(wbs)} WBS nodes, {len(tasks)} activities, data date {doc["dd"]}, plain {sz // 1024} KB, file {os.path.getsize(os.path.join(OUT, "gantt.bin")) // 1024} KB')

if __name__ == '__main__':
    main()
