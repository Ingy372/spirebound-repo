#!/usr/bin/env bash
# Files every issue drafted in .github/pending-issues/ (written while GitHub access was unavailable),
# then deletes the draft. Needs GitHub CLI (gh) logged in. Run from the repo root.
set -euo pipefail
shopt -s nullglob
for f in .github/pending-issues/*.md; do
  title=$(sed -n 's/^title: *"\{0,1\}\(.*[^"]\)"\{0,1\}$/\1/p' "$f" | head -1)
  labels=$(sed -n 's/^labels: *//p' "$f" | head -1)
  body=$(awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' "$f")
  gh issue create --title "$title" --label "$labels" --body "$body"
  git rm -q "$f" 2>/dev/null || rm "$f"
done
