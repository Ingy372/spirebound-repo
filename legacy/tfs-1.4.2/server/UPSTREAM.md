# Upstream: The Forgotten Server

| Field | Value |
|---|---|
| Repository | https://github.com/otland/forgottenserver |
| Tag | v1.4.2 |
| Commit | 31d6e85de2a86fb3f0e36c63509fba75b855b8bd |
| License | GPL-2.0 (see `LICENSE`) |

## What was imported

Imported as a single squashed snapshot (equivalent to `git subtree --squash`):
`src/`, `cmake/`, `CMakeLists.txt`, `LICENSE`, `AUTHORS`, `schema.sql`.

Deliberately **not** imported:
- `data/` — the upstream datapack carries CipSoft-derived content (monsters, NPCs, spells, item IDs, map). Our own datapack lives in `server/data/` and only reuses upstream engine-level Lua libraries (`lib/`, `events/`, NPC system library), which are TFS code, not game content.
- `key.pem` — upstream ships a publicly known RSA private key. Spirebound generates its own key on each server host (`ops/gen_rsa_key.sh`); the private key never enters git.
- `vc17/`, `Dockerfile`, `appveyor.yml` — not used.

## Our patches

Every change to upstream C++ is its own commit (`phase-N: Pn ...`) and is listed in `server/patches/README.md`.
