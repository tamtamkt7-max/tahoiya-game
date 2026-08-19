import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';

const projectDir = process.argv[2];
const statePath = process.argv[3] ?? 'pseudo_codex_framework/PROJECT_STATE.json';
if (!projectDir) throw new Error('usage: node run-node-ci.mjs <projectDir> [statePath]');

const pkgPath = path.join(projectDir, 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const required = state.validation.required_checks.filter((name) => name !== 'state');

for (const check of required) {
  if (!pkg.scripts?.[check]) {
    console.error(`MISSING_REQUIRED_SCRIPT ${check}`);
    process.exit(2);
  }
  console.log(`RUN ${check}`);
  const result = spawnSync('npm', ['run', check], {
    cwd: projectDir,
    stdio: 'inherit',
    shell: process.platform === 'win32'
  });
  if (result.status !== 0) {
    console.error(`CHECK_FAILED ${check} exit=${result.status ?? 1}`);
    process.exit(result.status ?? 1);
  }
}

console.log(`NODE_CI_OK checks=${required.join(',')}`);
