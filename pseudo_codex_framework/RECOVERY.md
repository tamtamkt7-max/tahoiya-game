# Pseudo Codex Recovery Rules v1

## Recovery source

Always resume from `PROJECT_STATE.json`, then verify the branch head and CI status. Chat history is helpful context, not the source of truth.

## Resume sequence

1. Read `PROJECT_STATE.json`.
2. Confirm the repository and working branch still exist.
3. Read the current branch head SHA.
4. Compare it with `validation.last_checked_sha` and `last_known_good_sha`.
5. Read the compact CI status for the current head.
6. If CI is pending or absent, do not guess the result. Re-check later or trigger validation with a safe state-only change when appropriate.
7. If CI failed, follow the exact workflow run and job logs before editing.
8. If CI passed, continue with `next_action`.

## State-only commits

`validation.last_checked_sha` records the implementation commit whose application behavior was validated. Updating the authoritative state itself creates a newer commit, so it must not be rewritten merely to point at its own state-only commit.

When the current head is newer than `last_checked_sha`, compare the commits. If every intervening change is limited to the authoritative state or other explicitly non-runtime pseudo-Codex metadata, and CI at the current head passes, treat the implementation validation as current. If runtime code, tests, dependencies, build configuration, or workflow behavior changed, require fresh validation and update `last_checked_sha` to that implementation-changing commit.

This rule prevents an endless state-update -> new SHA -> state-update loop.

## Safe stop conditions

Set phase to `blocked` and stop autonomous edits when any of these is true:

- `attempts_used >= max_attempts` and validation still fails;
- required work would touch a forbidden path/action;
- a secret, paid service, deployment, release, merge, deletion, or irreversible external change is required;
- the specification is missing or contradictory enough to change the outcome materially;
- the branch head changed unexpectedly outside the current task and the change cannot be safely reconciled;
- required CI cannot run or its result cannot be verified.

## Interrupted session

No special recovery command is required. A new ChatGPT session or Scheduled Task reads the repository state and follows the resume sequence. This avoids copying long logs or reconstructing state from conversation history.

## PC restart

For GitHub-hosted CI, a Windows PC restart has no effect on in-flight or future CI. Local-PC recovery rules are only needed for projects that explicitly require local-only tooling or hardware.

## Failed CI

Use the compact commit status to locate the exact Actions run. Fetch only the failing job log, identify the first actionable root cause, record one repair attempt, apply the smallest fix, and rerun. Do not restart successful unrelated work.

## Stale or invalid state

If `PROJECT_STATE.json` fails validation, do not continue development. Repair state only when its correct values can be derived from GitHub history and current CI evidence; otherwise stop as blocked.
