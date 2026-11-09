#!/usr/bin/env bash
# Creates one GitHub issue per build phase. Requires GitHub CLI (gh) logged in. Run once from the repo root.
set -euo pipefail
gh label create owner   --color FBCA04 --force >/dev/null
gh label create handoff --color 5319E7 --force >/dev/null
gh label create phase   --color 0E8A16 --force >/dev/null
titles=(
 "Phase 0 — Toolchain and empty world"
 "Phase 1 — Core rules"
 "Phase 2 — Floor 1 world"
 "Phase 3 — Economy, items, crafting"
 "Phase 4 — Houses, guilds, PvP contracts"
 "Phase 5 — Secrets framework, Vesper, Underkeep wings 1–2"
 "Phase 6 — Floors 2–5"
 "Phase 7 — Client UI and website"
 "Phase 8 — Art, scale, operations"
 "Phase 9 — Closed beta, tuning, wipe, launch kit"
 "Phase 10 — Wardrobe store"
)
for t in "${titles[@]}"; do
  gh issue create --title "$t" --label phase --body "Tasks and gate: see docs/04_BUILD_PHASES.md. Close only when every gate test is recorded in STATUS.md."
done
