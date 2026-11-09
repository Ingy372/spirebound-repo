# server/

Spirebound's own server files. The Canary engine itself is **not** stored here: `tools/build_server.py` downloads the pinned release (see `PINS.env`) and assembles a runnable server in `.build/server/`.

| Path | What it is |
|---|---|
| `PINS.env` | Exact Canary and OTClient versions we use |
| `config-overrides.lua` | Our settings, applied on top of Canary's default config |
| `core-overrides/` | Files that replace Canary core files (e.g. `stages.lua` = XP rates) |
| `data-spirebound/` | Our datapack (world, NPCs, monsters, scripts). Started from Canary's small `data-canary` pack (GPL-2.0, same license as Canary) with all CipSoft-named monsters, NPCs, raids and quests removed |
| `data-spirebound/scripts/spirebound/` | Spirebound systems + in-game tests (`tests/`), run by `tools/test_boot.sh` |
| `local.env` | Your database password (git-ignored, never committed) |

Run the automated check: `tools/test_boot.sh` (Linux / cloud). Jay's Windows setup comes in roadmap task 1.5.
