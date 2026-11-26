// Service worker: deixa o app abrir sem internet.
// Arquivos do app: rede primeiro (pega a versão nova), cache como reserva.
const CACHE = 'ofensiva-v1';
const SHELL = ['./', 'index.html', 'style.css', 'app.js', 'firebase-config.js', 'questions.json', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // Firebase e login: sempre pela rede, sem cache.
  if (url.origin !== location.origin && !url.hostname.endsWith('gstatic.com') && !url.hostname.startsWith('fonts.')) return;
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('index.html')))
  );
});
