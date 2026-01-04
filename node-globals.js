/**
 * Minimal Node.js globals for build-time compatibility
 * This MUST be loaded first in the Node.js process
 */

// Create mock objects for browser APIs used during the build
global.document = {
  createElement: () => ({ style: {}, classList: { add: () => {}, remove: () => {} } }),
  querySelector: () => null,
  querySelectorAll: () => [],
  documentElement: { style: {} }
};

global.window = {
  document: global.document,
  localStorage: { getItem: () => null, setItem: () => null },
  sessionStorage: { getItem: () => null, setItem: () => null },
  location: { pathname: '/' }
};

global.navigator = { userAgent: 'node' };

// Disable server-side rendering module in @react-router
process.env.REFLEX_DISABLE_SSR = '1';
process.env.VITE_DISABLE_SSR = '1';
process.env.VITE_RSC_BUILD = 'false';

// Log message so we know this is running
console.log('[node-globals] Installed Node.js browser API polyfills');