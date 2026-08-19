import fs from 'node:fs';
import path from 'node:path';

const roots = ['src', 'test'];
const forbidden = [/console\.log\s*\(/, /\bTODO\b/];
let failed = false;

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.name.endsWith('.js')) {
      const text = fs.readFileSync(full, 'utf8');
      for (const pattern of forbidden) {
        if (pattern.test(text)) {
          console.error(`LINT_FAIL ${full}: ${pattern}`);
          failed = true;
        }
      }
    }
  }
}

for (const root of roots) walk(root);
if (failed) process.exit(1);
console.log('LINT_OK');
