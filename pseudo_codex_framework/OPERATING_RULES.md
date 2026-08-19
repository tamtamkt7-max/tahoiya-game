# Pseudo Codex Operating Rules v1

## Purpose

Provide a reusable development loop where ChatGPT can inspect and edit an isolated GitHub branch, GitHub Actions validates the change, ChatGPT reads the result and logs, and repairs continue until PASS or a safety/decision boundary is reached.

## Authoritative state

`pseudo_codex_framework/PROJECT_STATE.json` is the single authoritative handoff state. In installed projects the equivalent file is `.pseudo-codex/STATE.json`. Do not duplicate live state into multiple documents.

## Core loop

1. Read the authoritative state and the project specification.
2. Confirm repository, working branch, allowed paths, forbidden actions, required checks, and repair budget.
3. Inspect only the code needed for the current task.
4. Edit only the isolated working branch.
5. Let CI run automatically on push.
6. Read compact commit status.
7. If FAIL, follow its workflow/job logs, identify the smallest root-cause fix, increment repair attempts, edit, and let CI rerun.
8. Stop if the repair budget is exhausted or a forbidden/high-risk action is required.
9. When every required check passes, review the diff against the specification before declaring completion.

## Batch changes

Treat one logical feature or repair as one commit whenever possible. For multi-file changes, prefer Git blob/tree/commit creation followed by a non-forced branch ref update. This keeps related edits atomic and triggers CI once instead of once per file.

Before moving the branch ref, re-check the current branch head. Never force-update over an unexpected concurrent change. Sequential file writes are a fallback, not the default.

## Safety boundaries

Never autonomously perform deployment, release, default-branch merge, secret retrieval, paid AI API use, destructive external actions, or irreversible data changes.

Application code may call its already-configured external services during an explicitly approved integration test only when the project specification permits it. CI should prefer mocked or local tests by default.

## Validation contract

For Node projects, run scripts only when they exist in `package.json`, in this preferred order:

1. `test`
2. `typecheck`
3. `lint`
4. `build`

A missing required script is a failure when it is listed in the authoritative state's `validation.required_checks`.

CI must publish one compact commit status with a target URL pointing to the exact workflow run. Full logs stay in GitHub Actions and are fetched only when needed.

## Repair limits

Default maximum automatic repair attempts: 3 per task. A repair attempt means a code/configuration change made after a failed validation. Do not loop indefinitely.

## State-only updates

State updates create commits too. `validation.last_checked_sha` therefore points to the implementation-changing commit that was validated, not recursively to every later state-only commit. A later state-only commit remains valid when its CI passes and comparison confirms that no runtime code, tests, dependencies, build configuration, or CI behavior changed. This prevents an endless state-update loop.

## Completion

PASS from CI is necessary but not sufficient. Completion requires:

- every required validation check passing;
- diff reviewed against the specification;
- no forbidden path/action used;
- no unresolved blocker;
- state updated so a future session can resume without chat history.
