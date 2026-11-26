# Art count: borrowed sprites a player can see on Floors 1 to 3 (roadmap N4)

Counted 2026-11-25 from the game as it stands on GitHub (commit d7b3b437). The map, monster files, NPC list and
item tables were read by `tools/art_count.py` (rerun it any time to refresh these numbers); nothing in the game
was changed. Monsters the Step 2 session is adding today
(for example the Granite Warden) are not in this count yet.

**"Ours"** = art Jay has approved from the Blender pipeline (`art/APPROVED.txt`), or our own spell effects.
**"Borrowed"** = everything else a player sees: Tibia's art, standing in until ours exists.

## The table

| Kind | Looks seen on Floors 1-3 | Ours now | Borrowed now | Still to make | Hours to make (Claude) |
|---|---|---|---|---|---|
| Monsters (incl. elites and bosses) | 65 kinds | 14 have their own approved sprite | 51 | 40 new bodies + 11 variants | ~32 |
| NPCs | 47 | 0 in the game (9 approved, waiting for look numbers) | 47 | 38 | ~20 |
| Player outfits and mounts | ~11 outfits x 2 (male/female), 2 shop outfits, 1 mount | 0 in the game (4 class outfits approved, need a second pass) | all | ~10 outfits + 1 mount | ~21 |
| Items (gear, loot, food, potions, kits) | 142 | 0 | 142 | 142 | ~28 (Jay's Grok time, or Claude stills) |
| Walls, doors, roofs, windows | 79 | 0 | 79 | 79 | ~26 |
| Ground (grass, roads, floors, water, edges) | 42 | 0 | 42 | 42 | ~10 |
| Map objects (trees, rocks, furniture, signs, lamps) | 186 | 0 | 186 | 186 | ~62 |
| Effects (hits, spells, missiles) | ~104 Tibia effects named in the scripts, plus our 18 | 18 spell effects | ~104 (upper bound: a few are only used on later floors) | ~70-104 | ~26 |
| Interface (windows, buttons, icons, bars) | ~250 pieces a player actually sees (of ~2,070 image files in the client) | 4 | ~250 | see note | ~40, only if we replace it |
| **Total** | **~950 looks** | **~36** | **~900** | | **~265 hours** |

About 265 hours is roughly 65 long work sessions. Jay's own time on top: reviewing each creature sheet (a few
minutes each) and, if items stay on the Grok route, pasting about 140 prompts.

### How many 32x32 pieces that is (for the map and items)
The client draws everything from 32x32 pieces. For the non-moving art on Floors 1-3:
ground 228 pieces, walls 127, map objects 562, items 314: **about 1,230 pieces**. Creatures and outfits are made as
whole animated sheets by the Blender pipeline, so they are counted by look above, not by piece.

## What sits behind each line

**Monsters (65 kinds: 45 on Floor 1, 10 on Floor 2, 10 on Floor 3).**
- 14 show their own approved sprite: Field Rat, Pen Rat, Bristle Boar, Burrow Mole, Hopper Toad, Meadow Wasp,
  Mossback Snapper, Reed Snapper, Thornsnap, Field Shardling, Meadow Wolf, Grey Alpha, Stonehorn Ram, Sproutling.
- 11 are variants that wear their cousin's approved sprite (fine for now, each wants a recolour plus a signature
  feature later): Vault Rat, Mire Toad, Moonhowl, Hollowfang, Wolf Companion, Old Tusk, Old Bristleback,
  Bramblejaw, Blackthorn, Briar Mother, Prism Shardling.
- 12 wear one of our sprites but are a different animal, so the look is wrong: Black Crawler (rat), Blight Wasp
  (rat), Drain Matron and Herd Bull (toad), Horned Grazer (wolf), Ridge Cat (alpha), Dust Strider (boar),
  Stonehide Bull (thornsnap), Hill Cutthroat (shardling), Sleeping Trunk (sproutling), Mossback Warden (ram),
  Moss Crawler (the Floor 10 boss's look).
- 28 still wear a Tibia look. Ten of them share one Tibia knight look (the wardens, sentinels, ghoul and the Axe
  Lord), five share the Tibia hunter look (bandits, archer, Iron Shade, Mesa Wyrmling). Drafts already exist for
  the bandit, captain, archer, sentinel and warden, which cover about half of these.

**NPCs (47 on Floors 1-3).** All wear Tibia citizen-style outfits today. Bess, Corwin, the merchant, Pell, Vesper,
the priest, the Registrar, the banker and Veyra are approved; they go in together once NPCs get look numbers of
their own (one server change plus a client update, already noted in ART_REQUESTS.md). The other 38 are mostly
townsfolk on the shared human body, so each is about half a creature's work.

**Player outfits.** New players pick from Canary's standard free outfit list (about 11, each male and female),
all Tibia's. The two shop outfits and the Stone Hound mount use placeholder looks. Our four class outfits are
approved but need the second pass noted in ART_REQUESTS.md before they go in. A smaller list of our own
(4 class outfits, 2 shop outfits, a few starter looks) is enough for launch.

**Items (142).** Every item a player can loot, buy, wear or carry on Floors 1-3: weapons and armour bases for the
gear tables, potions, food, crafting materials, house kits, coins, bags. 15 of them also lie on the map.

**Walls, ground, map objects.** Read straight from the generated map: 318 different item ids on Floor 1, 73 on
Floor 2, 50 on Floor 3. Walls include every wall family's posts, corners, doors, windows and roofs. Ground includes
the shore and grass edges `Map.edge_grounds` adds. Each new ground or wall family has to tile seamlessly in every
direction, which is why these cost more per piece than an item icon.

**Effects.** Our 18 spell effects (made by `art/effects/make_fx.py`) already replace the player spells. Monster
attacks, hit sparks, blood, arrows and teleports still use Tibia's: about 78 effects and 27 missiles are named
across the scripts. These are quick to make with the same effect maker.

**Interface.** The client's windows, buttons and bars come with OTClient (the open-source client we use), not from
Tibia's sprite files, so they are a lower risk than everything above. Some icons in it do copy Tibia's look
(status icons, skulls, inventory slot outlines). Before a public launch, check those few and replace them; the
plain window skin can likely stay. The hours above are only if we replace the whole interface.

## How the hours were worked out
- Creatures: 6-8 approved models a long session so far (ART_REQUESTS.md) = about 0.6 hours a model; bosses
  (64x64) about 1.5 hours; variants about 0.25 hours; humanoid NPCs about 0.5 hours.
- Outfits: about 2 hours each (four directions, walking, addons, male and female).
- Items: about 12 minutes each, whether by Grok or a Claude still render.
- Ground about 15 minutes a piece, walls about 20, map objects about 20 (many are 2x2 or bigger), effects about 15.
- These are first estimates. The first floor's worth of tiles will tell us the real pace.

## Q21 recommendation (also in QUESTIONS.md)
Mix the two. Keep making everything that moves ourselves (monsters, NPCs, outfits, mounts) with the Blender
pipeline, and the effects with our effect maker: that is where Spirebound's look lives, and it is about 100 of
the 265 hours. For the still world (ground, walls, map objects, about 300 looks and about 100 hours) start from
the one open-licence Tibia-style pack that exists, the OpenTibia Sprite Pack (Creative Commons Attribution 4.0:
free to use if we credit the artists). It is small (about 7,700 pieces against Tibia's 150,000) and not updated
for years, so it will not cover everything, but Floors 1-3 only need about 1,200 pieces. First step: check which
of our 300 map looks it covers, then make the gaps ourselves in a style that matches it.
