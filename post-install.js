#!/usr/bin/env node
/**
 * Post-install script voor npm om automatisch emitter.ts te patchen
 * Dit script wordt automatisch uitgevoerd na npm install
 */

const { execSync } = require('child_process');

console.log('==== Volta-Optima Reflex SSR Fix Post-Install ====');
console.log('Voer patch_emitter.js uit na npm install...');

try {
  // Voer het patch script uit
  execSync('node /app/patch_emitter.js', { stdio: 'inherit' });
  console.log('Post-install patch voltooid!');
} catch (error) {
  console.error('Error bij uitvoeren patch script:', error.message);
  console.log('Proberen om de error te negeren en door te gaan...');
}

console.log('==== Post-Install Voltooid ====');