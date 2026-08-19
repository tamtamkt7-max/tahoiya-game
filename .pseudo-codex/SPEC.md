# New App v1 Specification

## Goal

Create a new small Node application from scratch that provides a reusable greeting function.

## Required behavior

- Export `greet(name)` from `new_app_demo/src/greeting.js`.
- `greet('Kazuya')` returns `Hello, Kazuya!`.
- Leading and trailing whitespace is ignored.
- An empty or whitespace-only name returns `Hello, guest!`.
- Provide automated tests.
- Required checks are test, typecheck, lint, and build.

## Scope

Only `new_app_demo/`, `.pseudo-codex/`, and `.github/workflows/pseudo-codex-ci.yml` may be changed.

## Completion

CI must pass and the final diff must be reviewed against every required behavior.
