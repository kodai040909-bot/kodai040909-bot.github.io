// 入口の Service Worker。入口のページとアイコンだけを預かる
// /nemuri-garden/ と /kintore/ は、それぞれのアプリの Service Worker（より狭い範囲）が受け持つので、ここでは触らない
const CACHE = 'hub-v1-2026-11-11';
const FILES = ['/', '/index.html', '/manifest.webmanifest', '/icons/apple-touch-icon-180.png', '/icons/icon-192.png', '/icons/icon-512.png', '/icons/icon-maskable-512.png', '/nemuri-garden/icons/icon-192.png', '/kintore/icons/icon-192.png'];

self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('hub-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || !FILES.includes(url.pathname)) return;
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    if (self.navigator && self.navigator.onLine === false) { const hit = await c.match(e.request, { ignoreSearch: true }); if (hit) return hit; }
    try { const res = await fetch(e.request, { cache: 'no-cache' }); if (res.ok) c.put(e.request, res.clone()); return res; }
    catch (err) { const hit = await c.match(e.request, { ignoreSearch: true }); if (hit) return hit; throw err; }
  })());
});
