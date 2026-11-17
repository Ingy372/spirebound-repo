# Spirebound spell effects

Our own spell effects (ids 401 and up, `SpireFx` in `server/data-spirebound/lib/spirebound/spells.lua`). Made with
Blender plus painted light, pixelized to the game's 64×64 effect size. All of it is original art and is committed.

## Make, look, install

```bash
python art/effects/make_fx.py                # all effects (about 20 s), or name a few: make_fx.py meteor bloom
```
1. `paints.py` paints the light (glows, bolts, rings, sigils); `solids.py` builds the solid parts in Blender
   (sword, rocks, thorns, crystals, meteor, banner) and `render_fx.py` renders them; `make_fx.py` puts the two together
   and pixelizes.
2. Look at `art/effects/output/all_effects.png` and each `output/<name>/<name>_sheet.png` (4x, grey and dark).
3. The packed game files land in `art/effects/game/` (sprite sheets + `effects.json`). `tools/install_effects.py` puts
   them into the client (Start-Spirebound does this at every start) and the server (`tools/build_server.py` does it at
   every build). After installing, a client that was already open must be restarted.
4. Check them in the real client: `python tools/spell_routes.py` then `python tools/autopilot.py spells_<vocation>`
   casts every spell with screenshots; `python tools/spell_routes.py --report` prints what each cast did.

## Rules (keep to them for every new effect)

1. **Banded, not foggy.** Use `Canvas.orb`, `flame`, `band`, `bolt`: three or four hard steps of one palette with a
   white-hot core. Soft glows only as a faint extra. Fog and pastel washes disappear on grass.
2. **One palette per vocation** (`fx2d.py`): Vanguard gold, crimson and steel; Ranger daylight; Arcanist ember and
   violet; Mystic frost and leaf. Shared or neutral effects use white.
3. **Readable at 1x.** The main shape covers at least a third of the tile; check `all_effects.png` at 2x, not only
   the 4x sheets.
4. **The game's drawing rule.** The spell's tile is the bottom-right 32×32 of the 64×64 canvas. Anything tall rises
   up and a little left (`fx2d.UP`); things on the ground are true circles.
5. **Anticipation, peak, quick fade.** Something is visible on the first frame (`frame_time` starts one-shot effects
   a little in); the peak comes in the first third; the end fades fast. Effects that repeat (the banner) loop cleanly.
6. **Solid things are 3D, light is painted.** Swords, rocks, crystals, thorns and cloth come from Blender (they get a
   dark outline); light, sparks and rings are painted.
7. **Every effect gets light** around it on the ground (`LIGHT` in `make_fx.py`) in its palette's colour.
8. **Ids never change** once an effect is in the game; a new effect takes the next free id and a row in `EFFECTS`.
9. **Test in the client before showing Jay**: the spell routes above, then look at the screenshots.
