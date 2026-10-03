// Venstogram Ecosystem WebApp & Landing scripts

// Register Service Worker for PWA & Offline Support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then(reg => {
        console.log('✅ Venstogram PWA ServiceWorker registered with scope:', reg.scope);
      })
      .catch(err => {
        console.warn('⚠️ ServiceWorker registration failed:', err);
      });
  });
}

// Telegram WebApp initialization (if opened inside Telegram)
if (window.Telegram && window.Telegram.WebApp) {
  try {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
    console.log('🚀 Venstogram opened inside Telegram Mini App');
  } catch (e) {
    console.log('Not in Telegram context');
  }
}
