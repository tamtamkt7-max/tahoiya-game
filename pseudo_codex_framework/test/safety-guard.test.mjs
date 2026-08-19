import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateSafety } from '../scripts/safety-guard.mjs';

function baseState() {
  return {
    phase: 'implementing',
    validation: { last_result: 'pass' },
    repair_budget: { max_attempts: 3, attempts_used: 0 },
    safety: {
      allowed_paths: ['src/', 'test/'],
      forbidden_actions: ['deploy', 'release', 'merge_to_default_branch', 'access_secrets']
    }
  };
}

test('allows an edit inside an allowed path', () => {
  assert.deepEqual(evaluateSafety(baseState(), { action: 'edit', paths: ['src/app.ts'] }), { allowed: true, reason: 'allowed' });
});

test('blocks a forbidden action', () => {
  assert.deepEqual(evaluateSafety(baseState(), { action: 'deploy', paths: [] }), { allowed: false, reason: 'forbidden_action:deploy' });
});

test('blocks a path outside the allowed scope', () => {
  assert.deepEqual(evaluateSafety(baseState(), { action: 'edit', paths: ['production/config.ts'] }), { allowed: false, reason: 'path_not_allowed:production/config.ts' });
});

test('blocks when repair budget is exhausted after failure', () => {
  const state = baseState();
  state.validation.last_result = 'fail';
  state.repair_budget.attempts_used = 3;
  assert.deepEqual(evaluateSafety(state, { action: 'edit', paths: ['src/app.ts'] }), { allowed: false, reason: 'repair_budget_exhausted' });
});

test('blocks a state already marked blocked or complete', () => {
  const blocked = baseState(); blocked.phase = 'blocked';
  const complete = baseState(); complete.phase = 'complete';
  assert.equal(evaluateSafety(blocked).allowed, false);
  assert.equal(evaluateSafety(complete).allowed, false);
});
