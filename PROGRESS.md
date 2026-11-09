# Progress log

Newest at the bottom. 2–3 lines per finished task, plain English.

---

### 2026-11-08 — Session 1: new plan, repo cleanup
- **Repo fix:** your PC's copy of the repo was linked to your *Dojo-game* GitHub repo instead of *spirebound-repo*. Re-linked it to spirebound-repo and brought in the one newer commit that was only on GitHub. (Stray branch in Dojo-game: see QUESTIONS.md Q2.)
- **Kept, not deleted:** the October design pack (`docs/`, `data/`, `tools/`) and the phase-0 TFS server work. The old `CLAUDE.md` is replaced by the new one; the old `STATUS.md`, `CHANGELOG.md` and `OWNER_INPUT.md` (your player-experience answers, which DESIGN.md still draws on) moved into `docs/` with "_2026-10" in their names. Work now happens on the `main` branch (the phase-0 branch was merged in).
- **Task 1.1 done:** wrote DESIGN.md (game bible from your brief, gaps marked "Claude's call"), ROADMAP.md (10 phases, Phase 1 = character creation → Floor 1 boss → Floor 2 unlocks), CLAUDE.md (your working rules), QUESTIONS.md (9 questions, each with a recommendation already assumed), PLAYTEST.md, ART_REQUESTS.md (first batch with Grok prompts), MAP_REQUESTS.md.
- **Research:** Canary v3.6.1 (protocol 15.11) and OTClient Redemption 4.2 both publish ready-made Windows builds, so your PC never needs a compiler. Cyntara's bot rules summarized in DESIGN.md §12.

### 2026-11-08 — Task 1.2: old TFS setup archived
- Moved the TFS 1.4.2 server, its config scripts, the 10.98 art pipeline, the old test client and old CI into `legacy/tfs-1.4.2/` (nothing deleted; `legacy/README.md` lists every item and why).
- Kept in use: name checker (now also scans DESIGN.md, ART_REQUESTS.md and the new datapack), table generator, map writer and map compiler. Name check: 0 banned names.

### 2026-11-08 — Tasks 1.3, 1.4, 1.12: the Canary server boots with our datapack
- `tools/build_server.py` downloads the pinned Canary v3.6.1 and assembles a server from it plus our own files; `tools/test_boot.sh` starts it, runs in-game tests and fails on any error. Result: **server online, 0 errors, 1 in-game test passed** (cloud test box).
- New datapack `server/data-spirebound/` (from Canary's small sample pack, all CipSoft-named monsters/NPCs/quests stripped). Prey, hunting tasks, Wheel of Destiny, Forge monsters and boosted boss are switched off; newbie protection set to level 50; 2 characters online per account.
- XP stages from DESIGN.md 5.5 are live (25x early down to 2x at 401+), checked by an in-game test. The world map is still Canary's sample map as a stand-in until task 1.8.
