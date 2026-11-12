#!/usr/bin/env python3
"""Rebuild the slides of the SBARC Earned Value presentation from the portal data.

Nothing in the slides is typed by hand: every figure comes from
  - the P6 weekly export        builder/p6/p6.bin (encrypted; needs SBARC_PASSWORD)
  - the exec dashboard          builder/_data/exec   (daily report: villas, buildings, manpower, site layout)
  - the Management Tracking dashboard  builder/_data/frame_p02b.html (recovery plan, actuals)
  - builder/deck_config.json    handover sequence and target dates (edit this file for the handover slide)

Usage:  SBARC_PASSWORD=... python3 builder/tools/deck_build.py --out <folder> [--today YYYY-MM-DD]
Writes  <folder>/project/slides/{progress,manpower,works,villas,external,handover}.html
(the published Slides artifact keeps its own deck.json; slide ids and order stay as they are).
Nothing readable is stored in the repository: the folder is a scratch folder.
"""
import argparse, datetime, json, math, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_style

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EXEC = os.path.join(ROOT, 'builder', '_data', 'exec')
FRAME = os.path.join(ROOT, 'builder', '_data', 'frame_p02b.html')
CFG = os.path.join(ROOT, 'builder', 'deck_config.json')

BC = "font-family:'Barlow Condensed', Arial, sans-serif"
SG = "font-family:'Space Grotesk', Arial, sans-serif"
STRIPE = ('<div style="position:absolute;left:0;top:0;width:960px;height:10px;background:#14304F"></div>'
          '<div style="position:absolute;left:960px;top:0;width:960px;height:10px;background:#C9A227"></div>\n')
def logos_html():
    L = json.load(open(CFG)).get('logos') or []
    if not L: return ''
    imgs = ''.join(f'<img src="{l["src"]}" alt="{esc(l["alt"])}" style="width:{l["w"]}px;height:68px;object-fit:contain;border-radius:8px">' for l in L)
    return f'<div style="position:absolute;right:128px;top:30px;display:flex;flex-direction:row;gap:14px;align-items:center">{imgs}</div>\n'


MO = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


# ---------------------------------------------------------------- data
def exec_ds(name):
    d = json.load(open(os.path.join(EXEC, 'datasets', name + '.json')))
    return json.load(open(os.path.join(EXEC, 'blobs', d['source']['url'].split('/')[-1] + '.json')))


def p6_data():
    pw = os.environ.get('SBARC_PASSWORD')
    if not pw:
        sys.exit('SBARC_PASSWORD is not set')
    out = tempfile.mktemp(suffix='.json')
    subprocess.run(['node', os.path.join(ROOT, 'builder', 'decrypt.js'), os.path.join(ROOT, 'builder', 'p6', 'p6.bin'), pw, out], check=True, capture_output=True)
    d = json.load(open(out)); os.remove(out)
    return d


def frame_data():
    from playwright.sync_api import sync_playwright
    js = """() => { const d = window.dash, g = (k) => d.data(k).data; const la = g('latest_actual')[0];
      const T = g('activities').reduce((s, r) => s + Number(r.budget), 0);
      const act = {}; g('activities').forEach((r) => { act[r.activity] = { area: r.area, budget: +r.budget, e0: +r.earned }; });
      g('actuals').forEach((r) => { if (r.week_end === la.date && act[r.activity]) act[r.activity].er = +r.earned_to_date; });
      Object.values(act).forEach((a) => { if (a.er == null) a.er = a.e0; });
      const by = {}; g('actuals').forEach((r) => { by[r.week_end] = (by[r.week_end] || 0) + (+r.earned_to_date); });
      const wa = {}; g('weekly_activities').forEach((r) => { (wa[r.activity] = wa[r.activity] || { area: r.area, finish: r.finish, m: {} }).m[r.month] = r.month_pts * T; });
      return { T, la, act, wa, by, updates: g('updates'), wt: g('weekly_totals').filter((r) => r.scope === 'All'), rs: (g('recovery_summary') || [])[0] }; }"""
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto('file://' + FRAME); pg.wait_for_timeout(4000)
        out = pg.evaluate(js); b.close()
    return out


# ---------------------------------------------------------------- helpers
def fd(s):
    y, m, d = map(int, s.split('-')); return f"{d} {MO[m - 1]}" + (f" {str(y)[2:]}" if y != 2026 else '')


def fdl(s):
    y, m, d = map(int, s.split('-')); return f"{d} {MO[m - 1]} {y}"


def n0(v): return f"{round(v):,}"
def pct2(v): return f"{v * 100:.2f}%"
def esc(s): return s.replace('&', '&amp;')


