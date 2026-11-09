phase: 0
state: IN PROGRESS (branch phase-0-toolchain) — every automated gate check passes; waiting on GitHub access and a test server for the owner login
last_gate_passed: none (phase 0 gate 2 of 4 and 3 of 4 pass; see gate_progress)
pinned:
  tfs: v1.4.2 @ 31d6e85de2a86fb3f0e36c63509fba75b855b8bd
  otclient_mehah: 396f0b396741bdd4469f27cf9376103930712cff
  myaac: 31aed126d307c0ade8fc919fab5b90de354a2bb8
host:
  staging: unset (owner decision pending: .github/pending-issues/01-owner-test-server.md)
  production: unset
load_test: unset
owner_notes: []

gate_progress:  # phase 0 gate, docs/04_BUILD_PHASES.md
  - gate: "A second machine logs in with our client and sees our placeholder town; client data/things holds only our files"
    state: PARTIAL
    evidence:
      - "tools/loadbot/spire_client.py (headless 10.98 client) logs in and enters the world at the temple 5010,5009,7 — result: PASS (cloud dev box, 2026-10-05)"
      - "tools/package_client.py refuses to build a client unless data/things/1098 holds only Spirebound.dat/.spr, the bot module is gone and the third-party asset downloader is off (tested against the pinned OTClient tree)"
    blocked_on:
      - "GitHub access for the build agent (push + Actions) to run .github/workflows/client-windows.yml"
      - "a server your PC can reach (owner decision 01)"
  - gate: "Server boot log has zero missing-item warnings"
    state: PASS
    evidence: "tools/gate_phase0.sh step 6 — 'Spirebound Server Online!', 0 warning/error lines (the only filtered line is 'executed as root user' on the dev box)"
  - gate: "build_assets round-trip test passes"
    state: PASS
    evidence: "python3 tools/build_assets.py --install — 253 items (max id 8051), 9 outfits, 175 effects, 54 missiles, 1115 sprites; dat, spr pixels and otb re-read and match"
  - gate: "OWNER logs in once and confirms they can walk around"
    state: NOT STARTED (needs the Windows client build and a reachable server)
  automated_gate_command: "tools/gate_phase0.sh <env file>  ->  7 passed, 0 failed (2026-10-05)"
  map_preview: docs/previews/phase0_test_town.png

phase0_tasks:
  1_repo_and_pins: DONE (TFS imported as squashed snapshot in server/, see server/UPSTREAM.md; pins above)
  2_tfs_build_db_config: DONE on Ubuntu 24.04 (cloud dev box) — MariaDB schema, ops/config.lua.tpl + ops/render_config.sh, own RSA key via ops/gen_rsa_key.sh
  3_otclient_windows_linux: WRITTEN, NOT RUN — .github/workflows/client-windows.yml (Windows x64); Linux client deferred (nice to have)
  4_P1_spire_ids: DONE — server/src/spire_ids.h, server/patches/hardcoded_ids.md, tools/check_hardcoded_ids.sh
  5_art_tools: DONE — tools/placeholder_art.py, tools/procedural_tiles.py (grass, dirt, cobble, water, planks, marble, walls, fence, nature), tools/build_assets.py
  6_map_tools_test_town: DONE — tools/compile_map.py, tools/render_map.py, maps/src/test_town (temple, depot, one house, one NPC, one spawn)
  7_check_names: DONE — tools/check_names.py (whole-word, near-miss warnings); found and removed CipSoft content in upstream TFS Lua (achievement list)
  extra: CI .github/workflows/server.yml runs the whole automated gate on every push to phase branches

