# Legacy: the October 2026 TFS 1.4.2 setup

Moved here on 2026-11-08 (roadmap task 1.2) when the engine changed from TFS 1.4.2 (protocol 10.98) to **Canary v3.6.1 (protocol 15.11)** at Jay's request. Nothing was deleted; it is kept for reference.

| What | Why it moved |
|---|---|
| `tfs-1.4.2/server/` | The imported TFS engine and its datapack. Canary replaces it. |
| `tfs-1.4.2/ops/` | Config template and key scripts for TFS. |
| `tfs-1.4.2/assets/` + `tools/build_assets.py`, `placeholder_art.py`, `procedural_tiles.py`, `package_client.py` | The 10.98 `.dat/.spr/.otb` art pipeline. Canary/OTClient 15.x use a different format (appearances + sprite sheets); a new pipeline comes in roadmap task 6.4 and may reuse the PNG generators. |
| `tools/loadbot/`, `gate_phase0.sh`, `dev_account.py`, `check_hardcoded_ids.sh` | Test client and scripts written for the 10.98 protocol and the TFS database. |
| `tools/create_phase_issues.sh`, `file_pending_issues.sh`, `github/pending-issues/` | GitHub issue workflow from the old phase plan. |
| `github/server.yml`, `github/client-windows.yml` | CI for the TFS build and the source-built client. |

Still in use from the old setup: `tools/check_names.py`, `tools/banned_names.txt`, `tools/gen_tables.py`, `tools/secrets_src.csv`, `tools/otformats.py` (map file writer), `tools/compile_map.py` and `tools/render_map.py` (being ported to 15.x item ids), `maps/src/`, `data/`, `docs/`.