def slide(sid, kick, title, body, aside, note=None, pad='96px 128px 120px', gap=20, tsize=64, font="'Barlow', Arial, sans-serif"):
    foot = f'<p style="position:absolute;left:128px;bottom:56px;width:1664px;font-size:24px;color:#5A6577">{note}</p>\n' if note else ''
    return f'''<section id="{sid}" data-transition="fade" style="background:#F6F4EE;color:#14304F;font-family:{font};padding:{pad};display:flex;flex-direction:column;gap:{gap}px">
{STRIPE}{logos_html()}<div style="position:relative;display:flex;flex-direction:column;gap:6px">
<p style="font-size:24px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#8A6A12">{kick}</p>
<h1 style="{BC};font-size:{tsize}px;font-weight:700;line-height:1">{title}</h1>
</div>
{body}
{foot}<aside>{aside}</aside>
</section>
'''


CARD = 'background:#FFFEFB;border:1px solid #DDD8CA;border-radius:16px;padding:24px 28px'


# ---------------------------------------------------------------- slide 1: actual vs planned
def s_progress(F, P6):
    tot = P6['total']; la = F['la']; T = F['T']
    actual = la['actual_pct']; plan = la['plan_pct']; gap = plan - actual
    pv = tot['pvu'] / tot['bu']; spi = tot['eu'] / tot['pvu']
    date = la['date']
    # S-curve
    t0 = datetime.date(2026, 8, 28)
    X = lambda s: 80 + (datetime.date.fromisoformat(s) - t0).days * 900 / 156
    Y = lambda p: 20 + (1 - p) * 1384.5
    act_pts = [('2026-08-28', F['updates'][0]['earned'] / F['updates'][0]['budget']), ('2026-09-25', F['updates'][1]['earned'] / F['updates'][1]['budget'])]
    act_pts += [(d, e / T) for d, e in sorted(F['by'].items()) if d > '2026-09-25']
    act_pts = [(d, p) for d, p in act_pts if d <= date]
    wt = [r for r in F['wt'] if r.get('to')]
    plan_pts = [(wt[0]['from'], wt[0]['cum_pct'] - wt[0]['pts'])] + [(r['to'], r['cum_pct']) for r in wt]
    plan_pts = [(d, p) for d, p in plan_pts if d >= '2026-09-25']
    if plan_pts[-1][0] < '2027-01-31': plan_pts.append(('2027-01-31', 1.0))
    pline = ' '.join(('M' if i == 0 else 'L') + f"{X(d):.1f} {Y(p):.1f}" for i, (d, p) in enumerate(plan_pts))
    aline = ' '.join(('M' if i == 0 else 'L') + f"{X(d):.1f} {Y(p):.1f}" for i, (d, p) in enumerate(act_pts))
    xa, ya = X(date), Y(actual)
    ms = F['rs'] or {}; mdate = ms.get('deadline', '2026-12-31'); mpct = ms.get('plan_dec_pct', 0.937)
    ticks = ''.join(f'<line x1="{X(f"{y}-{m:02d}-01"):.1f}" y1="380" x2="{X(f"{y}-{m:02d}-01"):.1f}" y2="388" stroke="#7C8798" stroke-width="2"/>' for y, m in ((2026, 9), (2026, 10), (2026, 11), (2026, 12), (2027, 1)))
    mlab = ''.join(f'<p style="position:absolute;top:386px;left:{X(f"{y}-{m:02d}-01") + 6:.0f}px;width:80px;font-family:Inter, Arial, sans-serif;font-size:24px;color:#5a6577">{n}</p>' for y, m, n in ((2026, 9, 'Sep'), (2026, 10, 'Oct'), (2026, 11, 'Nov'), (2026, 12, 'Dec'), (2027, 1, 'Jan')))
    dots = ''.join(f'<circle cx="{X(d):.1f}" cy="{Y(p):.1f}" r="7" fill="#FFFEFB" stroke="#2E6FB7" stroke-width="4"/>' for d, p in act_pts[:-1])
    ypl = Y(plan)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 420" aria-label="S-curve: actual earned progress from {act_pts[0][1] * 100:.2f}% on 28 Aug to {actual * 100:.2f}% on {fd(date)} 2026, against the recovery plan rising to {mpct * 100:.1f}% on {fd(mdate)} 2026 and 100% on 31 Jan 2027" style="width:1000px; height:420px">
