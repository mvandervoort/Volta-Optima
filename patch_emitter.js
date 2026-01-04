/**
 * Patch script voor het fixen van document is not defined fouten in emitter.ts
 * 
 * Dit script vindt het emitter.ts bestand in de node_modules en patcht het
 * om veilig te draaien in een Node.js omgeving zonder browser APIs.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Log helper
function log(message) {
  console.log(`[patch_emitter] ${message}`);
}

// Find the emitter.ts file
function findEmitterFile() {
  log('Zoeken naar emitter.ts in node_modules...');
  
  try {
    // First, use find to locate the file (faster than recursive search)
    const result = execSync('find /app/.web/node_modules -name "emitter.ts"')
      .toString()
      .trim()
      .split('\n')
      .filter(file => file.includes('/core/emitter.ts'));
    
    if (result.length > 0) {
      log(`Gevonden: ${result[0]}`);
      return result[0];
    }
    
    log('Geen emitter.ts gevonden met find, probeer handmatige zoeklocaties...');
    
    // Fallback locations to check directly
    const possibleLocations = [
      '/app/.web/node_modules/src/core/emitter.ts',
      '/app/.web/node_modules/@react-router/core/emitter.ts',
      '/app/.web/node_modules/@reflex/core/emitter.ts'
    ];
    
    for (const loc of possibleLocations) {
      if (fs.existsSync(loc)) {
        log(`Gevonden op fallback locatie: ${loc}`);
        return loc;
      }
    }
    
    log('Emitter.ts niet gevonden in bekende locaties');
    return null;
  } catch (error) {
    log(`Error bij zoeken naar bestand: ${error.message}`);
    return null;
  }
}

// Patch the emitter.ts file
function patchEmitterFile(filePath) {
  if (!filePath) {
    log('Geen emitter.ts bestand gevonden om te patchen');
    return false;
  }
  
  try {
    log(`Lezen van origineel bestand: ${filePath}`);
    const originalContent = fs.readFileSync(filePath, 'utf8');
    
    // Backup the original file
    const backupPath = `${filePath}.backup`;
    fs.writeFileSync(backupPath, originalContent);
    log(`Backup gemaakt naar: ${backupPath}`);
    
    // Find problematic forEach line
    if (originalContent.includes('document.addEventListener')) {
      log('Document addEventListener gevonden, patching...');
      
      // Replace document.addEventListener with safe SSR-compatible code
      const patchedContent = originalContent.replace(
        /document\.addEventListener\([^)]+\);?/g,
        'typeof document !== "undefined" && document.addEventListener && document.addEventListener($1);'
      ).replace(
        /(\w+)\.forEach\(/g,
        'Array.isArray($1) && $1.forEach('
      );
      
      // Write the patched file
      fs.writeFileSync(filePath, patchedContent);
      log('Bestand succesvol gepatcht');
      
      // Print a diff for verification
      log('Verschillen:');
      try {
        const diff = execSync(`diff -u "${backupPath}" "${filePath}" | grep -v '^---' | grep -v '^+++'`).toString();
        console.log(diff);
      } catch (error) {
        // Diff will return non-zero if files differ, which is expected
        console.log(error.stdout?.toString() || 'Geen diff beschikbaar');
      }
      
      return true;
    } else {
      log('Geen document.addEventListener patronen gevonden om te patchen');
      
      // Try more generic patching for forEach
      const patchedContent = originalContent.replace(
        /(\w+)\.forEach\(/g,
        '$1 && Array.isArray($1) && $1.forEach('
      );
      
      // Only write if changes were made
      if (patchedContent !== originalContent) {
        fs.writeFileSync(filePath, patchedContent);
        log('Generieke forEach patch toegepast');
        return true;
      }
      
      log('Geen veranderingen gemaakt (geen forEach patronen gevonden)');
      return false;
    }
  } catch (error) {
    log(`Error bij patchen van bestand: ${error.message}`);
    return false;
  }
}

// Create a no-ssr flag file to completely disable SSR
function createNoSsrFlag() {
  const flagPath = '/app/.web/node_modules/.no-ssr';
  try {
    fs.writeFileSync(flagPath, 'SSR disabled by patch_emitter.js');
    log(`No-SSR vlagbestand aangemaakt op ${flagPath}`);
    return true;
  } catch (error) {
    log(`Kon .no-ssr vlag niet aanmaken: ${error.message}`);
    return false;
  }
}

// Main execution
(function main() {
  log('Starten van emitter.ts patch proces...');
  
  // First, find the emitter.ts file
  const emitterFile = findEmitterFile();
  
  // Try to patch the file if found
  const patchResult = patchEmitterFile(emitterFile);
  
  // Always create the no-ssr flag file
  const flagResult = createNoSsrFlag();
  
  if (patchResult) {
    log('Patch proces succesvol afgerond');
  } else if (flagResult) {
    log('Kon emitter.ts niet patchen, maar wel .no-ssr vlag aangemaakt');
  } else {
    log('WAARSCHUWING: Kon geen patches toepassen');
  }
})();