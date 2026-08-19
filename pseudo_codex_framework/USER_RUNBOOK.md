# Pseudo Codex User Runbook v1

## What the user does

### Existing app already current on GitHub

1. Finalize the application specification with ChatGPT.
2. Say `開発開始`.

ChatGPT creates an isolated `pseudo-codex/...` branch, installs the project-local state/CI files when needed, implements changes, reads GitHub Actions results, repairs failures within the repair budget, reviews the final diff against the specification, and reports completion.

### Existing app whose Windows local copy is newer than GitHub

Run the approved Windows bootstrap once. It creates a new isolated branch from the current local repository, scans common secret file paths and token/private-key patterns, commits the current local state, and pushes only that new branch. Then return to ChatGPT and say that bootstrap finished.

After that, normal development happens through GitHub without repeatedly copying logs or files from Windows.

### New app

The current ChatGPT GitHub connector cannot create a brand-new GitHub repository. Create an empty repository once and make it accessible to the connected GitHub app. After that, finalize the specification and say `開発開始`; ChatGPT can create the working branch and application files itself.

## Normal autonomous loop

`spec -> isolated branch -> batched code change -> CI -> result -> failing job log only when needed -> bounded repair -> CI -> diff/spec review -> complete`

One logical change should normally be one commit. New pushes cancel older in-progress CI for the same pseudo-Codex branch.

## What still requires user approval

- deployment or production release
- merge into the default branch when that changes the official code line
- new paid service or unexpected charge
- secret/API-key acquisition or permission expansion
- destructive data/repository deletion
- irreversible external changes
- a material product/specification decision that cannot be derived safely

## Recovery

Chat history is not required to reconstruct development state. The authoritative `.pseudo-codex/STATE.json` plus GitHub branch/CI evidence is used to resume after a chat interruption or PC restart.

For GitHub-hosted CI, the Windows PC does not need to stay on. Windows is only needed when the latest code exists only locally or a project has genuinely local-only tooling/hardware.

## Cost behavior

No paid AI API or Codex execution engine is required by this framework. CI runs only on pseudo-Codex branch pushes, uses a bounded repair count, batches multi-file edits, cancels superseded runs, and has a workflow timeout.
