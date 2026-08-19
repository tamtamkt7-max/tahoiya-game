import fs from 'node:fs';
import process from 'node:process';

export function evaluateSafety(state, intent = {}) {
  if (state.phase === 'blocked') return { allowed: false, reason: 'state_blocked' };
  if (state.phase === 'complete') return { allowed: false, reason: 'state_complete' };
  if (state.validation?.last_result === 'fail' && state.repair_budget?.attempts_used >= state.repair_budget?.max_attempts) {
    return { allowed: false, reason: 'repair_budget_exhausted' };
  }

  const action = intent.action ?? 'edit';
  if (state.safety?.forbidden_actions?.includes(action)) {
    return { allowed: false, reason: `forbidden_action:${action}` };
  }

  const paths = Array.isArray(intent.paths) ? intent.paths : [];
  for (const target of paths) {
    const normalized = String(target).replaceAll('\\', '/');
    const allowed = state.safety?.allowed_paths?.some((prefix) => normalized.startsWith(String(prefix).replaceAll('\\', '/')));
    if (!allowed) return { allowed: false, reason: `path_not_allowed:${normalized}` };
  }

  return { allowed: true, reason: 'allowed' };
}

if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('safety-guard.mjs')) {
  const statePath = process.argv[2];
  const intentPath = process.argv[3];
  if (!statePath) throw new Error('usage: node safety-guard.mjs <state.json> [intent.json]');
  const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  const intent = intentPath ? JSON.parse(fs.readFileSync(intentPath, 'utf8')) : {};
  const result = evaluateSafety(state, intent);
  console.log(JSON.stringify(result));
  if (!result.allowed) process.exit(3);
}
