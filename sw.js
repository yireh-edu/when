// 캐시 우선: 캐시에 있으면 바로 보여 주고, 뒤에서 최신 파일을 받아 캐시를 갱신한다
// (새 버전은 다음 실행 때 반영). 캐시에 없거나 처음이면 네트워크에서 받는다.
// 캐시 이름은 'when-' 으로 시작하는 것만 정리한다 (같은 출처의 다른 앱 캐시를 건드리지 않기 위해).
const CACHE = 'when-v2';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('when-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  const update = fetch(e.request).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  });
  e.waitUntil(update.then(() => {}, () => {}));
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true })
      .then(hit => hit || (e.request.mode === 'navigate' ? caches.match('./') : undefined))
      .then(hit => hit || update)
  );
});
