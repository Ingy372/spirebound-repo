# Corpse rules: every monster leaves a body that matches it

Jay, 2026-11-26: "you don't want a boar dying and leaving behind an alligator body".

## Part 1 — monsters still on a borrowed Tibia look (or redrawn in place of one)

The corpse is a Tibia corpse item (no approval needed). Pick the corpse of the creature the monster **looks like in
the game**: for a borrowed look, the Tibia creature it borrows; for a look we redrew in place (`CREATURES` in
`tools/make_creature_sheets.py`: look 119 is now our boar, not a crocodile), the animal we drew.

- **K1 The fresh corpse.** Use the first item of the decay chain (the 10-second one that decays into the 300-second
  one), never a later step: a later step skips the fresh body or starts already rotting.
- **K2 It must hold the loot.** The corpse's container size must be at least the number of loot rows the monster has
  (a full corpse loses loot). Some Tibia corpses are not containers at all (dead snake 3998, poison gas 2127):
  never use those for a monster with loot. Check: count `{ id =` lines in the monster file against items.xml.
- **K3 Find it by name.** `items.xml` (in the Canary data download) names every corpse ("dead boar"); follow its
  `decayTo` chain. Prefer the creature, then its family (a highland antelope: dead rhindeer; a mountain cat: dead lion).
- **K4 Floors 2-10 placeholders** take their corpse with their look (`LOOKS` pairs in `tools/gen_monsters.py`);
  monsters with their own look get theirs from `OWN_CORPSES`.

## Part 2 — monsters with our own art (looks 2201+, 2301+)

Their own dead body, made with the Blender pipeline from the approved monster model.

- **C1 Same model, lying down.** `art/models/corpse_<monster>.py` is two lines (`corpse_kit.make(globals(), "<monster>")`).
  It reuses the approved model untouched (parts, palette, pixel rules), so the body matches the living monster
  exactly. It rests on the ground (nothing floats or sinks) and is centred on its tile.
- **C2 Placement.** Like the animals: against the tile's right and bottom edges, spilling up-left (`AUTO_PLACE`).
  A normal monster's body fits one tile plus spill; a 2x2 boss's body fills the 64x64 canvas.
- **C3 How each body lies.** Four-legged animals roll onto their side and are seen from the west: legs in the air,
  the classic "dead" read. People lie on their back, seen from the east (head to the left). Insects flip belly-up,
  legs in the air. Plants and floating spirits sink flat where they were.
- **C4 Three steps of decay.** 1 fresh (the body), 2 rotting (the body sunk flatter, its colours greyed toward a
  dull green-brown and darkened: `decay()` in `tools/make_corpse_sheets.py`), 3 the end (C5). The outline stays.
- **C5 The end step.** Flesh-and-blood monsters end as a small bone pile (`corpse_bones.py`; `corpse_bones_big.py`
  for big animals and 2x2 bosses): skull with sockets and a dropped jaw, ribcage over a spine, two crossed long
  bones. Monsters with no bones (stone, chitin, plants, spirits) end as a dried husk: the body flatter still and darker.
- **C6 Weapons stay with the body** (the bandit's blade, the sentinel's spear): Tibia's people corpses do the same,
  and it tells you who died.
- **C7 Parts limit.** The 33-part limit applies (`render_creature.py` refuses more). The Axe-Lord's approved model
  has 34 parts, so it keeps the Tibia "dead black knight" (an armoured warrior: a fair match) until its model is
  slimmed.
- **C8 Approval first.** Corpse art goes in the game only after Jay approves the sheet in writing (quote in
  `art/APPROVED.txt`). Until then the monster keeps the best-matching Tibia corpse from Part 1.

### Make and check

```bash
sh art/pipeline/render.sh corpse_<monster>        # also corpse_bones and corpse_bones_big, once
python tools/make_corpse_sheets.py                # decay steps + ART_FOR_JAY/corpses_sheet.png (plain grey)
```

The sheet shows each monster standing, then its three steps, at 2x on plain grey. Look at each row and ask: could I
name the monster from its body alone? Is step 2 clearly the same body, older? Is step 3 small and quiet?

### Installing (after approval; roadmap task N7)

Corpses are items, not outfits. Plan: for each approved monster take one Tibia corpse chain that no Spirebound
monster or map uses, reskin those item ids in the client with our three steps (steps 1 and 2 of Tibia's four-item
chain both show our fresh body), rename them through `data/item_renames.json` ("dead ridge cat"), and point the
monster's `corpse=` at the first item. Same install path as the creature looks (`tools/install_effects.py`).

## The audit (2026-11-26)

| Monster | Look | Old corpse | Now |
|---|---|---|---|
| Bristle Boar, Bramblejaw, Old Bristleback | 119 (our boar) | dead crocodile | dead boar 12321 |
| Old Tusk | 2311 (boar) | dead crocodile | dead boar 12321 (own art drafted) |
| Burrow Mole | 26 (our mole) | dead crocodile | dead mole 27646 |
| Meadow Wasp | 44 (our wasp) | dead rat | dead wasp 5989 |
| Reed Snapper, Mossback Snapper | 112 (our snapping turtle) | dead toad | dead thornback tortoise 6073 |
| Thornsnap, Blackthorn | 28 (our snapping plant) | dead snake (holds no loot) | dead carniphila 6047 |
| Briar Mother | 2313 (plant) | dead snake | dead carniphila 6047 (own art drafted) |
| Sproutling | 19 (our walking plant) | poison gas (holds no loot) | dead swampling 17622 |
| Field Shardling, Prism Shardling | 122 (our crystal) | dead bat | dead crystal golem 16177 |
| Ruin Sentinel, Granite Warden | 2204 (stone guardian) | dead black knight | split stone golem 6005 |
| Ruin Archer | 2203 (skeleton) | dead hunter | slain skeleton 5963 |
| Stonehorn Ram | 607 (our ram) | dead moohtant | dead sheep 5994 |
| Black Crawler | 2301 (cave beetle) | dead rat | dead lancer beetle 10458 |
| Vault Wraith | 2324 (wraith) | dead assassin | slain betrayed wraith 6315 |
| The Underkeeper | 2323 (skeletal jailer) | dead black knight | slain skeleton 5972 |
| Hollowfang | 2312 (wolf) | dead wolf (winter) | dead war wolf 6009 |
| Blight Wasp (F2) | 2302 | (rotation) | dead waspoid 13983 |
| Ridge Cat (F2) | 2303 | (rotation) | dead lion 5986 |
| Herd Bull, Stonehide Bull (F2) | 2304, 2305 | (rotation) | dead water buffalo 17422 |
| Horned Grazer (F2) | 2306 | (rotation) | dead rhindeer 42230 |
| Dust Strider (F2) | 2307 | (rotation) | dead draptor 12329 |
| Hill Cutthroat (F2) | 2210 | (rotation) | dead bandit 18050 |
| Floors 2-10 placeholders on looks 119/122/28/19/61/607 | | crocodile, bat, snake, goblin, gas, moohtant | boar, crystal golem, carniphila, swampling, slain demon, sheep |

Already right and unchanged: the rats (dead rat), toads and the Drain Matron (dead toad), wolves and Moonhowl, the
Grey Alpha (winter wolf), the bandits (dead bandit), the Gate Hound (dead hellhound), the Axe-Lord and the armoured
Underkeep guards (dead black knight), the Trap Mimic (dead tortoise), the Iron Shade (dead hunter).

Known leftover (not opened yet): some Floors 3-10 placeholders have more loot rows than their corpse holds (K2);
fix when those floors get their own monsters.
