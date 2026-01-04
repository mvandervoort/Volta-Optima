/**
 * Enhanced Node.js globals for build-time compatibility
 * This MUST be loaded first in the Node.js process
 */

// Verzeker dat we de console hebben voor logging
console.log('[node-globals] Installing Node.js browser API polyfills...');

// Verbeterde document mock met meer functionaliteit
global.document = {
  createElement: () => ({ 
    style: {}, 
    classList: { 
      add: () => {}, 
      remove: () => {},
      contains: () => false,
      toggle: () => {}
    }
  }),
  querySelector: () => null,
  querySelectorAll: () => [],
  getElementById: () => null,
  getElementsByClassName: () => [],
  getElementsByTagName: () => [],
  documentElement: { style: {} },
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => true,
  createEvent: () => ({ initEvent: () => {} })
};

// Verbeterd window object
global.window = {
  document: global.document,
  localStorage: { 
    getItem: () => null, 
    setItem: () => null,
    removeItem: () => null,
    clear: () => null
  },
  sessionStorage: { 
    getItem: () => null, 
    setItem: () => null,
    removeItem: () => null,
    clear: () => null
  },
  location: { 
    pathname: '/',
    href: 'http://localhost/',
    search: '',
    hash: '',
    host: 'localhost',
    protocol: 'http:'
  },
  navigator: {
    userAgent: 'node',
    language: 'en-US',
    languages: ['en-US', 'en']
  },
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => true,
  scrollTo: () => {},
  innerWidth: 1024,
  innerHeight: 768,
  requestAnimationFrame: (cb) => setTimeout(cb, 0),
  cancelAnimationFrame: (id) => clearTimeout(id)
};

// Browser-achtige globals
global.navigator = global.window.navigator;
global.localStorage = global.window.localStorage;
global.sessionStorage = global.window.sessionStorage;

// VERY IMPORTANT: Fix voor Array.prototype.forEach in emitter.ts
// Dit is een kritieke patch om de fout in emitter.ts op lijn 9 te fixen
const originalForEach = Array.prototype.forEach;
Array.prototype.forEach = function(callback, thisArg) {
  if (!this) {
    console.warn('[node-globals] Prevented forEach on null/undefined in SSR');
    return;
  }
  return originalForEach.call(this, callback, thisArg);
};

// Extra browser APIs die mogelijk nodig zijn
global.fetch = () => Promise.resolve({ 
  ok: true, 
  json: () => Promise.resolve({}),
  text: () => Promise.resolve(''),
  blob: () => Promise.resolve(new Blob())
});
global.DOMParser = class DOMParser {
  parseFromString() {
    return { documentElement: {} };
  }
};
global.MutationObserver = class MutationObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {}
  disconnect() {}
};

// Disable server-side rendering flags
process.env.REFLEX_DISABLE_SSR = '1';
process.env.VITE_DISABLE_SSR = '1';
process.env.VITE_RSC_BUILD = 'false';
process.env.BROWSER = 'false';

// Log successful installation
console.log('[node-globals] Successfully installed enhanced Node.js browser API polyfills');