<line x1="80" y1="{Y(.8):.1f}" x2="980" y2="{Y(.8):.1f}" stroke="#DDD8CA" stroke-width="2"/><line x1="80" y1="{Y(.9):.1f}" x2="980" y2="{Y(.9):.1f}" stroke="#DDD8CA" stroke-width="2"/><line x1="80" y1="20" x2="980" y2="20" stroke="#DDD8CA" stroke-width="2"/><line x1="80" y1="380" x2="980" y2="380" stroke="#7C8798" stroke-width="2"/>
{ticks}
<line x1="{xa:.1f}" y1="20" x2="{xa:.1f}" y2="380" stroke="#14304F" stroke-width="2" stroke-dasharray="4 6"/>
<path d="{pline}" fill="none" stroke="#7C8798" stroke-width="4" stroke-dasharray="10 8"/>
<path d="{aline} L{xa:.1f} 380 L80 380 Z" fill="#2E6FB7" fill-opacity="0.12"/>
<path d="{aline}" fill="none" stroke="#2E6FB7" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>
{dots}
<circle cx="{xa:.1f}" cy="{ya:.1f}" r="9" fill="#2E6FB7" stroke="#FFFEFB" stroke-width="3"/>
<circle cx="{xa:.1f}" cy="{ypl:.1f}" r="7" fill="#7C8798" stroke="#FFFEFB" stroke-width="3"/>
<path d="M{X(mdate):.1f} {Y(mpct) - 12:.1f} l12 12 l-12 12 l-12 -12 Z" fill="#8A6A12"/><path d="M980 8 l12 12 l-12 12 l-12 -12 Z" fill="#8A6A12"/>
</svg>'''
    labels = (f'<p style="position:absolute;top:{Y(.8) - 17:.0f}px;left:0;width:70px;font-family:Inter, Arial, sans-serif;font-size:24px;text-align:right;color:#5a6577">80%</p>'
              f'<p style="position:absolute;top:{Y(.9) - 17:.0f}px;left:0;width:70px;font-family:Inter, Arial, sans-serif;font-size:24px;text-align:right;color:#5a6577">90%</p>'
              '<p style="position:absolute;top:3px;left:0;width:70px;font-family:Inter, Arial, sans-serif;font-size:24px;text-align:right;color:#5a6577">100%</p>' + mlab +
              f'<p style="position:absolute;top:{ya + 11:.0f}px;left:{xa + 18:.0f}px;width:260px;font-family:Inter, Arial, sans-serif;font-size:24px;font-weight:600;color:#1f5594">Actual {actual * 100:.2f}%</p>'
              f'<p style="position:absolute;top:{ypl - 48:.0f}px;left:{xa - 248:.0f}px;width:230px;font-family:Inter, Arial, sans-serif;font-size:24px;font-weight:600;text-align:right;color:#5a6577">Plan {plan * 100:.2f}%</p>'
              f'<p style="position:absolute;top:{Y(mpct) - 20:.0f}px;left:{X(mdate) - 245:.0f}px;width:225px;font-family:Inter, Arial, sans-serif;font-size:24px;font-weight:600;text-align:right;color:#8a6a12">{mpct * 100:.1f}% · {fd(mdate)}</p>'
              '<p style="position:absolute;top:24px;left:672px;width:200px;font-family:Inter, Arial, sans-serif;font-size:24px;font-weight:600;text-align:right;color:#8a6a12">100% · 31 Jan</p>')
    # gained activities
    G = []
    for g in P6['groups']:
        t = {k: sum(a[k] for a in g['areas']) for k in ('bu', 'pvu', 'eu', 'wk')}
        if t['bu'] and t['wk'] > 0: G.append((g['n'], t))
    G.sort(key=lambda x: -x[1]['wk'])
    nm = lambda n: ('Zone ' + n) if re.fullmatch(r'A\d+', n) else n.replace('Fixand', 'Fix and')
    wk_total = sum(t['wk'] for _, t in G); behind = sum(1 for _, t in G if t['eu'] < t['pvu'])
    show = G[:14]
    rows = ''.join(f'<tr><td>{esc(nm(n))}</td><td style="text-align:right">+{n0(t["wk"])}</td></tr>' for n, t in show)
    more = f'<p style="font-family:Inter, Arial, sans-serif; font-size:24px; color:#5a6577">+ {len(G) - len(show)} more smaller gains</p>' if len(G) > len(show) else ''

    def kpi(l, v, s, c='#14304f'):
        return f'<div style="display:flex; flex-direction:column; gap:8px; flex:1; padding:24px 28px; background:#fffefb; border:1px solid #ddd8ca; border-radius:14px"><p style="font-family:Inter, Arial, sans-serif; font-size:24px; color:#5a6577">{l}</p><p style="font-family:\'Space Grotesk\', Arial, sans-serif; font-size:60px; font-weight:700; line-height:1.1; color:{c}">{v}</p><p style="font-family:Inter, Arial, sans-serif; font-size:24px; color:#5a6577">{s}</p></div>'
    sign = '−' if gap > 0 else '+'
    cards = (kpi('Actual earned', pct2(actual), f'{n0(la["earned"])} of {n0(T)} MH') + kpi('Recovery plan (Plan A)', pct2(plan), f'planned at {fd(date)} 2026') +
             kpi('Variance to Plan A', f'{sign}{abs(gap) * 100:.2f} pts', f'{n0(abs(gap) * T)} MH {"behind" if gap > 0 else "ahead"}', '#a8440f' if gap > 0 else '#17694a'))
    body = f'''<div style="display:flex; flex-direction:row; gap:24px">{cards}</div>
