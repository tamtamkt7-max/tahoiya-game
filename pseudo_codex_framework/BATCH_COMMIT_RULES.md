# Batch Commit Rules

When a task changes multiple files, create the complete change set as one Git tree/commit whenever the GitHub connector supports it. Update the working branch ref only after every blob and the new tree are ready.

This reduces unnecessary CI runs and keeps one logical repair or feature change in one commit.

Fallback to sequential file updates only when batching is unavailable or a safe conflict check requires it.
