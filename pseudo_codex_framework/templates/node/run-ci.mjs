import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';

const statePath = process.env.PSEUDO_CODEX_STATE ?? '.pseudo-codex/STATE.json';
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

const requiredTopLevel = ['version','repository','working_branch','phase','task','runtime','safety','validation','repair_budget','next_action','updated_at'];
for (const key of requiredTopLevel) {
  if (!(key in state)) throw new Error(`STATE_INVALID missing:${key}`);
}
if (state.version !== 1) throw new Error('STATE_INVALID unsupported_version');
if (state.runtime.kind !== 'node') throw new Error(`STATE_INVALID runtime:${state.runtime.kind}`);
if (state.runtime.package_manager !== 'npm') throw new Error(`UNSUPPORTED_PACKAGE_MANAGER ${state.runtime.package_manager}`);
if (state.validation.last_result === 'fail' && state.repair_budget.attempts_used >= state.repair_budget.max_attempts) {
  throw new Error('SAFETY_STOP repair_budget_exhausted');
}

const projectRoot = path.resolve(state.runtime.project_root || '.');
const pkgPath = path.join(projectRoot, 'package.json');
if (!fs.existsSync(pkgPath)) throw new Error(`PROJECT_INVALID package.json_missing:${projectRoot}`);
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

function run(command, args, cwd = projectRoot) {
  console.log(`RUN ${command} ${args.join(' ')}`);
  const result = spawnSync(command, args, {
    cwd,
    stdio: 'inherit',
    shell: process.platform === 'win32'
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

if (fs.existsSync(path.join(projectRoot, 'package-lock.json'))) {
  run('npm', ['ci', '--no-audit', '--no-fund']);
} else {
  run('npm', ['install', '--no-audit', '--no-fund']);
}

for (const check of state.validation.required_checks) {
  if (check === 'state') continue;
  if (!pkg.scripts?.[check]) {
    console.error(`MISSING_REQUIRED_SCRIPT ${check}`);
    process.exit(2);
  }
  console.log(`CHECK ${check}`);
  run('npm', ['run', check]);
}

console.log(`PSEUDO_CODEX_CI_OK checks=${state.validation.required_checks.join(',')}`);
