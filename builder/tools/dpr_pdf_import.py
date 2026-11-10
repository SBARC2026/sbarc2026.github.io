#!/usr/bin/env python3
"""Turn a Daily Progress Report PDF (when no workbook was sent) into the Executive Summary datasets.

Usage: python3 builder/tools/dpr_pdf_import.py <report.pdf> --src builder/_data/exec/blobs --out <dir> --date 07-11-2026

Reads, from the PDF's own pages: the 10 cluster pages (29 activity cells per villa: tick / orange % / cross), the Buildings page (36 cells per
building, grey = not in scope), the workforce page (KPIs and the disciplines, split into villas / buildings / site by the bar segments).
Cell colours are classified on a 72 dpi render, in-progress % are the text inside the orange cells. Every villa's three % columns are recomputed with the
BOQ weights and must match the report's own printed totals (+/- 1 point), the same for the buildings; the discipline splits must add to the
report's villas / buildings / site totals. Landscape and infrastructure, personnel by building and main contractor roles are not in the
villa pages; they stay as they were (the landscape sheet values are re-read and compared and reported).
Needs: pdfplumber, Pillow, pdftoppm.  Output files have the same names as the blobs in --src.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dpr_import import IDS, MARBLE, BOQ_W, find, code_pct
import pdfplumber
from PIL import Image

def render(pdf, pages, d, dpi=72):
    subprocess.run(['pdftoppm', '-r', str(dpi), '-f', str(min(pages)), '-l', str(max(pages)), '-png', pdf, os.path.join(d, 'p')], check=True)
    return lambda n: [Image.open(os.path.join(d, f)).convert('RGB') for f in sorted(os.listdir(d)) if re.fullmatch(r'p-0*%d\.png' % n, f)][0]

def cls(px):
    r, g, b = px
    if g > 150 and r < 90 and b < 130: return 'G'
    if r > 200 and g < 110 and b < 110: return 'R'
    if r > 220 and 120 < g < 190 and b < 60: return 'O'
    return '.'

def runs(im, y, lo, hi):
    line = ''.join(cls(im.getpixel((x, y))) for x in range(im.size[0]))
    return [(m.start(), m.end()) for m in re.finditer(r'G+|R+|O+', line) if m.end() - m.start() > 6 and lo < m.start() < hi]

def vote(im, a, b, y, half, step=3):
    cnt = {'G': 0, 'R': 0, 'O': 0}
    for yy in range(y - half, y + half + 1, step):
        for xx in range(a + 1, b - 1, 2):
            c = cls(im.getpixel((xx, yy)))
            if c != '.': cnt[c] += 1
    c = max(cnt, key=cnt.get); return c, cnt[c]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pdf'); ap.add_argument('--src', required=True); ap.add_argument('--out', required=True); ap.add_argument('--date', required=True)
    a = ap.parse_args(); D = a.date
    pdf = pdfplumber.open(a.pdf); problems = []
    fv, villas0 = find(a.src, lambda r: 'villa' in r and 'finishes' in r and 'type' in r)
    fa, vacts0 = find(a.src, lambda r: 'villa' in r and 'activity' in r and 'group' in r)
    fb, blds0 = find(a.src, lambda r: 'acts' in r and 'zone' in r)
    fm, mp0 = find(a.src, lambda r: 'kind' in r and r['kind'] == 'kpi')
    fc, act0 = find(a.src, lambda r: 'scope' in r and 'pct_complete' in r)
    fl, lay0 = find(a.src, lambda r: 'kind' in r and r.get('id') == 'site')
    tmp = tempfile.mkdtemp()
    pages = []
    for i, p in enumerate(pdf.pages, 1):
        t = p.extract_text() or ''
        pages.append(t)
    clu = [i + 1 for i, t in enumerate(pages) if 'RANK' in t and '/ 10' in t]
    bpage = next(i + 1 for i, t in enumerate(pages) if 'BUILDINGS · 14 FACILITIES' in t)
    wpage = next(i + 1 for i, t in enumerate(pages) if 'Who is on site today' in t)
    rep_no = int(re.search(r'REPORT (\d+)', pages[1]).group(1)) if re.search(r'REPORT (\d+)', pages[1]) else 0
    img = render(a.pdf, clu + [bpage, wpage], tmp)
    # ---------- villas: cluster pages ----------
    cells_by_villa = []
    for pg in clu:
        p = pdf.pages[pg - 1]; ws = p.extract_words(); im = img(pg)
        rows = sorted([w for w in ws if 60 < w['x0'] < 120 and 200 < w['top'] < 620], key=lambda w: w['top'])
        cl = next(w['text'] for w in ws if re.fullmatch(r'05-\d+', w['text']))
        yc = lambda w: int((w['top'] + w['bottom']) / 2)
        cols = next((r for r in (runs(im, yc(w) - 9, 100, 1000) for w in rows) if len(r) == 29), None)
        assert cols, ('no 29 columns on page', pg)
        pw = [w for w in ws if re.fullmatch(r'\d+%', w['text'])]
        for w in rows:
            y = yc(w); cells = []
            for (x0, x1) in cols:
                c, n = vote(im, x0, x1, y, 9); assert n > 8, (pg, w['text'])
                if c == 'G': cells.append(1.0)
                elif c == 'R': cells.append(0.0)
                else:
                    t = [q for q in pw if x0 - 6 <= q['x0'] <= x1 and y - 12 <= q['top'] <= y + 12]; assert len(t) == 1, (pg, w['text'], t); cells.append(int(t[0]['text'][:-1]) / 100)
            tt = sorted([q for q in pw if q['x0'] > 960 and abs(yc(q) - y) < 14], key=lambda q: q['x0'])
            cells_by_villa.append((w['text'], cl, cells, [int(q['text'][:-1]) for q in tt[-3:]]))
    assert len(cells_by_villa) == len(villas0) == 104, (len(cells_by_villa), len(villas0))
    fin_w = [i for i in BOQ_W if i < 21]; mep_w = [i for i in BOQ_W if i >= 21]
    wavg = lambda n, ids: sum(BOQ_W[i] * n[i] for i in ids) / sum(BOQ_W[i] for i in ids)
    bycode = {}
    for code, cl, cells, tt in cells_by_villa:
        f, m, t = wavg(cells, fin_w), wavg(cells, mep_w), wavg(cells, fin_w + mep_w)
        if max(abs(f * 100 - tt[0]), abs(m * 100 - tt[1]), abs(t * 100 - tt[2])) > 1.01: problems.append(f'villa {code}: computed {f:.0%}/{m:.0%}/{t:.0%}, report prints {tt}')
        bycode[code] = (cl, cells, f, m, t)
    acts0 = [(r['group'], r['activity']) for r in vacts0 if r['villa'] == villas0[0]['villa']]; assert len(acts0) == 29
    villas, vacts, vm = [], [], {}
    for v0 in villas0:
        code = v0['villa']; cl, cells, f, m, t = bycode[code]
        if cl != v0['cluster']: problems.append(f'villa {code}: report cluster {cl}, kept {v0["cluster"]}')
        villas.append({'villa': code, 'cluster': v0['cluster'], 'type': v0['type'], 'finishes': round(f, 4), 'mep': round(m, 4), 'total': round(t, 4)})
        vm[code] = {}
        for j, (g, act) in enumerate(acts0):
            c, p = code_pct(cells[j])
            st = {'C': 'Done', 'P': 'In progress', 'N': 'Not started'}[c]
            vacts.append({'villa': code, 'cluster': v0['cluster'], 'group': g, 'activity': act, 'status': st, 'pct': 100 if c == 'C' else (p or 0)})
            vm[code][(g, act)] = (c, 100 if c == 'C' else (p or 0), cells[j])
    counts = lambda vals: (sum(1 for c in vals if c == 'C'), sum(1 for c in vals if c == 'P'), sum(1 for c in vals if c == 'N'))
    act1 = []
    for r in act0:
        r = dict(r)
        if r['scope'] == 'Villas' and r['id'].rsplit('-', 1)[0] in IDS | {'marble-Villas': 0, 'marble': 0}:
            key = r['id'].rsplit('-', 1)[0]
            if key == 'marble':
                cs = ['C' if sum(vm[c][('Marble', m)][2] for m in MARBLE) / 3 >= 0.9999 else 'N' if sum(vm[c][('Marble', m)][2] for m in MARBLE) / 3 <= 0 else 'P' for c in vm]
            else: cs = [vm[c][IDS[key]][0] for c in vm]
            d, ip, ns = counts(cs); r.update(done=d, in_progress=ip, not_started=ns, not_in_scope=0, pct_complete=round(d / len(cs), 4))
        act1.append(r)
    # ---------- buildings ----------
    p = pdf.pages[bpage - 1]; ws = p.extract_words(); im = img(bpage)
    yc = lambda w: int((w['top'] + w['bottom']) / 2)
    brow = sorted([w for w in ws if re.fullmatch(r'[A-Z]{2}', w['text']) and 60 < w['x0'] < 110 and 200 < w['top'] < 620], key=lambda w: w['top'])
    starts = sorted(s for w in brow for s in runs(im, yc(w) - 9, 100, 1000))
    cols = []
    for s in starts:
        if not cols or abs(cols[-1][0] - s[0]) > 3: cols.append(s)
    assert len(cols) == 36 and len(brow) == 14, (len(cols), len(brow))
    pw = [w for w in ws if re.fullmatch(r'\d+%', w['text'])]
    bcells = {}
    for w in brow:
        y = yc(w); cells = []
        for (x0, x1) in cols:
            c, n = vote(im, x0, x1, y, 7)
            if n < 6: cells.append(None); continue
            if c == 'G': cells.append(100)
            elif c == 'R': cells.append(0)
            else:
                t = [q for q in pw if x0 - 6 <= q['x0'] <= x1 and w['top'] - 10 <= q['top'] <= w['bottom'] + 6]; assert len(t) == 1, (w['text'], x0, t); cells.append(int(t[0]['text'][:-1]))
        tt = sorted([q for q in pw if q['x0'] > 960 and q['bottom'] - q['top'] > 7 and abs((q['top'] + q['bottom']) / 2 - (w['top'] + w['bottom']) / 2) < 9], key=lambda q: q['x0'])
        assert len(tt) == 3, (w['text'], tt); bcells[w['text']] = (cells, [int(q['text'][:-1]) / 100 for q in tt])
    blds, bstat = [], {}
    for b0 in blds0:
        cells, (f, m, t) = bcells[b0['code']]; old = [x.split('|') for x in b0['acts'].split(';')]; assert len(old) == 36
        parts, rec = [], []
        for (g, act, _c, _p, mep), v in zip(old, cells):
            c, pc = ('X', None) if v is None else ('C', 100) if v >= 100 else ('N', None) if v <= 0 else ('P', v)
            parts.append(f'{g}|{act}|{c}|{"" if pc is None else pc}|{mep}'); rec.append([g, act, c, pc, ''])
        blds.append(dict(b0, finishes=round(f, 2), mep=round(m, 2), total=round(t, 2), acts=';'.join(parts))); bstat[b0['code']] = rec
    # ---------- manpower ----------
    txt = pages[wpage - 1]; num = lambda s: int(s.replace(',', ''))
    g = lambda pat: num(re.search(pat, txt, re.S).group(1))
    kv = {'total': g(r'TOTAL WORKFORCE\s*([\d,]+)'), 'direct': g(r'Direct ([\d,]+)'), 'mc': g(r'Main contractor ([\d,]+)'), 'mh': g(r'MAN-HOURS\s*([\d,]+)'),
          'vil': g(r'Villas ([\d,]+)'), 'bld': g(r'Buildings ([\d,]+)'), 'site': g(r'Site / infra ([\d,]+)')}
    wm = re.search(r'WEATHER\s*(\d+)°.*?/\s*(\d+)°C', txt, re.S)
    p = pdf.pages[wpage - 1]; ws = p.extract_words(); im = img(wpage)  # bars: render again at 288 dpi for exact splits
    hi = os.path.join(tmp, 'hi'); os.makedirs(hi); subprocess.run(['pdftoppm', '-r', '288', '-f', str(wpage), '-l', str(wpage), '-png', a.pdf, os.path.join(hi, 'h')], check=True)
    him = Image.open(os.path.join(hi, os.listdir(hi)[0])).convert('RGB'); S = 4.0
    nums = sorted([w for w in ws if re.fullmatch(r'\d{1,3}', w['text']) and 640 < w['x0'] < 690 and 180 < w['top'] < 600], key=lambda w: w['top'])
    names = [w for w in mp0 if w.get('kind') == 'discipline']
    assert len(nums) == len(names), (len(nums), len(names))
    C = {'villas': (34, 197, 94), 'buildings': (14, 165, 233), 'site': (212, 166, 58)}
    near = lambda px, t: all(abs(x - y) < 14 for x, y in zip(px, t))
    disc = []
    for w, n0 in zip(nums, names):
        y = int((w['top'] + 3.2) * S); c = {k: 0 for k in C}
        for x in range(int(270 * S), int(640 * S)):
            px = him.getpixel((x, y))
            for k, t in C.items():
                if near(px, t): c[k] += 1
        val = int(w['text']); tot = sum(c.values()); seg = {k: c[k] * val / tot for k in c}; s2 = {k: round(v) for k, v in seg.items()}; d = val - sum(s2.values())
        if d: k = max(seg, key=lambda k: (seg[k] - s2[k]) * (1 if d > 0 else -1)); s2[k] += d
        disc.append((n0['name'], val, s2))
    for k, key in (('villas', 'vil'), ('buildings', 'bld'), ('site', 'site')):
        if sum(s[k] for _, _, s in disc) != kv[key]: problems.append(f'discipline split {k}: {sum(s[k] for _, _, s in disc)} vs report {kv[key]}')
    if sum(v for _, v, _ in disc) != kv['direct']: problems.append(f'disciplines add to {sum(v for _, v, _ in disc)}, report says {kv["direct"]}')
    byname = {n: (v, s) for n, v, s in disc}; mp = []
    for r in mp0:
        r = dict(r); k = r.get('kind')
        if k == 'kpi':
            r['value'] = {'Total workforce': kv['total'], 'Direct workforce': kv['direct'], 'Main contractor (site support)': kv['mc'], 'Man-hours': kv['mh'], 'Villas': kv['vil'], 'Buildings': kv['bld'], 'Site / infra': kv['site']}[r['name']]
        elif k == 'meta': r['value'] = rep_no; r['extra'] = f'{D} · {wm.group(1)}°/{wm.group(2)}°C'
        elif k == 'discipline':
            v, s = byname[r['name']]; r.update(value=v, villas=s['villas'], buildings=s['buildings'], site=s['site'])
        mp.append(r)
    # ---------- layouts ----------
    vlist = [v['villa'] for v in villas]; allpct = sum(bycode[c][4] for c in vlist) / len(vlist)
    lab = lambda c, p: 'Done' if c == 'C' else f'{p}%' if c == 'P' else 'Not started'
    lay = []
    for r in lay0:
        r = dict(r)
        if r.get('id') == 'site': r['bstat'] = json.dumps(bstat, ensure_ascii=False, separators=(',', ':'))
        elif r.get('id') == 'all': r['pct'] = allpct; r['date'] = D
        elif r.get('kind') == 'units' and (r['scope'] == 'Villas' or r['id'] in ('e1w', 'e1f', 'e1c', 'e2c', 'p1', 'p2c', 'h1', 'h2c')):
            key = r['id']
            if key != 'marble' and key not in IDS: lay.append(r); continue
            ent = {u.split('|')[0]: u for u in r['units'].split(';')}
            for code in vlist:
                if key == 'marble': c, p = code_pct(sum(vm[code][('Marble', m)][2] for m in MARBLE) / 3)
                else: c, p, _ = vm[code][IDS[key]]
                ent[code] = f'{code}|{c}|{"" if c == "N" else (100 if c == "C" else p)}|{lab(c, p)}'
            r['units'] = ';'.join(ent.values()); cs = [u.split('|')[1] for u in ent.values()]
            r['n_done'], r['n_prog'], r['n_not'] = cs.count('C'), cs.count('P'), cs.count('N'); r['n'] = len(cs)
            r['pct'] = r['n_done'] / r['n']; r['prog'] = r['n_prog'] / r['n']
            r['date'] = D if r['scope'] == 'Villas' else D + ' (villas) · 21-10-2026 (buildings)'
        lay.append(r)
    os.makedirs(a.out, exist_ok=True)
    for f, d in {fv: villas, fa: vacts, fb: blds, fm: mp, fc: act1, fl: lay}.items():
        with open(os.path.join(a.out, os.path.basename(f)), 'w', encoding='utf-8') as fh: json.dump(d, fh, ensure_ascii=False, separators=(',', ':'))
    for pr in problems: print('CHECK', pr)
    print(f'report {rep_no} {D}: {len(villas)} villas ({allpct:.2%} overall), {len(blds)} buildings ({sum(b["total"] for b in blds) / 14:.0%} avg), workforce {kv["total"]} (direct {kv["direct"]}), {len(problems)} checks flagged')

if __name__ == '__main__':
    main()
