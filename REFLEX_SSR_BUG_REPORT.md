# Reflex SSR "document is not defined" Bug Report

## Problem Summary
When deploying a Reflex app to Railway (or any Docker containerized environment), the frontend build consistently fails with:

```
ReferenceError: document is not defined
    at forEach (file:///app/.web/node_modules/src/core/emitter.ts:9:3)
```

## Configuration Used to Disable SSR

### reflex.json
```json
{
  "name": "Volta-Optima",
  "frontend": {
    "ssr": false,
    "build": {
      "envVars": {
        "VITE_DISABLE_SSR": "1",
        "VITE_RSC_BUILD": "false"
      }
    },
    "options": {
      "disableSsr": true
    }
  }
}
```

### Environment Variables
```
REFLEX_ENV=prod
REFLEX_DISABLE_SSR=1
VITE_DISABLE_SSR=1
VITE_RSC_BUILD=false
```

##  Issue
Despite all official methods to disable SSR being used, the frontend build process still:
1. Attempts pre-rendering/SSR
2. Calls browser APIs (specifically `document`) in a Node.js context
3. Fails in `emitter.ts` when calling forEach on a collection that accesses `document`

## Expected Behavior
When SSR is disabled via reflex.json and environment variables, the frontend build should not attempt any server-side rendering or call browser APIs during the build.

## Current Workarounds Attempted
- NODE_OPTIONS with polyfills → Causes other modules to fail (babel-dead-code-elimination)
- Patching emitter.ts → Too invasive, not maintainable
- Skipping frontend build during Docker build → SSR error occurs at runtime instead

## Environment
- Reflex version: (from requirements.txt)
- Node.js version: 20.x
- Deployment: Railway (Docker container)
- OS: Debian (python:3.11-slim base image)

## Request
Is there an official way to completely disable SSR and skip pre-rendering during production build? Or is this a bug in how Reflex processes the SSR configuration?