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

## Part 2 — own corpse art, only where Tibia has nothing that fits

Jay, 2026-11-26: "corpses that already exist in tibia do not need to be re-drawn for a custom corpse. simple use
what tibia has already created. but for monster that dont have anything that would work, our custom golems for
example, would need their own corpse art drawn." So the order is:

1. **Use a Tibia corpse** whenever one fits what the monster looks like (Part 1). Our own-art bandits, cats, bulls,
   antelopes, lizards, boars, wolves, beetles, wasps, the skeleton archer and the briar plant all have one.
2. **Draw our own** only when nothing fits. Today: the Ruin Sentinel / Granite Warden (our stone golem), the
   Underkeeper (a caged-skull jailer in a robe, with lantern and chain) and the Vault Wraith (a hooded purple spirit:
   Tibia's "betrayed wraith" corpse is an armoured knight). Later floors' golems and constructs will join them.

### What Tibia's corpses look like (studied 2026-11-26 from the client: boar, wolf, lion, deer, buffalo, bandit,
### human, black knight, wasp, beetle, carniphila, stone golem, skeleton, hellhound, draptor)

- **C1 Never the living sprite turned over.** Jay rejected the first draft for exactly that ("it looks like you just
  rotated the living body and slightly recolor'd"). A corpse is a new pose of the same creature, in the same
  camera view and at the same size as the living sprite, usually facing left.
- **C2 Animals slump.** The chest and belly sink to the ground, the legs buckle under and splay out, the head drops
  to the ground with the mouth open, the tail lies limp. People collapse onto their knees and hands, head down.
  (`mode="slump"` in `art/pipeline/corpse_kit.py` does the animal pose, for a future animal with no Tibia match.)
- **C3 Blood.** Red gashes on the flank and a small pool by the head, deep red with a brighter wet line, never
  orange (`wounds()` and `pool()` in `tools/make_corpse_sheets.py`).
- **C4 Four items, three looks.** Tibia's chain is a 10-second item and a 300-second item that look the same (the
  fresh body), then an older look, then the last remains. Flesh: rotting (duller, darker, wounds opened, ribs
  showing through), then the skeleton in the same pose, skull still recognisable (the buffalo keeps its horns).
- **C5 Things without flesh break apart.** A stone golem becomes a spread of its own stone chunks over its tile and
  the ones up-left of it, fewer at each step. Insects burst or snap, with bits scattered; plants collapse into a
  heap of torn leaves. Spirits leave what they wore.
- **C6 Dead means no glow.** Glowing eyes, visors and lanterns go dark after the fresh step.

### How ours are made

- **C7 Shatter** (`mode="shatter"`): the approved model falls apart where it stood. Every solid piece lands on the
  ground, thrown up-left by its height plus a random spread (`fall`, `scatter`), long pieces lying flat; cloth
  (robe, hood, shroud) sinks into a flat crumpled heap where it hung, and parts hidden under it (`soft=`) sink
  with it. Steps 2 and 3 keep fewer pieces (`keep`); things that should vanish with the creature are `hide=`n
  (the wraith's claws, its gold).
- **C8 The model is reused untouched** (two-line file `art/models/corpse_<monster>.py`), so colours and parts
  match the living monster. Each corpse sits against its tile's right and bottom edges like the animals.
- **C9 Look before showing.** Put the three steps beside Tibia's own corpse of the closest kind
  (`.local/corpseref/`, local only, never shipped) and ask: is it a new pose, not the living sprite? Does each
  step read older than the last? Could you name the monster from the remains?
- **C10 Approval first.** Corpse art goes in the game only after Jay approves the sheet in writing (quote in
  `art/APPROVED.txt`). Until then the monster keeps the closest Tibia corpse from Part 1.

### Make and check

```bash
sh art/pipeline/render.sh corpse_<monster>        # frames 0-2 = the three steps
python tools/make_corpse_sheets.py                # item/1_fresh, 2_rot, 3_end + ART_FOR_JAY/corpses_sheet.png
```

### Installing (roadmap task N7, built 2026-11-26)

Corpses are items, not outfits. Each approved corpse reskins one Tibia corpse chain that no Spirebound monster or
map uses (four items: fresh 10 s, 300 s, 300 s, 60 s; the first a container big enough for the loot):

| Corpse | Chain (was) | Name in game | Monsters |
|---|---|---|---|
| corpse_sentinel | 13865-13868 (dead crawler) | broken stone guardian | Ruin Sentinel, Granite Warden |
| corpse_underkeeper | 12340, 12337-12339 (dead midnight panther) | fallen underkeeper | The Underkeeper |
| corpse_vault_wraith | 10430-10433 (dead terramite) | faded vault wraith | Vault Wraith |

- `CORPSE_ITEMS` in `tools/make_creature_sheets.py` packs the three steps into one sheet per corpse (items 1 and 2
  show the fresh step, item 3 the older one, item 4 the last remains) and lists the items in `creatures.json`.
- `tools/install_effects.py` redraws those items in the client at every start (`reskin_object`); `check` confirms
  each item shows our sprite. The server keeps the chain's decay times and containers from items.xml.
- The names come from `tools/gen_gear.py` (written to `data/item_renames.json`, applied by `tools/build_server.py`).
- The monster's `corpse=` in `tools/gen_monsters.py` is the first item of its chain.
- A new corpse: add its chain to `CORPSE_ITEMS`, its names to `gen_gear.py`, its `corpse=`; check the chain is unused
  (`grep -rw <id> server/data-spirebound tools maps data`).

## The audit (2026-11-26)

| Monster | Look | Old corpse | Now |
|---|---|---|---|
| Bristle Boar, Bramblejaw, Old Bristleback | 119 (our boar) | dead crocodile | dead boar 12321 |
| Old Tusk | 2311 (boar) | dead crocodile | dead boar 12321 |
| Burrow Mole | 26 (our mole) | dead crocodile | dead mole 27646 |
| Meadow Wasp | 44 (our wasp) | dead rat | dead wasp 5989 |
| Reed Snapper, Mossback Snapper | 112 (our snapping turtle) | dead toad | dead thornback tortoise 6073 |
| Thornsnap, Blackthorn | 28 (our snapping plant) | dead snake (holds no loot) | dead carniphila 6047 |
| Briar Mother | 2313 (plant) | dead snake | dead carniphila 6047 |
| Sproutling | 19 (our walking plant) | poison gas (holds no loot) | dead swampling 17622 |
| Field Shardling, Prism Shardling | 122 (our crystal) | dead bat | dead crystal golem 16177 |
| Ruin Sentinel, Granite Warden | 2204 (stone guardian) | dead black knight | our broken stone guardian 13865 |
| Ruin Archer | 2203 (skeleton) | dead hunter | slain skeleton 5963 |
| Stonehorn Ram | 607 (our ram) | dead moohtant | dead sheep 5994 |
| Black Crawler | 2301 (cave beetle) | dead rat | dead lancer beetle 10458 |
| Vault Wraith | 2324 (wraith) | dead assassin | our faded vault wraith 10430 |
| The Underkeeper | 2323 (skeletal jailer) | dead black knight | our fallen underkeeper 12340 |
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
