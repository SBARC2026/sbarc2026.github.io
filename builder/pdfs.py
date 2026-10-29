"""Full-report PDFs for the portal's PDF menu (Executive Summary, Management Tracking).

Rendered from the same dashboard frames as the site, with a cover page, then encrypted with the portal
password so only signed-in users can open them. Rebuilt only when the figures change, because Chromium
PDFs are never byte-identical and each rebuild adds several MB to the repository.
Needs Playwright (pre-installed) and pypdf (`pip install pypdf`).
"""
import asyncio, hashlib, hmac, io, json, os, subprocess

W = 1440

PDF_CSS = """*,*::before,*::after{animation:none!important;transition:none!important}
.sb-nav,#pc-present,.pc-present,.pc-ctl{display:none!important}
.sb-rise{opacity:1!important;transform:none!important}
*{filter:none!important;backdrop-filter:none!important;box-shadow:none!important;text-shadow:none!important}"""

EXPAND = """(() => {
  document.querySelectorAll('*').forEach((el) => {
    const cs = getComputedStyle(el);
    if (/(auto|scroll)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 4 && el.tagName !== 'HTML' && el.tagName !== 'BODY') { el.style.maxHeight = 'none'; el.style.height = 'auto'; el.style.overflowY = 'visible'; }
  });
})()"""

P02B_TABS = [('overview', 'Overview & S-curve'), ('general-plan', 'General plan'), ('recovery', 'Dec recovery plan'), ('dec-target', 'December target'),
             ('weekly-targets', 'Weekly targets'), ('after-dec', 'After December'), ('lookahead', 'Lookahead'), ('remaining', 'Remaining work')]


def cover_html(fontcss, logos, art, doc_title, doc_sub, status, issued, contents):
    items = ''.join(f'<li><span>{t}</span><i></i><b>{n}</b></li>' for t, n in contents)
    return f"""<!doctype html><html><head><meta charset="utf-8">{fontcss}<style>
:root{{--gold:#E8C27A;--ink:#F3F6FA;--mut:#8FA3BD;--line:#2A4066}}
html,body{{margin:0;width:{W}px;height:900px}}
body{{background:radial-gradient(1100px 760px at 74% 46%,#173561 0%,#0C1D38 55%,#081326 100%);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(143,163,189,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(143,163,189,.06) 1px,transparent 1px);background-size:40px 40px}}
.frame{{position:absolute;inset:28px;border:1.5px solid rgba(232,194,122,.35)}}
.art{{position:absolute;right:30px;top:70px;width:860px;height:760px}}
.art .glow{{fill:none;stroke:var(--gold);stroke-width:34;opacity:.10}}
.art .bd{{fill:rgba(20,44,78,.55);stroke:var(--gold);stroke-width:9;stroke-linejoin:round}}
.art .v{{fill:#5FD3B6;opacity:.75}}
.art .b{{fill:rgba(143,163,189,.12);stroke:#8FA3BD;stroke-width:4}}
.art .c{{fill:var(--gold);font:700 40px Archivo;font-stretch:80%;text-anchor:middle;opacity:.9}}
.left{{position:absolute;left:92px;top:64px;width:440px}}
.logos{{position:absolute;left:92px;bottom:40px;display:flex;gap:12px}}
.lg{{height:56px;display:flex;align-items:center;border-radius:9px;overflow:hidden;background:#fff;padding:4px 7px;box-shadow:0 0 0 1px rgba(232,194,122,.35)}}
.lg img{{height:100%;width:auto;display:block}}
.lg-sterling{{padding:0;background:#000}}
.eyebrow{{font:500 15px 'IBM Plex Mono';letter-spacing:.22em;text-transform:uppercase;color:var(--gold)}}
h1{{margin:14px 0 0;font:800 176px/0.86 Archivo;font-stretch:70%;letter-spacing:-.01em}}
h2{{margin:22px 0 6px;font:700 46px/1.05 Archivo;font-stretch:82%;color:#fff}}
.sub{{font-size:19px;color:#C9D4E3;max-width:30em;line-height:1.45}}
ol{{list-style:none;margin:34px 0 0;padding:20px 0 0;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:9px;counter-reset:c}}
li{{display:flex;align-items:baseline;gap:12px;font-size:17px;color:#DCE4EE;counter-increment:c}}
li::before{{content:counter(c,decimal-leading-zero);font:500 13px 'IBM Plex Mono';color:var(--gold);width:26px}}
li i{{flex:1;border-bottom:1px dotted rgba(143,163,189,.45);transform:translateY(-4px)}}
li b{{font:500 14px 'IBM Plex Mono';color:var(--mut);font-weight:500}}
.tb{{position:absolute;right:28px;bottom:28px;display:grid;grid-template-columns:repeat(3,auto);border-top:1.5px solid rgba(232,194,122,.35);border-left:1.5px solid rgba(232,194,122,.35);background:rgba(8,19,38,.75)}}
.tb div{{padding:10px 18px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:3px}}
.tb div:last-child{{border-right:0}}
.tb span{{font:500 10.5px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}}
.tb b{{font:600 15px 'IBM Plex Mono';color:#fff}}
body.dense h1{{font-size:150px}}
body.dense h2{{margin-top:16px;font-size:40px}}
body.dense .sub{{font-size:17px}}
body.dense ol{{margin-top:20px;padding-top:14px;gap:5px}}
body.dense li{{font-size:15px}}
</style></head><body class="{'dense' if len(contents) > 8 else ''}"><div class="grid"></div><div class="frame"></div>{art}
{logos}<div class="left"><div class="eyebrow">Management dashboards</div><h1>SBARC</h1><h2>{doc_title}</h2><div class="sub">{doc_sub}</div><ol>{items}</ol></div>
<div class="tb"><div><span>Project</span><b>SBARC</b></div><div><span>Status</span><b>{status}</b></div><div><span>Issued</span><b>{issued}</b></div></div>
</body></html>"""


