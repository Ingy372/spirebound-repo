# maps

Maps are ASCII text, compiled by `tools/compile_map.py` into `build/spirebound.otbm` + spawns + houses.
Nobody opens a map editor. Format and validation rules are in the header of `tools/compile_map.py`
and in docs/11_FLOORS_AND_MAPS.md.

| Path | What |
|---|---|
| src/legend.csv | character -> item(s) per layer |
| src/<area>/meta.csv | area origin and name |
| src/<area>/zNN_ground.txt, zNN_objects.txt | one character per tile |
| src/<area>/points.csv | towns, NPCs, spawns, houses, doors, zones, signs, secret triggers |
| build/ | generated (git-ignored) |

Preview: `python3 tools/render_map.py` (writes `preview/`, git-ignored). Phase-gate previews are copied to `docs/previews/`.

Areas so far: `test_town` (phase 0, GM/test region at 5000,5000).
