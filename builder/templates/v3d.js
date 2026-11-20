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

  // ===== Scene: SBARC architecture (cream plaster, crenellated parapets, arched recesses, brown aluminium, timber pergolas) =====
  function buildScene(T, cv, D, V, BL) {
    const U = 0.5; // plan units are ~0.5 m: all sizes below are in plan units
    const R = new T.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
    R.shadowMap.enabled = true; R.shadowMap.type = T.PCFSoftShadowMap; R.outputColorSpace = T.SRGBColorSpace;
    R.toneMapping = T.ACESFilmicToneMapping; R.toneMappingExposure = 1.08;
    const maxTex = R.capabilities.maxTextureSize, mobile = Math.min(screen.width, screen.height) < 700;
    const S = new T.Scene();
    const cam = new T.PerspectiveCamera(40, 16 / 9, 2, 60000);
    // ---------- sky (gradient dome with sun glow) and image-based lighting from it
    const SUN = new T.Vector3(-0.55, 0.62, -0.56).normalize();
    const skyMat = new T.ShaderMaterial({ side: T.BackSide, depthWrite: false, fog: false,
      uniforms: { sun: { value: SUN } },
      vertexShader: 'varying vec3 vD; void main(){ vD = normalize((modelMatrix*vec4(position,1.0)).xyz - cameraPosition); gl_Position = projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.0); gl_Position.z = gl_Position.w; }',
      fragmentShader: 'uniform vec3 sun; varying vec3 vD; void main(){ float h = clamp(vD.y,-1.0,1.0); vec3 top = vec3(0.10,0.28,0.62); vec3 mid = vec3(0.36,0.56,0.82); vec3 hor = vec3(0.86,0.86,0.84); vec3 gnd = vec3(0.80,0.74,0.64);' +
        ' vec3 c = h > 0.0 ? mix(hor, mix(mid, top, smoothstep(0.15,0.9,h)), smoothstep(0.0,0.22,h)) : mix(hor, gnd, smoothstep(0.0,0.08,-h));' +
        ' float s = max(dot(vD, sun), 0.0); c += vec3(1.0,0.92,0.75)*(pow(s, 900.0)*6.0 + pow(s, 12.0)*0.18); gl_FragColor = vec4(c,1.0); }' });
    const sky = new T.Mesh(new T.SphereGeometry(1, 48, 24), skyMat); sky.scale.setScalar(50000); sky.frustumCulled = false; sky.renderOrder = -1; S.add(sky);
    { const es = new T.Scene(); const s2 = new T.Mesh(new T.SphereGeometry(1, 32, 16), skyMat); s2.scale.setScalar(50); es.add(s2);
      const pm = new T.PMREMGenerator(R); S.environment = pm.fromScene(es, 0.02).texture; pm.dispose(); }
    S.fog = new T.Fog(0xd9d6cd, 2500, 16000);
    S.add(new T.HemisphereLight(0xcfe0ff, 0xb59a74, 0.15));
    const sun = new T.DirectionalLight(0xfff0d8, 3.6); sun.castShadow = true; const SM = mobile ? 2048 : 4096; sun.shadow.mapSize.set(SM, SM);
    sun.shadow.camera.near = 10; sun.shadow.camera.far = 9000; sun.shadow.normalBias = 0.6; S.add(sun, sun.target);
    function fitShadow(tx, tz, r) {
      const s = Math.min(2300, Math.max(110, r * 0.85)), c = sun.shadow.camera;
      const tex = (2 * s) / SM; const ux = Math.round(tx / tex) * tex, uz = Math.round(tz / tex) * tex; // snap to texels: no shimmer
      sun.target.position.set(ux, 0, uz);
      sun.position.set(ux + SUN.x * 4000, SUN.y * 4000, uz + SUN.z * 4000);
      if (c.right !== s) { c.left = -s; c.right = s; c.top = s; c.bottom = -s; c.updateProjectionMatrix(); sun.shadow.bias = -0.00012 * (s / 400); }
    }
    // ---------- procedural textures
    const cnv = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
    let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    function noiseTex(size, base, amp, tile) {
      const c = cnv(size, size), g = c.getContext('2d'), im = g.createImageData(size, size);
      for (let i = 0; i < size * size; i++) { const n = (rnd() - 0.5) * amp; im.data[i * 4] = base[0] + n; im.data[i * 4 + 1] = base[1] + n; im.data[i * 4 + 2] = base[2] + n; im.data[i * 4 + 3] = 255; }
      g.putImageData(im, 0, 0); g.globalAlpha = 0.5; g.drawImage(c, 0, 0, size / 2, size / 2, 0, 0, size, size); // low-frequency blotches
      const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; if (tile) t.repeat.set(tile, tile); t.colorSpace = T.SRGBColorSpace; return t;
    }
    const plasterTex = noiseTex(256, [236, 231, 220], 14, 1);
    const detailTex = noiseTex(512, [128, 128, 128], 70, 1); detailTex.colorSpace = T.NoColorSpace;
    // ---------- materials
    const std = (o) => new T.MeshStandardMaterial(o);
    // rough render: world-space (triplanar) plaster grain and bump, so big and small walls get the same texture
    function plaster(mat, bump) {
      mat.onBeforeCompile = (sh) => { sh.uniforms.detailMap = { value: detailTex };
        sh.vertexShader = 'varying vec3 vPW; varying vec3 vPN;\n' + sh.vertexShader.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\n vec4 pw = vec4(transformed,1.0); vec3 pn = objectNormal;\n#ifdef USE_INSTANCING\n pw = instanceMatrix * pw; pn = mat3(instanceMatrix) * pn;\n#endif\n vPW = (modelMatrix * pw).xyz; vPN = normalize(mat3(modelMatrix) * pn);');
        sh.fragmentShader = 'uniform sampler2D detailMap; varying vec3 vPW; varying vec3 vPN;\n' + sh.fragmentShader
          .replace('#include <map_fragment>', '#include <map_fragment>\n vec3 bw = abs(vPN) + 1e-4; bw /= (bw.x + bw.y + bw.z);\n float n1 = texture2D(detailMap, vPW.yz*0.21).r*bw.x + texture2D(detailMap, vPW.xz*0.21).r*bw.y + texture2D(detailMap, vPW.xy*0.21).r*bw.z;\n float n2 = texture2D(detailMap, vPW.yz*0.017).r*bw.x + texture2D(detailMap, vPW.xz*0.017).r*bw.y + texture2D(detailMap, vPW.xy*0.017).r*bw.z;\n diffuseColor.rgb *= (0.9 + 0.2*n1) * (0.93 + 0.14*n2);')
          .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\n { vec3 dpx = dFdx(-vViewPosition), dpy = dFdy(-vViewPosition); float hx = dFdx(n1), hy = dFdy(n1); vec3 r1 = cross(dpy, normal), r2 = cross(normal, dpx); float det = dot(dpx, r1); vec3 gr = sign(det) * (hx * r1 + hy * r2); normal = normalize(abs(det) * normal - ' + bump.toFixed(2) + ' * gr); }'); };
      return mat;
    }
    function jaliTex() { const c = cnv(128, 128), x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); x.globalCompositeOperation = 'destination-out';
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { const cx = 16 + i * 32, cy = 16 + j * 32; x.beginPath(); for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4, r = k % 2 ? 6 : 12; x.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); } x.fill(); }
      const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(1.5, 2); return t; }
    const M = {
      wall: plaster(std({ color: 0xeee6d8, roughness: 0.95, envMapIntensity: 0.6 }), 0.5),
      recess: plaster(std({ color: 0xe0d5c2, roughness: 0.97, envMapIntensity: 0.5 }), 0.5),
      white: plaster(std({ color: 0xf6f3ee, roughness: 0.9, envMapIntensity: 0.7 }), 0.4),
      sail: std({ color: 0xfbfaf6, roughness: 0.85, side: T.DoubleSide, envMapIntensity: 0.8 }),
      jali: plaster(std({ color: 0xe6dccb, roughness: 0.95, alphaMap: jaliTex(), alphaTest: 0.5, side: T.DoubleSide }), 0.3),
      lamp: std({ color: 0x3b2d22, roughness: 0.5, metalness: 0.6 }), lantern: std({ color: 0xffe2a8, emissive: 0xffb860, emissiveIntensity: 0.6, roughness: 0.4 }),
      asph: std({ color: 0x77736d, roughness: 0.95 }), sand: std({ color: 0xeadfc6, roughness: 1 }),
      roof: std({ color: 0xd8cfbf, roughness: 0.95, envMapIntensity: 0.4 }),
      plinth: std({ color: 0x8c8378, roughness: 0.55 }),
      frame: std({ color: 0x6e4f36, roughness: 0.55, metalness: 0.15 }),
      glass: std({ color: 0x1c2730, roughness: 0.04, metalness: 0.85, envMapIntensity: 1.4 }),
      wood: std({ color: 0x80603f, roughness: 0.75 }),
      turf: std({ color: 0x6c923c, roughness: 1 }),
      metal: std({ color: 0xa7adb2, roughness: 0.4, metalness: 0.6 }),
      dome: plaster(std({ color: 0xf4efe4, roughness: 0.7, envMapIntensity: 0.8 }), 0.3),
      water: std({ color: 0x2aa8c9, roughness: 0.05, metalness: 0.2, envMapIntensity: 1.2, emissive: 0x063445, emissiveIntensity: 0.35 }),
      deck: std({ color: 0xe3dccd, roughness: 0.8 }),
      bark: std({ color: 0x7b6650, roughness: 1 }), leafA: std({ color: 0x66783b, roughness: 0.9 }), leafB: std({ color: 0x7c8c45, roughness: 0.9 }),
      paint: std({ color: 0xf5f6f7, roughness: 0.3, metalness: 0.4, envMapIntensity: 1.1 }), tyre: std({ color: 0x1b1b1b, roughness: 0.9 }),
    };
    // ---------- geometry kit: everything merged per material
    function flip(g) { for (const k in g.attributes) { const a = g.attributes[k], n = a.itemSize, arr = a.array; for (let i = 0; i < a.count; i += 3) for (let j = 0; j < n; j++) { const t = arr[(i + 1) * n + j]; arr[(i + 1) * n + j] = arr[(i + 2) * n + j]; arr[(i + 2) * n + j] = t; } } return g; }
    function mergeList(list) {
      let n = 0; const gs = list.map(([g, m]) => { const x = (g.index ? g.toNonIndexed() : g.clone()).applyMatrix4(m); n += x.attributes.position.count; return x; });
      const P = new Float32Array(n * 3), N = new Float32Array(n * 3), UV = new Float32Array(n * 2); let o = 0;
      gs.forEach((g) => { P.set(g.attributes.position.array, o * 3); N.set(g.attributes.normal.array, o * 3); if (g.attributes.uv) UV.set(g.attributes.uv.array, o * 2); o += g.attributes.position.count; g.dispose(); });
      const out = new T.BufferGeometry(); out.setAttribute('position', new T.BufferAttribute(P, 3)); out.setAttribute('normal', new T.BufferAttribute(N, 3)); out.setAttribute('uv', new T.BufferAttribute(UV, 2)); out.computeBoundingSphere(); return out;
    }
    class Kit {
      constructor() { this.p = {}; }
      add(mat, geo, x, y, z, ry = 0, rx = 0) { (this.p[mat] = this.p[mat] || []).push([geo, new T.Matrix4().compose(new T.Vector3(x, y, z), new T.Quaternion().setFromEuler(new T.Euler(rx, ry, 0)), new T.Vector3(1, 1, 1))]); }
      box(mat, x0, y0, z0, x1, y1, z1) { this.add(mat, new T.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); }
      build(mirror) { const out = {}; for (const k in this.p) { let g = mergeList(this.p[k]); if (mirror) { g.applyMatrix4(new T.Matrix4().makeScale(-1, 1, 1)); flip(g); } out[k] = g; } return out; }
    }
    const shapeArch = (w, h) => { const s = new T.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(w / 2, h - w / 2); s.absarc(0, h - w / 2, w / 2, 0, Math.PI, false); s.lineTo(-w / 2, 0); return s; };
    const shapeRect = (w, h) => { const s = new T.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(w / 2, h); s.lineTo(-w / 2, h); s.lineTo(-w / 2, 0); return s; };
    const ext = (s, d) => new T.ExtrudeGeometry(s, { depth: d, bevelEnabled: false, curveSegments: 10 });
    // a face of a block: origin on the wall surface, +z outward
    function face(b, side) {
      const cx = (b.x0 + b.x1) / 2, cz = (b.z0 + b.z1) / 2;
      return ({ f: [cx, b.z1, 0, b.x1 - b.x0], k: [cx, b.z0, Math.PI, b.x1 - b.x0], r: [b.x1, cz, Math.PI / 2, b.z1 - b.z0], l: [b.x0, cz, -Math.PI / 2, b.z1 - b.z0] })[side];
    }
    function onFace(K, b, side, u, y, mat, geo, out = 0) {
      const [a, c, ry, len] = face(b, side); const s = Math.sin(ry), co = Math.cos(ry);
      // local (u along face, out along normal) -> world
      let x, z; if (side === 'f' || side === 'k') { x = a + (side === 'f' ? u : -u); z = c + (side === 'f' ? out : -out); } else { z = c + (side === 'r' ? -u : u); x = a + (side === 'r' ? out : -out); }
      K.add(mat, geo, x, y, z, ry); return len;
    }
    // window: brown frame, dark reflective glass, mullion
    function win(K, b, side, u, y, w, h, arched) {
      const sh = arched ? shapeArch : shapeRect;
      onFace(K, b, side, u, y - 0.4, 'recess', ext(sh(w + 1.6, h + 1.2), 0.08), 0.02);
      onFace(K, b, side, u, y, 'frame', ext(sh(w + 0.6, h + 0.3), 0.18), 0.03);
      onFace(K, b, side, u, y + 0.15, 'glass', ext(sh(w - 0.2, h - 0.25), 0.1), 0.12);
      onFace(K, b, side, u, y + 0.15, 'frame', new T.BoxGeometry(0.35, h - (arched ? w / 2 : 0.3), 0.12).translate(0, (h - (arched ? w / 2 : 0.3)) / 2, 0.06), 0.18);
      if (arched && w > 1.5) { const sy = y + 0.15 + h - w / 2; onFace(K, b, side, u, sy, 'frame', new T.BoxGeometry(w, 0.3, 0.12), 0.2);
        for (let k = 1; k < 6; k++) { const a = k * Math.PI / 6, r = w / 2 - 0.2; onFace(K, b, side, u, sy, 'frame', new T.BoxGeometry(0.16, r, 0.1).translate(0, r / 2, 0).rotateZ(a - Math.PI / 2), 0.21); } }
    }
    function sail(K, x0, x1, z0, z1, y, up = 1.6) {
      const g = new T.PlaneGeometry(x1 - x0, z1 - z0, 10, 10); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
      for (let i = 0; i < p.count; i++) { const u = (p.getX(i) - (-(x1 - x0) / 2)) / (x1 - x0), v = (p.getZ(i) + (z1 - z0) / 2) / (z1 - z0);
        p.setY(i, up * ((1 - u) * (1 - v) + u * v) - up * 0.35 * ((1 - u) * v + u * (1 - v)) - 0.6 * Math.sin(u * Math.PI) * Math.sin(v * Math.PI)); }
      g.computeVertexNormals(); K.add('sail', g, (x0 + x1) / 2, y, (z0 + z1) / 2);
    }
    const blind = (K, b, side, u, y, w, h) => onFace(K, b, side, u, y, 'recess', ext(shapeArch(w, h), 0.12), 0.01);
    // block with parapet, crenellations, plinth band and roof slab
    function block(K, b, h, cren = true, mat = 'wall') {
      K.box(mat, b.x0, 0.8, b.z0, b.x1, h - 2.6, b.z1);
      K.box('plinth', b.x0 - 0.15, 0, b.z0 - 0.15, b.x1 + 0.15, 0.8, b.z1 + 0.15);
      K.box('roof', b.x0 + 0.5, h - 2.6, b.z0 + 0.5, b.x1 - 0.5, h - 2.45, b.z1 - 0.5);
      const t = 0.6; // parapet walls
      K.box(mat, b.x0, h - 2.6, b.z0, b.x1, h, b.z0 + t); K.box(mat, b.x0, h - 2.6, b.z1 - t, b.x1, h, b.z1);
      K.box(mat, b.x0, h - 2.6, b.z0, b.x0 + t, h, b.z1); K.box(mat, b.x1 - t, h - 2.6, b.z0, b.x1, h, b.z1);
      K.box(mat, b.x0 - 0.25, h - 4.2, b.z0 - 0.25, b.x1 + 0.25, h - 3.8, b.z1 + 0.25); // cornice line
      if (!cren) return;
      for (const side of ['f', 'k', 'l', 'r']) { const len = face(b, side)[3], n = Math.max(1, Math.floor(len / 3.4));
        for (let i = 0; i < n; i++) { const u = -len / 2 + (i + 0.5) * len / n; if (i % 2 === 0) continue; onFace(K, b, side, u, h, mat, new T.BoxGeometry(1.2, 1.7, 0.6).translate(0, 0.85, -0.3), 0); } }
    }
    function railing(K, x0, x1, z, y, alongX = true) {
      const n = Math.floor(Math.abs(x1 - x0) / 0.9);
      for (let i = 0; i <= n; i++) { const p = x0 + (x1 - x0) * i / n; K.add('wood', new T.BoxGeometry(0.34, 2.1, 0.34), alongX ? p : z, y + 1.05, alongX ? z : p); }
      K.add('wood', new T.BoxGeometry(alongX ? Math.abs(x1 - x0) + 0.4 : 0.6, 0.4, alongX ? 0.6 : Math.abs(x1 - x0) + 0.4), alongX ? (x0 + x1) / 2 : z, y + 2.2, alongX ? z : (x0 + x1) / 2);
      K.add('wood', new T.BoxGeometry(alongX ? Math.abs(x1 - x0) : 0.4, 0.3, alongX ? 0.4 : Math.abs(x1 - x0)), alongX ? (x0 + x1) / 2 : z, y + 0.25, alongX ? z : (x0 + x1) / 2);
    }
    function pergola(K, x0, x1, z0, z1, y) {
      for (const [px, pz] of [[x0, z0], [x1, z0], [x0, z1], [x1, z1]]) K.add('wood', new T.BoxGeometry(0.8, 6.2, 0.8), px, y + 3.1, pz);
      K.box('wood', x0 - 0.5, y + 6.2, z1 - 0.4, x1 + 0.5, y + 7.0, z1 + 0.4); K.box('wood', x0 - 0.5, y + 6.2, z0 - 0.4, x1 + 0.5, y + 7.0, z0 + 0.4);
      for (let x = x0; x <= x1 + 0.01; x += 1.1) K.add('wood', new T.BoxGeometry(0.35, 0.5, z1 - z0 + 1.2), x, y + 7.2, (z0 + z1) / 2);
    }
    function arcade(K, x0, x1, z, h, n, d, sailRoof = false, mat = 'wall') { // front wall with arched openings, depth d back from z
      const w = x1 - x0, s = new T.Shape(); s.moveTo(0, 0); s.lineTo(w, 0); s.lineTo(w, h); s.lineTo(0, h); s.lineTo(0, 0);
      const aw = Math.min(5.2, w / n - 1.4), ah = h - 2.2;
      for (let i = 0; i < n; i++) { const cx = (i + 0.5) * w / n, p = new T.Path(); p.moveTo(cx - aw / 2, 0.01); p.lineTo(cx - aw / 2, ah - aw / 2); p.absarc(cx, ah - aw / 2, aw / 2, Math.PI, 0, true); p.lineTo(cx + aw / 2, 0.01); p.lineTo(cx - aw / 2, 0.01); s.holes.push(p); }
      K.add(mat, ext(s, 1.4), x0, 0, z - 1.4);
      if (sailRoof) { for (const x of [x0, x1 - 1.4]) K.box(mat, x, 0, z - d, x + 1.4, h + 0.9, z - d + 1.4);
        K.box(mat, x0, h - 0.4, z - d, x0 + 1.4, h + 0.9, z); K.box(mat, x1 - 1.4, h - 0.4, z - d, x1, h + 0.9, z); K.box(mat, x0, h - 0.4, z - d, x1, h + 0.9, z - d + 1.2);
        sail(K, x0 + 0.7, x1 - 0.7, z - d + 0.6, z - 0.7, h + 0.4); return; }
      K.box(mat, x0, h - 0.1, z - d, x1, h + 0.9, z); K.box('roof', x0 + 0.4, h + 0.9, z - d + 0.4, x1 - 0.4, h + 1.0, z - 0.4);
      K.box(mat, x0 - 0.2, h + 0.9, z - 0.6, x1 + 0.2, h + 2.0, z);
    }
    // ---------- villa templates (R1 / R2 / R3), front = +z
    function villaKit(type) {
      const K = new Kit();
      const big = type === 'R1', small = type === 'R3';
      const A = { x0: -18, x1: small ? -3 : -1, z0: -13, z1: 8 }, Cw = { x0: small ? -3 : -1, x1: big ? 18 : 15, z0: -13, z1: 3 };
      const hA = 18.5, hC = 15;
      block(K, A, hA); block(K, Cw, hC);
      // tower front: 3 tall windows ground floor, 3 blind arches above, vents under parapet
      const aw = A.x1 - A.x0;
      for (let i = -1; i <= 1; i++) { win(K, A, 'f', i * aw / 4, 1.2, 2.8, 6.0, false); blind(K, A, 'f', i * aw / 4, 8.6, 3.2, 5.8); onFace(K, A, 'f', i * aw / 4, hA - 6.3, 'recess', new T.BoxGeometry(3.0, 1.5, 0.1), 0.02); }
      // tower sides: arched windows
      win(K, A, 'l', -4, 9.2, 2.4, 5.0, true); win(K, A, 'l', 4, 9.2, 2.4, 5.0, true); win(K, A, 'l', 0, 1.6, 2.6, 5.0, false);
      win(K, A, 'k', -4, 9.2, 2.4, 5.0, true); win(K, A, 'k', 4, 1.6, 2.4, 5.0, false);
      // wing: first-floor arched windows to the terrace, ground windows
      const cw = Cw.x1 - Cw.x0;
      win(K, Cw, 'f', -cw / 4, 1.4, 3.0, 5.4, false); win(K, Cw, 'f', cw / 4, 1.4, 3.0, 5.4, false);
      win(K, Cw, 'r', -3, 8.6, 2.4, 5.0, true); win(K, Cw, 'r', 3, 8.6, 2.4, 5.0, true); win(K, Cw, 'k', 0, 8.6, 2.4, 5.0, true); win(K, Cw, 'k', -6, 1.6, 2.4, 4.6, false);
      // roof terrace on the wing (open part over the front), pergola and railing
      const tx0 = Cw.x0 + 3, tx1 = Cw.x1 - 1.5;
      pergola(K, tx0, tx1, -6, 2.4, hC - 2.45); railing(K, tx0, tx1, 2.6, hC);
      // first-floor balcony with pergola on the tower side
      K.box('wall', A.x0 + 2, 7.2, A.z1, A.x0 + 9, 7.8, A.z1 + 3.2); railing(K, A.x0 + 2.2, A.x0 + 8.8, A.z1 + 3.0, 7.8);
      // arched carport / entrance arcade in front of the wing
      if (!small) arcade(K, Cw.x0 + 1, Cw.x1, Cw.z1 + 10, 7.5, big ? 3 : 2, 10, true);
      else arcade(K, A.x0 + 2, A.x1 - 1, A.z1 + 8, 7.2, 2, 8, true);
      K.add('jali', new T.BoxGeometry(4.6, 6.6, 0.5), small ? A.x1 + 3 : Cw.x0 - 2.6, 3.3, (small ? A.z1 : Cw.z1) + 8.4);
      for (const u of [-aw / 2 + 1.6, aw / 2 - 1.6]) { onFace(K, A, 'f', u, 5.2, 'lamp', new T.BoxGeometry(0.9, 1.4, 0.7), 0.4); onFace(K, A, 'f', u, 5.35, 'lantern', new T.BoxGeometry(0.6, 1.0, 0.6), 0.45); }
      // boundary wall with a gap for the gate, turf garden at the back
      const W0 = -23, W1 = 23, Z0 = -19, Z1 = 19, wh = 5, t = 0.6;
      K.box('wall', W0, 0, Z0, W1, wh, Z0 + t); K.box('wall', W0, 0, Z0, W0 + t, wh, Z1); K.box('wall', W1 - t, 0, Z0, W1, wh, Z1);
      K.box('wall', W0, 0, Z1 - t, -1, wh, Z1); K.box('wall', 13, 0, Z1 - t, W1, wh, Z1);
      for (const x of [W0, W1]) K.box('wall', x - 0.3, wh, Z0 - 0.3, x + 0.3, wh + 0.5, Z1 + 0.3);
      K.box('turf', W0 + 1, 0, Z0 + 1, W1 - 1, 0.15, -14); K.box('turf', A.x0 - 4, 0, -13, A.x0 - 0.5, 0.15, Z1 - 1);
      K.box('deck', -1, 0, Cw.z1, 13, 0.12, Z1);
      return K;
    }
    // ---------- roads and land from the site plan (ground texture)
    const PW = D.w, PH = D.h, Kp = Math.min(1.6, (Math.min(maxTex, mobile ? 4096 : 8192)) / PW);
    const gc = cnv(Math.round(PW * Kp), Math.round(PH * Kp)), g = gc.getContext('2d'); g.scale(Kp, Kp);
    const pat = (size, draw) => { const c = cnv(size, size), x = c.getContext('2d'); draw(x, size); return g.createPattern(c, 'repeat'); };
    const sandP = pat(256, (x, s) => { x.fillStyle = '#d6c6a3'; x.fillRect(0, 0, s, s); for (let i = 0; i < 2600; i++) { x.fillStyle = `rgba(${rnd() < 0.5 ? '120,100,70' : '255,248,230'},${0.05 + rnd() * 0.08})`; x.fillRect(rnd() * s, rnd() * s, 1 + rnd() * 3, 1 + rnd() * 3); } });
    const baseP = pat(256, (x, s) => { x.fillStyle = '#d3ccbd'; x.fillRect(0, 0, s, s); for (let i = 0; i < 1800; i++) { x.fillStyle = `rgba(${rnd() < 0.5 ? '110,100,85' : '250,246,236'},${0.05 + rnd() * 0.07})`; x.fillRect(rnd() * s, rnd() * s, 1 + rnd() * 4, 1 + rnd() * 2); } });
    const stampP = pat(128, (x, s) => { x.fillStyle = '#d8c8aa'; x.fillRect(0, 0, s, s); x.strokeStyle = 'rgba(120,98,70,.5)'; x.lineWidth = 0.8;
      for (let i = 0; i < 140; i++) { const cx = rnd() * s, cy = rnd() * s, r = 3 + rnd() * 4; x.beginPath(); for (let k = 0; k < 6; k++) { const a = k / 6 * Math.PI * 2 + rnd() * 0.5; x.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); } x.closePath(); x.stroke(); }
      for (let i = 0; i < 300; i++) { x.fillStyle = `rgba(255,255,255,${rnd() * 0.08})`; x.fillRect(rnd() * s, rnd() * s, 1, 1); } });
    const turfP = pat(64, (x, s) => { x.fillStyle = '#6b9139'; x.fillRect(0, 0, s, s); for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(${rnd() < 0.5 ? '40,70,20' : '160,190,90'},${0.12 + rnd() * 0.15})`; x.fillRect(rnd() * s, rnd() * s, 1, 1 + rnd() * 2); } });
    stampP.setTransform(new DOMMatrix().scale(0.12)); turfP.setTransform(new DOMMatrix().scale(0.25)); baseP.setTransform(new DOMMatrix().scale(0.5));
    g.fillStyle = sandP; g.fillRect(-PW, -PH, PW * 3, PH * 3);
    // beach along the north-east edge (the sea is beyond it)
    const e1 = [1975, 55], e2 = [2955, 608], edx = e2[0] - e1[0], edy = e2[1] - e1[1], eln = Math.hypot(edx, edy), nx = edy / eln, ny = -edx / eln;
    const band = (o0, o1, st) => { g.fillStyle = st; g.beginPath(); g.moveTo(e1[0] - edx * 3 + nx * o0, e1[1] - edy * 3 + ny * o0); g.lineTo(e2[0] + edx * 3 + nx * o0, e2[1] + edy * 3 + ny * o0); g.lineTo(e2[0] + edx * 3 + nx * o1, e2[1] + edy * 3 + ny * o1); g.lineTo(e1[0] - edx * 3 + nx * o1, e1[1] - edy * 3 + ny * o1); g.fill(); };
    band(10, 200, '#efe5cd'); band(150, 200, '#e2d4b4');
    const bnd = new Path2D(D.boundary); g.fillStyle = baseP; g.fill(bnd);
    const L = D.land || {}, fill = (p, st) => { if (p) { g.fillStyle = st; g.fill(new Path2D(p)); } }, line = (p, c, w) => { if (p) { g.strokeStyle = c; g.lineWidth = w; g.lineCap = g.lineJoin = 'round'; g.stroke(new Path2D(p)); } };
    if (L.interlock) { fill(L.interlock[0], stampP); fill(L.interlock[1], stampP); }
    if (L.soft) { fill(L.soft[0], turfP); g.globalAlpha = 0.75; fill(L.soft[1], turfP); g.globalAlpha = 1; }
    if (L.curb) { line(L.curb[2], 'rgba(70,66,60,.55)', 1.6); line(L.curb[2], '#ebe7df', 0.9); }
    if (L.bike) { line(L.bike[2], '#b4846c', 2.6); line(L.bike[3], '#b4846c', 2.6); }
    const gtx = new T.CanvasTexture(gc); gtx.colorSpace = T.SRGBColorSpace; gtx.anisotropy = R.capabilities.getMaxAnisotropy();
    gtx.generateMipmaps = true; gtx.minFilter = T.LinearMipmapLinearFilter;
    const groundMat = std({ map: gtx, roughness: 0.97, envMapIntensity: 0.3 });
    groundMat.onBeforeCompile = (sh) => { sh.uniforms.detailMap = { value: detailTex };
      sh.fragmentShader = 'uniform sampler2D detailMap;\n' + sh.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n float dn = texture2D(detailMap, vMapUv * vec2(' + (PW / 9).toFixed(1) + ',' + (PH / 9).toFixed(1) + ')).r; float dn2 = texture2D(detailMap, vMapUv * vec2(' + (PW / 80).toFixed(1) + ',' + (PH / 80).toFixed(1) + ')).r; diffuseColor.rgb *= (0.86 + 0.28 * dn) * (0.93 + 0.14 * dn2);'); };
    const ground = new T.Mesh(new T.PlaneGeometry(PW * 3, PH * 3), groundMat); ground.rotation.x = -Math.PI / 2; ground.position.set(PW / 2, 0, PH / 2); ground.receiveShadow = true;
    { const uv = ground.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 3 - 1, uv.getY(i) * 3 - 1); }
    gtx.wrapS = gtx.wrapT = T.ClampToEdgeWrapping; S.add(ground);
    // sea: reflective water with moving ripples
    const wn = (() => { const n = 256, c = cnv(n, n), x = c.getContext('2d'), im = x.createImageData(n, n), hgt = new Float32Array(n * n);
      for (let k = 0; k < 40; k++) { const fx = 1 + Math.floor(rnd() * 8), fy = Math.floor(rnd() * 8) - 4, ph = rnd() * 6.28, a = 1 / (1 + Math.hypot(fx, fy)); for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) hgt[j * n + i] += a * Math.sin(2 * Math.PI * (fx * i + fy * j) / n + ph); }
      for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const dx = hgt[j * n + (i + 1) % n] - hgt[j * n + (i + n - 1) % n], dy = hgt[((j + 1) % n) * n + i] - hgt[((j + n - 1) % n) * n + i], o = (j * n + i) * 4; im.data[o] = 128 - dx * 60; im.data[o + 1] = 128 - dy * 60; im.data[o + 2] = 255; im.data[o + 3] = 255; }
      x.putImageData(im, 0, 0); const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(160, 50); t.colorSpace = T.NoColorSpace; return t; })();
    const seaMat = std({ color: 0x1f6f8f, roughness: 0.06, metalness: 0.15, envMapIntensity: 1.25, normalMap: wn, normalScale: new T.Vector2(0.35, 0.35) });
    const sea = new T.Mesh(new T.PlaneGeometry(40000, 12000), seaMat); sea.rotation.x = -Math.PI / 2; sea.rotation.z = -Math.atan2(edy, edx);
    sea.position.set((e1[0] + e2[0]) / 2 + nx * (185 + 6000), 0.35, (e1[1] + e2[1]) / 2 + ny * (185 + 6000)); sea.receiveShadow = true; S.add(sea);
    const tick = (t) => { wn.offset.set(t * 0.004, t * 0.0025); };
    const desert = new T.Mesh(new T.CircleGeometry(60000, 64), std({ color: 0xcdbd9c, roughness: 1 })); desert.rotation.x = -Math.PI / 2; desert.position.set(PW / 2, -0.8, PH / 2); S.add(desert);
    // perimeter wall along the site boundary
    const bp = (D.boundary.match(/-?\d+(?:\.\d+)? -?\d+(?:\.\d+)?/g) || []).map((s) => s.split(' ').map(Number));
    { const K = new Kit(); for (let i = 0; i < bp.length; i++) { const [x0, z0] = bp[i], [x1, z1] = bp[(i + 1) % bp.length], len = Math.hypot(x1 - x0, z1 - z0);
        K.add('wall', new T.BoxGeometry(len, 6, 0.8), (x0 + x1) / 2, 3, (z0 + z1) / 2, -Math.atan2(z1 - z0, x1 - x0)); K.add('wall', new T.BoxGeometry(len, 0.6, 1.3), (x0 + x1) / 2, 6.3, (z0 + z1) / 2, -Math.atan2(z1 - z0, x1 - x0)); }
      const gs = K.build(false); for (const k in gs) { const m = new T.Mesh(gs[k], M[k]); m.castShadow = m.receiveShadow = true; S.add(m); } }
    // curb lines -> street points (for tree rows, cars and villa orientation)
    const curbPts = [];
    if (L.curb && L.curb[2]) { const segs = L.curb[2].split('M').filter(Boolean).map((s) => { const n = s.trim().split(/[\s,]+/).map(Number), out = []; for (let i = 0; i + 1 < n.length; i += 2) out.push([n[i], n[i + 1]]); return out; });
      segs.forEach((pts) => { let acc = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); acc += d; if (acc >= 5) { acc = 0; curbPts.push([pts[i][0], pts[i][1], Math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0])]); } } }); }
    // ---------- villas: one template per type and hand, instanced
    const ROT = -Math.atan2(553, 980), pick = [], wallMeshes = [];
    const nearest = (x, y) => { let b = null, bd = 1e9; for (const p of curbPts) { const d = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (d < bd) { bd = d; b = p; } } return b; };
    const kits = {}, groups = {};
    V.forEach((v, i) => {
      const t = ['R1', 'R2', 'R3'].includes(v.t) ? v.t : 'R2', mir = i % 2 === 1, key = t + (mir ? 'm' : '');
      const n = nearest(v.x, v.y); let rot = ROT;
      if (n) { const a = Math.atan2(n[0] - v.x, n[1] - v.y); let best = 0, bd = 9; for (let k = 0; k < 4; k++) { const r = ROT + k * Math.PI / 2; let dd = Math.abs(((a - r) % (2 * Math.PI) + 3 * Math.PI) % (2 * Math.PI) - Math.PI); if (dd < bd) { bd = dd; best = r; } } rot = best; }
      v.rot = rot; v.hl = [48, 22, 40]; v.h = 22; v.kind = 'V';
      (groups[key] = groups[key] || []).push(v);
    });
    const m4 = new T.Matrix4(), q4 = new T.Quaternion(), one = new T.Vector3(1, 1, 1), yAx = new T.Vector3(0, 1, 0), white = new T.Color(1, 1, 1);
    for (const key in groups) {
      const t = key.slice(0, 2), mir = key.endsWith('m'); kits[t] = kits[t] || villaKit(t); const geos = kits[t].build(mir), list = groups[key];
      for (const mat in geos) {
        const im = new T.InstancedMesh(geos[mat], M[mat], list.length); im.castShadow = mat !== 'turf' && mat !== 'deck'; im.receiveShadow = true;
        list.forEach((v, i) => { im.setMatrixAt(i, m4.compose(new T.Vector3(v.x, 0, v.y), q4.setFromAxisAngle(yAx, v.rot), one)); if (mat === 'wall' || mat === 'recess') im.setColorAt(i, white); });
        im.userData.list = list; S.add(im);
        if (mat === 'wall') { pick.push(im); wallMeshes.push(im); } if (mat === 'recess') wallMeshes.push(im);
      }
    }
    // ---------- community buildings
    const SPEC = { AD: [150, 110, 4, 'admin'], BA: [130, 90, 2, 'bach'], CC: [150, 110, 3, 'civic'], CO: [160, 90, 2, 'shed'], HB: [130, 90, 4, 'civic'], IS: [170, 120, 3, 'shed'],
      MQ: [90, 90, 2, 'mosque'], PA: [100, 50, 1, 'pav'], RG: [60, 26, 1, 'gate2'], SC: [120, 100, 1, 'swim'], SG: [60, 26, 1, 'gate2'], SR: [80, 50, 2, 'gateSR'], UT: [90, 60, 2, 'shed'], WS: [140, 90, 2, 'shed'] };
    const SEA = { PA: 1, SC: 1 }; // these face the sea (local +z toward the beach)
    const FH = 8.4;
    function civicFacade(K, b, floors, h, sides = ['f', 'k', 'l', 'r']) {
      for (const side of sides) { const len = face(b, side)[3], n = Math.max(2, Math.floor((len - 8) / 9));
        for (let i = 0; i < n; i++) { const u = -len / 2 + 4 + (i + 0.5) * (len - 8) / n;
          for (let f = 0; f < floors; f++) { const y = 1.4 + f * FH;
            if (f === floors - 1 && floors > 1) win(K, b, side, u, y + 0.4, 3.6, 6.4, true);
            else if (f === 0 && side === 'f') win(K, b, side, u, y, 4.4, 6.0, false);
            else { win(K, b, side, u - 1.3, y + 0.8, 1.6, 4.6, false); win(K, b, side, u + 1.3, y + 0.8, 1.6, 4.6, false); } } }
        for (const s2 of [-1, 1]) onFace(K, b, side, s2 * (len / 2 - 1.5), 0.8, 'wall', new T.BoxGeometry(3, h - 3.4, 0.7).translate(0, (h - 3.4) / 2, 0.35), 0); }
    }
    function parking(K, x0, x1, z0, z1) { // asphalt bays under rows of white shade sails
      K.box('asph', x0, 0, z0, x1, 0.12, z1); const rows = Math.max(1, Math.floor((z1 - z0) / 22));
      for (let r = 0; r < rows; r++) { const zz = z0 + 4 + r * 22; for (let x = x0 + 2; x < x1 - 9; x += 10) { K.box('metal', x + 4.6, 0, zz + 5.5, x + 5.2, 6.5, zz + 6.1); sail(K, x, x + 9.6, zz, zz + 11, 6.2, 1.2); } }
    }
    function twinArch(K, x0, z, w, h, d, mat) { // monumental gate with two arches (security reception)
      const s = new T.Shape(); s.moveTo(0, 0); s.lineTo(w, 0); s.lineTo(w, h); s.lineTo(0, h); s.lineTo(0, 0);
      const aw = w * 0.36, ah = h * 0.78;
      for (const cx of [w * 0.25, w * 0.75]) { const p = new T.Path(); p.moveTo(cx - aw / 2, 0.01); p.lineTo(cx - aw / 2, ah - aw / 2); p.absarc(cx, ah - aw / 2, aw / 2, Math.PI, 0, true); p.lineTo(cx + aw / 2, 0.01); p.lineTo(cx - aw / 2, 0.01); s.holes.push(p); }
      K.add(mat, ext(s, d), x0, 0, z - d);
      const b = { x0, x1: x0 + w, z0: z - d, z1: z }; for (let i = 0; i < Math.floor(w / 3.4); i += 2) { K.box(mat, x0 + 1 + i * 3.4, h, z - 0.6, x0 + 2.2 + i * 3.4, h + 1.8, z); K.box(mat, x0 + 1 + i * 3.4, h, z - d, x0 + 2.2 + i * 3.4, h + 1.8, z - d + 0.6); }
      for (const cx of [w * 0.25, w * 0.75]) for (let k = 0; k < 18; k++) { const a = Math.PI * (k + 0.5) / 18, r = aw / 2 - 0.4; K.add('wood', new T.BoxGeometry(0.4, 0.4, d - 1.2), x0 + cx + Math.cos(a) * r, ah - aw / 2 + Math.sin(a) * r, z - d / 2); }
      return b;
    }
    BL.forEach((bd) => {
      const [w, d, floors, kind] = SPEC[bd.c] || [100, 70, 2, 'civic'], K = new Kit(), b = { x0: -w / 2, x1: w / 2, z0: -d / 2, z1: d / 2 };
      let h = floors * FH + 3.5, top = h;
      if (kind === 'civic') { block(K, b, h); civicFacade(K, b, floors, h);
        const c = { x0: -w / 2 + 16, z0: -d / 2 + 14 }; block(K, { x0: c.x0, x1: c.x0 + 24, z0: c.z0, z1: c.z0 + 16 }, h + 9); top = h + 9;
        if (bd.c === 'CC') { for (let i = 0; i < 6; i++) for (let j = 0; j < 3; j++) K.add('white', new T.CylinderGeometry(0.9, 1.1, 16, 12), -30 + i * 12, 8, d / 2 + 16 + j * 12); // plaza canopy columns
          K.box('deck', -40, 0, d / 2 + 4, 40, 0.2, d / 2 + 46); parking(K, -w / 2 - 70, -w / 2 - 6, -d / 2, d / 2); } }
      if (kind === 'admin') { // four-storey ring around a planted courtyard, colonnade with sails, shaded parking
        const t = 24, blocks = [{ x0: -w / 2, x1: w / 2, z0: d / 2 - t, z1: d / 2 }, { x0: -w / 2, x1: w / 2, z0: -d / 2, z1: -d / 2 + t }, { x0: -w / 2, x1: -w / 2 + t, z0: -d / 2 + t, z1: d / 2 - t }, { x0: w / 2 - t, x1: w / 2, z0: -d / 2 + t, z1: d / 2 - t }];
        blocks.forEach((bb, i) => { block(K, bb, h); civicFacade(K, bb, floors, h, i === 0 ? ['f', 'k', 'l', 'r'] : i === 1 ? ['k', 'f', 'l', 'r'] : i === 2 ? ['l', 'r'] : ['r', 'l']); });
        block(K, { x0: -w / 2 - 4, x1: -w / 2 + 34, z0: d / 2 - 30, z1: d / 2 + 2 }, h + 6); top = h + 6;
        K.box('turf', -w / 2 + t, 0, -d / 2 + t, w / 2 - t, 0.2, d / 2 - t);
        arcade(K, -w / 2, w / 2, d / 2 + 14, 9, 12, 12, true); parking(K, -w / 2, w / 2, d / 2 + 26, d / 2 + 72); }
      if (kind === 'bach') { // U-shaped two-storey blocks round a courtyard, gallery with pergola
        const L = { x0: -w / 2, x1: -w / 2 + 34, z0: -d / 2, z1: d / 2 - 10 }, Rr = { x0: w / 2 - 30, x1: w / 2, z0: -d / 2, z1: d / 2 }, Bk = { x0: -w / 2 + 34, x1: w / 2 - 30, z0: -d / 2, z1: -d / 2 + 18 };
        block(K, L, 11.5); block(K, Rr, h); block(K, Bk, h); civicFacade(K, Rr, floors, h, ['r', 'f']); civicFacade(K, Bk, floors, h, ['k']); win(K, L, 'f', -8, 1.4, 4.4, 5, false); win(K, L, 'f', 8, 1.4, 4.4, 5, false); win(K, L, 'l', 0, 1.4, 4.4, 5, false);
        for (let z = Bk.z1 + 4; z < Rr.z1 - 4; z += 8) win(K, Rr, 'l', z - (Rr.z0 + Rr.z1) / 2, 1.4, 3.4, 6, true);
        K.box('wall', Rr.x0 - 6, FH, Bk.z1, Rr.x0, FH + 0.6, Rr.z1 - 4); railing(K, Bk.z1 + 1, Rr.z1 - 5, Rr.x0 - 5.8, FH + 0.6, false); pergola(K, Rr.x0 - 6, Rr.x0 - 0.5, Bk.z1 + 1, Rr.z1 - 5, FH + 0.6);
        arcade(K, L.x1, Rr.x0, d / 2, 8.5, 3, 2); K.box('deck', L.x1, 0, Bk.z1, Rr.x0, 0.2, d / 2); parking(K, w / 2 + 6, w / 2 + 36, -d / 2, d / 2); }
      if (kind === 'pav') { // white beach pavilion: open arcade, raised clerestory, timber louvre canopy
        block(K, b, 11.5, false, 'white'); arcade(K, -w / 2, w / 2 - 22, d / 2 + 12, 10.5, 5, 12, false, 'white');
        K.box('white', -w / 2 + 20, 11.5, -d / 2 + 10, w / 2 - 20, 15, d / 2 - 10);
        for (let x = -w / 2; x <= w / 2 - 22; x += 1.6) K.box('wood', x, 11.4, d / 2 + 12, x + 0.5, 11.9, d / 2 + 21);
        for (let x = -w / 2 + 4; x <= w / 2 - 22; x += 16) { K.box('wood', x, 11.0, d / 2 + 12, x + 0.6, 11.4, d / 2 + 21); K.add('wood', new T.BoxGeometry(0.5, 5, 0.5), x + 0.3, 9.2, d / 2 + 13.6, 0, 0.6); }
        K.box('deck', -w / 2 - 20, 0, -d / 2 - 12, w / 2 + 20, 0.25, d / 2 + 40); top = 15; }
      if (kind === 'swim') { // pool courtyard framed by arcades, main block with crenellated parapet
        const back = { x0: -w / 2, x1: w / 2, z0: -d / 2, z1: -d / 2 + 26 }; block(K, back, 17); civicFacade(K, back, 2, 17, ['k', 'l', 'r']);
        for (let x = -w / 2 + 10; x < w / 2 - 6; x += 12) win(K, back, 'f', x - 0, 1.4, 5, 8, true);
        const sideL = { x0: -w / 2, x1: -w / 2 + 14, z0: -d / 2 + 26, z1: d / 2 }, sideR = { x0: w / 2 - 14, x1: w / 2, z0: -d / 2 + 26, z1: d / 2 };
        block(K, sideL, 10); block(K, sideR, 10); for (let z = -d / 2 + 34; z < d / 2 - 4; z += 10) { win(K, sideL, 'r', z - (sideL.z0 + sideL.z1) / 2, 1.0, 4.6, 7, true); win(K, sideR, 'l', -(z - (sideR.z0 + sideR.z1) / 2), 1.0, 4.6, 7, true); }
        arcade(K, -w / 2 + 14, w / 2 - 14, d / 2, 9, 6, 1.4, false); for (let x = -w / 2 + 18; x < w / 2 - 18; x += 15) sail(K, x, x + 14, d / 2 - 12, d / 2 - 1.4, 9.4, 1.0);
        K.box('deck', -w / 2 + 14, 0, -d / 2 + 26, w / 2 - 14, 0.3, d / 2); K.box('water', -w / 2 + 22, 0, -d / 2 + 34, w / 2 - 22, 0.42, d / 2 - 16); top = 19; }
      if (kind === 'gateSR') { // security reception block and the monumental twin-arch gate
        block(K, b, h); civicFacade(K, b, floors, h, ['f', 'k', 'l']); const g = twinArch(K, w / 2, d / 2, 74, 34, 14, 'wall'); top = 36;
        K.box('wall', -w / 2 - 40, 0, d / 2 - 1, -w / 2, 6, d / 2); K.box('wall', w / 2 + 74, 0, d / 2 - 1, w / 2 + 120, 6, d / 2);
        for (let x = 0; x < 40; x += 1.2) K.box('wood', w / 2 + 4 + x, 0, d / 2 + 2, w / 2 + 4.5 + x, 4.5, d / 2 + 2.5); bd.wide = w + 74; }
      if (kind === 'gate2') { // secondary gatehouse: two crenellated portal frames, glazed booth with timber, slatted timber fence
        for (const [x0, span] of [[-34, 26], [6, 30]]) { K.box('wall', x0, 0, -3, x0 + 5, 18, 3); K.box('wall', x0 + span, 0, -3, x0 + span + 5, 18, 3); K.box('wall', x0, 18, -3, x0 + span + 5, 22, 3);
          for (let x = x0 + 2; x < x0 + span + 3; x += 3.4) K.box('wall', x, 22, -0.5, x + 0.9, 23.4, 0.5); for (let x = x0 + 6; x < x0 + span; x += 1.4) K.box('wood', x, 16.4, -2.8, x + 0.5, 17.6, 2.8); }
        K.box('glass', -6, 0, -4, 4, 14, 4); K.box('wood', -6.3, 7, -4.3, 4.3, 9, 4.3); K.box('wall', -6.5, 14, -4.5, 4.5, 15, 4.5);
        for (let x = -60; x < 60; x += 1.1) { if (x > -38 && x < 40) continue; K.box('wood', x, 0, 10, x + 0.55, 6 + ((x * 7) % 3), 10.6); } top = 24; }
      if (kind === 'shed') { const hb = floors * FH + 8; h = hb; block(K, b, hb, false);
        for (let x = -w / 2 + 8; x < w / 2 - 4; x += 10) onFace(K, b, 'k', x, 4, 'recess', new T.BoxGeometry(6, hb - 9, 0.15), 0.02);
        const a = { x0: -w / 2 + 8, x1: w / 2 - 8, z0: d / 2, z1: d / 2 + 16 }; block(K, a, 13.5); const len = a.x1 - a.x0, n = Math.floor(len / 9);
        for (let i = 0; i < n; i++) { win(K, a, 'f', -len / 2 + (i + 0.5) * len / n, 1.0, 3.6, 7.6, true); }
        for (let i = 0; i < 10; i++) K.box('metal', -w / 2 + 10 + (i % 5) * (w - 20) / 5, hb - 2.45, -d / 2 + 12 + Math.floor(i / 5) * 24, -w / 2 + 16 + (i % 5) * (w - 20) / 5, hb + 1.5, -d / 2 + 18 + Math.floor(i / 5) * 24);
        top = hb; }
      if (kind === 'mosque') { block(K, b, 17); for (const side of ['f', 'k', 'l', 'r']) for (let i = -2; i <= 2; i++) win(K, b, side, i * 14, 2.2, 3.4, 9.5, true);
        K.add('dome', new T.CylinderGeometry(21, 21, 4, 48), 0, 16.5, 0); K.add('dome', new T.SphereGeometry(21, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), 0, 18.5, 0);
        K.add('frame', new T.CylinderGeometry(0.5, 0.5, 6, 8), 0, 42, 0); K.add('dome', new T.SphereGeometry(1.2, 12, 8), 0, 45.5, 0);
        const mx = w / 2 + 9, mz = -d / 2 + 9; K.box('wall', mx - 4.5, 0, mz - 4.5, mx + 4.5, 28, mz + 4.5); K.add('wall', new T.CylinderGeometry(3.2, 3.6, 30, 24), mx, 43, mz);
        K.add('wall', new T.CylinderGeometry(5, 5, 1.2, 24), mx, 46, mz); K.add('dome', new T.ConeGeometry(3.4, 9, 24), mx, 62.5, mz); K.add('wall', new T.CylinderGeometry(3, 3, 12, 24), mx, 52, mz);
        for (let i = -1; i <= 1; i++) win(K, { x0: mx - 4.5, x1: mx + 4.5, z0: mz - 4.5, z1: mz + 4.5 }, 'f', 0, 6 + (i + 1) * 7, 1.6, 4, true);
        top = 46; h = 17; }
      const G = new T.Group(); G.position.set(bd.x, 0, bd.y); G.rotation.y = ROT + (SEA[bd.c] ? Math.PI : 0); S.add(G);
      const gs = K.build(false); for (const k in gs) { const m = new T.Mesh(gs[k], M[k]); m.castShadow = !['deck', 'water', 'asph', 'turf'].includes(k); m.receiveShadow = true; G.add(m); if (k === 'wall' || (k === 'white' && !gs.wall)) { m.userData.it = bd; pick.push(m); bd.wallMesh = m; bd.wallBase = M[k]; } }
      bd.kind = 'B'; bd.rot = G.rotation.y; bd.hl = [w + 8, top + 3, d + 8]; bd.h = top; bd.size = Math.max(w, d);
    });
    // ---------- trees along the streets, palms near the community buildings, a few parked cars
    const blockers = [...V.map((v) => [v.x, v.y, 31]), ...BL.map((b) => [b.x, b.y, (SPEC[b.c] || [100])[0] * 0.75 + 14])];
    const free = (x, y) => !blockers.some((p) => (p[0] - x) ** 2 + (p[1] - y) ** 2 < p[2] * p[2]);
    const nearB = (x, y) => BL.some((b) => (b.x - x) ** 2 + (b.y - y) ** 2 < 260 * 260);
    const treePos = [], palmPos = [];
    curbPts.forEach((p, i) => { if (i % 5) return; const off = (i % 10 ? 3.5 : -3.5), x = p[0] + Math.sin(p[2]) * off, y = p[1] - Math.cos(p[2]) * off; if (!free(x, y)) return; (nearB(x, y) && i % 3 === 0 ? palmPos : treePos).push([x, y, 0.75 + rnd() * 0.5]); });
    if (L.soft && L.soft[0]) { const sp = new Path2D(L.soft[0]), tc = cnv(4, 4).getContext('2d'); for (let k = 0; k < 9000 && treePos.length < 2600; k++) { const x = rnd() * PW, y = rnd() * PH; if (tc.isPointInPath(sp, x, y) && free(x, y) && rnd() < 0.5) treePos.push([x, y, 0.8 + rnd() * 0.6]); } }
    { // young street tree: slim trunk, open crown of several clumps
      const K = new Kit(); K.add('bark', new T.CylinderGeometry(0.22, 0.32, 7, 6), 0, 3.5, 0);
      const KL = new Kit(); for (let i = 0; i < 10; i++) { const a = i * 2.4, r = 0.6 + (i % 4) * 0.5; KL.add('leafA', new T.IcosahedronGeometry(1.1 + (i % 3) * 0.35, 1), Math.cos(a) * r, 6.6 + (i % 5) * 0.6, Math.sin(a) * r); }
      const gt = K.build(false).bark, gl = KL.build(false).leafA, n = treePos.length;
      const it = new T.InstancedMesh(gt, M.bark, n), il = new T.InstancedMesh(gl, std({ color: 0xffffff, roughness: 0.9 }), n); it.castShadow = il.castShadow = true; il.receiveShadow = true;
      const col = new T.Color(); treePos.forEach((p, i) => { const s = p[2]; m4.compose(new T.Vector3(p[0], 0, p[1]), q4.setFromAxisAngle(yAx, rnd() * 6.28), new T.Vector3(s, s * (0.9 + rnd() * 0.3), s)); it.setMatrixAt(i, m4); il.setMatrixAt(i, m4); il.setColorAt(i, rnd() < 0.12 ? col.setHSL(0.93 + rnd() * 0.03, 0.55, 0.5) : col.setHSL(0.2 + rnd() * 0.06, 0.38 + rnd() * 0.15, 0.17 + rnd() * 0.08)); });
      S.add(it, il);
    }
    { // date palm: tall trunk and drooping fronds (alpha-textured leaf blades)
      const fc = cnv(64, 256), fx = fc.getContext('2d'); fx.strokeStyle = '#5f7a34'; fx.lineWidth = 3; fx.beginPath(); fx.moveTo(32, 0); fx.lineTo(32, 256); fx.stroke();
      for (let y = 6; y < 250; y += 5) { const w = 30 * Math.sin((y / 256) * Math.PI) + 3; fx.strokeStyle = y % 10 ? '#6f8c3c' : '#58722e'; fx.lineWidth = 2; fx.beginPath(); fx.moveTo(32, y); fx.lineTo(32 - w, y + 9); fx.moveTo(32, y); fx.lineTo(32 + w, y + 9); fx.stroke(); }
      const ft = new T.CanvasTexture(fc); ft.colorSpace = T.SRGBColorSpace;
      const frondMat = std({ map: ft, alphaTest: 0.4, side: T.DoubleSide, roughness: 0.85 });
      const crown = []; for (let i = 0; i < 16; i++) { const g2 = new T.PlaneGeometry(2.6, 9, 1, 6); const p = g2.attributes.position; for (let k = 0; k < p.count; k++) { const yy = p.getY(k) + 4.5; p.setY(k, yy); p.setZ(k, -0.035 * yy * yy); }
        g2.computeVertexNormals(); g2.rotateX(-Math.PI / 2 + (i < 8 ? 0.55 : 1.05)); g2.rotateY(i * (Math.PI * 2 / 8) + (i < 8 ? 0 : 0.4)); g2.translate(0, 15, 0); crown.push([g2, new T.Matrix4()]); }
      const gc2 = mergeList(crown), n = palmPos.length, trunkG = new T.CylinderGeometry(0.55, 0.8, 15, 8).translate(0, 7.5, 0);
      const pt = new T.InstancedMesh(trunkG, M.bark, n), pf = new T.InstancedMesh(gc2, frondMat, n); pt.castShadow = pf.castShadow = true;
      palmPos.forEach((p, i) => { const s = p[2] * 1.1; m4.compose(new T.Vector3(p[0], 0, p[1]), q4.setFromAxisAngle(yAx, rnd() * 6.28), new T.Vector3(s, s, s)); pt.setMatrixAt(i, m4); pf.setMatrixAt(i, m4); });
      S.add(pt, pf);
    }
    { // shrubs (lavender and green) at the tree pits, lantern street lamps along the curbs
      const sh = [], col = new T.Color(); treePos.forEach((p) => { if (rnd() < 0.55) for (let k = 0; k < 3; k++) sh.push([p[0] + (rnd() - 0.5) * 7, p[1] + (rnd() - 0.5) * 7, 0.6 + rnd() * 0.7]); });
      const ims = new T.InstancedMesh(new T.IcosahedronGeometry(1.1, 1), std({ color: 0xffffff, roughness: 0.95 }), sh.length); ims.castShadow = true; ims.receiveShadow = true;
      sh.forEach((p, i) => { ims.setMatrixAt(i, m4.compose(new T.Vector3(p[0], p[2] * 0.6, p[1]), q4.identity(), new T.Vector3(p[2] * 1.4, p[2], p[2] * 1.4))); ims.setColorAt(i, rnd() < 0.45 ? col.setHSL(0.74, 0.32, 0.45) : col.setHSL(0.24, 0.35, 0.22 + rnd() * 0.08)); }); S.add(ims);
      const KL = new Kit(); KL.add('lamp', new T.CylinderGeometry(0.22, 0.32, 10, 8), 0, 5, 0); KL.add('lamp', new T.BoxGeometry(2.6, 0.22, 0.22), 1.2, 9.8, 0); KL.add('lamp', new T.BoxGeometry(1.1, 0.25, 1.1), 2.4, 9.55, 0);
      KL.add('lantern', new T.CylinderGeometry(0.5, 0.35, 1.6, 6), 2.4, 8.6, 0); KL.add('lamp', new T.ConeGeometry(0.75, 0.6, 6), 2.4, 9.75, 0);
      const lp = []; curbPts.forEach((p, i) => { if (i % 9 !== 4) return; const off = -2.4, x = p[0] + Math.sin(p[2]) * off, y = p[1] - Math.cos(p[2]) * off; if (free(x, y)) lp.push([x, y, -p[2] + Math.PI / 2]); });
      const gl = KL.build(false); for (const k in gl) { const im = new T.InstancedMesh(gl[k], M[k], lp.length); im.castShadow = k === 'lamp'; lp.forEach((p, i) => im.setMatrixAt(i, m4.compose(new T.Vector3(p[0], 0, p[1]), q4.setFromAxisAngle(yAx, p[2]), one))); S.add(im); }
    }
    { // cars: parked in front of the community buildings and here and there along villa streets
      const K = new Kit(); K.box('paint', -4.6, 0.7, -1.9, 4.6, 2.4, 1.9); K.box('paint', -2.4, 2.4, -1.75, 1.6, 3.7, 1.75); K.box('glass', -2.3, 2.5, -1.8, 1.5, 3.55, 1.8); K.box('glass', 1.55, 2.5, -1.6, 1.75, 3.5, 1.6);
      for (const [x, z] of [[-3, -1.7], [3, -1.7], [-3, 1.7], [3, 1.7]]) K.add('tyre', new T.CylinderGeometry(0.8, 0.8, 0.6, 12), x, 0.8, z, 0, Math.PI / 2);
      const gs = K.build(false), cars = [];
      BL.forEach((b) => { const [w, d] = SPEC[b.c] || [100, 70]; const n = Math.min(10, Math.floor(w / 14)); for (let i = 0; i < n; i++) { if (rnd() < 0.35) continue; const lx = -w / 2 + 8 + i * 6.5 * 2, lz = d / 2 + (b.c === 'SC' ? 62 : 26);
        const cx = Math.cos(ROT), sx = Math.sin(ROT); cars.push([b.x + lx * cx + lz * sx, b.y - lx * sx + lz * cx, ROT + Math.PI / 2 + (rnd() < 0.5 ? Math.PI : 0)]); } });
      curbPts.forEach((p, i) => { if (i % 37 || rnd() < 0.5) return; const x = p[0] + Math.sin(p[2]) * -5, y = p[1] - Math.cos(p[2]) * -5; if (free(x, y)) cars.push([x, y, -p[2]]); });
      const tint = [0xf5f6f7, 0xf5f6f7, 0xe9e9e6, 0x2b2f36, 0x9ea4aa, 0x1d3f74, 0xf5f6f7], col = new T.Color();
      for (const k in gs) { const im = new T.InstancedMesh(gs[k], M[k], cars.length); im.castShadow = true; cars.forEach((c, i) => { im.setMatrixAt(i, m4.compose(new T.Vector3(c[0], 0, c[1]), q4.setFromAxisAngle(yAx, c[2]), one)); if (k === 'paint') im.setColorAt(i, col.set(tint[i % tint.length])); }); S.add(im); }
    }
    // ---------- progress colours
    const pmats = {};
    function setProgress(on, pcol) {
      wallMeshes.forEach((im) => { im.userData.list.forEach((v, i) => im.setColorAt(i, on ? new T.Color(pcol(v.tot)).lerp(white, im.material === M.recess ? 0.25 : 0.1) : white)); im.instanceColor.needsUpdate = true; });
      BL.forEach((b) => { if (!b.wallMesh) return; if (on) { const k = pcol(b.tot); b.wallMesh.material = pmats[k] || (pmats[k] = std({ color: k, map: plasterTex, roughness: 0.85 })); } else b.wallMesh.material = b.wallBase || M.wall; });
    }
    const itemFromHit = (h) => (h.object.isInstancedMesh ? h.object.userData.list[h.instanceId] : h.object.userData.it);
    return { R, S, cam, pick, itemFromHit, setProgress, fitShadow, tick };
  }

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
    const SC = buildScene(T, cv, D, V, BL), R = SC.R, S = SC.S, cam = SC.cam, pick = SC.pick;
    let quality = '2';
    // highlight box
    const hl = new T.Group(); S.add(hl);
    const hlMat = new T.LineBasicMaterial({ color: 0x7fe8ff, transparent: true }), hlFill = new T.MeshBasicMaterial({ color: 0x37c8ff, transparent: true, opacity: 0.05, depthWrite: false });
    let sel = null;
    function select(it, fly) {
      sel = it; hl.clear();
      if (!it) { pop.hidden = true; return; }
      const [w, h, d] = it.hl, geo = new T.BoxGeometry(w, h, d), s = new T.Group();
      s.add(new T.LineSegments(new T.EdgesGeometry(geo), hlMat), new T.Mesh(geo, hlFill)); s.position.set(it.x, h / 2, it.y); s.rotation.y = it.rot; hl.add(s);
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
      const to = it === 'all' ? { tx: 1520, ty: 0, tz: 1220, az: 1.05, pol: 0.95, r } : { tx: it.x, ty: it.kind === 'B' ? 10 : 8, tz: it.y, az: (() => { const f = Math.atan2(Math.cos(it.rot || 0), Math.sin(it.rot || 0)) + 0.55; return goal.az + Math.atan2(Math.sin(f - goal.az), Math.cos(f - goal.az)); })(), pol: it.kind === 'B' ? 1.08 : 1.12, r };
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
      const h = ray.intersectObjects(pick, false)[0], it = h ? SC.itemFromHit(h) : null; select(it, !!it); menuOn(it ? (it.kind === 'V' ? 'vil' : it.c) : ''); }
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
      SC.setProgress(prog, pcol); q('.v3-leg').style.display = prog ? 'block' : 'none'; }));
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
      if (C.ty < 0) C.ty = 0;
      cam.position.set(C.tx + C.r * Math.sin(C.pol) * Math.cos(C.az), C.ty + C.r * Math.cos(C.pol), C.tz + C.r * Math.sin(C.pol) * Math.sin(C.az)); cam.lookAt(C.tx, C.ty, C.tz);
      const p = 0.6 + 0.4 * Math.sin(now / 160); hlMat.opacity = p; hlFill.opacity = 0.03 + 0.04 * p;
      SC.fitShadow(C.tx, C.tz, C.r); SC.tick(now / 1000); R.render(S, cam);
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