def cover_art(geo):
    vb = ' '.join(f'{v:.0f}' for v in geo['vb'])
    dots = ''.join(f'<circle class="v" cx="{x:.0f}" cy="{y:.0f}" r="16"/>' for _, x, y, _ in geo['villas'])
    blds = ''.join(f'<rect class="b" x="{x - 46:.0f}" y="{y - 26:.0f}" width="92" height="52" rx="10"/>' for _, x, y in geo['buildings'])
    tags = ''.join(f'<text class="c" x="{x:.0f}" y="{y:.0f}">{n}</text>' for n, x, y in geo['clusters'])
    return (f'<svg class="art" viewBox="{vb}" preserveAspectRatio="xMidYMid meet"><path class="glow" d="{geo["boundary"]}"/>'
            f'<path class="bd" d="{geo["boundary"]}"/>{blds}{dots}{tags}</svg>')


async def _pdf_now(pg, height=None):
    await pg.evaluate('document.fonts.ready')
    await pg.wait_for_timeout(250)
    h = height or await pg.evaluate('Math.ceil(document.documentElement.scrollHeight)')
    return await pg.pdf(width=f'{W}px', height=f'{h + 2}px', print_background=True, margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})


async def _open(pg, path):
    await pg.goto('file://' + path)
    await pg.add_style_tag(content=PDF_CSS)
    await pg.wait_for_timeout(2500)


