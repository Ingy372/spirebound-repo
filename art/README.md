# Spirebound art pipeline (pre-rendered pixel art)

Every creature sprite is made the same way, so they all share one camera, one light, one scale and one palette.
All art here is original: built from simple 3D shapes in Blender. No Tibia sprite is copied or traced.

## How a sprite is made

1. **Model + walk cycle** — `art/models/<name>.py` builds the creature from a few smooth shapes and poses it for
   each frame (a script, so it can be re-tuned and re-rendered any time). The posed model is also saved as
   `art/models/<name>.blend` so it can be opened in Blender.
2. **Render** — `art/pipeline/render_creature.py` (runs inside Blender, no window) uses the shared rig
   `art/pipeline/rig.py` and renders three small images per frame at 4× size:
   *which part each pixel is* (body, ear, eye, tail...), *which way the surface faces*, and *how far away it is*.
3. **Pixel cleanup** — `art/pipeline/pixelize.py` (normal Python + Pillow) shrinks to 1×, lights every pixel,
   snaps it to the palette in `art/pipeline/palette.json`, removes speckles, adds a few fur tufts, a dark 1-px
   outline, and dark lines where a leg is behind the body. The rules are listed at the top of that file.
4. **Output** — `art/output/<name>/`:
   - `frames/<dir>_<n>.png` — 64×64 frames in the client's layout (the creature's own tile is the bottom-right
     quarter); frame 0 = standing, 1–8 = walk; dir = N, E, S, W
   - `<name>_sheet.png` — every frame, rows S / E / N / W (4× for small animals, 3× for tall figures)
   - `walk_<dir>.gif` (1×) and `walk_<dir>_4x.gif`
   - `compare/` — the same beside reference sprites on real grass. **Git-ignored, never shipped**: the references
     are Tibia's own art, pulled from the client files on Jay's PC by `tools/art_refs.py` for comparison only.

## Render a creature

```bash
python tools/art_refs.py              # once: reference sprites (rat, human outfits tinted like the client)
                                      #       + a grass tile into .local/artref (local only)
sh art/pipeline/render.sh rat          # Blender render + pixel cleanup, about 5 seconds
```

