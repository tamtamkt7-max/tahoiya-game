import fs from 'node:fs';

fs.rmSync('dist', { recursive: true, force: true });
fs.mkdirSync('dist', { recursive: true });
fs.copyFileSync('src/greeting.js', 'dist/greeting.js');
console.log('BUILD_OK');