<div style="display:flex; flex-direction:row; gap:40px; align-items:start">
<div style="position:relative; width:1000px; height:420px; display:flex; flex-direction:column">{svg}{labels}</div>
<div style="display:flex; flex-direction:column; gap:14px; flex:1">
<h3 style="font-family:'Space Grotesk', Arial, sans-serif; font-size:28px; font-weight:700; color:#14304f">Activities gained last week</h3>
<table style="font-family:Inter, Arial, sans-serif; font-size:24px; color:#14304f"><tr><th style="font-weight:600; width:70%; color:#5a6577">Activity</th><th style="font-weight:600; width:30%; text-align:right; color:#5a6577">Gain (MH)</th></tr>{rows}</table>{more}
<p style="font-family:Inter, Arial, sans-serif; font-size:24px; line-height:1.3; color:#46546a">{len(G)} activities gained <b>+{n0(wk_total)} MH</b>; {behind} of them are still behind plan.</p>
</div></div>'''
    aside = (f"Actual earned labour units are {pct2(actual)} at the {fdl(date)} data date. The recovery plan (Plan A) called for {pct2(plan)}, so the project is {abs(gap) * 100:.2f} points, or {n0(abs(gap) * T)} man-hours, {'behind' if gap > 0 else 'ahead of'} it. "
             f"The table lists the {len(G)} P6 activities that gained progress in the week, {n0(wk_total)} man-hours in total; {behind} of them are still behind plan.")
    return slide('progress', 'SBARC · Earned value · Labour units', 'Actual vs planned progress', body, aside, pad='96px 128px 96px', gap=28, tsize=60, font="'Inter', Arial, sans-serif").replace(f'<h1 style="{BC};font-size:60px', f'<h1 style="{SG};font-size:60px')


# ---------------------------------------------------------------- slide 2: manpower
def s_manpower(M):
    kp = {r['name']: r['value'] for r in M if r['kind'] == 'kpi'}
    meta = next((r for r in M if r['kind'] == 'meta'), {})
    D = sorted([r for r in M if r['kind'] == 'discipline'], key=lambda r: -r['value'])
    direct = kp['Direct workforce']; mx = D[0]['value']
    date = (meta.get('extra') or '').split(' ')[0]
    try: dlab = fdl(datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d'))
    except Exception: dlab = date
    vi, bu, si = kp['Villas'], kp['Buildings'], kp['Site / infra']

    def card(c, l, v, s):
        return f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;background:#FFFEFB;border:1px solid #DDD8CA;border-radius:14px;box-shadow:0 2px 8px rgba(20,48,79,0.06);padding:24px 28px"><div style="width:40px;height:5px;border-radius:3px;background:{c}"></div><p style="font-size:24px;color:#5A6577">{l}</p><p style="{SG};font-size:60px;font-weight:700;line-height:1.1;color:#14304F">{v}</p><p style="font-size:24px;color:#5A6577">{s}</p></div>'
    cards = (card('#14304F', 'Direct workforce on site', f'{direct:,}', dlab) + card('#14304F', 'Villas', f'{vi:,}', f'{vi / direct * 100:.1f}% of direct') +
             card('#6FA3DC', 'Buildings', f'{bu:,}', f'{bu / direct * 100:.1f}% of direct') + card('#D9822B', 'Site / infrastructure', f'{si:,}', f'{si / direct * 100:.1f}% of direct'))
    G2 = 'display:grid;grid-template-columns:380px 120px 150px 110px 90px;column-gap:12px;align-items:center'
    H2 = lambda t, r=1: f'<p style="font-size:24px;color:#5A6577;{"text-align:right" if r else ""}">{t}</p>'
    cells = H2('DISCIPLINE', 0) + H2('VILLAS') + H2('BUILDINGS') + H2('SITE') + H2('TOTAL')
    for r in D:
        z = lambda v: '<span style="color:#9AA3B2">–</span>' if not v else str(v)
        nm2 = esc(r["name"].replace(" and ", " & ", 1) if r["name"].startswith("Infra") else r["name"])
        cells += (f'<p style="font-size:24px;line-height:1.2;border-top:1px solid #ECE8DC;padding:1px 0">{nm2}</p>' + ''.join(f'<p style="font-size:24px;line-height:1.2;text-align:right;border-top:1px solid #ECE8DC;padding:1px 0">{z(r[k])}</p>' for k in ('villas', 'buildings', 'site'))
                  + f'<p style="font-size:24px;line-height:1.2;font-weight:700;text-align:right;border-top:1px solid #ECE8DC;padding:1px 0">{r["value"]}</p>')
    bars = f'<div style="{G2}">{cells}</div>'
    top2 = D[0]['value'] + D[1]['value']
    area = ''

    def leg(c, l, v): return f'<div style="display:flex;gap:14px;align-items:center"><div style="width:18px;height:18px;border-radius:4px;background:{c}"></div><p style="flex:1;font-size:24px">{l}</p><p style="font-size:24px;font-weight:600">{v:,} · {v / direct * 100:.1f}%</p></div>'
    right = f'''<div style="flex:1;display:flex;flex-direction:column;gap:14px">
