#!/usr/bin/env python3
"""Build the SBARC Project Portal site from the latest dashboard data.

Usage:
  SBARC_PASSWORD=... python3 builder/build.py          # build site/ from builder/_data
  python3 builder/build.py --needs                     # list data files still to download (JSON)

Output goes to docs/, which GitHub Pages publishes. builder/_data/<dash>/ is filled from the two Claude dashboards before building (see UPDATE.md).
It holds the readable figures, so it is never committed (.gitignore). Only the encrypted site is.
"""
import base64, glob, hashlib, json, mimetypes, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'builder')
DATA = os.path.join(B, '_data')
SITE = os.path.join(ROOT, 'docs')  # published by GitHub Pages (main branch, /docs)
T = os.path.join(B, 'templates')

DASHBOARDS = [
    {'id': 'exec', 'title': 'Executive Summary', 'url': 'https://claude.ai/artifact/UGmYsefN6QhW1Mt17uqpRS'},
    {'id': 'p02b', 'title': 'Management Tracking', 'url': 'https://claude.ai/artifact/88dbsUWtiu6vG7kdgZB7dK'},
]
EMAIL = os.environ.get('SBARC_UPDATE_EMAIL', '')  # where 'Send update' emails go; kept out of the repository

def rd(p, mode='r'):
    with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()

def b64(p):
    return base64.b64encode(rd(p, 'rb')).decode()

def doc(path):
    d = json.loads(rd(path))
    return d.get('data', d) if isinstance(d, dict) and isinstance(d.get('data'), dict) else d

def js_json(o):
    t = o if isinstance(o, str) else json.dumps(o, separators=(',', ':'), ensure_ascii=False)
    return t.replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

# ------------------------------------------------------------------ data access
def datasets(dash):
    out = {}
    for p in sorted(glob.glob(f'{DATA}/{dash}/datasets/*.json')):
        out[os.path.basename(p)[:-5]] = doc(p)
    return out

def blob_id(url):
    return url.rsplit('/', 1)[-1]

def blob_path(dash, bid):
    return f'{DATA}/{dash}/blobs/{bid}.json'

def asset_refs(o, acc):
    if isinstance(o, dict):
        for v in o.values(): asset_refs(v, acc)
    elif isinstance(o, list):
        for v in o: asset_refs(v, acc)
    elif isinstance(o, str) and o.startswith('/_blob/'):
        acc.add(o[7:])
    return acc

def needs():
    missing = []
    for d in DASHBOARDS:
        dash, url = d['id'], d['url']
        if not os.path.exists(f'{DATA}/{dash}/files/index.html.json'):
            missing.append({'dashboard': dash, 'what': 'page', 'tool': 'ArtifactData list', 'url': url, 'collection': 'files', 'out_dir': f'builder/_data/{dash}'})
        ds = datasets(dash)
        if not ds:
            missing.append({'dashboard': dash, 'what': 'datasets', 'tool': 'ArtifactData list', 'url': url, 'collection': 'datasets', 'out_dir': f'builder/_data/{dash}'})
            continue
        for name, meta in ds.items():
            bid = blob_id(meta['source']['url'])
            if not os.path.exists(blob_path(dash, bid)):
                missing.append({'dashboard': dash, 'what': f'dataset {name}', 'tool': 'Artifact read', 'url': url, 'path': bid, 'out_dir': f'builder/_data/{dash}/blobs'})
                continue
            for aid in sorted(asset_refs(json.loads(rd(blob_path(dash, bid))), set())):
                if not glob.glob(f'{DATA}/{dash}/assets/{aid}.*'):
                    missing.append({'dashboard': dash, 'what': f'asset in {name}', 'tool': 'Artifact read', 'url': url, 'path': aid, 'out_dir': f'builder/_data/{dash}/assets'})
    return missing

