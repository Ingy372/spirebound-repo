# assets

`assets.csv` lists every client thing (items, outfits, effects, missiles). Items that exist in the design
tables (`data/weapons.csv`, `armor.csv`, `materials.csv`, `consumables.csv`) get a client thing automatically;
everything else is a row here. `tools/build_assets.py` turns it into `build/Spirebound.dat`, `Spirebound.spr`,
`items.otb`, `items.xml` and runs a round-trip test.

## Columns

`id, category, name, flags, size, frames, png, xml, notes`

- **category**: item | outfit | effect | missile
- **flags** (items, `;`-separated): ground:SPEED, border, bottom, top, container, stackable, forceuse, multiuse,
  writable:LEN, fluid, splash, block, immovable, blockmissile, blockpath, pickup, hangable, hooksouth, hookeast,
  rotate, light:INTENSITY:COLOR, height, corpse, animate, minimap:COLOR, fullground, look, cloth:SLOT, usable
- **size**: WxH in 32-px tiles (2x2 for large objects)
- **frames**: animation phases (outfits: walk frames; frame 0 is idle)
- **png**: `generated:<path>` for procedural art, a path under `png/`, or blank (then `png/items/<id>.png`)
- **xml**: server-side items.xml attributes, `key=value;key=value`

## Where art comes from (first hit wins)

1. `png/<path>` — Grok, commissioned, or hand-made art (committed; every non-generated file gets a row in `LICENSES.md`)
2. `generated/<path>` — `tools/procedural_tiles.py` output (git-ignored, rebuilt automatically)
3. a labeled placeholder from `tools/placeholder_art.py`

Outfits: `png/outfits/<lookType>/<n|e|s|w>_<frame>.png`. Effects: `png/effects/<id>.png` (horizontal strip).
Missiles: `png/missiles/<id>.png`.

## ID ranges

| Range | Use |
|---|---|
| 100–999 | grounds, borders |
| 1000–1499 | walls, doors, stairs, structures |
| 1500–1599 | fields (engine ids, `server/src/spire_ids.h`) |
| 1600–1999 | nature, furniture, props |
| 2000–2099 | engine core items: coins, containers, depot, mail, splashes, player corpses (`spire_ids.h`) |
| 3000–3999 | monster corpses |
| 5100–5999 | materials (data/materials.csv) |
| 6000–6999 | weapons and shields (data/weapons.csv) |
| 7000–7999 | armor (data/armor.csv) |
| 8000–8999 | consumables and tools (data/consumables.csv) |

Server item id = client item id (no remapping).