known_gaps:
  # Items found reading the design as a builder. "Proposed" = smallest fix; nothing here is applied to the design docs yet.
  - id: G1
    what: "Phase 0 gate says 'a second machine on the LAN'. The owner has no second machine or helper."
    proposed: "Read it as: the owner's Windows PC logs in to a server that is not running on that PC (staging VPS). Owner decision 01."
  - id: G2
    what: "12_TOWNS_NPCS_SHOPS 'Dye Merchant Lisbet' is one letter from a banned source name (tools/banned_names.txt)."
    proposed: "Rename to 'Dye Merchant Odile' when NPCs are built in phase 2. check_names.py now warns on one-letter near misses."
  - id: G3
    what: "banned_names.txt said 'substring match', which would fail ordinary words (agil->agility, argo->cargo, demon->demonic)."
    proposed: "DONE in tooling: whole-word match incl. plurals/possessives; header of banned_names.txt updated."
  - id: G4
    what: "06/10 use 'effect 207' for the marked-tile telegraph; TFS 1.4.2's highest magic effect id is 175."
    proposed: "Phase 1 adds one engine effect id (176, CONST_ME_SPIRE_MARK) and its client art; docs refer to 'the marked-tile effect'."
  - id: G5
    what: "06/13: the floor perk unlocks after 'both story quests', but floor 1 has three (Q1-1, Q1-2, Q1-3)."
    proposed: "Unlock after all story quests of that floor."
  - id: G6
    what: "12 says town guards attack black skulls only; 05 says Guarded-zone unjust killers are marked for guards for 30 min."
    proposed: "05 wins (authority order): guards attack black skulls and guard-marked killers. Fix the line in 12 during phase 1."
  - id: G7
    what: "16 first says host in 'US East (Ashburn or New York)', later and in 02 'Miami'."
    proposed: "02 wins: Miami. Fix the line in 16."
  - id: G8
    what: "Floor-1 hunting capacity differs: 11 (~410 slots, 14 camps x 2 pockets) vs 23 (~230 camp slots)."
    proposed: "Phase 2 measures capacity from the compiled map and corrects both."
  - id: G9
    what: "15 says '104 houses + 2 guild halls'; data/houses.csv has 104 rows = 102 houses + 2 halls."
    proposed: "Wording fix in 15."
  - id: G10
    what: "Head-start cap: 02/15 use half the district; the phase 4 gate computes ceil(20/2) from the credit list (same answer for Highrest's 20 houses)."
    proposed: "Implement 02 (half the district, rounded up); reword the phase 4 gate."
  - id: G11
    what: "Death drop rules don't say what happens to items inside bags in the backpack."
    proposed: "Each unbound item rolls on its own at any depth; a bag never drops as one unit."
  - id: G12
    what: "Art prompts (18b) are scheduled for phase 7, but the phase 8 gate needs final outfits, floor-1 monsters and tiles; Grok or an artist needs lead time."
    proposed: "Generate the first prompt batch (player outfits + floor-1 monsters) in phase 2 and open the handoff issue then."
  - id: G13
    what: "Upstream OTClient ships an auto-downloader for a third-party copy of official client files."
    proposed: "DONE in tooling: package_client.py disables it and fails the build if it can't."
  - id: G14
    what: "Upstream TFS engine Lua held CipSoft content (achievement list) despite being 'library' code."
    proposed: "Removed; check_names scans server/data on every CI run. A line-by-line audit of the remaining upstream Lua (lib/, events/) continues in phase 1."
  - id: G15
    what: "Our .dat/.spr have only been validated by our own reader (written from OTClient's parser), not by the real client — OTClient's dependency downloads are blocked in this build environment."
    proposed: "First real check is the Windows CI build plus the owner login. If the client rejects the files, the fix is in tools/otformats.py."
  - id: G16
    what: "data/secrets.csv and tools/secrets_src.csv contain every secret's location and trigger."
    proposed: "Keep the repository private. Before any part goes public (e.g. open-sourcing tools), move secret content to a private store."
  - id: G17
    what: "03 says the TFS fork lives in server/ as a git subtree."
    proposed: "Done as a squashed snapshot (same result, simpler history); documented in server/UPSTREAM.md."
  - id: G18
    what: "Build agent access: the repo is private and this session's GitHub token is invalid, so it can commit locally but cannot push, open issues, or run Actions."
    proposed: "Owner reconnects GitHub for Claude (see the session report). Until then commits stay on the local branch and issue drafts wait in .github/pending-issues/ (tools/file_pending_issues.sh files them)."

next_action: "Owner: reconnect GitHub access and answer decision 01. Agent: push phase-0-toolchain, file pending + phase issues, run client-windows.yml, then (once a server is reachable) deploy the test town for the owner login. Phase 1 does not start until the phase 0 gate passes (CLAUDE.md: one phase at a time)."
