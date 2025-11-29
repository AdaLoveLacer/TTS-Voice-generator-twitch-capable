// Service Worker para Speakerbot PWA
const CACHE_NAME = 'speakerbot-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/service-worker.js'
];

// Instalar - cachear assets básicos
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('💾 Cacheando assets básicos');
      return cache.addAll(ASSETS_TO_CACHE);
    }).catch(err => console.warn('⚠️ Erro ao cachear:', err))
  );
  self.skipWaiting();
});

// Ativar - limpar caches antigos
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker ativado');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log(`🗑️ Deletando cache antigo: ${cacheName}`);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch - servir do cache quando offline, atualizar quando online
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Não cachear requisições para /v1/ (API)
  if (url.pathname.startsWith('/v1/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache das requisições de síntese com sucesso
          if (request.method === 'POST' && response.ok) {
            const cache = caches.open(CACHE_NAME);
            cache.then((c) => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          // Offline - tentar servir do cache
          return caches.match(request).catch(() => {
            return new Response('Offline - conecte à internet', { status: 503 });
          });
        })
    );
    return;
  }

  // Para assets estáticos - usar cache-first strategy
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }

      return fetch(request)
        .then((response) => {
          // Não cachear respostas inválidas
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clonar e cachear
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });

          return response;
        })
        .catch(() => {
          // Offline e sem cache
          if (request.destination === 'document') {
            return caches.match('/index.html');
          }
          return new Response('Recurso não disponível offline', { status: 503 });
        });
    })
  );
});

// Sincronização em background (quando voltar online)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-audio') {
    console.log('🔄 Sincronizando áudios pendentes...');
    event.waitUntil(Promise.resolve());
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    self.registration.showNotification('Speakerbot', {
      body: data.message || 'Síntese concluída',
      icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%23000" width="192" height="192"/><text x="50%" y="50%" font-size="100" font-weight="bold" fill="%23fff" text-anchor="middle" dominant-baseline="middle">🎙️</text></svg>',
      badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%23000" width="192" height="192"/><text x="50%" y="50%" font-size="100" font-weight="bold" fill="%23fff" text-anchor="middle" dominant-baseline="middle">🎙️</text></svg>'
    });
  }
});

console.log('🎙️ Service Worker carregado para Speakerbot');
