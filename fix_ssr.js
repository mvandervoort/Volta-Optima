/**
 * SSR fix for Reflex on Railway
 * 
 * Dit script voegt global polyfills toe voor browser-specifieke objecten
 * die niet bestaan in de Node.js omgeving tijdens server-side rendering.
 */

// Mock 'document' object voor server-side rendering
if (typeof document === 'undefined') {
  global.document = {
    addEventListener: () => {},
    removeEventListener: () => {},
    createElement: () => ({
      style: {},
      setAttribute: () => {},
      appendChild: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      classList: {
        add: () => {},
        remove: () => {},
      }
    }),
    querySelector: () => null,
    querySelectorAll: () => [],
    getElementById: () => null,
    getElementsByClassName: () => [],
    documentElement: {
      style: {},
      classList: {
        add: () => {},
        remove: () => {},
      }
    },
    body: {
      appendChild: () => {},
      classList: {
        add: () => {},
        remove: () => {},
      },
      style: {},
    },
    head: {
      appendChild: () => {},
    },
  };
}

// Mock 'window' object
if (typeof window === 'undefined') {
  global.window = {
    addEventListener: () => {},
    removeEventListener: () => {},
    location: { pathname: '/' },
    document: global.document,
    localStorage: {
      getItem: () => null,
      setItem: () => null,
      removeItem: () => null,
    },
    sessionStorage: {
      getItem: () => null,
      setItem: () => null,
      removeItem: () => null,
    },
    getComputedStyle: () => ({}),
    screen: { width: 1024, height: 768 },
    navigator: { userAgent: 'node', language: 'en-US' },
  };
}

// Mock 'navigator' object
if (typeof navigator === 'undefined') {
  global.navigator = {
    userAgent: 'node',
    language: 'en-US',
  };
}

console.log('SSR browser polyfills geïnstalleerd voor Reflex Node.js omgeving');