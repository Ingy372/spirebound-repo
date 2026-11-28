# Item icon rules: items made with the creature pipeline

Jay, 2026-11-27, after two Grok batches: "it looks like the art was imported from another game ... I'm leaning
towards just having you build everything and cutting grok out", then "Do it please. Take your time and try to make
them look detailed." Items are built like the monsters (a small 3D model, rendered, then pixelized with the same
palette rules and outline), so they look like they belong to the same game.

## Make and check

```bash
python art/pipeline/item_palettes.py          # colours -> palette.json (after changing item_palettes.py)
sh art/pipeline/render.sh item_<name>          # Blender render + pixel cleanup
python tools/make_item_icons.py                # icon.png per item + ART_FOR_JAY/items_review.png
```

- Model: `art/models/item_<name>.py`, built on `art/models/item_kit.py` (`from item_kit import *`). Colours:
  `ITEMS` in `art/pipeline/item_palettes.py` (8-tone ramps from shared materials: STEEL, GOLD, LEATHER...).
- Output: `art/output/item_<name>/icon.png` (32x32, the game sprite) and `icon_4x.png`.
- Review: `ART_FOR_JAY/items_review.png` puts each item beside the Grok version (if any) and the closest Tibia
  item (`LOOKALIKES` in `tools/make_item_icons.py`, drawn from the client files on Jay's PC, never committed).

## Rules (learned on the first 11, 2026-11-27)

- **I1 Write the brief first.** Each model's docstring says: silhouette (what makes it readable from the outline
  alone), colours (base materials plus ONE bright accent), details, and the Tibia look-alike and how ours differs.
- **I2 Tibia's weapon pose.** Long things (swords, bows, wands, rods, spyglasses) lie diagonally, handle or butt
  bottom-left, tip top-right. Build along `at(s, n)` (s along the diagonal, n across it).
- **I3 Flat things use the flat-item camera** (the kit default): `HEIGHT_SHEAR = 0.3` and `"light": LIGHT`
  (light from the screen's top-left). With the creatures' full 45-degree lean, the up-left half of anything
  lying flat folds out of sight behind its crest, and the creatures' light (from the south-west) lights both halves
  of a diagonal blade the same: the blade came out one flat colour.
- **I4 Standing things** (mugs, bottles standing up) use `globals().update(STANDING)`: the animals' tilted camera
  and the creatures' own light, so the front is upright and lit. Do not set `"light"` for them. In the slanted
  view their visible faces turned away from the light and the top filled the picture.
- **I5 Things with a side profile lie on their side.** Boots seen from the tilted camera showed the round tops
  of their shafts (balls, then pipes). Build them standing, then lay them down under a `Lay` empty rotated -90
  degrees about x (see `item_millrace_boots.py`): the flat-item camera then sees the side profile straight on.
- **I6 Size by kind, like Tibia.** Rings and amulets are small in the middle of the tile (about 14-20 px), bottles
  and mugs medium, weapons and maps reach across the tile. `SIZE` in the model; `make_item_icons.py` warns over
  32x32 and centres every item on its tile (1 px low-right).
- **I7 One eye-catcher, big enough.** The accent that names the item (a flame, a flower, a gem, a lit door) must be
  several pixels across at 1x. Tibia's fire wand is mostly flame; our first flame and bud were too small to read.
- **I8 Show what makes it that item.** A spyglass's lens tips up towards the viewer (`lift`), a tankard keeps its
  front clear (no lid, foam on top), a medallion leans up so its face catches the light, a ring stands half up so
  the stone shows. If a feature is edge-on, turn the object until it is not.
- **I9 Detail through parts, not texture.** At 32 px detail comes from separate parts with their own ramps (bands,
  rims, wraps, knots, runes) and the dark lines between parts. Texture grain only for wood, stone and leather.
  Parts smaller than about 2 px vanish: make them bigger or drop them (the sabre's red edge gleam read as pink).
- **I10 At most 33 parts**, as for creatures. Many objects can share one part (all chain links are "chain").
- **I11 Approval.** Items go in the game only after Jay approves them in writing (quote in `art/APPROVED.txt`).
  Installing them in the client (reskinning the Tibia item each one replaces, like the corpses in
  `CORPSE_RULES.md`) is its own task.

## Kit shapes (`item_kit.py`)

`lathe` (revolve a profile: mugs, bottles, tubes, knobs) · `torus` (rings, chain links, handles) · `slab`
(a flat outline with an optional raised crest: blades, leaves, paper) · `curve_outline` (a blade outline around a
curved spine) · `place` (location, rotation in degrees, scale) · `set_tube_pts` (bows, vines, strings, branches,
on `m.tube`) · plus the creature shapes (`m.ellipsoid`, `m.box`, `m.cone`, `m.capsule`, `m.frustum`).
