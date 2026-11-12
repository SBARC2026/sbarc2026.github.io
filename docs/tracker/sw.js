// SBARC Site Tracker: opens offline from cache; data always comes live from GitHub.
const CACHE = 'sbarc-tracker-2';
const CORE = ['./', 'index.html', 'guide.html', 'manifest.webmanifest'];
self.addEventListener('install', (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener('activate', (e) => e.waitUntil(caches.keys().then((k) => Promise.all(k.filter((x) => x.startsWith('sbarc-tracker-') && x !== CACHE).map((x) => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== self.location.origin) return;
  e.respondWith(fetch(e.request, { cache: 'no-store' }).then((r) => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then((x) => x.put(e.request, c)); } return r; })
    .catch(() => caches.match(e.request).then((r) => r || caches.match('index.html'))));
});