async def _exec_pages(pg, path):
    out = []
    await _open(pg, path)

    async def keep(ids):
        await pg.evaluate("""(ids) => {
          const root = document.getElementById('overview').parentElement;
          [...root.children].forEach((el) => {
            const k = ids.includes(el.id) || ids.some((i) => i.startsWith('.') && el.matches(i));
            el.style.display = k ? '' : 'none';
          });
          window.scrollTo(0, 0);
        }""", ids)
        await pg.evaluate(EXPAND)
    await keep(['overview', 'kpis', '.sb-row2']); out.append(('Overview & KPIs', await _pdf_now(pg)))
    await keep(['clusters', 'activities']); out.append(('Clusters & activities', await _pdf_now(pg)))
    await keep(['villas']); out.append(('Villas', await _pdf_now(pg)))
    for sid, title in (('buildings', 'Buildings'), ('manpower', 'Manpower')):  # newer sections, when the page has them
        if await pg.query_selector('#' + sid):
            await keep([sid]); await pg.wait_for_timeout(300); out.append((title, await _pdf_now(pg)))
    await keep(['layouts'])
    groups = await pg.evaluate("[...document.querySelectorAll('#lay-groups button')].map(b => b.firstChild.textContent.trim())")
    for gi, g in enumerate(groups):
        await pg.click(f'#lay-groups button >> nth={gi}'); await pg.wait_for_timeout(500)
        n = await pg.evaluate("document.querySelectorAll('#lay-tabs button').length")
        for k in range(n):
            await pg.click(f'#lay-tabs button >> nth={k}'); await pg.wait_for_timeout(450)
            await pg.evaluate(EXPAND)
            name = await pg.evaluate(f"document.querySelectorAll('#lay-tabs button')[{k}].firstChild.textContent.trim()")
            out.append(('Site map · all activities' if g == 'Site map' else f'{g} · {name}', await _pdf_now(pg)))
    return out


async def _p02b_pages(pg, path):
    out = []
    await _open(pg, path)
    for t, title in P02B_TABS:
        if not await pg.query_selector(f'.pc-tab[data-tab="{t}"]'):
            continue
        await pg.click(f'.pc-tab[data-tab="{t}"]'); await pg.wait_for_timeout(900)
        await pg.evaluate(EXPAND)
        if t == 'remaining':
            await pg.evaluate("""() => {
              const tb = document.querySelector('#remaining table tbody'); if (!tb) return;
              const rows = [...tb.rows]; const LIMIT = 40;
              rows.forEach((r, i) => { if (i >= LIMIT) r.style.display = 'none'; });
              if (rows.length > LIMIT) {
                const tr = document.createElement('tr'); const td = document.createElement('td'); td.colSpan = rows[0].cells.length;
                td.textContent = 'Showing the first ' + LIMIT + ' of ' + rows.length.toLocaleString('en') + ' detailed activities. The full list is in the portal.';
                td.style.cssText = 'padding:14px 10px;font-style:italic;color:var(--color-fg-muted)'; tr.append(td); tb.append(tr);
              }
            }""")
        out.append((title, await _pdf_now(pg)))
    return out


def _dedupe_images(w):
    from pypdf.generic import NameObject
    canon = {}

    def key(o):
        sm = o.get('/SMask')
        smk = hashlib.md5(sm.get_object()._data).hexdigest() if sm is not None else ''
        return hashlib.md5(o._data).hexdigest() + str(o.get('/Width')) + str(o.get('/Height')) + smk

    def walk(res, depth=0):
        res = res.get_object() if res is not None else None
        if not res or '/XObject' not in res:
            return
        xo = res['/XObject'].get_object()
        for name in list(xo.keys()):
            ref = xo.raw_get(name); o = ref.get_object()
            if o.get('/Subtype') == '/Image':
                k = key(o)
                if k in canon: xo[NameObject(name)] = canon[k]
                else: canon[k] = ref
            elif o.get('/Subtype') == '/Form' and depth < 5:
                walk(o.get('/Resources'), depth + 1)
    for p in w.pages:
        walk(p.get('/Resources'))


def _assemble(title, cover_pdf, pages):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    w.append(PdfReader(io.BytesIO(cover_pdf)))
    w.add_outline_item('Cover', 0)
    for t, data in pages:
        idx = len(w.pages)
        w.append(PdfReader(io.BytesIO(data)))
        w.add_outline_item(t, idx)
    _dedupe_images(w)
    for p in w.pages:
        p.compress_content_streams()
    w.add_metadata({'/Title': title, '/Author': 'SBARC Project Controls', '/Creator': 'SBARC Project Controls', '/Producer': 'SBARC Project Controls'})
    buf = io.BytesIO(); w.write(buf); buf.seek(0)
    w2 = PdfWriter(clone_from=PdfReader(buf))  # drops objects nothing points to any more
    out = io.BytesIO(); w2.write(out)
    return out.getvalue(), len(w2.pages)