<h3 style="{SG};font-size:28px;font-weight:700;color:#14304F">Distribution by area</h3>
<div style="display:flex;flex-direction:column;gap:4px">{leg('#14304F', 'Villas', vi)}{leg('#6FA3DC', 'Buildings', bu)}{leg('#D9822B', 'Site / infrastructure', si)}</div>
<h3 style="{SG};font-size:28px;font-weight:700;color:#14304F;padding:10px 0 0 0">Concentration</h3>
<div style="display:flex;flex-direction:column;gap:4px"><div style="display:flex;gap:14px;align-items:center"><p style="flex:1;font-size:24px">Top two disciplines</p><p style="font-size:24px;font-weight:600">{top2:,} · {top2 / direct * 100:.1f}%</p></div><div style="display:flex;gap:14px;align-items:center"><p style="flex:1;font-size:24px">Other {len(D) - 2} disciplines</p><p style="font-size:24px;font-weight:600">{direct - top2:,} · {(direct - top2) / direct * 100:.1f}%</p></div></div>
<p style="font-size:24px;line-height:1.35;color:#5A6577">Top two: {esc(D[0]['name'].lower())}, and {esc(D[1]['name'].lower())}.</p></div>'''
    body = f'''<div style="display:flex;gap:24px">{cards}</div>
