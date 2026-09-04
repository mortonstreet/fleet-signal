#!/usr/bin/env bash
set -euo pipefail
OFFER="${1:?offer runtime slug required, e.g. fleet}"
BASE="${2:-main}"
INT="int/${OFFER}"
if git show-ref --verify --quiet "refs/heads/$INT"; then
  echo "$INT already exists"
else
  git branch "$INT" "$BASE"
fi
for lane in ingest domain api-cli ui qa; do
  branch="feat/${OFFER}/${lane}"
  wt="../wt-${OFFER}-${lane}"
  if ! git show-ref --verify --quiet "refs/heads/$branch"; then git branch "$branch" "$INT"; fi
  if [ ! -d "$wt" ]; then git worktree add "$wt" "$branch"; fi
done
printf 'created/verified integration branch %s and five offer worktrees\n' "$INT"
