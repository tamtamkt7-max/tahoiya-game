import test from 'node:test';
import assert from 'node:assert/strict';
import { greet } from '../src/greeting.js';

test('greets a provided name', () => {
  assert.equal(greet('Kazuya'), 'Hello, Kazuya!');
});

test('trims surrounding whitespace', () => {
  assert.equal(greet('  Kazuya  '), 'Hello, Kazuya!');
});

test('uses guest for empty names', () => {
  assert.equal(greet(''), 'Hello, guest!');
  assert.equal(greet('   '), 'Hello, guest!');
});
