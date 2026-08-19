import fs from 'node:fs';
import process from 'node:process';

const path = process.argv[2] ?? 'pseudo_codex_framework/PROJECT_STATE.json';
const state = JSON.parse(fs.readFileSync(path, 'utf8'));
const required = ['version','repository','working_branch','phase','task','safety','validation','repair_budget','next_action','updated_at'];
for (const key of required) {
  if (!(key in state)) throw new Error(`missing state key: ${key}`);
}
if (state.version !== 1) throw new Error('unsupported state version');
const phases = new Set(['planning','implementing','validating','repairing','review','blocked','complete']);
if (!phases.has(state.phase)) throw new Error(`invalid phase: ${state.phase}`);
if (!Array.isArray(state.safety.allowed_paths) || state.safety.allowed_paths.length === 0) throw new Error('allowed_paths must be non-empty');
if (!Array.isArray(state.validation.required_checks) || state.validation.required_checks.length === 0) throw new Error('required_checks must be non-empty');
const { max_attempts: max, attempts_used: used } = state.repair_budget;
if (!Number.isInteger(max) || !Number.isInteger(used) || max < 0 || used < 0 || used > max || max > 10) {
  throw new Error('invalid repair budget');
}
console.log(`STATE_OK phase=${state.phase} attempts=${used}/${max}`);