# ------------------------------------------------------------------ fonts, frames
def face(family, path, weight, extra=''):
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{b64(path)}) format('woff2');font-weight:{weight};font-style:normal;font-display:block;{extra}}}"

F = os.path.join(B, 'fonts')
FONTCSS = '<style>' + ''.join([
    face('Archivo', f'{F}/archivo-latin-wdth-normal.woff2', '100 900', 'font-stretch:62% 125%;'),
    *[face('IBM Plex Sans', f'{F}/ibm-plex-sans-latin-{w}-normal.woff2', w) for w in ('400', '500', '600', '700')],
    *[face('IBM Plex Mono', f'{F}/ibm-plex-mono-latin-{w}-normal.woff2', w) for w in ('400', '500', '600')],
]) + '</style>'

BASE_HEAD = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{color-scheme:light;box-sizing:border-box}body{margin:0;padding:0;font:14px "IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>
'''
TOKENS = FONTCSS + '\n<style>' + rd(f'{T}/tokens.css') + '''
body{background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:var(--cds-font-size-body);line-height:1.45}
#dash-root{padding:24px max(16px,3vw) 40px}
</style>'''
D3_TAG = '<script>' + rd(f'{B}/vendor/d3.min.js').replace('</script', '<\\/script') + '</script>'
DASH_SHIM = rd(f'{T}/dash_shim.html')
GLASS_CSS = '<style>' + rd(f'{T}/glass.css') + '</style>'

def inline_assets(dash, o):
    if isinstance(o, dict): return {k: inline_assets(dash, v) for k, v in o.items()}
    if isinstance(o, list): return [inline_assets(dash, v) for v in o]
    if isinstance(o, str) and o.startswith('/_blob/'):
        hits = glob.glob(f'{DATA}/{dash}/assets/{o[7:]}.*')
        if not hits: raise SystemExit(f'missing asset {o} for {dash}: run --needs')
        mt = mimetypes.guess_type(hits[0])[0] or 'application/octet-stream'
        return f'data:{mt};base64,' + b64(hits[0])
    return o

def dash_frame(dash, glass=False):
    """glass=True: the site version (glass theme on by default); False: the PDF version (original look)."""
    page = doc(f'{DATA}/{dash}/files/index.html.json')['text']
    data = {name: json.loads(rd(blob_path(dash, blob_id(meta['source']['url'])))) for name, meta in datasets(dash).items()}
    data = inline_assets(dash, data)
    pp = f'{DATA}/{dash}/dash/params.json'
    params = doc(pp) if os.path.exists(pp) else {}
    pre = '<script>window.__DATA__=' + js_json(data) + ';window.__PARAMS__=' + js_json(params) + ';</script>'
    h = BASE_HEAD + TOKENS + (GLASS_CSS if glass else '') + D3_TAG + pre + DASH_SHIM + '</head><body><div id="dash-root">' + page + '</div></body></html>'
    if glass:
        h = h.replace('<!doctype html><html>', '<!doctype html><html class="glass" data-theme="dark">', 1)
    h = h.replace('--font-anthropic-sans', '--font-ui-sans').replace('--font-anthropic-serif', '--font-ui-display')
    return h

# ------------------------------------------------------------------ entrance artwork (site plan from the Executive Summary layouts)
CLUSTER_COLORS = ['#5FD3B6', '#7CC4F2', '#E8C27A', '#B9A6F2', '#F2A07C', '#8EE08A', '#F28FB5', '#6FE0E0', '#F2D86B', '#A8B8F5']

def site_geometry():
    ds = datasets('exec')
    rows = json.loads(rd(blob_path('exec', blob_id(ds['layouts']['source']['url']))))
    s = [r for r in rows if r.get('kind') == 'site'][0]
    villas = [(v.split(',')[0], float(v.split(',')[1]), float(v.split(',')[2]), v.split(',')[3]) for v in s['villas'].split(';')]
    blds = [(v.split(',')[0], float(v.split(',')[1]), float(v.split(',')[2])) for v in s['buildings'].split(';')]
    clusters = [(c.split(',')[0], float(c.split(',')[1]), float(c.split(',')[2])) for c in s['clusters'].split(';')]
    nums = list(map(float, re.findall(r'-?[0-9.]+', s['boundary'])))
    xs, ys = nums[0::2], nums[1::2]
    vb = (min(xs) - 60, min(ys) - 60, max(xs) - min(xs) + 120, max(ys) - min(ys) + 120)
    plan = glob.glob(f'{DATA}/exec/assets/{s["plan"][7:]}.*')[0] if s.get('plan') else None
    return {'boundary': s['boundary'], 'villas': villas, 'buildings': blds, 'clusters': clusters, 'vb': vb, 'plan': plan}

def art_detailed():
    g = site_geometry()
    vb = ' '.join(f'{v:.0f}' for v in g['vb'])
    col = {n: CLUSTER_COLORS[i % len(CLUSTER_COLORS)] for i, (n, _, _) in enumerate(g['clusters'])}
    counts = {}
    for *_, cl in g['villas']: counts[cl] = counts.get(cl, 0) + 1
    dots = ''.join(
        f'<circle class="v" cx="{x:.0f}" cy="{y:.0f}" r="17" style="--d:{(i % 26) * 0.045 + (i // 26) * 0.12:.2f}s;fill:{col.get(cl, "#5FD3B6")}"><title>Villa {vid} · cluster {cl}</title></circle>'
        for i, (vid, x, y, cl) in enumerate(g['villas']))
    blds = ''.join(f'<g class="b"><rect x="{x - 50:.0f}" y="{y - 27:.0f}" width="100" height="54" rx="12"/><text x="{x:.0f}" y="{y + 1:.0f}">{n}</text><title>Building {n}</title></g>' for n, x, y in g['buildings'])
    tags = ''.join(f'<g class="c" style="--cc:{col[n]}"><rect x="{x - 72:.0f}" y="{y - 44:.0f}" width="144" height="74" rx="16"/>'
                   f'<text class="c1" x="{x:.0f}" y="{y - 16:.0f}">{n}</text><text class="c2" x="{x:.0f}" y="{y + 14:.0f}">{counts.get(n, 0)} villas</text></g>' for n, x, y in g['clusters'])
    plan = ''
    if g['plan']:
        plan = f'<image class="plan" href="data:image/png;base64,{b64(g["plan"])}" x="0" y="0" width="3370" height="2384" preserveAspectRatio="none" clip-path="url(#bclip)"/>'
    return (f'<svg class="art" viewBox="{vb}" preserveAspectRatio="xMidYMid meet" aria-label="SBARC site plan">'
            f'<defs><clipPath id="bclip"><path d="{g["boundary"]}"/></clipPath></defs><path class="fillb" d="{g["boundary"]}"/>{plan}'
            f'<path class="glow" d="{g["boundary"]}"/><path class="bd" d="{g["boundary"]}" pathLength="1000"/>'
            f'<g class="bs">{blds}</g><g class="vs">{dots}</g><g class="cs">{tags}</g></svg>')

def logos_row():
    L = [('kharafi', 'Mohammed Abdulmohsin Al-Kharafi &amp; Sons'), ('gcd', 'Gulf Coast Development'), ('sterling', 'Sterling Ark')]
    return '<div class="logos">' + ''.join(f'<span class="lg lg-{n}"><img src="data:image/png;base64,{b64(f"{B}/logos/{n}.png")}" alt="{a}"></span>' for n, a in L) + '</div>'

def blob_rows(dash, name):
    return json.loads(rd(blob_path(dash, blob_id(datasets(dash)[name]['source']['url']))))

def explorer_data(status):
    """Compact villa / building / cluster data for the Site explorer tab (encrypted with the rest)."""
    g = site_geometry()
    site = [r for r in blob_rows('exec', 'layouts') if r.get('kind') == 'site'][0]
    acts, idx, per = [], {}, {}
    code = {'Done': 'C', 'In progress': 'P', 'Not started': 'N', 'Not in scope': 'X'}
    for r in blob_rows('exec', 'villa_activities'):
        k = (r['group'], r['activity'])
        if k not in idx: idx[k] = len(acts); acts.append(list(k))
        per.setdefault(r['villa'], {})[idx[k]] = (code.get(r['status'], 'N'), r.get('pct'))
    villas = {}
    for v in blob_rows('exec', 'villas'):
        a = per.get(v['villa'], {})
        villas[v['villa']] = [v['cluster'], v.get('type', ''), round(v['finishes'], 4), round(v['mep'], 4), round(v['total'], 4),
                              ''.join(a.get(i, ('X', None))[0] for i in range(len(acts))),
                              [a.get(i, ('X', None))[1] if a.get(i, ('X', None))[0] == 'P' else None for i in range(len(acts))]]
    def js(t):
        try: return json.loads(t or '{}')
        except ValueError: return {}
    return {'status': status, 'vb': [round(x) for x in g['vb']], 'boundary': g['boundary'],
            'pos': [[n, round(x), round(y), c] for n, x, y, c in g['villas']], 'bpos': [[n, round(x), round(y)] for n, x, y in g['buildings']],
            'cpos': [[n, round(x), round(y)] for n, x, y in g['clusters']], 'acts': acts, 'villas': villas,
            'vx': js(site.get('vextra')), 'bs': js(site.get('bstat'))}

def dmy(iso):
    return f'{iso[8:10]}-{iso[5:7]}-{iso[0:4]}'

def dates():
    ex = datasets('exec')
    m = re.search(r'Status date (\d\d-\d\d-\d{4})', ex.get('villas', {}).get('description', ''))
    stamps = [(meta.get('updated') or {}).get('at', '') for d in DASHBOARDS for meta in datasets(d['id']).values()]
    latest = max(s for s in stamps if s) if any(stamps) else ''
    if not m:  # e.g. "Site tracker in the Daily Progress Report 28-10-2026."
        m = re.search(r'(\d\d-\d\d-\d{4})', ex.get('villas', {}).get('description', ''))
    status = m.group(1) if m else dmy(latest)
    try:  # Management Tracking: latest reported week end
        p02b = dmy(max(r['week_end'] for r in blob_rows('p02b', 'actuals') if r.get('week_end')))
    except Exception:
        p02b = dmy(max((meta.get('updated') or {}).get('at', '') for meta in datasets('p02b').values()))
    return status, dmy(latest), p02b

ANDROID_TWEAK = '<script>if(/; wv\\)/.test(navigator.userAgent))document.write(' + json.dumps(rd(f'{T}/android_body.html')).replace('</', '<\\/') + ');</script>'

def build():
    if not EMAIL:
        raise SystemExit('Set SBARC_UPDATE_EMAIL (the address team updates are sent to) before building.')
    if not os.environ.get('SBARC_PASSWORD'):
        raise SystemExit('Set SBARC_PASSWORD (the portal password) before building.')
    miss = needs()
    if miss:
        print(json.dumps(miss, indent=1)); raise SystemExit(f'{len(miss)} data file(s) missing; download them first (see UPDATE.md).')
    status, issued, status_p02b = dates()
    frames = {d['id']: dash_frame(d['id']) for d in DASHBOARDS}           # PDFs: original print look
    site_frames = {d['id']: dash_frame(d['id'], glass=True) for d in DASHBOARDS}  # site: glass theme
    geo = site_geometry()
    pdf_list = pdfs.build_pdfs(frames, {'fontcss': FONTCSS, 'logos': logos_row(), 'art': pdfs.cover_art(geo), 'issued': issued,
                                        'status': {'exec': status, 'p02b': status_p02b}},
                               SITE, os.path.join(B, '_data'), os.environ['SBARC_PASSWORD'], os.path.join(B, 'encrypt.js'))
    # Site explorer tab removed at the owner's request (28-10-2026). To bring it back, add
    # {'id': 'explorer', 'title': 'Site explorer', 'native': True} to tabs and 'explorer': explorer_data(status) to the payload.
    tabs = [{'id': d['id'], 'title': d['title']} for d in DASHBOARDS] + [{'id': 'week', 'title': 'This week', 'native': True}]
    payload = {'project': 'SBARC', 'dashboards': tabs, 'frames': site_frames, 'upload': {'email': EMAIL}, 'pdfs': pdf_list}
    tmp = os.path.join(B, '_data', 'payload.json')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    vault_p = os.path.join(B, '_data', 'vault.json')
    subprocess.run(['node', os.path.join(B, 'encrypt.js'), tmp, os.environ['SBARC_PASSWORD'], vault_p], check=True)
    os.remove(tmp)
    v = json.loads(rd(vault_p))
    projects = [{'name': 'SBARC', 'aliases': ['sbarc project', 'phase 02-b', 'phase 02b', 'phase 2b'],
                 'vault': {'id': 'SBARC', 'salt': v['salt'], 'iv': v['iv'], 'iter': v['iter']}}]
    pwa_head = '''<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#0C1D38">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="SBARC">
<meta name="application-name" content="SBARC">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">'''
    t = rd(f'{T}/portal.html')
    reps = {
        '<!--FONTCSS-->': FONTCSS, '<!--ART-->': art_detailed(), '<!--LOGOS-->': logos_row(),
        '<!--STATUS-->': status, '<!--ISSUED-->': issued,
        '<!--VAULT-->': '<script type="text/plain" id="vault-SBARC">' + v['ct'] + '</script>',
        '<!--CRYPTOJS-->': '<script>' + rd(f'{B}/vendor/crypto-js.js').replace('</script', '<\\/script') + '</script>',
        '/*PROJECTS*/[]': json.dumps(projects),
        '<!--PWAHEAD-->': pwa_head, '<!--PWABODY-->': rd(f'{T}/pwa_body.html') + ANDROID_TWEAK,
    }
    for k, val in reps.items():
        assert t.count(k) == 1, k
        t = t.replace(k, val)
    low = t.lower()
    assert 'claude' not in low and 'anthropic' not in low, 'vendor name leaked into the page'
    assert EMAIL not in t, 'readable data leaked into the page'
    os.makedirs(f'{SITE}/icons', exist_ok=True)
    with open(f'{SITE}/index.html', 'w', encoding='utf-8') as f: f.write(t)
    for name in ('manifest.webmanifest', '_headers', 'web.config', 'install.html'):
        shutil.copy(f'{T}/{name}', f'{SITE}/{name}')
    for name in ('icon-192.png', 'icon-512.png', 'maskable-192.png', 'maskable-512.png', 'apple-touch-icon.png', 'favicon-32.png'):
        shutil.copy(f'{B}/icons/{name}', f'{SITE}/icons/{name}')
    version = hashlib.sha256(t.encode()).hexdigest()[:12]
    with open(f'{SITE}/sw.js', 'w') as f: f.write(rd(f'{T}/sw.js.tpl').replace('__VERSION__', version))
    open(f'{SITE}/.nojekyll', 'w').close()  # serve every file as-is (no Jekyll)
    with open(f'{SITE}/version.json', 'w') as f: json.dump({'status': status, 'data_updated': issued, 'build': version}, f)
    print(f'site built: status {status}, data updated {issued}, version {version}, index {len(t.encode()) // 1024} KB')

if __name__ == '__main__':
    if '--needs' in sys.argv:
        m = needs(); print(json.dumps(m, indent=1)); sys.exit(3 if m else 0)
    build()
