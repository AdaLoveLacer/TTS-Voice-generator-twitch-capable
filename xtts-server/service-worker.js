// Service Worker para Speakerbot PWA
const CACHE_NAME = 'speakerbot-v1';
const ASSETS_TO_CACHE = [
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

  // SEMPRE buscar versão mais recente do HTML (não cachear)
  if (request.destination === 'document' || url.pathname === '/') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          return response;
        })
        .catch(() => {
          // Offline - tentar servir do cache
          return caches.match(request).catch(() => {
            return new Response('Offline - página não disponível', { status: 503 });
          });
        })
    );
    return;
  }

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
          return new Response('Recurso não disponível offline', { status: 503 });
        });
    })
  );
});

// ============================================================================
// BACKGROUND FILE MONITORING (runs even when browser is closed)
// ============================================================================

let fileMonitoringState = {
  active: false,
  file_path: '',
  interval: 500,
  last_line_count: 0,
  language: 'pt',
  voice: '',
  use_random_voice: false,
  last_check: Date.now()
};

// Background monitoring loop - runs independently
async function runBackgroundFileMonitoring() {
  if (!fileMonitoringState.active || !fileMonitoringState.file_path) {
    return;
  }

  const now = Date.now();
  const timeSinceLastCheck = now - fileMonitoringState.last_check;
  
  // Only check if interval has passed
  if (timeSinceLastCheck < fileMonitoringState.interval) {
    return;
  }

  fileMonitoringState.last_check = now;

  try {
    // Call backend to check for new lines
    const response = await fetch('/v1/monitor/read-file', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_path: fileMonitoringState.file_path,
        last_line_count: fileMonitoringState.last_line_count
      })
    });

    if (!response.ok) {
      console.log('❌ Background monitor: HTTP error', response.status);
      return;
    }

    const data = await response.json();

    if (!data.success) {
      console.log('⚠️ Background monitor error:', data.error);
      return;
    }

    // Update line count
    fileMonitoringState.last_line_count = data.total_lines;

    // If there are new lines, notify all clients (tabs/windows)
    if (data.new_lines && data.new_lines.length > 0) {
      console.log(`✅ Background monitor: ${data.new_lines.length} new line(s) detected`);
      
      // Broadcast to all open clients
      const clients = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      });

      clients.forEach(client => {
        client.postMessage({
          type: 'FILE_MONITOR_UPDATE',
          data: {
            new_lines: data.new_lines,
            total_lines: data.total_lines
          }
        });
      });
    }
  } catch (error) {
    console.log('⚠️ Background monitor error:', error.message);
  }
}

// Run background monitoring on a timer
setInterval(runBackgroundFileMonitoring, 250);

// Message handler - receive commands from clients
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;

  if (type === 'START_FILE_MONITORING') {
    fileMonitoringState.active = true;
    fileMonitoringState.file_path = payload.file_path;
    fileMonitoringState.interval = payload.interval || 500;
    fileMonitoringState.language = payload.language || 'pt';
    fileMonitoringState.voice = payload.voice || '';
    fileMonitoringState.use_random_voice = payload.use_random_voice || false;
    fileMonitoringState.last_line_count = payload.last_line_count || 0;
    fileMonitoringState.last_check = Date.now();
    
    console.log('🎯 Background monitoring started:', fileMonitoringState);
    
    // Immediately run first check
    runBackgroundFileMonitoring();
  } 
  else if (type === 'STOP_FILE_MONITORING') {
    fileMonitoringState.active = false;
    console.log('⏹ Background monitoring stopped');
  }
  else if (type === 'UPDATE_FILE_MONITOR_STATE') {
    Object.assign(fileMonitoringState, payload);
    console.log('📝 Background monitor state updated:', fileMonitoringState);
  }
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
