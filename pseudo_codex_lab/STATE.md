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
- Actions can write a compact test report back to the isolated branch.
- ChatGPT can read a failed report, diagnose the defect, patch the code, and obtain a passing rerun without user copy/paste.

next:
- Verify whether ChatGPT Scheduled Tasks can resume from repository state across chat/session boundaries using the connected GitHub app.
- Do not expand beyond this isolated lab scope until that probe is confirmed.