async def _render(frames_paths, ctx):
    from playwright.async_api import async_playwright
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': W, 'height': 900})
        await pg.emulate_media(media='screen')
        ex = await _exec_pages(pg, frames_paths['exec'])
        contents, groups = [], {}
        for k, (t, _) in enumerate(ex):  # page k + 2 (the cover is page 1)
            if ' · ' in t and not t.startswith('Site map'):
                g = t.split(' · ')[0]
                if g not in groups: groups[g] = [k + 2, k + 2]; contents.append([g, None])
                groups[g][1] = k + 2
            else:
                contents.append([t, f'p {k + 2}'])
        for c in contents:
            if c[1] is None:
                a, z = groups[c[0]]; n = z - a + 1
                c[0], c[1] = f'Layouts · {c[0]} ({n})', (f'p {a}' if n == 1 else f'p {a}–{z}')
        contents = [tuple(c) for c in contents]
        await pg.set_content(cover_html(ctx['fontcss'], ctx['logos'], ctx['art'], 'Executive Summary',
                                        'Villas &amp; buildings progress, cluster ranking, activity status, manpower and every site layout still in progress.',
                                        ctx['status']['exec'], ctx['issued'], contents))
        res['exec'] = _assemble('SBARC Executive Summary', await _pdf_now(pg, 900), ex)

        pc = await _p02b_pages(pg, frames_paths['p02b'])
        contents = [(t, f'p {i + 2}') for i, (t, _) in enumerate(pc)]
        await pg.set_content(cover_html(ctx['fontcss'], ctx['logos'], ctx['art'], 'Management Tracking',
                                        'Phase 02-B earned value control: actual vs the recovery plan, the general plan, December target, weekly targets and remaining work.',
                                        ctx['status']['p02b'], ctx['issued'], contents))
        res['p02b'] = _assemble('SBARC Management Tracking', await _pdf_now(pg, 900), pc)
        await b.close()
    return res


TITLES = {'exec': 'Executive Summary', 'p02b': 'Management Tracking'}
COVER_VERSION = '4'  # bump when the cover or page selection changes, to force new PDFs


def build_pdfs(frames, ctx, site_dir, tmp_dir, password, encrypt_js):
    """Returns the PDF list for the portal menu. Reuses the previous PDFs when nothing changed."""
    pdir = os.path.join(site_dir, 'pdf')
    os.makedirs(pdir, exist_ok=True)
    idx_p = os.path.join(pdir, 'index.json')
    prev = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
    # keyed hash: says whether the figures changed without revealing anything about them
    key = hmac.new(password.encode(), (COVER_VERSION + json.dumps([frames['exec'], frames['p02b'], ctx['status'], ctx['issued']])).encode(), 'sha256').hexdigest()[:24]
    have = all(os.path.exists(os.path.join(pdir, f'{d}.bin')) for d in TITLES)
    if prev.get('key') == key and have:
        print('PDFs unchanged')
        return prev['list']
    try:
        paths = {}
        for d in TITLES:
            paths[d] = os.path.join(tmp_dir, f'frame_{d}.html')
            with open(paths[d], 'w', encoding='utf-8') as f: f.write(frames[d])
        res = asyncio.run(_render(paths, ctx))
    except Exception as e:  # keep the last good PDFs; the menu shows their status date
        print(f'WARNING: PDFs not rebuilt ({type(e).__name__}: {e}); keeping the previous ones.')
        return prev.get('list', [])
    out = []
    for d, (data, pages) in res.items():
        raw = os.path.join(tmp_dir, f'{d}.pdf')
        with open(raw, 'wb') as f: f.write(data)
        subprocess.run(['node', encrypt_js, '--bin', raw, password, os.path.join(pdir, f'{d}.bin')], check=True)
        os.remove(raw)
        ver = hashlib.sha256(open(os.path.join(pdir, f'{d}.bin'), 'rb').read()).hexdigest()[:10]
        out.append({'id': d, 'title': TITLES[d], 'pages': pages, 'size': len(data), 'status': ctx['status'][d], 'file': f'pdf/{d}.bin', 'v': ver})
        print(f'PDF {TITLES[d]}: {pages} pages, {len(data) // 1024} KB')
    with open(idx_p, 'w') as f: json.dump({'key': key, 'list': out}, f)
    return out
