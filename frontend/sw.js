const CACHE_NAME = 'stockchart-v1.0.0';
const urlsToCache = [
  '/mobile.html',
  '/js/tradingview-chart-engine.js',
  '/js/mobile-chart-interface.js',
  '/css/mobile.css',
  '/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.log('Cache failed:', error);
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        
        return fetch(event.request).then((response) => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone response (can only be consumed once)
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
      .catch(() => {
        // Return offline page if available
        if (event.request.destination === 'document') {
          return caches.match('/mobile.html');
        }
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync for offline predictions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync-predictions') {
    event.waitUntil(syncPredictions());
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '새로운 시장 업데이트가 있습니다',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: '확인하기',
        icon: '/icons/check.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/icons/close.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('StockChart', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    // Open app
    event.waitUntil(
      clients.openWindow('/mobile.html')
    );
  }
});

// Sync predictions function
async function syncPredictions() {
  try {
    // Get pending predictions from IndexedDB
    const db = await openDB();
    const predictions = await getOfflinePredictions(db);
    
    // Sync each prediction
    for (const prediction of predictions) {
      await fetch('/api/predictions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(prediction)
      });
      
      // Remove from offline storage
      await removeOfflinePrediction(db, prediction.id);
    }
  } catch (error) {
    console.log('Sync failed:', error);
  }
}

// IndexedDB helpers
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('StockChartDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      const objectStore = db.createObjectStore('predictions', { keyPath: 'id' });
    };
  });
}

function getOfflinePredictions(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['predictions'], 'readonly');
    const objectStore = transaction.objectStore('predictions');
    const request = objectStore.getAll();
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removeOfflinePrediction(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['predictions'], 'readwrite');
    const objectStore = transaction.objectStore('predictions');
    const request = objectStore.delete(id);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}