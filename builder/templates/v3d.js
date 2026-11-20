// Live 3D progress tab: interactive site model built from the encrypted villa / building data (session.v3d).
(function () {
  'use strict';
  const CSS = `
.v3{position:absolute;inset:0;background:#0b1622;overflow:hidden;font-family:Inter,"Segoe UI",Arial,sans-serif;color:#fff;user-select:none;-webkit-user-select:none}
.v3 canvas{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}
.v3 canvas.drag{cursor:grabbing}
.v3-shade{position:absolute;left:0;right:0;top:0;height:120px;background:linear-gradient(rgba(8,18,30,.6),rgba(8,18,30,0));pointer-events:none}
.v3-hd{position:absolute;left:16px;top:12px;right:16px;display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;pointer-events:none}
.v3-hd>*{pointer-events:auto}
.v3-t .k{font-size:10.5px;letter-spacing:3px;color:#E0C163;font-weight:700;text-transform:uppercase}
.v3-t .h{font-size:22px;font-weight:800;text-shadow:0 1px 8px rgba(0,0,0,.4)}
.v3-live{display:inline-flex;align-items:center;gap:6px;background:#1f9d55;border-radius:10px;padding:2px 10px;font-size:11.5px;font-weight:600;margin-top:4px}
.v3-live i{width:7px;height:7px;border-radius:50%;background:#fff;animation:v3p 1.6s infinite}@keyframes v3p{50%{opacity:.25}}
.v3-kpis{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}
.v3-kpi{background:rgba(14,20,28,.62);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:6px 12px;min-width:96px}
.v3-kpi b{display:block;font-size:19px;font-weight:800}.v3-kpi span{font-size:10.5px;color:#b9c4d2;letter-spacing:.3px}
.v3-tools{position:absolute;right:14px;top:84px;display:flex;flex-direction:column;gap:6px;align-items:flex-end}
.v3-btn{background:rgba(14,20,28,.7);backdrop-filter:blur(6px);color:#fff;border:1px solid rgba(255,255,255,.16);border-radius:6px;padding:7px 11px;font:600 12px Inter,Arial,sans-serif;cursor:pointer;display:flex;gap:6px;align-items:center}
.v3-btn:hover{background:rgba(44,170,200,.55)}.v3-btn.on{background:rgba(44,170,200,.85);border-color:transparent}
.v3-seg{display:flex;border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,.16)}.v3-seg .v3-btn{border:0;border-radius:0}
.v3-find{background:rgba(14,20,28,.7);color:#fff;border:1px solid rgba(255,255,255,.16);border-radius:6px;padding:7px 10px;font:500 12px Inter,Arial,sans-serif;width:150px;outline:none}
.v3-find::placeholder{color:#9aa6b4}
.v3-menu{position:absolute;left:50%;transform:translateX(-50%);bottom:16px;display:flex;background:rgba(18,22,28,.62);backdrop-filter:blur(8px);border-radius:8px;overflow:hidden;max-width:calc(100% - 24px);overflow-x:auto;scrollbar-width:none}
.v3-mi{flex:none;width:112px;height:68px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;color:#fff;font-size:12px;font-weight:500;cursor:pointer;border:0;background:none;font-family:inherit}
.v3-mi:hover{background:rgba(255,255,255,.08)}.v3-mi.on{background:rgba(44,170,200,.82)}
.v3-mi svg{width:23px;height:23px}
.v3-pop{position:absolute;background:rgba(14,17,22,.9);padding:12px 16px;border-radius:4px;min-width:250px;max-width:300px;font-size:14px;line-height:1.35;box-shadow:0 8px 28px rgba(0,0,0,.45);pointer-events:auto}
.v3-pop .x{position:absolute;right:8px;top:4px;font-size:17px;color:#ccc;cursor:pointer;background:none;border:0;padding:2px 6px}
.v3-pop .n{font-size:16px;font-weight:600;padding-right:22px}.v3-pop .s{font-weight:600}
.v3-pop .m{font-size:12px;color:#b9c4d2;margin-top:2px}
.v3-row{display:flex;align-items:center;gap:8px;font-size:12px;color:#c9d1db;margin-top:5px}
.v3-row b{width:62px;font-weight:500}.v3-tr{flex:1;height:6px;background:#333a44;border-radius:3px;overflow:hidden}.v3-tr i{display:block;height:100%;background:#2cc0e0}
.v3-row em{width:36px;text-align:right;font-style:normal;color:#fff}
.v3-op{margin-top:8px;border-top:1px solid rgba(255,255,255,.12);padding-top:6px;font-size:11.5px;color:#c9d1db}
.v3-op div{display:flex;justify-content:space-between;gap:10px;padding:1px 0}.v3-op div span:last-child{color:#ffcf5a;font-weight:600}
.v3-lbl{position:absolute;transform:translate(-50%,-50%);font-size:11px;font-weight:700;color:#fff;background:rgba(20,48,79,.78);border:1px solid rgba(224,193,99,.7);border-radius:10px;padding:1px 8px;pointer-events:none;white-space:nowrap}
.v3-leg{position:absolute;left:16px;bottom:100px;background:rgba(14,20,28,.7);backdrop-filter:blur(6px);border-radius:8px;padding:8px 10px;font-size:11.5px;display:none}
.v3-leg div{display:flex;align-items:center;gap:7px;margin:2px 0}.v3-leg i{width:12px;height:12px;border-radius:3px}
.v3-ready{position:absolute;left:18px;bottom:96px;font-size:14px;text-shadow:0 1px 4px #000;transition:opacity .6s}
.v3-help{position:absolute;right:16px;bottom:96px;font-size:11px;color:#d8dee6;text-shadow:0 1px 3px #000}
.v3-msg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:15px;color:#c9d1db}
@media (max-width:700px){.v3-kpis{display:none}.v3-tools .v3-seg:nth-of-type(2){display:none}.v3-mi{width:84px;font-size:10.5px}.v3-help{display:none}.v3-t .h{font-size:17px}}
`;
  const IC = {
    all: '<path d="M12 3 20 7.5v9L12 21l-8-4.5v-9z M4 7.5 12 12l8-4.5M12 12v9" fill="none" stroke="#fff" stroke-width="1.6"/>',
    pool: '<path d="M2 15c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M2 19c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M8 12V5a2 2 0 0 1 4 0M14 12V5a2 2 0 0 1 4 0M8 8h6" fill="none" stroke="#fff" stroke-width="1.6"/>',
    umb: '<path d="M3 11a9 9 0 0 1 18 0zM12 11v9M9 20h6" fill="none" stroke="#fff" stroke-width="1.6"/>',
    ball: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="#fff" stroke-width="1.6"/><path d="M3.5 12h17M12 3.5c-3 3-3 14 0 17M12 3.5c3 3 3 14 0 17" fill="none" stroke="#fff" stroke-width="1.3"/>',
    cc: '<path d="M3 20V9l9-5 9 5v11zM9 20v-6h6v6" fill="none" stroke="#fff" stroke-width="1.6"/>',
    mq: '<path d="M6 20v-6a6 6 0 0 1 12 0v6zM12 8V5M4 20h16M20 20V9" fill="none" stroke="#fff" stroke-width="1.6"/>',
    hot: '<path d="M4 20V6h10v14M14 10h6v10M7 9h2M7 12h2M7 15h2M2 20h20" fill="none" stroke="#fff" stroke-width="1.6"/>',
    vil: '<path d="M3 20V11l5-4 5 4v9zM13 20v-6l4-3 4 3v6M6 20v-4h4v4" fill="none" stroke="#fff" stroke-width="1.6"/>',
    gate: '<path d="M3 20V8h4v12M17 20V8h4v12M7 11h10M7 15h10" fill="none" stroke="#fff" stroke-width="1.6"/>',
    tour: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="#fff" stroke-width="1.6"/><path d="M10 8.5v7l5.5-3.5z" fill="#fff"/>',
  };
  const MENU = [['all', 'Overview', 'all'], ['SC', 'Swim Club', 'pool'], ['PA', 'Beach Pavilion', 'umb'], ['IS', 'Indoor Sports', 'ball'], ['CC', 'Community Ctr', 'cc'],
    ['MQ', 'Mosque', 'mq'], ['HB', 'Hospitality', 'hot'], ['vil', 'Villas', 'vil'], ['RG', 'Gatehouses', 'gate'], ['tour', 'Tour', 'tour']];
  const SZ = { AD: [120, 26, 80], BA: [150, 30, 70], CC: [150, 22, 110], CO: [110, 18, 80], HB: [130, 30, 90], IS: [170, 34, 120], MQ: [90, 20, 90], PA: [90, 12, 60],
    RG: [55, 10, 30], SC: [110, 14, 70], SG: [55, 10, 30], SR: [80, 14, 55], UT: [90, 16, 60], WS: [140, 18, 90] };
  const ROT = -Math.atan2(553, 980);
  const pc = (x) => (x == null ? '–' : Math.round(x * 100) + '%');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const pcol = (x) => (x == null ? '#9aa3ad' : x >= 0.999 ? '#2e9e5b' : x >= 0.9 ? '#8cc95f' : x >= 0.7 ? '#f0b43c' : x >= 0.4 ? '#e8743b' : '#d64541');
  let st = null, threeP = null, data = null, root = null, on = false;

  function loadThree() {
    if (window.THREE) return Promise.resolve();
    if (!threeP) threeP = new Promise((res, rej) => { const s = document.createElement('script'); s.src = 'vendor/three.min.js'; s.onload = res; s.onerror = () => { threeP = null; rej(new Error('3D engine did not load')); }; document.head.append(s); });
    return threeP;
  }
  function open(el, d) {
    if (!d) { el.innerHTML = '<div class="v3-msg">No 3D data in this build.</div>'; return; }
    if (!document.getElementById('v3-css')) { const s = document.createElement('style'); s.id = 'v3-css'; s.textContent = CSS; document.head.append(s); }
    if (st && data === d && root === el) { on = true; st.resize(); st.loop(); return; }
    reset(); data = d; root = el; on = true;
    el.innerHTML = '<div class="v3-msg">Loading the 3D site model…</div>';
    loadThree().then(() => { if (data === d) { st = build(el, d); } }).catch((e) => { el.innerHTML = '<div class="v3-msg">' + esc(e.message) + '. Check the connection and open the tab again.</div>'; });
  }
  function active(a) { on = a; if (a && st) { st.resize(); st.loop(); } }
  function reset() { if (st) st.dispose(); st = null; data = null; if (root) root.innerHTML = ''; root = null; }

  function build(el, D) {
    const T = THREE;
    el.innerHTML = `<canvas></canvas><div class="v3-shade"></div><div class="v3-lbls"></div>
<div class="v3-hd"><div class="v3-t"><div class="v3-live"><i></i>Live · status ${esc(D.status)}</div></div><div class="v3-kpis"></div></div>
<div class="v3-tools"><input class="v3-find" list="v3-list" placeholder="Find villa or building"><datalist id="v3-list"></datalist>
<div class="v3-seg"><button class="v3-btn on" data-mode="real">Realistic</button><button class="v3-btn" data-mode="prog">Progress colours</button></div>
<div class="v3-seg"><button class="v3-btn" data-q="1">HD</button><button class="v3-btn on" data-q="2">Retina</button><button class="v3-btn" data-q="4k">4K</button></div>
<button class="v3-btn" data-act="shot">⤓ 4K image</button><button class="v3-btn" data-act="fs">⛶ Full screen</button></div>
<div class="v3-leg"></div><div class="v3-ready">System Ready</div><div class="v3-help">Drag to rotate · right-drag or two fingers to pan · scroll or pinch to zoom · click a villa or building</div>
<div class="v3-menu"></div><div class="v3-pop" hidden></div>`;
    const q = (s) => el.querySelector(s), cv = q('canvas'), pop = q('.v3-pop'), lbls = q('.v3-lbls');
    // ---------- data
    const V = D.V.map((r) => ({ c: r[0], x: r[1], y: r[2], cl: r[3], t: r[4], tot: r[5], f: r[6], m: r[7], op: r[8], kind: 'V' }));
    const BL = D.B.map((r) => ({ c: r[0], n: r[1], x: r[2], y: r[3], tot: r[4], f: r[5], m: r[6], w: r[7], d: r[8], op: r[9], kind: 'B' }));
    const avg = (a) => { const v = a.filter((x) => x != null); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
    q('.v3-kpis').innerHTML = [[pc(avg(V.map((v) => v.tot))), 'Villas average'], [V.filter((v) => v.tot >= 0.95).length + ' / ' + V.length, 'Villas ≥ 95%'],
      [pc(avg(BL.map((b) => b.tot))), 'Buildings average'], [BL.length, 'Buildings']].map((k) => `<div class="v3-kpi"><b>${k[0]}</b><span>${k[1]}</span></div>`).join('');
    q('#v3-list').innerHTML = [...V.map((v) => v.c), ...BL.map((b) => b.n)].map((s) => `<option value="${esc(s)}">`).join('');
    q('.v3-menu').innerHTML = MENU.map((m) => `<button class="v3-mi" data-go="${m[0]}"><svg viewBox="0 0 24 24">${IC[m[2]]}</svg>${m[1]}</button>`).join('');
    q('.v3-leg').innerHTML = '<b style="font-size:11px">Total progress</b>' + [['#2e9e5b', '100%'], ['#8cc95f', '90–99%'], ['#f0b43c', '70–89%'], ['#e8743b', '40–69%'], ['#d64541', 'below 40%']].map((x) => `<div><i style="background:${x[0]}"></i>${x[1]}</div>`).join('');
    // ---------- renderer
    const R = new T.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true });
    R.shadowMap.enabled = true; R.shadowMap.type = T.PCFSoftShadowMap; R.outputColorSpace = T.SRGBColorSpace; R.toneMapping = T.ACESFilmicToneMapping; R.toneMappingExposure = 1.05;
    let quality = '2';
    const S = new T.Scene();
    { const c = document.createElement('canvas'); c.width = 2; c.height = 256; const g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 256);
      gr.addColorStop(0, '#5d8fc9'); gr.addColorStop(0.55, '#a9c8e6'); gr.addColorStop(1, '#e9e3d6'); g.fillStyle = gr; g.fillRect(0, 0, 2, 256);
      const tx = new T.CanvasTexture(c); tx.colorSpace = T.SRGBColorSpace; S.background = tx; }
    S.fog = new T.Fog(0xdcd9cf, 3000, 9000);
    const cam = new T.PerspectiveCamera(42, 16 / 9, 5, 30000);
    S.add(new T.HemisphereLight(0xdfeaff, 0xb59d78, 1.15));
    const sun = new T.DirectionalLight(0xfff1dc, 2.4); sun.position.set(2600, 1900, 2600); sun.target.position.set(1500, 0, 1200);
    sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); Object.assign(sun.shadow.camera, { left: -1900, right: 1900, top: 1600, bottom: -1600, near: 100, far: 7000 }); sun.shadow.bias = -0.0004;
    S.add(sun, sun.target);
    // ---------- ground from the site plan
    const PW = D.w, PH = D.h, K = 1.2, gc = document.createElement('canvas'); gc.width = PW * K; gc.height = PH * K;
    const g = gc.getContext('2d'); g.scale(K, K); g.fillStyle = '#d9c7a2'; g.fillRect(0, 0, PW, PH);
    const e1 = [1975, 55], e2 = [2955, 608], dx = e2[0] - e1[0], dy = e2[1] - e1[1], ln = Math.hypot(dx, dy), nx = dy / ln, ny = -dx / ln;
    g.fillStyle = '#efe2c4'; g.beginPath(); g.moveTo(e1[0] - dx * 3 + nx * 40, e1[1] - dy * 3 + ny * 40); g.lineTo(e2[0] + dx * 3 + nx * 40, e2[1] + dy * 3 + ny * 40);
    g.lineTo(e2[0] + dx * 3 + nx * 100, e2[1] + dy * 3 + ny * 100); g.lineTo(e1[0] - dx * 3 + nx * 100, e1[1] - dy * 3 + ny * 100); g.fill();
    const bnd = new Path2D(D.boundary); g.fillStyle = '#cfcac0'; g.fill(bnd);
    const L = D.land || {}, fp = (p, c) => { if (p) { g.fillStyle = c; g.fill(new Path2D(p)); } }, sp = (p, c, w) => { if (p) { g.strokeStyle = c; g.lineWidth = w; g.lineCap = g.lineJoin = 'round'; g.stroke(new Path2D(p)); } };
    if (L.interlock) { fp(L.interlock[0], '#bfb3a0'); fp(L.interlock[1], '#c7bba6'); }
    if (L.soft) { fp(L.soft[0], '#7fa05a'); fp(L.soft[1], '#9bab6e'); }
    if (L.curb) sp(L.curb[2], '#8b8b88', 2);
    if (L.bike) { sp(L.bike[2], '#b8735f', 4); sp(L.bike[3], '#b8735f', 4); }
    g.strokeStyle = '#e8e2d4'; g.lineWidth = 14; g.stroke(bnd);
    const gtx = new T.CanvasTexture(gc); gtx.colorSpace = T.SRGBColorSpace; gtx.anisotropy = R.capabilities.getMaxAnisotropy();
    const ground = new T.Mesh(new T.PlaneGeometry(PW, PH), new T.MeshStandardMaterial({ map: gtx, roughness: 1 }));
    ground.rotation.x = -Math.PI / 2; ground.position.set(PW / 2, 0, PH / 2); ground.receiveShadow = true; S.add(ground);
    const desert = new T.Mesh(new T.PlaneGeometry(40000, 40000), new T.MeshStandardMaterial({ color: 0xd9c7a2, roughness: 1 }));
    desert.rotation.x = -Math.PI / 2; desert.position.set(PW / 2, -0.6, PH / 2); desert.receiveShadow = true; S.add(desert);
    const sea = new T.Mesh(new T.PlaneGeometry(40000, 12000), new T.MeshStandardMaterial({ color: 0x2f86a8, roughness: 0.25, metalness: 0.1 }));
    sea.rotation.x = -Math.PI / 2; sea.rotation.z = -Math.atan2(dy, dx); sea.position.set((e1[0] + e2[0]) / 2 + nx * 6100, 0.4, (e1[1] + e2[1]) / 2 + ny * 6100); S.add(sea);
    // ---------- materials and models
    const M = { wall: new T.MeshStandardMaterial({ color: 0xf3eee4, roughness: 0.85 }), wall2: new T.MeshStandardMaterial({ color: 0xe6dccb, roughness: 0.85 }),
      roof: new T.MeshStandardMaterial({ color: 0xfaf8f3, roughness: 0.9 }), glass: new T.MeshStandardMaterial({ color: 0x5b7a93, roughness: 0.15, metalness: 0.4 }),
      wood: new T.MeshStandardMaterial({ color: 0x9b7a55, roughness: 0.8 }), gold: new T.MeshStandardMaterial({ color: 0xd8c79e, roughness: 0.4, metalness: 0.3 }),
      pool: new T.MeshStandardMaterial({ color: 0x2fb6d6, roughness: 0.1, metalness: 0.1, emissive: 0x0a3a48, emissiveIntensity: 0.4 }),
      grass: new T.MeshStandardMaterial({ color: 0x6f9a4a, roughness: 1 }), court: new T.MeshStandardMaterial({ color: 0x3f8f6a, roughness: 0.9 }),
      trunk: new T.MeshStandardMaterial({ color: 0x8a6a48 }), leaf: new T.MeshStandardMaterial({ color: 0x4e7d3a, roughness: 0.9 }) };
    const pmat = {}; const progMat = (x) => { const k = pcol(x); return pmat[k] || (pmat[k] = new T.MeshStandardMaterial({ color: k, roughness: 0.75 })); };
    const pick = [], tint = [];
    const box = (w, h, d, m, x, y, z, par) => { const o = new T.Mesh(new T.BoxGeometry(w, h, d), m); o.position.set(x, y + h / 2, z); o.castShadow = o.receiveShadow = true; par.add(o); return o; };
    const grp = (x, z, r) => { const o = new T.Group(); o.position.set(x, 0, z); o.rotation.y = r; S.add(o); return o; };
    V.forEach((v, i) => {
      const G = grp(v.x, v.y, ROT + (i % 2 ? Math.PI : 0)), w = 34, d = 26;
      const a = box(w, 11, d, M.wall, 0, 0, 0, G), b = box(w * 0.72, 10, d * 0.8, M.wall2, -w * 0.12, 11, -d * 0.05, G);
      box(w + 1, 1.2, d + 1, M.roof, 0, 11, 0, G); box(w * 0.72 + 1, 1.4, d * 0.8 + 1, M.roof, -w * 0.12, 21, -d * 0.05, G);
      for (const s of [-1, 1]) { box(8, 6, 0.6, M.glass, s * 8, 3, d / 2 + 0.1, G); box(6, 5, 0.6, M.glass, s * 7 - 3, 13, d * 0.35 + 0.2, G); }
      box(10, 0.6, 8, M.wood, w * 0.32, 11.6, d * 0.25, G);
      box(w + 14, 0.4, d + 16, M.grass, 0, -0.1, 4, G).castShadow = false;
      box(9, 0.5, 6, M.pool, w * 0.3, 0, d / 2 + 6, G).castShadow = false;
      a.userData.it = b.userData.it = v; pick.push(a, b); tint.push([a, M.wall, v], [b, M.wall2, v]);
      v.G = G; v.hl = [38, 24, 30]; v.h = 26;
    });
    BL.forEach((b) => {
      const [w, h, d] = SZ[b.c] || [100, 20, 70], G = grp(b.x, b.y, ROT);
      const body = box(w, h, d, M.wall, 0, 0, 0, G); box(w + 3, 1.6, d + 3, M.roof, 0, h, 0, G); box(w + 0.6, 2.2, d + 0.6, M.wood, 0, h - 3, 0, G);
      const n = Math.floor(w / 14); for (let i = 0; i < n; i++) box(7, h * 0.42, 0.8, M.glass, -w / 2 + 10 + i * (w - 16) / Math.max(1, n - 1), h * 0.28, d / 2 + 0.2, G);
      let top = h + 4;
      if (b.c === 'MQ') { const dm = new T.Mesh(new T.SphereGeometry(26, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.gold); dm.position.y = h + 1.6; dm.castShadow = true; G.add(dm);
        const mi = new T.Mesh(new T.CylinderGeometry(4, 5, 82, 16), M.wall); mi.position.set(w / 2 + 10, 41, -d / 2 + 6); mi.castShadow = true; G.add(mi);
        const mt = new T.Mesh(new T.ConeGeometry(5, 12, 16), M.gold); mt.position.set(w / 2 + 10, 88, -d / 2 + 6); G.add(mt); top = h + 30; }
      if (b.c === 'SC' || b.c === 'HB') { box(b.c === 'SC' ? 90 : 50, 0.6, 40, M.pool, 0, 0, d / 2 + 34, G).castShadow = false; box(110, 0.3, 62, M.roof, 0, -0.1, d / 2 + 34, G).castShadow = false; }
      if (b.c === 'IS') { box(70, 0.5, 40, M.court, -30, 0, d / 2 + 36, G).castShadow = false; box(w * 0.8, 6, d * 0.7, M.roof, 0, h, 0, G); }
      if (b.c === 'CC') { box(40, 0.5, 40, M.court, -w / 2 - 30, 0, 0, G).castShadow = false; box(30, 0.6, 20, M.pool, w / 2 + 24, 0, 10, G).castShadow = false; }
      if (b.c === 'PA') box(w + 40, 0.4, d + 30, M.wood, 0, -0.1, 0, G).castShadow = false;
      body.userData.it = b; pick.push(body); tint.push([body, M.wall, b]);
      b.G = G; b.hl = [w + 6, top, d + 6]; b.h = top; b.size = Math.max(w, d);
    });
    // palms
    { let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      const pts = [...V.map((v) => [v.x, v.y, 36]), ...BL.map((b) => [b.x, b.y, (SZ[b.c] || [100])[0] * 1.05 + 30])];
      const bp = (D.boundary.match(/-?\d+(?:\.\d+)? -?\d+(?:\.\d+)?/g) || []).map((s) => s.split(' ').map(Number));
      const inside = (x, y) => { let c = false; for (let i = 0, j = bp.length - 1; i < bp.length; j = i++) { const [a, b] = bp[i], [p, qq] = bp[j]; if ((b > y) !== (qq > y) && x < (p - a) * (y - b) / (qq - b) + a) c = !c; } return c; };
      const NT = 900, ti = new T.InstancedMesh(new T.CylinderGeometry(1, 1.6, 16, 6), M.trunk, NT), li = new T.InstancedMesh(new T.IcosahedronGeometry(7, 0), M.leaf, NT);
      ti.castShadow = li.castShadow = true; const m4 = new T.Matrix4(), qt = new T.Quaternion(); let nt = 0, guard = 0;
      while (nt < NT && guard++ < 60000) { const x = rnd() * PW, y = rnd() * PH; if (!inside(x, y) || pts.some((p) => Math.hypot(p[0] - x, p[1] - y) < p[2])) continue;
        const s = 0.5 + rnd() * 0.45; m4.compose(new T.Vector3(x, 8 * s, y), qt.identity(), new T.Vector3(s, s, s)); ti.setMatrixAt(nt, m4);
        m4.compose(new T.Vector3(x, 17 * s, y), qt.setFromEuler(new T.Euler(rnd(), rnd(), 0)), new T.Vector3(s * 1.2, s * 0.7, s * 1.2)); li.setMatrixAt(nt, m4); nt++; }
      ti.count = li.count = nt; S.add(ti, li); }
    // highlight box
    const hl = new T.Group(); S.add(hl);
    const hlMat = new T.LineBasicMaterial({ color: 0x7fe8ff, transparent: true }), hlFill = new T.MeshBasicMaterial({ color: 0x37c8ff, transparent: true, opacity: 0.18, depthWrite: false });
    let sel = null;
    function select(it, fly) {
      sel = it; hl.clear();
      if (!it) { pop.hidden = true; return; }
      const [w, h, d] = it.hl, geo = new T.BoxGeometry(w, h, d), s = new T.Group();
      s.add(new T.LineSegments(new T.EdgesGeometry(geo), hlMat), new T.Mesh(geo, hlFill)); s.position.set(it.x, h / 2, it.y); s.rotation.y = it.G.rotation.y; hl.add(s);
      const bar = (l, v) => `<div class="v3-row"><b>${l}</b><span class="v3-tr"><i style="width:${(v || 0) * 100}%"></i></span><em>${pc(v)}</em></div>`;
      const ops = (it.op || []).length ? '<div class="v3-op"><div style="color:#9fb0c2"><span>Open items</span><span style="color:#9fb0c2">done</span></div>' + it.op.slice(0, 6).map((a) => `<div><span>${esc(a[0])}</span><span>${a[1]}%</span></div>`).join('') + '</div>' : '';
      pop.innerHTML = it.kind === 'V'
        ? `<button class="x" aria-label="Close">✕</button><div class="n">Villa ${esc(it.c)} -</div><div class="s" style="color:${it.tot >= 0.999 ? '#53d8a0' : '#ffcf5a'}">${pc(it.tot)} complete${it.tot >= 0.999 ? ' · ready for handover' : ''}</div><div class="m">Cluster ${esc(it.cl)} · Type ${esc(it.t)}${D.vtarget ? ' · ' + esc(D.vtarget) : ''}</div>${bar('Finishes', it.f)}${bar('MEP', it.m)}${ops}`
        : `<button class="x" aria-label="Close">✕</button><div class="n">${esc(it.n)} -</div><div class="s" style="color:#ffcf5a">${pc(it.tot)} complete${it.w ? ' · Wave ' + it.w : ''}</div><div class="m">${it.d ? 'Handover target (major finish): ' + esc(it.d) : ''}</div>${bar('Finishes', it.f)}${bar('MEP', it.m)}${ops}`;
      pop.hidden = false; pop.querySelector('.x').onclick = () => select(null);
      if (fly) flyTo(it);
    }
    // ---------- camera control (orbit / pan / zoom)
    const C = { tx: 1520, ty: 0, tz: 1220, az: 1.05, pol: 0.95, r: 2200 }; let goal = { ...C };
    const lim = () => { goal.pol = Math.min(1.45, Math.max(0.18, goal.pol)); goal.r = Math.min(6000, Math.max(60, goal.r)); goal.tx = Math.min(PW + 400, Math.max(-400, goal.tx)); goal.tz = Math.min(PH + 400, Math.max(-400, goal.tz)); };
    let tween = null;
    function flyTo(it) {
      const r = it === 'all' ? 2200 : it.kind === 'B' ? Math.max(220, it.size * 2.4) : 150;
      const to = it === 'all' ? { tx: 1520, ty: 0, tz: 1220, az: 1.05, pol: 0.95, r } : { tx: it.x, ty: it.kind === 'B' ? 10 : 8, tz: it.y, az: goal.az + 0.35, pol: it.kind === 'B' ? 1.08 : 1.12, r };
      tween = { from: { ...C }, to, t0: performance.now(), dur: 1800 }; goal = { ...to };
    }
    const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
    let drag = null, moved = 0, lastUser = performance.now(); const ptrs = new Map();
    cv.addEventListener('contextmenu', (e) => e.preventDefault());
    cv.addEventListener('pointerdown', (e) => { cv.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]); drag = { b: e.button === 2 || e.shiftKey ? 'pan' : 'rot', x: e.clientX, y: e.clientY }; moved = 0; tween = null; stopTour(); cv.classList.add('drag'); lastUser = performance.now(); });
    cv.addEventListener('pointermove', (e) => {
      if (!drag || !ptrs.has(e.pointerId)) return; const prev = ptrs.get(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]);
      const ddx = e.clientX - prev[0], ddy = e.clientY - prev[1]; moved += Math.abs(ddx) + Math.abs(ddy); lastUser = performance.now();
      if (ptrs.size === 2) { const [a, b] = [...ptrs.values()], d2 = Math.hypot(a[0] - b[0], a[1] - b[1]); if (drag.d2) goal.r *= drag.d2 / d2; drag.d2 = d2; pan(ddx / 2, ddy / 2); lim(); return; }
      if (drag.b === 'rot') { goal.az += ddx * 0.005; goal.pol -= ddy * 0.004; } else pan(ddx, ddy); lim();
    });
    function pan(ddx, ddy) { const k = goal.r * 0.0011, s = Math.sin(goal.az), c = Math.cos(goal.az); goal.tx += (-ddx * s - ddy * c) * k; goal.tz += (ddx * c - ddy * s) * k; }
    const up = (e) => { ptrs.delete(e.pointerId); if (ptrs.size === 0) { cv.classList.remove('drag'); if (drag && moved < 6) clickAt(e); drag = null; } else if (drag) drag.d2 = 0; };
    cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
    cv.addEventListener('wheel', (e) => { e.preventDefault(); tween = null; stopTour(); goal.r *= Math.exp(e.deltaY * 0.0012); lim(); lastUser = performance.now(); }, { passive: false });
    const ray = new T.Raycaster(), v2 = new T.Vector2();
    function clickAt(e) { const r = cv.getBoundingClientRect(); v2.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(v2, cam);
      const h = ray.intersectObjects(pick, false)[0]; select(h ? h.object.userData.it : null, !!h); menuOn(h ? (h.object.userData.it.kind === 'V' ? 'vil' : h.object.userData.it.c) : ''); }
    // ---------- menu, find, modes, quality, tour
    function menuOn(id) { el.querySelectorAll('.v3-mi').forEach((b) => b.classList.toggle('on', b.dataset.go === id || (id === 'SG' && b.dataset.go === 'RG'))); }
    let vilIx = 0;
    const best = [...V].sort((a, b) => (b.tot || 0) - (a.tot || 0));
    el.querySelector('.v3-menu').addEventListener('click', (e) => {
      const b = e.target.closest('.v3-mi'); if (!b) return; const go = b.dataset.go; stopTour();
      if (go === 'tour') { startTour(); return; }
      menuOn(go); if (go === 'all') { select(null); flyTo('all'); return; }
      if (go === 'vil') { select(best[vilIx++ % best.length], true); return; }
      const it = BL.find((x) => x.c === go); if (it) select(it, true);
    });
    q('.v3-find').addEventListener('change', (e) => { const s = e.target.value.trim().toLowerCase(); const it = V.find((v) => v.c.toLowerCase() === s) || BL.find((b) => b.n.toLowerCase() === s || b.c.toLowerCase() === s);
      if (it) { stopTour(); select(it, true); menuOn(it.kind === 'V' ? 'vil' : it.c); e.target.blur(); } });
    el.querySelectorAll('[data-mode]').forEach((b) => b.addEventListener('click', () => {
      const prog = b.dataset.mode === 'prog'; el.querySelectorAll('[data-mode]').forEach((x) => x.classList.toggle('on', x === b));
      tint.forEach(([m, base, it]) => { m.material = prog ? progMat(it.tot) : base; }); q('.v3-leg').style.display = prog ? 'block' : 'none'; }));
    el.querySelectorAll('[data-q]').forEach((b) => b.addEventListener('click', () => { quality = b.dataset.q; el.querySelectorAll('[data-q]').forEach((x) => x.classList.toggle('on', x === b)); resize(); }));
    q('[data-act="fs"]').addEventListener('click', () => { if (document.fullscreenElement) document.exitFullscreen(); else if (el.requestFullscreen) el.requestFullscreen().catch(() => {}); });
    q('[data-act="shot"]').addEventListener('click', () => {
      const w = 3840, h = 2160, pr = R.getPixelRatio(), sz = R.getSize(new T.Vector2());
      R.setPixelRatio(1); R.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); R.render(S, cam);
      cv.toBlob((blob) => { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'SBARC_Live_3D_' + D.status + '.png'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); }, 'image/png');
      R.setPixelRatio(pr); R.setSize(sz.x, sz.y, false); resize();
    });
    const TOUR = ['all', 'SC', 'CC', 'MQ', 'IS', 'PA', 'vil'];
    let tour = null;
    function startTour() { tour = { i: 0, t: performance.now() - 99999 }; menuOn('tour'); }
    function stopTour() { if (tour) { tour = null; menuOn(''); } }
    function tourStep(now) {
      if (!tour || now - tour.t < 5200) return; tour.t = now; const go = TOUR[tour.i++ % TOUR.length];
      if (go === 'all') { select(null); flyTo('all'); } else if (go === 'vil') select(best[vilIx++ % best.length], true); else select(BL.find((x) => x.c === go), true);
      el.querySelectorAll('.v3-mi').forEach((b) => b.classList.toggle('on', b.dataset.go === 'tour' || b.dataset.go === go));
    }
    // cluster labels
    const cl = D.clusters.map((c) => { const d = document.createElement('div'); d.className = 'v3-lbl'; d.textContent = c[0]; lbls.append(d); return { d, x: c[1], y: c[2] }; });
    // ---------- size, loop
    function resize() {
      const w = el.clientWidth || 1, h = el.clientHeight || 1;
      const pr = quality === '1' ? 1 : quality === '4k' ? Math.max(1, 3840 / w) : Math.min(window.devicePixelRatio || 1, 2);
      R.setPixelRatio(pr); R.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
    }
    const ro = new ResizeObserver(() => resize()); ro.observe(el);
    const vp = new T.Vector3();
    const proj = (x, y, z) => { vp.set(x, y, z).project(cam); return [(vp.x + 1) / 2 * el.clientWidth, (1 - vp.y) / 2 * el.clientHeight, vp.z]; };
    let raf = 0, alive = true; const t0 = performance.now();
    function frame(now) {
      raf = 0; if (!alive || !on || el.hidden || !el.offsetParent) return;
      tourStep(now);
      if (tween) { const k = Math.min(1, (now - tween.t0) / tween.dur), e = ease(k); for (const key in C) C[key] = tween.from[key] + (tween.to[key] - tween.from[key]) * e;
        C.r += Math.sin(k * Math.PI) * Math.min(900, Math.hypot(tween.from.tx - tween.to.tx, tween.from.tz - tween.to.tz) * 0.35); if (k >= 1) tween = null; }
      else { if (now - lastUser > 9000 && !drag) goal.az += 0.0006; for (const key in C) C[key] += (goal[key] - C[key]) * 0.12; }
      cam.position.set(C.tx + C.r * Math.sin(C.pol) * Math.cos(C.az), C.ty + C.r * Math.cos(C.pol), C.tz + C.r * Math.sin(C.pol) * Math.sin(C.az)); cam.lookAt(C.tx, C.ty, C.tz);
      const p = 0.6 + 0.4 * Math.sin(now / 160); hlMat.opacity = p; hlFill.opacity = 0.12 + 0.1 * p;
      R.render(S, cam);
      if (sel && !pop.hidden) { const [sx, sy, z] = proj(sel.x, sel.h + 4, sel.y); const W = el.clientWidth, pw = pop.offsetWidth, ph = pop.offsetHeight;
        pop.style.visibility = z < 1 ? 'visible' : 'hidden'; pop.style.left = Math.max(8, Math.min(W - pw - 8, sx + 30)) + 'px'; pop.style.top = Math.max(84, Math.min(el.clientHeight - ph - 96, sy - ph / 2)) + 'px'; }
      const far = C.r > 900; cl.forEach((c) => { if (!far) { c.d.style.display = 'none'; return; } const [sx, sy, z] = proj(c.x, 40, c.y); c.d.style.display = z < 1 ? 'block' : 'none'; c.d.style.left = sx + 'px'; c.d.style.top = sy + 'px'; });
      q('.v3-ready').style.opacity = now - t0 < 4000 ? 1 : 0;
      loop();
    }
    function loop() { if (!raf && alive) raf = requestAnimationFrame(frame); }
    resize(); menuOn('all');
    C.r = 5200; C.pol = 0.6; tween = { from: { ...C }, to: { ...goal }, t0: performance.now(), dur: 2600 };
    loop();
    return { resize, loop, dispose() { alive = false; if (raf) cancelAnimationFrame(raf); ro.disconnect(); R.dispose(); S.traverse((o) => { if (o.geometry) o.geometry.dispose(); }); } };
  }
  window.V3D = { open, active, reset };
})();
