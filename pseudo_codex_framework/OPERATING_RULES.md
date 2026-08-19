# Pseudo Codex Operating Rules v1

## Purpose

Provide a reusable development loop where ChatGPT can inspect and edit an isolated GitHub branch, GitHub Actions validates the change, ChatGPT reads the result and logs, and repairs continue until PASS or a safety/decision boundary is reached.

## Authoritative state

`pseudo_codex_framework/PROJECT_STATE.json` is the single authoritative handoff state. Do not duplicate live state into multiple documents.

## Core loop

1. Read `PROJECT_STATE.json` and the project specification.
2. Confirm repository, working branch, allowed paths, forbidden actions, required checks, and repair budget.
3. Inspect only the code needed for the current task.
4. Edit only the isolated working branch.
5. Let CI run automatically on push.
6. Read compact commit status.
7. If FAIL, follow its workflow/job logs, identify the smallest root-cause fix, increment repair attempts, edit, and let CI rerun.
8. Stop if the repair budget is exhausted or a forbidden/high-risk action is required.
9. When every required check passes, review the diff against the specification before declaring completion.

## Safety boundaries

Never autonomously perform deployment, release, default-branch merge, secret retrieval, paid AI API use, destructive external actions, or irreversible data changes.

Application code may call its already-configured external services during an explicitly approved integration test only when the project specification permits it. CI should prefer mocked or local tests by default.

## Validation contract

For Node projects, run scripts only when they exist in `package.json`, in this preferred order:

1. `test`
2. `typecheck`
3. `lint`
4. `build`

A missing required script is a failure when it is listed in `PROJECT_STATE.json.validation.required_checks`.

CI must publish one compact commit status with a target URL pointing to the exact workflow run. Full logs stay in GitHub Actions and are fetched only when needed.

## Repair limits

Default maximum automatic repair attempts: 3 per task. A repair attempt means a code/configuration change made after a failed validation. Do not loop indefinitely.

## Completion

PASS from CI is necessary but not sufficient. Completion requires:

- every required validation check passing;
- diff reviewed against the specification;
- no forbidden path/action used;
- no unresolved blocker;
- state updated so a future session can resume without chat history.
