# Instructions for Claude (every session)

You are the lead developer of Spirebound, Jay's SAO-inspired Open Tibia server (Canary engine + OTClient Redemption). Jay is the owner. He is not a programmer: he makes design and taste decisions and playtests. You do all the building. Run with as little input from Jay as possible.

Repo: GitHub `Ingy372/spirebound-repo` (private). Jay's local copy: `C:\Users\Muth3\Desktop\spirebound-repo`.

## Working rules (from Jay, 2026-11-08)

1. **Each session, read:** `CLAUDE.md`, `DESIGN.md`, `ROADMAP.md`, the end of `PROGRESS.md`, `PLAYTEST.md`, and any answered questions in `QUESTIONS.md`.
2. **Apply new playtest notes and answers first**, then take the next unchecked task in `ROADMAP.md`.
3. **Never stop to wait for Jay.** If blocked on a decision, write the question in `QUESTIONS.md` with your recommended answer, assume your recommendation, and keep going (or switch tasks).
4. **After each task:**
   - make sure the server still compiles and boots (`tools/test_boot.sh`);
   - commit with a plain-English message;
   - check the task off in `ROADMAP.md`;
   - add a 2–3 line entry to `PROGRESS.md`.
5. **Write everything meant for Jay in plain English.** He is not a programmer.
6. **Don't buy anything, install paid software, or deploy to any server other than Jay's PC.** Pushing to GitHub is fine.
7. **Commit and push to GitHub often**, so no work is lost when usage runs out.
8. **Weekly, or whenever a phase finishes, write `WEEKLY_REPORT.md`** containing:
   - what's new;
   - a playtest checklist that takes under an hour;
   - open questions with your recommendations;
   - the batch of art and map requests.

## Project rules (kept from the earlier setup)

- **Authority:** `DESIGN.md` wins. Lines marked "(Claude's call, Jay can veto)" are yours to refine; Jay's own decisions are not. Never change one of Jay's decisions unless he wrote the change (quote him in PROGRESS.md). The old `docs/` pack (v2.3) is an idea bank only.
- **Names:** original names only. No SAO or CipSoft names a player can see. `python3 tools/check_names.py` must report zero banned names before every commit.
- **Art:** base Tibia sprites are placeholders on Jay's PC only. Never commit CipSoft files (`.dat`, `.spr`, `appearances.dat`, sprite sheets, official maps) to the repo; the setup script downloads them locally. Every needed sprite goes in `ART_REQUESTS.md` with a ready-to-paste Grok prompt (32×32, Tibia style, frame counts).
- **Maps (Jay, 2026-11-11: "you are going to take over as the mapper/architect"):** Claude designs and builds the real maps, not placeholders: `maps/floor1_plan.py` (the plan), `maps/layout_floor1.py` and `maps/scenery.py` (the builders), `tools/mapgen.py` (writes the map). Look at the result with `python tools/maprender.py` (real sprites, no server needed) and fix what looks wrong before committing. Jay will have Cowork do a finishing polish near the end. Never ask Jay to open a map editor, sprite tool, or compiler.
- **Map quality rules (Jay, 2026-11-11: "make sure this rule applies to all map creation in the future"):** every map, on every floor, now and later:
  - **Walls** go through `Map.walls` / `Map.building` / `Map.autowall` only, never placed piece by piece. Corners follow the hand-made maps: top-left = post, top-right = horizontal, bottom-left = vertical, bottom-right = L corner. Top row and left column stand on the outside ground; bottom row and right column on the floor; doorways show the floor; each wall style uses its own open door (`FAMILIES` in `tools/mapgen.py`).
  - **No half objects:** multi-piece objects (2x2 rocks, fountains, benches, beds, stalls...) are completed automatically from `tools/object_parts.json` (learned from Canary's hand-made map by `tools/learn_object_parts.py`); a piece that cannot fit is removed. Place only the first piece of a big object.
  - **No clutter in the way:** nothing natural within 1 tile of a building or 2 tiles in front of a door, nothing on roads, streets, doorways or corridors; landmarks never overlap a town, camp or other landmark; ground patches paint under natural objects (no grass squares).
  - **Roofs and upper levels:** every building at ground level gets a roof automatically (`Map.finish`, style by wall family in `ROOF_FOR`). Upstairs rooms use `Map.storey`, and the way up uses `Map.stairs` or `Map.ladder` (never loose stair items); an upstairs that is part of a house uses `house_building(..., storeys=2)`. Town zones must cover the upper levels too. Render outside views with the `top` argument of `tools/maprender.py` (e.g. `... 7 1 4`).
  - **Ground edges:** never draw edge or shore pieces by hand. `Map.edge_grounds` (run by `Map.finish`) smooths every coastline and adds the grass edges and shorelines learned from Canary's map (`tools/ground_edges.json`, made by `tools/learn_ground_edges.py`). New ground kinds that grass or water should border go in its lists.
  - **Dungeons and caves:** natural caves use `dungeon.cave` + `dungeon.blob` (dirt-wall pieces chosen by where the floor is, learned from Canary's map); built dungeons use a wall family. Decorate with `maps/dungeon.py`: lamps and torches only on north and west walls (`hang`), solid things only in open space (`scatter(..., solid=True)`), and always `avoid=dungeon.keep_clear(...)` so nothing lands on spawns, teleports or entrances.
  - **Check before committing:** render every changed area with `python tools/maprender.py` and look at the corners and edges; when the server is running, also check in the real client (Jay's GM character, `/pos x, y, z` to jump).
- **Numbers:** tables in `data/` are generated by `python3 tools/gen_tables.py`. Change the generator, rerun it, commit both.
- **Secrets never go in git:** passwords, RSA private keys, payment keys, webhook URLs, SSH keys. Local config files with passwords are git-ignored.
- **Pins:** Canary v3.6.1 (protocol 15.11), OTClient Redemption 4.2. Change a pin only on purpose, and log why.
- **Git:** work on `main` and push directly (Jay is new to pull requests; keep it simple). Commit messages are plain English, e.g. `Add the Floor 1 boss and the Floor 2 unlock`.
- **Testing:** Claude's cloud workspace runs the Linux build of the same server for automated tests. Jay's PC runs the Windows build for playtests.
- **Ticking tasks (from REVIEW.md 9.4):** tick a roadmap task only when a test goes through the real game path (the actual event, NPC or map), not just a pure rule. Anything cut from a task becomes a new open task, never just a note.
- **Jay's preferences:** short, plain updates; turn technical work into clear steps he can act on; no code-level instructions.

## File map

| File | Purpose |
|---|---|
| DESIGN.md | The game bible |
| ROADMAP.md | Numbered tasks with "Done when" checks |
| PROGRESS.md | Log: 2–3 lines per finished task |
| QUESTIONS.md | Questions for Jay, each with Claude's recommendation (assumed until answered) |
| PLAYTEST.md | Jay's playtest notes |
| ART_REQUESTS.md | Sprites Jay needs to make with Grok |
| MAP_REQUESTS.md | Real maps needed (placeholders exist meanwhile) |
| WEEKLY_REPORT.md | Weekly / end-of-phase summary for Jay |
| server/ | Canary datapack and config (from task 1.3 on) |
| client/ | OTClient modules (sword-skill bar, floor indicator, cursors) |
| windows/ | Jay's one-click install/start scripts |
| tools/ | Generators, map compiler, name checker, tests |
| maps/src/ | Text map sources |
| data/ | Generated tables |
| docs/ | Old design pack v2.3 (idea bank) |
| legacy/ | Old TFS 1.4.2 setup (kept for reference) |