<div style="display:flex;gap:56px;align-items:flex-start"><div style="width:940px;display:flex;flex-direction:column;gap:11px;background:#FFFEFB;border:1px solid #DDD8CA;border-radius:14px;box-shadow:0 2px 8px rgba(20,48,79,0.06);padding:24px 28px">{bars}</div>{right}</div>'''
    aside = (f"The direct workforce on site on {dlab} was {direct:,}: {vi:,} on villas, {bu:,} on buildings and {si:,} on site and infrastructure. {D[0]['name']} ({D[0]['value']}) and {D[1]['name']} ({D[1]['value']}) are the two largest disciplines, together {top2:,} people or {top2 / direct * 100:.1f}% of the direct workforce. "
             "Main contractor site support is not included.")
    return slide('manpower', f"SBARC · Resources · Daily report {meta.get('value', '')}", 'Site manpower', body, aside, pad='72px 128px 72px', gap=28, tsize=60, font="'Inter', Arial, sans-serif").replace(f'<h1 style="{BC};font-size:60px', f'<h1 style="{SG};font-size:60px')


# ---------------------------------------------------------------- slides 3-5: every activity with Nov / Dec and finish
def plan_rows(F):
    act, wa = F['act'], F['wa']
    get = lambda names, label: dict(name=label, budget=sum(act[n]['budget'] for n in names), er=sum(act[n]['er'] for n in names),
                                    nov=sum(wa[n]['m'].get('Nov', 0) for n in names), dec=sum(wa[n]['m'].get('Dec', 0) for n in names), fin=max(wa[n]['finish'] for n in names))
    clean = lambda n: n.split(' — ')[0]
    order = lambda L: sorted(L, key=lambda n: (wa[n]['finish'], -act[n]['budget']))
    V = [get([n], clean(n)) for n in order([n for n in wa if wa[n]['area'] == 'Villas'])]
    B = [get([n], clean(n)) for n in order([n for n in wa if wa[n]['area'] == 'Buildings'])]
    I = [n for n in wa if wa[n]['area'] == 'Infrastructure & landscape']; Pw = [n for n in wa if wa[n]['area'] == 'Project-wide']
    used = set(); ext = []
    GROUPS = [(['Storm Water Network - Zones & Clusters', 'Storm Water Network - Sea Outfall'], 'Storm water network'),
              (['Sanitary Network - Main Loop', 'Sanitary Network - Zones & Clusters'], 'Sanitary network (main, zones)'),
              (['Sanitary Network - Lifting Station'], 'Sanitary lifting station'), ([f'A{i}' for i in range(1, 12)], 'Zones A1 to A11'),
              (['All Services except SWA'], 'All services except SWA'), (['LV & ELV System - Zones & Clusters'], 'LV & ELV (zones)'), (['LV & ELV System - Main Loop'], 'LV & ELV (main loop)'),
              (['Street Light - Zones & Clusters'], 'Street light (zones)'), (['Street Light - Main Loop'], 'Street light (main loop)'),
              (['Kerbstone - Main Loop', 'Kerbstone - Zones & Clusters'], 'Kerbstone'), (['Paving Works - Main Loop', 'Paving Works - Zones & Clusters'], 'Paving works'),
              (['Roundabout (Zone G)'], 'Roundabout (Zone G)'), (['Main Entrance Road'], 'Main entrance road'), (['Boundary Wall'], 'Boundary wall'),
              (['Interlock Tiles - Zones & Clusters'], 'Interlock (zones)'), (['Interlock Tiles - Main Loop'], 'Interlock (main loop)'), (['Special Tiles'], 'Special tiles'),
              (['Softscape'], 'Softscape'), (['Misc Item'], 'Misc. items'), (['Activities outside Plot'], 'Activities outside plot'), (['Signage'], 'Signage'),
              (['Road Furniture'], 'Road furniture'), (['Tie-ins'], 'Tie-ins')]
    for names, label in GROUPS:
        names = [n for n in names if n in wa]
        if names: used.update(names); ext.append(get(names, label))
    for n in sorted(set(I) - used, key=lambda n: wa[n]['finish']):  # any activity the plan adds later is listed on its own
        ext.append(get([n], n))
    ext += [get([n], n) for n in sorted(Pw, key=lambda n: (wa[n]['finish'], n))]
    return V, B, ext


def s_plan(F, V, B, ext, today):
    la = F['la']; date = la['date']
    NOTE = (f'Done = earned share of the activity at the {fd(date)} P6 update. Nov and Dec = share of the activity planned for that month in the recovery plan (Plan A). '
            'Expected finish = Plan A finish; red = past its finish date and not complete.')
    HDR = lambda t, r=0: f'<p style="font-size:24px;letter-spacing:2px;color:#5A6577;{"text-align:right" if r else ""}">{t}</p>'
    pc = lambda v, b: '–' if v < 0.5 else ('&lt;1%' if v / b * 100 < 0.5 else f'{round(v / b * 100)}%')
    dc = lambda p: '#17694A' if p >= 90 else ('#14304F' if p >= 30 else '#A8440F')

    def fin(r, size, bt):
        p = r['er'] / r['budget'] * 100; od = r['fin'] < today and p < 99.5
        return f'<p style="{BC};font-size:{size}px;font-weight:700;color:{"#A8440F" if od else "#14304F"};{bt}">{fd(r["fin"])}</p>'

    def full(rows):
        G = 'display:grid;grid-template-columns:760px 150px 150px 150px 250px;column-gap:20px;align-items:center;padding:0 4px'
        h = HDR('ACTIVITY') + HDR('DONE ' + fd(date).upper(), 1) + HDR('NOV', 1) + HDR('DEC', 1) + HDR('EXPECTED FINISH')
        c = ''
        for r in rows:
            p = r['er'] / r['budget'] * 100; bt = 'border-top:1px solid #ECE8DC;padding:7px 0'
            c += (f'<p style="{BC};font-size:30px;font-weight:600;{bt}">{esc(r["name"])}</p>'
                  f'<p style="{BC};font-size:30px;font-weight:700;text-align:right;color:{dc(p)};{bt}">{round(p)}%</p><p style="{BC};font-size:30px;font-weight:700;text-align:right;{bt}">{pc(r["nov"], r["budget"])}</p><p style="{BC};font-size:30px;font-weight:700;text-align:right;{bt}">{pc(r["dec"], r["budget"])}</p>{fin(r, 30, bt)}')
        return f'<div style="{G}">{h}{c}</div>'

    def half(rows):
        G = 'display:grid;grid-template-columns:350px 80px 84px 84px 140px;column-gap:10px;align-items:center'
        h = HDR('ACTIVITY') + HDR('DONE', 1) + HDR('NOV', 1) + HDR('DEC', 1) + HDR('FINISH')
        c = ''
        for r in rows:
            p = r['er'] / r['budget'] * 100; bt = 'border-top:1px solid #ECE8DC;padding:2px 0'
            c += (f'<p style="{BC};font-size:26px;font-weight:600;line-height:1.05;{bt}">{esc(r["name"])}</p><p style="{BC};font-size:26px;font-weight:700;text-align:right;color:{dc(p)};{bt}">{round(p)}%</p>'
                  f'<p style="{BC};font-size:26px;font-weight:700;text-align:right;{bt}">{pc(r["nov"], r["budget"])}</p><p style="{BC};font-size:26px;font-weight:700;text-align:right;{bt}">{pc(r["dec"], r["budget"])}</p>{fin(r, 26, bt)}')
        return f'<div style="{G}">{h}{c}</div>'

    def aside_for(rows, what):
        return f"{what}: every planned activity with its progress at the {fdl(date)} P6 update, the share planned for November and December in the recovery plan (Plan A) and its Plan A finish date. " + '; '.join(f"{r['name']} {round(r['er'] / r['budget'] * 100)}% done, finish {fd(r['fin'])}" for r in rows) + '.'
    s3 = slide('works', 'Recovery plan · Villas', 'Villas · every activity', f'<div style="{CARD};display:flex;flex-direction:column">{full(V)}</div>', aside_for(V, 'Villas'), NOTE)
    s4 = slide('villas', 'Recovery plan · Buildings', 'Buildings · every activity', f'<div style="{CARD};display:flex;flex-direction:column">{full(B)}</div>', aside_for(B, 'Buildings'), NOTE)
    k = (len(ext) + 1) // 2
    body = f'<div style="display:flex;gap:24px"><div style="flex:1;{CARD}">{half(ext[:k])}</div><div style="flex:1;{CARD}">{half(ext[k:])}</div></div>'
    s5 = slide('external', f'Recovery plan · {len(ext)} lines, matching networks grouped · status {fd(date)} 2026', 'External works · every activity', body, aside_for(ext, 'External works and project-wide items'), NOTE, tsize=60)
    return s3, s4, s5


# ---------------------------------------------------------------- slide 6: partial handover
def s_handover(L, VI, VA):
    cfg = json.load(open(CFG))['handover']
    site = next(x for x in L if x['kind'] == 'site')
    vill = [v.split(',') for v in site['villas'].split(';')]
    bld = [b.split(',') for b in site['buildings'].split(';')]
    cls = {c.split(',')[0]: c.split(',') for c in site['clusters'].split(';')}
    tot = {v['villa']: v['total'] for v in VI}
    cl_of = {v['villa']: v['cluster'] for v in VI}
    step_of = {c: i for i, s in enumerate(cfg['steps']) for c in s['clusters']}
    COL = [s['color'] for s in cfg['steps']]; TINT = [s['tint'] for s in cfg['steps']]
    circ = ''.join(f'<circle cx="{x}" cy="{y}" r="38" fill="{COL[step_of[c]] if c in step_of else "#C4CAD3"}"/>' for _, x, y, c in vill)
    rect = ''.join(f'<rect x="{int(x) - 34}" y="{int(y) - 34}" width="68" height="68" rx="8" fill="#14304F"/>' for _, x, y in bld)
    ready_lab = ' '.join(f'cluster {c}' for c in cfg['steps'][0]['clusters'])
    svg = (f'<svg aria-label="Site layout: {len(vill)} villas coloured by handover sequence. Dark squares are the {len(bld)} buildings." width="780" height="627" viewBox="-23 -5 3038 2443">'
           f'<path d="{site["boundary"]}" fill="#F1EEE4" stroke="#B9B29D" stroke-width="10" stroke-linejoin="round"/>{circ}{rect}</svg>')
    lab = ''
    for c, v in sorted(cls.items()):
        n = int(c.split('-')[1]); left = (int(v[1]) + 23) * 780 / 3038 - 22; top = (int(v[2]) + 5) * 627 / 2443 - 17
        lab += f'<p style="position:absolute;left:{left:.0f}px;top:{top:.0f}px;width:{50 if n > 9 else 44}px;text-align:center;font-size:24px;font-weight:600;color:#14304F;text-shadow:0 0 4px #FFFEFB, 0 0 4px #FFFEFB, 0 0 6px #FFFEFB">{n}</p>'
    mp = (f'<div style="position:relative;width:780px;height:627px;background:#FFFEFB;border:1px solid #DDD8CA;border-radius:14px">{svg}{lab}'
          f'<p style="position:absolute;left:24px;top:20px;width:420px;font-size:24px;color:#5A6577">Numbers = cluster 05-n</p><p style="position:absolute;left:24px;bottom:18px;width:420px;font-size:24px;color:#5A6577">■ Buildings ({len(bld)})</p></div>')
    cavg = lambda c: sum(tot[v] for v in tot if cl_of[v] == c) / sum(1 for v in tot if cl_of[v] == c)
    cnt = lambda cs: sum(1 for v in cl_of if cl_of[v] in cs)
    thr = cfg.get('handover_pct')
    wd = lambda d: datetime.date.fromisoformat(d).strftime('%a') + ' ' + fd(d)
    pcol = lambda v: '#17694A' if thr and v * 100 >= thr - 0.5 else '#A8440F'
    rows = ''; planned = set()
    for i, s in enumerate(cfg['steps']):
        planned.update(s['clusters'])
        prog = ' · '.join(f'<span style="color:{pcol(cavg(c))}">{cavg(c) * 100:.0f}%</span>' for c in s['clusters'])
        st = f'<span style="color:#17694A">✓ {s.get("done_label", "Done")}</span>' if s.get('done') else wd(s['date'])
        rows += (f'<tr style="background:{TINT[i]}"><td>{i + 1}</td><td>{", ".join(s["clusters"])}</td><td style="text-align:right">{cnt(s["clusters"])}</td>'
                 f'<td style="text-align:right">{prog}</td><td style="text-align:right">{s.get("target_pct", thr)}%</td><td style="text-align:right">{st}</td></tr>')
    rest = sorted(set(cls) - planned, key=lambda c: -cavg(c))
    th = lambda w, t, r=0: f'<th style="width:{w}%;text-align:{"right" if r else "left"};color:#5A6577;font-weight:600">{t}</th>'
    tbl = f'<table style="font-size:24px;color:#14304F;padding:12px 10px"><tr>{th(5, "#")}{th(24, "Clusters")}{th(10, "Villas", 1)}{th(20, "Progress", 1)}{th(11, "Target", 1)}{th(30, "Status", 1)}</tr>{rows}</table>'
    dot = lambda c, t: f'<p style="font-size:24px;color:#46546A"><span style="color:{c}">●</span> {t}</p>'
    legend = '<div style="display:flex;gap:24px;flex-wrap:wrap">' + ''.join(dot(COL[i], cfg['steps'][i].get('legend') or f'Step {i + 1}') for i in range(len(COL))) + dot('#C4CAD3', 'Later') + '</div>'
    first = [v for v in cl_of if cl_of[v] in cfg['steps'][0]['clusters']]
    plan_v = [v for v in cl_of if cl_of[v] in planned]
    done_ed = {r['villa'] for r in VA if r['activity'] == 'External doors' and r['status'] == 'Done'}
    todo_cl = {c for s in cfg['steps'] if not s.get('done') for c in s['clusters']}
    todo_v = [v for v in cl_of if cl_of[v] in todo_cl]
    need = sum(1 for v in todo_v if v not in done_ed)
    s0 = cfg['steps'][0]
    ns = next((x for x in cfg['steps'] if not x.get('done')), None)
    nxt = (f" Next: {' and '.join(ns['clusters'])} at {' and '.join(f'{cavg(c) * 100:.0f}%' for c in ns['clusters'])} now, to reach {thr}% by {fd(ns['date'])}." if ns and thr else '')

    def stat(big, tc, t):
        return f'<div style="flex:1;display:flex;flex-direction:column;gap:6px;background:#FFFEFB;border:1px solid #DDD8CA;border-radius:14px;box-shadow:0 2px 8px rgba(20,48,79,0.06);padding:20px 22px"><p style="{SG};font-size:44px;font-weight:700;line-height:1.1;color:{tc}">{big}</p><p style="font-size:24px;line-height:1.3;color:#46546A">{t}</p></div>'
    cards = []
    done_v = [v for v in cl_of if any(cl_of[v] in s['clusters'] for s in cfg['steps'] if s.get('done'))]
    if done_v: cards.append(stat(f'{len(done_v)} villas', '#17694A', 'Partially handed over: ' + ', '.join(c for s in cfg['steps'] if s.get('done') for c in s['clusters'])))
    if ns:
        gap = max(0, thr - min(cavg(c) * 100 for c in ns['clusters'])) if thr else 0
        cards.append(stat(fd(ns['date']), '#2E6FB7', f'Next: {", ".join(ns["clusters"])} · {cnt(ns["clusters"])} villas' + (f' · +{gap:.0f} pts to {thr}%' if gap >= 0.5 else '')))
    cards.append(stat(f'{need} villas', '#A8440F', f'of the {len(todo_v)} still to hand over need external doors'))
    stats = '<div style="display:flex;gap:16px">' + ''.join(cards) + '</div>'
    right = f'<div style="flex:1;display:flex;flex-direction:column;gap:22px"><h3 style="{SG};font-size:28px;font-weight:700;color:#14304F">Sequence · partial handover at {thr}% progress</h3>{tbl}{legend}{stats}</div>'
    body = f'<div style="display:flex;gap:48px;align-items:flex-start">{mp}{right}</div>'
    seq = '; '.join(f'step {i + 1}: {", ".join(s["clusters"])} ({cnt(s["clusters"])} villas), {"handed over (partial)" if s.get("done") else "target " + fdl(s["date"])}' for i, s in enumerate(cfg['steps']))
    aside = (f'The November plan covers {len(cfg["steps"][0]["clusters"]) + sum(len(s["clusters"]) for s in cfg["steps"][1:])} villa clusters, {len(plan_v)} villas. Sequence and target dates: {seq}. '
             f'{"The other clusters are not in the plan and have no target date yet. " if rest else ""}{cfg["status_note"]}{nxt} Target dates are the dates set in the handover configuration, not contractual handover dates.')
    return slide('handover', cfg['kicker'], cfg.get('title', 'Partial handover layout &amp; plan'), body, aside, pad='96px 128px 96px', gap=28, tsize=60, font="'Inter', Arial, sans-serif").replace(f'<h1 style="{BC};font-size:60px', f'<h1 style="{SG};font-size:60px')


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--today', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    out = os.path.join(a.out, 'project', 'slides'); os.makedirs(out, exist_ok=True)
    P6 = p6_data(); F = frame_data()
    V, B, ext = plan_rows(F)
    s3, s4, s5 = s_plan(F, V, B, ext, a.today)
    slides = {'progress': s_progress(F, P6), 'manpower': s_manpower(exec_ds('manpower')), 'works': s3, 'villas': s4, 'external': s5,
              'handover': s_handover(exec_ds('layouts'), exec_ds('villas'), exec_ds('villa_activities'))}
    for k, s in slides.items():
        flat = re.sub(r'<svg\b.*?</svg>', '<svg></svg>', s, flags=re.S)  # an svg counts as one element
        n = len(re.findall(r'<(?:div|p|h1|h2|h3|svg|img|tr|td|th|table|span|b)\b', flat))
        s = deck_style.band(s)
        open(os.path.join(out, k + '.html'), 'w').write(s)
        print(f'{k}: {len(s):,} bytes, ~{n} elements' + ('  WARNING: near the 200-element limit' if n > 190 else ''))


if __name__ == '__main__':
    main()
