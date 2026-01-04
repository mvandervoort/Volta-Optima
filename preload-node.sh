#!/bin/bash
# Preload script voor Node.js om browser globals te injecteren vóór de build

# Print debugging info
echo "Starting Node.js with browser polyfills preloaded"
echo "Node version: $(node --version)"
echo "Working directory: $(pwd)"

# Gebruik NODE_OPTIONS om de preload script te injecteren in alle Node.js processen
export NODE_OPTIONS="--require=$(pwd)/node-globals.js ${NODE_OPTIONS}"

# Print bevestiging
echo "NODE_OPTIONS set to: $NODE_OPTIONS"

# Voer het oorspronkelijke commando uit met de nieuwe opties 
exec "$@"