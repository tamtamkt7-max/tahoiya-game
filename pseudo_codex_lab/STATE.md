# Pseudo Codex Lab State

status: phase3_core_loop_verified
branch: pseudo-codex-lab-20260820
scope: pseudo_codex_lab/ and .github/workflows/pseudo-codex-lab.yml only
main_branch_changes: forbidden
pull_request_creation: forbidden
merge: forbidden
release_or_deploy: forbidden
paid_services: forbidden
scheduled_probe: pending

verified:
- ChatGPT can create a GitHub branch.
- ChatGPT can create and update files on that branch.
- GitHub Actions can run tests on a push.
- GitHub Actions can publish a compact PASS/FAIL commit status with a link to the exact workflow run.
- ChatGPT can follow that status to the workflow run, jobs, and decoded logs.
- A deliberate failure was detected from CI, diagnosed, repaired by ChatGPT, rerun automatically, and returned to PASS without user copy/paste.
- Repository state can be used as the handoff source instead of chat-only memory.

preferred_core_loop:
ChatGPT edits isolated branch -> GitHub Actions validates -> commit status reports PASS/FAIL -> ChatGPT follows failing run/logs -> ChatGPT repairs -> Actions validates again -> repeat until PASS or safety/decision boundary.

limitations:
- Direct branch-ref movement for an atomic multi-file commit was blocked by the safety layer. Use normal file create/update operations for now.
- Scheduled Tasks cannot rely on project-uploaded files, so cross-session state must live in GitHub or another connected app.
- Do not auto-merge, deploy, release, delete, or modify the default branch.

next:
- Verify whether ChatGPT Scheduled Tasks can resume from this repository state across chat/session boundaries using the connected GitHub app.
- After that, design the reusable project-state schema and a realistic Node/TypeScript CI profile without changing an existing production app.
