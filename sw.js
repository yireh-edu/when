// 네트워크 우선, 실패하면 캐시 (오프라인에서도 열리고, 온라인이면 최신 파일 사용)
// 캐시 이름은 'when-' 으로 시작하는 것만 정리한다 (같은 출처의 다른 앱 캐시를 건드리지 않기 위해).
const CACHE = 'when-v1';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('when-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// 같은 출처의 다른 SW가 캐시를 지웠을 수 있으니, 온라인일 때 빠진 파일을 다시 채운다.
function refill() {
  return caches.open(CACHE).then(c => Promise.all(FILES.map(f =>
    c.match(f).then(hit => hit || c.add(f).catch(() => {}))
  )));
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
          if (e.request.mode === 'navigate') e.waitUntil(refill());
        }
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true })
        .then(hit => hit || (e.request.mode === 'navigate' ? caches.match('./') : undefined)))
  );
});
