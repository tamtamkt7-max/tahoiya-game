# Real Case v1 Specification

## Goal

Extend the existing TypeScript calculator fixture with multiplication while preserving addition.

## Required behavior

- `add(2, 3)` returns `5`.
- Add an exported `multiply(a, b)` function.
- `multiply(4, 5)` returns `20`.
- `multiply(-2, 3)` returns `-6`.
- Keep strict TypeScript validation.
- All required checks must pass: test, typecheck, lint, build.

## Scope

Only the TypeScript fixture, `.pseudo-codex/`, and the pseudo-Codex CI workflow may be changed.

## Completion

The task is complete only after CI passes and the final diff is checked against every required behavior above.