Needs Blender 5.3 (free) at `C:\Program Files\Blender Foundation\Blender 5.3\` (or set `BLENDER=`), plus Python
with Pillow and numpy.

## A new creature

Copy `art/models/rat.py` (animals) or `art/models/vesper.py` (people), change the shapes, sizes and walk, add a ramp set to `palette.json`, render, and compare
at 1× and 4×. Do **not** change `rig.py` or the shared palette rules for one creature: if they change, they change
for every sprite and everything is re-rendered.

## Monsters: compare with a real Tibia look-alike (Jay, 2026-11-15)

Every monster is compared with the closest creature that already exists in Tibia, never the rat
(`LOOKALIKES` in `tools/art_refs.py`; run it to pull them into `.local/artref/look_<id>.png`, local only).
Match the look-alike's size on the canvas, its silhouette, how much detail shows and how the walk reads,
while keeping our own design. Knobs in a model file:

- `SIZE`: whole-creature size (the wolf is 1.7, the grey alpha 2.1).
- `GROUND_STRETCH`: how long the body looks walking north/south (rat 0.75; Tibia-sized animals 1.4-1.6).
- `CANVAS_OFFSET`: placement on the 64x64 canvas in pixels. It moves the camera, so nothing is clipped.
  Tibia's sprites fill the tile to its right and bottom edges and spill up-left.
- `PIXEL_RULES["texture"]`: part -> [fine, coarse] grain (fur, stone, skin). The grain sticks to the part,
  so it does not crawl while walking.
- `PIXEL_RULES["bands"]`: 7 light thresholds for 8-tone ramps (more shading tones, like hand-made sprites).

## Four-legged creatures

Follow `art/QUADRUPED_RULES.md` (recipe, 14 rules, worked example: the boar). Build on `art/models/quadruped.py`,
then `python art/pipeline/check_creature.py <name>` must print ALL PASS before the sprite is shown to Jay.
Insects, crawlers and plants follow `art/CRAWLER_RULES.md` as well.
Every creature then gets the refinement pass in `art/DETAIL_RULES.md`. Player outfits follow `art/OUTFIT_RULES.md`
and are built on `art/models/humanoid.py` (colours in `art/pipeline/outfit_palettes.py`).
Dead bodies follow `art/CORPSE_RULES.md`: `art/models/corpse_<name>.py` lays the approved model down
(`art/pipeline/corpse_kit.py`), `tools/make_corpse_sheets.py` makes the decay steps and the review sheet.
`AUTO_PLACE = (1, 1)` in a model file places each direction against the tile's right and bottom edges.

## Client sprite rules (Canary 3.6.1 + OTClient Redemption 4.2, client 15.11)

- Asset format: the 15.x "appearances" protobuf file plus LZMA-compressed sprite sheets (`catalog-content.json`).
- Creature outfits: 4 directions (N, E, S, W), 1 standing frame + 8 walk frames per direction (Tibia's rat: outfit 21).
- Each frame is stored on a 64×64 canvas; a small creature like the rat fills only the bottom-right 32×32 tile.
- Getting our own sprite into the client: `tools/make_creature_sheets.py` packs approved frames into sheets,
  `tools/install_effects.py` puts them in the client at every start and registers them with the server at every build.

## Own look numbers for people (roadmap 6.5, 2026-11-25)

Monsters replace the borrowed Tibia look they wore (`CREATURES` in `tools/make_creature_sheets.py`). People cannot:
many NPCs share one borrowed look, so reskinning it would change them all. Each approved NPC or player outfit gets a
**new look number** of its own (`NEW_LOOKS`). Rules:

- **Numbers start at 2001** (the client's highest outfit is 1875) and only ever grow. 2001-2009 class outfits,
  2010-2099 NPCs, 2100-2199 shop outfits, 2200-2499 monsters built on the humanoid body (they wore borrowed
  looks 129/131 that NPCs share too, so they cannot reskin them like the animals). Never renumber one in use: saved characters keep their number.
- **Ours go last, in rising order.** OTClient sizes its outfit table from the LAST outfit in the appearances file; a
  lower number after a higher one is written past the end of the table (a crash). `install_effects.py check` tests this.
- **People keep Tibia's 8 px shift.** Our figures are drawn 8 px low-right on the canvas (`CANVAS_OFFSET`), exactly
  where Tibia's raw outfit sprites sit, and Tibia's people carry an 8 px up-left shift (flag 26) in the client. A new
  person look gets the same shift, or it stands 8 px off its tile. Animals have no shift.
  The rule in code: every new look gets the shift unless its model uses `AUTO_PLACE` (animals, the Floor 1 bosses),
  read from the render's meta.json. Older people renders keep their offset in `canvas_offset`, newer ones in
  `placed`, so never decide by those fields: the live NPCs would lose their shift.
- **The server must know the number too.** Canary refuses (with a warning) an NPC, monster or player outfit whose
  look is not in its appearances file; `tools/build_server.py` lists ours there (id only) at every build.
- **Addons** (base, addon 1, addon 2) are extra pattern rows of the same look, packed from approved
  `<name>_a1` / `<name>_a2` overlays (`art/pipeline/addon_overlay.py`; rules A1-A7 in `art/OUTFIT_RULES.md`).
- **Player outfits** also need a line in `outfits.xml` (added by `tools/build_server.py`) and someone to grant them
  (`scripts/spirebound/class_outfits.lua`: each class gets its own when picked at the Registrar).
- **No colour layer yet:** an NPC's or outfit's head/body/legs/feet colours do nothing on our looks (set them to 0).
- **Every client needs the update at the same time.** Jay's client gets it at every start; the friends' package
  must be rebuilt (`windows\Share-Client.bat`) after new looks go in, or a friend's client draws nothing for them.

## Rig numbers (why they are what they are)

- **palette.json is generated** by `outfit_palettes.py`, `creature_palettes.py` (wrong-animal cleanup) and
  `boss_palettes.py` (bosses and variants). Never hand-edit it: on a merge conflict take main's copy and rerun all three.
- **At most 33 parts per model** ("none" plus 32). The id pass stores a part's number as number x 8 in one colour
  channel, so anything past 32 is read back as 32 and silently takes that part's colours. `render_creature.py` refuses
  more. A variant built on a frozen base that needs more parts reuses the base parts it hides, recoloured in its own
  palette (the Hedge Hexer's staff is the bandit's "hilt", her glow is the hidden "scarf").

- 1 tile = 1 Blender unit = 32 px. Two projections, chosen in each model file (`PROJECTION`):
  - **oblique** (standing figures, e.g. Vesper): Tibia's real drawing rule. The camera looks straight down at a
    slanted world, so fronts and faces are seen at full size and height slides up-left at 45°, like hand-made
    Tibia people. Figures use chunky Tibia proportions (big head, short wide body) and sit 8 px low-right on the
    canvas (`CANVAS_OFFSET`), where Tibia's own outfits sit.
  - **tilt** (low animals, the approved rat): camera tilted 45°, looking north. The rest of this list is for it.
- `GROUND_STRETCH = 0.75`: measured against hand-made Tibia creatures, their N/S bodies are only a little shorter
  than E/W. N/S bodies lean 12° so they run slightly diagonal, like hand-made sprites.
- Creatures stand 3 px below the tile centre (`CAM_SHIFT_Y`).
- Light from the upper left, a bit toward the viewer, with extra light on top surfaces (spine highlight, dark belly).
