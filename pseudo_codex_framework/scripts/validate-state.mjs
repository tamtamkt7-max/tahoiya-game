import fs from 'node:fs';
import process from 'node:process';

const path = process.argv[2] ?? 'pseudo_codex_framework/PROJECT_STATE.json';
const state = JSON.parse(fs.readFileSync(path, 'utf8'));
const required = ['version','repository','working_branch','phase','task','safety','validation','repair_budget','next_action','updated_at'];
const allowed = new Set([...required, 'runtime', 'last_known_good_sha', 'evidence', 'blockers']);

for (const key of required) {
  if (!(key in state)) throw new Error(`missing state key: ${key}`);
}
for (const key of Object.keys(state)) {
  if (!allowed.has(key)) throw new Error(`unknown state key: ${key}`);
}
if (state.version !== 1) throw new Error('unsupported state version');
const phases = new Set(['planning','implementing','validating','repairing','review','blocked','complete']);
if (!phases.has(state.phase)) throw new Error(`invalid phase: ${state.phase}`);
if (!state.task || typeof state.task.id !== 'string' || typeof state.task.goal !== 'string') throw new Error('invalid task');
if (state.runtime !== undefined) {
  if (!state.runtime || typeof state.runtime !== 'object' || Array.isArray(state.runtime)) throw new Error('invalid runtime');
  if (!new Set(['node','python','other']).has(state.runtime.kind)) throw new Error('invalid runtime kind');
  if (typeof state.runtime.project_root !== 'string' || !state.runtime.project_root) throw new Error('invalid runtime project_root');
}
if (!Array.isArray(state.safety.allowed_paths) || state.safety.allowed_paths.length === 0) throw new Error('allowed_paths must be non-empty');
if (!Array.isArray(state.safety.forbidden_actions)) throw new Error('forbidden_actions must be an array');
if (!Array.isArray(state.validation.required_checks) || state.validation.required_checks.length === 0) throw new Error('required_checks must be non-empty');
if (!new Set(['not_run','pass','fail']).has(state.validation.last_result)) throw new Error('invalid validation result');
const { max_attempts: max, attempts_used: used } = state.repair_budget;
if (!Number.isInteger(max) || !Number.isInteger(used) || max < 0 || used < 0 || used > max || max > 10) {
  throw new Error('invalid repair budget');
}
if (state.evidence !== undefined && (state.evidence === null || Array.isArray(state.evidence) || typeof state.evidence !== 'object')) {
  throw new Error('evidence must be an object');
}
console.log(`STATE_OK phase=${state.phase} attempts=${used}/${max}`);
