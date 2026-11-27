# Art requests

Base Tibia sprites stand in for all of these until the real art arrives, so nothing here blocks the build.

## Who makes what (new workflow, Jay 2026-11-14)
- **Anything that moves or turns** (creatures, NPCs, outfits, mounts): **Claude makes it** with the Blender pipeline (`art/`), then sends Jay the sheet and walk loops to approve. Jay does not need to generate these; their Grok prompts below are kept only as design descriptions. Made so far: 26 approved (see `art/APPROVED.txt`); 13 monsters are already in the game (below).
- **Single still images** (item and spell icons, UI, cursors, concept sketches, shop/website art): **Jay makes them with Grok** using the prompts below.

## In the game now, and the size of the rest (roadmap R22, 2026-11-24)
- **Working end to end:** Jay's approved monster sprites now show in the real client in place of the borrowed Tibia
  looks: rat, boar, mole, toad, wasp, snapper, thornsnap, shardling, wolf, grey alpha, ram, sproutling, Azhrakkar
  (`tools/make_creature_sheets.py`, put in at every start by `tools/install_effects.py`). Elites and minibosses borrow
  their ground's sprite. 18 spell effects were already ours.
- **Next step (needs one server change):** NPCs and player outfits. Many NPCs share one borrowed look today, so each of
  ours needs a new look number of its own, plus the client update in the friends' package at the same time.
  Approved and waiting for this: Bess, Corwin, the merchant, Pell, Vesper, the priest, the Registrar, the banker, Veyra,
  and the four class outfits.
- **2026-11-25 (task 6.5): ready to go in at the next restart.** The 9 approved NPCs and the 4 class outfits now have
  look numbers of their own (2001-2018, `NEW_LOOKS` in `tools/make_creature_sheets.py`; rules in `art/README.md`).
  NPCs wearing them: Vesper, Priest Odran, Registrar Maelis, Banker Tolliver, Merchant Wenna, Innkeeper Bess, Fisher
  Corwin, Guide Pell, Ascendant Veyra. Players get their class's outfit when they pick a class (older characters at
  their next login). Floors 2-10 priests and bankers and the second Hearthgate banker still wear borrowed looks.
- **2026-11-25: the Bounty Warden is redrawn** on the outfit body (`art/models/warden.py`): no hat any more (Vesper owns
  coat + hat), a crossbow on his back, grey beard, wanted poster, manacles. Sent to Jay for approval.
  Approved 2026-11-25 ("it looks good to me"): look 2019, Bounty Warden Cass.
- **2026-11-25: the other seven Floor 1 people redrawn** on the outfit body and sent to Jay together
  (`art/output/floor1_people_preview.png`): Guild Warden (banner staff), Quartermaster (crate of arrows on his back),
  Brannoch (wolf-pelt cap, bow on his back), Road Bandit (round hood, red scarf), Bandit Captain (three-cornered hat,
  sabre), Ruin Archer (skeleton with a bow), Ruin Sentinel (stone guard with a spear). All pass the checker.
  All seven approved 2026-11-25 ("huge improvement on everything. approved"): looks 2020-2022 (NPCs) and 2201-2204
  (monsters).
- **2026-11-25: outfit addons.** Outfits can now have Tibia's addon 1 and addon 2 (overlays, rules A1-A7 in
  `art/OUTFIT_RULES.md`). First pair for Jay's OK: the Vanguard's Crested Helm (addon 1) and Knight's Mantle (addon 2).
  Next: two addons each for the Ranger, Arcanist and Mystic, then quests that give them (roadmap 6.5c).
  Jay approved the Vanguard pair (2026-11-25: "Looks good to me"). Sent for his OK the same night: the Ranger's
  Hawk-Feather Hood and Huntsman's Horn, the Arcanist's Orbiting Runestones and Floating Grimoire, the Mystic's Antler
  Crown and Owl Companion.
  All six approved by Jay (2026-11-25: "Looks great to me"); they go in at the next restart.
- **Still to make:** 8 Floor 1 models in progress (archer, bandit, Brannoch, the captain, guild warden, quartermaster,
  sentinel, warden); about 90 Floors 2-10 monsters (perhaps 60 different bodies once shared bodies are counted) and
  about 45 kinds of NPC. At the pace so far (6-8 approved models a long session, including Jay's review), Floors 2-10
  are roughly 10-12 sessions of art, best done a floor at a time just before each floor opens.

## How to use this file (still images only)
1. Copy a prompt into Grok's pixel-art generator.
2. Save each frame as a PNG with the exact file name shown (one PNG per frame, or one sheet left-to-right in the frame order listed).
3. Drop the PNGs in `assets/incoming/` in the repo folder (Claude picks them up next session) and tick the box.

**Style lock (paste at the start of every prompt):**
> 32x32 pixel art sprite, classic Tibia MMORPG style, top-down 3/4 view facing the camera at an angle, transparent background, 1-pixel dark outline, limited 24-color palette, soft top-left lighting, no text, no border.

**Frames:** Tibia creatures face 4 directions (south, east, north, west). Each direction has 1 standing frame + 2 walking frames = **12 frames** unless stated. Big creatures are 64×64 (shown as 2×2 tiles).

---

## Batch 1 — Floor 1 and the 4 vocations (Priority: high)

| ✓ | File names | Size / frames | Grok prompt (after the style lock) |
|---|---|---|---|
| [~] | `outfit_vanguard_*` (first draft by the pipeline, in ART_FOR_JAY/vanguard; needs a second pass for more armour detail) | 32×32, 12 | A sturdy armored sword knight in steel plate with a blue tabard and a kite shield, short cape, helmetless with short hair. Walking cycle, 4 directions. |
| [~] | `outfit_ranger_*` (first draft by the pipeline, in ART_FOR_JAY/ranger; needs a second pass) | 32×32, 12 | A nimble ranger in green leather and a hooded cloak, quiver on the back, bracers. Walking cycle, 4 directions. |
| [~] | `outfit_arcanist_*` (first draft by the pipeline, in ART_FOR_JAY/arcanist; needs a second pass) | 32×32, 12 | A battle mage in deep red robes with gold trim and a high collar, glowing runes on the sleeves. Walking cycle, 4 directions. |
| [~] | `outfit_mystic_*` (first draft by the pipeline, in ART_FOR_JAY/mystic; needs a second pass) | 32×32, 12 | A nature mystic in pale green and white robes, leaf-shaped shoulder pieces, wooden beads. Walking cycle, 4 directions. |
| [x] | `mon_field_rat_*` (made by the pipeline, approved by Jay 2026-11-14) | 32×32, 12 | A plump brown field rat with a pink tail, harmless-looking. |
| [~] | `mon_hopper_toad_*` (drafted by the pipeline, in ART_FOR_JAY/toad, waiting for Jay's OK) | 32×32, 12 | A fat green-and-yellow toad with big eyes, mid-hop pose for walking frames. |
| [~] | `mon_sproutling_*` (drafted by the pipeline, in ART_FOR_JAY/sproutling, waiting for Jay's OK) | 32×32, 12 | A small walking plant creature, a bulb body with two leaf arms and a sprout on its head. |
| [~] | `mon_bristle_boar_*` (drafted by the pipeline, in ART_FOR_JAY/boar, waiting for Jay's OK) | 32×32, 12 | A wild boar with dark bristly fur, short tusks, angry red eyes. |
| [~] | `mon_meadow_wolf_*` (drafted by the pipeline, in ART_FOR_JAY/wolf, needs another pass: narrow from the front, no pale belly yet) | 32×32, 12 | A lean grey-brown wolf with a pale belly. |
| [~] | `mon_grey_alpha_*` (drafted by the pipeline, in ART_FOR_JAY/alpha, waiting for Jay's OK) | 32×32, 12 | A bigger silver-grey wolf with a scarred face and a darker mane (elite version of the wolf). |
| [~] | `mon_field_shardling_*` (drafted by the pipeline, in ART_FOR_JAY/shardling, waiting for Jay's OK) | 32×32, 12 | A small creature made of floating pale-blue crystal shards around a glowing core. |
| [~] | `mon_road_bandit_*` (drafted by the pipeline, in ART_FOR_JAY/bandit, waiting for Jay's OK) | 32×32, 12 | A human bandit with a brown hood, a face scarf and a short sword. |
| [~] | `mon_bandit_captain_*` (drafted by the pipeline, in ART_FOR_JAY/captain, waiting for Jay's OK) | 32×32, 12 | A bandit leader with a red sash, a feathered hat and a curved sabre. |
| [~] | `mon_thornsnap_*` (drafted by the pipeline, in ART_FOR_JAY/thornsnap, waiting for Jay's OK) | 32×32, 12 | A snapping plant with a thorny jaw-like flower head on a crawling vine body. |
| [~] | `mon_ruin_sentinel_*` (drafted by the pipeline, in ART_FOR_JAY/sentinel, waiting for Jay's OK) | 32×32, 12 | An old animated stone guard statue, cracked and mossy, holding a stone spear. |
| [~] | `mon_ruin_archer_*` (drafted by the pipeline, in ART_FOR_JAY/archer, waiting for Jay's OK) | 32×32, 12 | A skeletal archer in rotted leather with a bow. |
| [~] | `mon_stonehorn_ram_*` (drafted by the pipeline, in ART_FOR_JAY/ram, waiting for Jay's OK) | 32×32, 12 | A mountain ram with huge curled stone-grey horns and thick wool. |
| [x] | `boss_gate_hound_*` (made by the pipeline, approved by Jay 2026-11-25: "The bosses themselves look great") | **64×64**, 12 | A huge three-headed hound with black fur and ember-orange eyes, spiked collar on each neck. |
| [x] | `boss_axe_lord_*` (made by the pipeline, approved by Jay 2026-11-25: "The bosses themselves look great") | **64×64**, 12 | A towering armored warlord in rusted bronze plate with a horned helm and a giant double-bladed axe. |
| [x] | `boss_axe_lord_blade_*` (second draft 2026-11-25, `art/output/axe_lord_blade`: Jay couldn't see the phase change, so now scorched black plate with fire in the cracks, red eyes, a red-hot edge, torn pauldron and short tabard; approved by Jay 2026-11-25: "Yep much better") | **64×64**, 12 | The same warlord (rusted bronze plate, horned helm) now holding a long curved blade instead of the axe, battle-damaged armor. |
| [ ] | `npc_registrar.png` (registrar drafted by the pipeline, in ART_FOR_JAY/registrar, waiting for Jay's OK), `npc_priest.png` (priest drafted by the pipeline, in ART_FOR_JAY/priest, waiting for Jay's OK), `npc_vesper.png` (Vesper: made by the Blender pipeline, `art/output/vesper/`, approved by Jay 2026-11-14: "it looks flawless to me"), `npc_banker.png` (banker drafted by the pipeline, in ART_FOR_JAY/banker, waiting for Jay's OK), `npc_merchant.png` (merchant drafted by the pipeline, in ART_FOR_JAY/merchant, waiting for Jay's OK) | 32×32, 1 frame each (facing south) | Town NPCs: a clerk with a ledger; a temple priest in white; a sly information broker in a dark purple coat with a feathered hat and a small notebook; a banker with spectacles; a merchant with an apron. |

## Batch 1b — added overnight 2026-11-08 (Priority: medium)

| ✓ | File names | Size / frames | Grok prompt (after the style lock) |
|---|---|---|---|
| [ ] | `mon_old_tusk_*` | 32×32, 12 | A huge old wild boar with one broken tusk, grey-streaked bristles and scars, angry and battle-worn (secret mini-boss). |
| [ ] | `npc_bounty_warden.png` (drafted by the pipeline, in ART_FOR_JAY/warden, waiting for Jay's OK), `npc_guildwarden.png` (drafted by the pipeline, in ART_FOR_JAY/guildwarden, waiting for Jay's OK), `npc_quartermaster.png` (drafted by the pipeline, in ART_FOR_JAY/quartermaster, waiting for Jay's OK) | 32×32, 1 frame each (facing south) | Town NPCs: a stern bounty warden in a dark red coat with a wanted-poster scroll; a guild official in blue robes holding a banner staff; a quartermaster in a leather apron with a crate of arrows and potions. |
| [ ] | `mon_mire_toad_*`, `mon_black_crawler_*` | 32×32, 12 each | A bloated dark-green swamp toad dripping slime; a black, many-legged cave crawler with a shiny carapace (Underkeep monsters). |
| [ ] | `summon_ember_sprite_*`, `summon_wolf_companion_*` | 32×32, 12 each | A small floating fire spirit with a bright core; a loyal grey wolf with a green leaf collar (friendly spell summons). |

## Batch 2 — UI (Priority: high, small)

| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [ ] | `ui_cursor_green.png`, `ui_cursor_orange.png`, `ui_cursor_red.png`, `ui_cursor_black.png` | **11×11**, 1 each (the client's skull size) | A small downward-pointing diamond cursor marker floating above a character, glossy, colored green / orange / red / dark red with black outline. |
| [ ] | `ui_floor_badge.png` | 96×32, 1 | A sleek fantasy UI banner plate for showing "Floor 1" text, dark metal with a thin glowing cyan edge, empty center. |
| [ ] | `ui_skill_frame.png`, `ui_skill_frame_ready.png` | 36×36, 1 each | A square skill-slot frame, dark metal; the "ready" version has a soft cyan glow. |
| [ ] | `ui_difficulty_hardcore.png`, `ui_difficulty_deathgame.png` | 12×12, 1 each | A tiny flame icon; a tiny skull-with-crossed-blade icon. |

## Batch 3 — Sword skill icons (Priority: medium)
24 icons at 32×32, 1 frame each, file names `skill_<name>.png`: arc_slash, riposte_line, fourfold_rend, split_earth, hewing_turn, executioners_drop, bell_ringer, crushing_arc, tremor_blow, quickdraw, pinning_shot, arrow_storm, bolt_lance, ratchet_shot, siege_bolt, skewer, javelin_arc, comet_spear, spark_edge, flame_script, starfall_rite, thorn_edge, frost_script, verdant_burst.
Prompt: *"A square fantasy skill icon showing <one-line description of the move>, bold readable silhouette, glowing effect, dark background."* (Claude will add per-icon descriptions when task 1.14 is built.)

## Batch 5 — Spell effects (Priority: medium, added 2026-11-13)
**2026-11-17: made by Claude with the Blender pipeline (art/effects, 18 effects, in the game); ticked rows are done. Only the light arrow is still open.** Every spell already uses the best existing effect, so none of these block anything. Effects are 32×32 per tile, transparent background; "frames" play once, left to right. Design and placeholders: docs/design/spells.md section 6.

| ✓ | File names | Size / frames | Grok prompt (after the style lock) |
|---|---|---|---|
| [x] | `fx_whirlwind_{0..5}.png` | 96×96, 6 | A spinning steel sword arc circling a 3×3 area seen from above, crimson edge glow, motion blur, ring shape with an empty centre. |
| [x] | `fx_skyrend_{0..6}.png` | 32×64, 7 | A tall golden-crimson sword slash coming down onto one tile, bright flash at the bottom on the last frames. |
| [x] | `fx_undying_oath_{0..7}.png` | 32×32, 8 (loop) | A thin golden halo and shield ring circling a character's feet, small sparkles rising. |
| [ ] | `ani_dawn_arrow_{n,ne,e,se,s,sw,w,nw}.png` | 32×32, 1 per direction | A white-gold arrow made of light with a short glowing trail (distance/projectile sprite). |
| [x] | `fx_lightrain_{0..5}.png` | 32×32, 6 | Thin needles of white-gold light falling onto a tile and splashing into small sparks. |
| [x] | `fx_stormcall_{0..5}.png` | 32×64, 6 | A violet lightning bolt striking down onto a tile from a small dark cloud, purple sparks on impact. |
| [x] | `fx_arc_cataclysm_{h,v}_{0..3}.png` | 32×32, 4 per direction | A thick violet lightning beam segment, crackling edges; one horizontal and one vertical version that tile seamlessly. |
| [x] | `fx_thornfield_{0..5}.png` | 32×32, 6 | Green thorny vines bursting up out of the ground and pulling back, a few leaves flying. |
| [x] | `fx_lifeward_{0..7}.png` | 32×32, 8 (loop) | A translucent leaf-green bubble around a character, faint leaf pattern shimmering across it. |

## Batch 4 — Azhrakkar, the Cerulean Ruin (Priority: later, phase 5, but worth starting early)
| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [~] | `boss_azhrakkar_*` (walk: first draft by the pipeline, in ART_FOR_JAY/azhrakkar; attack swing not made yet) | **64×64**, 12 | A giant muscular blue-skinned horned fiend with glowing pale-cyan eyes, dark ridged armor plates on the shoulders, wielding an enormous jagged greatsword taller than itself. Menacing, original design. |
| [ ] | `boss_azhrakkar_attack_{s,e,n,w}_{0,1,2}.png` | **64×64**, 12 | The same blue fiend mid-swing with the enormous greatsword, blue fire trailing the blade. |
| [ ] | `fx_cerulean_sweep_{0..5}.png` | 32×32, 6 | A wide blue-fire sword-sweep slash effect, 6-frame animation, transparent background. |

## Shop placeholders (added 2026-11-10)
The donation shop (closed until launch) uses placeholder looks for 2 outfits (Hearth Cloak, Tower Mantle) and 1 mount (Stone Hound). Grok prompts when we get to launch art: "32x32 pixel-art outfit, Tibia style, 4 directions, 3 walk frames, [description]". No sprites needed for testing.

## Batch 1b — Floor 1 redesign (2026-11-11): new monsters and NPCs (Priority: medium)

| ✓ | File names | Size / frames | Grok prompt (after the style lock) |
|---|---|---|---|
| [~] | `mon_meadow_wasp_*` (drafted by the pipeline, in ART_FOR_JAY/wasp, waiting for Jay's OK) | 32×32, 12 | A large striped wasp the size of a dog, yellow and black, translucent wings, a long stinger. |
| [~] | `mon_burrow_mole_*` (drafted by the pipeline, in ART_FOR_JAY/mole, waiting for Jay's OK) | 32×32, 12 | A stocky grey-brown mole with huge pale digging claws, tiny eyes, a pink nose, a little dirt on its back. |
| [~] | `mon_reed_snapper_*` (drafted by the pipeline, in ART_FOR_JAY/snapper, waiting for Jay's OK) | 32×32, 12 | A big green-brown snapping turtle-crab with a reed-covered shell and a hooked beak, standing in shallow water. |
| [~] | `npc_ascendant_veyra_*` (drafted by the pipeline, in ART_FOR_JAY/veyra, waiting for Jay's OK) | 32×32, 12 | A calm priestess-scholar in white and violet robes with a tall collar and a glowing hand, serene face. |
| [~] | `npc_hunter_brannoch_*` (drafted by the pipeline, in ART_FOR_JAY/brannoch, waiting for Jay's OK) | 32×32, 12 | A weathered hunter in brown leathers with a wolf-pelt mantle, a bow across his back, a scar over one eye. |
| [~] | `npc_innkeeper_bess_*` (drafted by the pipeline, in ART_FOR_JAY/bess, waiting for Jay's OK) | 32×32, 12 | A cheerful round innkeeper in an apron with rolled sleeves, a ladle in one hand, red cheeks. |
| [~] | `npc_fisher_corwin_*` (drafted by the pipeline, in ART_FOR_JAY/corwin, waiting for Jay's OK) | 32×32, 12 | A lean fisher in a patched oilskin coat and a floppy hat, a fishing rod over his shoulder. |
| [~] | `npc_guide_pell_*` (drafted by the pipeline, in ART_FOR_JAY/pell, waiting for Jay's OK) | 32×32, 12 | A friendly young guide in a bright tabard with a satchel and a small pennant on a stick, wide smile. |

## Batch 6 — Gear progression (added 2026-11-23, Priority: medium)
Moving sprites (the mini-bosses) are made by Claude with the Blender pipeline; the still icons below keep a Grok prompt.

| ✓ | File names | Size / frames | Grok prompt / note |
|---|---|---|---|
| [ ] | `mon_hollowfang_*` (pipeline, on `art/models/quadruped.py`) | 32×32, 12 | Hidden mini-boss in Wolf Copse: a huge gaunt wolf, darker and bigger than the Grey Alpha, one torn ear, a ridge of bristling black fur. Compare with Tibia's war wolf. |
| [ ] | `mon_briar_mother_*` (pipeline, crawler rules) | 32×32, 12 | Hidden mini-boss in Thornsnap Hollow: a bloated thornsnap queen, a crown of curled thorns, dark red blooms. Compare with Tibia's carniphila. |
| [ ] | `mon_drowned_warden_*` (pipeline, outfit rules) | 32×32, 12 | Hidden mini-boss under the ruined well: a waterlogged stone knight, moss and weed hanging from rusted plate, green light in the visor. |
| [ ] | `item_hearth_shard_rough.png`, `_cut.png`, `_flawless.png` | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small warm-orange crystal shard; rough = jagged dull chip, cut = clean faceted shard, flawless = glowing gem with a soft halo." |
| [ ] | `item_mastery_respec_scroll.png` | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a rolled parchment tied with a silver ribbon and a blue wax seal showing a branching tree." |

## Batch 7 (2026-11-24): Floor 1 elites (no art needed yet)
Five rare elites now borrow their ground's monster sprite and glow (a coloured light): Old Bristleback (boar), Moonhowl
(wolf), Mossback Snapper, Blackthorn (thornsnap), Prism Shardling, and (2026-11-25) the Granite Warden on the Old
Quarry's Upper Cut (a grey-gold Ruin Sentinel outfit). Later, each could get a variant of its base creature
from the Blender pipeline (a scarred hide, a mossy shell, a darker thorn crown, a prismatic crystal, a cracked granite
shield) so players spot them at a glance. Not needed for the alpha.
**2026-11-26: all six drafted with the Blender pipeline, waiting for Jay** (`art/output/floor1_elites_preview.png`,
normal monster on the left, elite on the right; all pass the checker):
- `moonhowl`: moon-white wolf, midnight-blue saddle and tail tip, gold crescent on the brow, head held high.
- `bristleback` (Old Bristleback): a dark bark-olive boar with a mantle of long quills tipped bone-white, long curled tusks, amber eyes.
- `mossback` (Mossback Snapper): the snapper's shell buried under bright moss with two orange toadstools, olive skin, red eyes.
- `blackthorn`: an ink-black thornsnap with a blood-dark thorn crown, black barbs and a poison-green throat.
- `prism_shardling`: bigger, six shards in six rainbow colours round a pearl-blue core, plus a ring of white chips.
- `granite_warden`: the Ruin Sentinel in pink-grey granite with gold trim, ochre lichen, amber eyes and a cracked granite tower shield.

**Jay, 2026-11-26:** "love it all. but i think old bristleback should be the common npc and the darker with red top boar
npc should be the elite. upgrade the darker and red boar just a little more if possible. everything else is approved."
So: the quill boar (`bristleback`) is now the common **Bristle Boar**; the charcoal boar with the ember crest becomes
**Old Bristleback**, redrawn a little grander as `old_bristleback` (approved). Moonhowl, Mossback Snapper,
Blackthorn, Prism Shardling and the Granite Warden are approved.
In the game (next restart): the Bristle Boar wears the quill boar (look 119); the elites have looks of their own:
Moonhowl 2330, Old Bristleback 2331 (the upgraded ember-crested boar, approved), Mossback Snapper 2332, Blackthorn 2333,
Prism Shardling 2334, Granite Warden 2335. Preview of the swap: `art/output/boar_swap_preview.png`.

## Batch 7b (2026-11-25): two bandits for the group grounds (Priority: low, placeholders work)
The Smugglers' Cellar and the Old Watchtower now hold mixed packs (DESIGN.md 9.4: a front-liner, a ranged one and a
caster). Two new monsters borrow outfits for now: the **Bandit Crossbowman** (bandit outfit in green and brown, shoots
bolts from range) and the **Hedge Hexer** (a hooded woman in moss colours who casts earth magic and mends hurt allies;
players should learn to kill her first). For the Blender pipeline later (art/OUTFIT_RULES.md, humanoid base): a
crossbow held at the hip, a leather hood with a bolt quiver; the hexer with a bundle of herbs and a crooked staff, a
green glow when she mends.

## Batch 8 (2026-11-24): the Proving (Priority: low, placeholders work)
Made by Claude with the Blender pipeline when the art queue reaches them; until then they borrow stock looks.
- **Bramblejaw** (creature, the Proving's one-person boss): an old, scarred yard boar with brambles tangled in its bristles and a torn ear; bigger and shaggier than the Bristle Boar so it reads as "boss". Closest Tibia look-alike: Boar / War Boar (make ours obviously different: bramble-green and rust colours, the bramble tangle as the signature). Now: Bristle Boar's placeholder look (119).
- **Warden Ketta** (NPC): a stern trainer in a padded gambeson with a staff, keeper of the Proving. Now: a stock outfit (139).

## Batch 9 (2026-11-25): market-research features (Priority: low, placeholders work)
| Done | File | Size, frames | What it is / Grok prompt |
|---|---|---|---|
| [ ] | `item_beacon_ember.png` | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a glowing ember the size of a walnut, orange-red core, small flickering flame on top, soot-dark edges." Now: Tibia's fiery heart. |
| [ ] | `deco_beacon_bowl_unlit.png`, `_lit.png` | 32×32, 1 (lit: 4 frames) | "32x32 pixel-art, Tibia style, transparent background: a waist-high bronze fire bowl on three legs; unlit = cold ash; lit = tall golden flame." Now: Tibia's fire bowl. |
| [ ] | `item_chronicle_cup.png` | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small golden cup engraved with a tower climbing into clouds, a blue ribbon around the stem." Now: Tibia's golden goblet. |
| [ ] | `deco_arena_champion_statue.png` | 32×64, 1 | "Tibia-style pixel-art statue, transparent background, 32x64: a marble warrior on a plinth raising a sword, a laurel at the feet, a blank name plate on the plinth." The Arena MVP's statue in the Hearth Square. Now: Tibia's plain statue (2025). |

## Batch 10 (2026-11-25): login screen (Priority: low, the stock picture works)
| Done | File | Size, frames | What it is / Grok prompt |
|---|---|---|---|
| [ ] | `client/images/background.png` | 1920×1080, 1 | "Fantasy painting, wide 16:9 game login background: a colossal stone spire rising from green plains into the clouds, ten faint rings of light around it (one per floor), a walled town with timber houses at its foot, a stone road and a small band of adventurers (a knight, an archer, a mage, a healer) seen from behind walking toward it, warm morning light, painterly but crisp, no text, keep the bottom fifth calm and darker so a title can sit there." Now: OTClient's stock picture (the title says Spirebound since G5). |

## Batch 12 (2026-11-26): Waycrystals, one per floor (Priority: medium; placeholders work)
Jay's teleport crystals (DESIGN.md 3.7). Ten still icons of the SAME crystal in ten colours, each with its floor number, so a player can tell them apart in a backpack. Until they are drawn the game borrows base-game orbs and crystals (item numbers below; `tools/crystals.py`).

| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [ ] | `item_waycrystal_f1.png` (now item 3251) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized warm amber-orange crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 1 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f2.png` (now item 11454) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized leaf green crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 2 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f3.png` (now item 9240) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized bright sky blue crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 3 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f4.png` (now item 5944) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized deep violet crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 4 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f5.png` (now item 8225) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized blood red crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 5 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f6.png` (now item 9102) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized icy cyan crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 6 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f7.png` (now item 9697) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized soft rose pink crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 7 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f8.png` (now item 942) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized pale silver-white crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 8 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f9.png` (now item 9237) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized glossy black with a faint purple glint crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 9 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |
| [ ] | `item_waycrystal_f10.png` (now item 7281) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small hand-sized deep cerulean blue with a sapphire core crystal, a long hexagonal prism with a pointed tip, set in a simple pewter cap with a ring, a tiny engraved number 10 on the cap, a soft glow of the same colour. Same shape for all ten floors, only the colour and the number change." |

## Batch 13 (2026-11-26): small game and the Underkeep mini-boss (Priority: low; placeholders work)
Moving creatures: Claude makes them with the Blender pipeline (`art/`), compared with the closest Tibia creature as the monster art rules say; the notes are design descriptions.

| ✓ | File names | Size / frames | Note |
|---|---|---|---|
| [ ] | `mon_meadow_hare_*` (pipeline, quadruped) | 32×32, 12 | Small game: a sandy-grey hare with long black-tipped ears and a white tail, always about to bolt. Compare with Tibia's rabbit. |
| [ ] | `mon_dapple_fawn_*` (pipeline, quadruped) | 32×32, 12 | Small game: a slim russet fawn with white dapples along its back and a startled look. Compare with Tibia's deer. |
| [ ] | `mon_thistle_hen_*` (pipeline, crawler rules) | 32×32, 12 | Small game: a speckled brown hen with a purple thistle-tuft crest. Compare with Tibia's chicken. |
| [ ] | `mon_acorn_squirrel_*` (pipeline, quadruped) | 32×32, 12 | Small game: a red squirrel with a huge bushy tail, an acorn in its paws. Compare with Tibia's squirrel. |
| [ ] | `mon_sluice_warden_*` (pipeline, crawler rules) | 64×64, 12 | Underkeep Wing 1 mini-boss: a bloated grey-green sluice toad wearing a rusted iron sluice gate as a collar, water dripping from its jaws. Compare with Tibia's swamp troll / toad: ours is armoured and much bigger. |

## Batch 11 (2026-11-25): money monsters for the website banner (Priority: with each monster)
Jay: the website banner is reserved for "monsters that vets will look forward to running into once in the game. Bosses, the fire boar, and a few others that haven't been made yet." Each walks across the banner as soon as its art is approved (`SHOWCASE` in `tools/gen_site.py`; pictures by `tools/site_art.py`). On the banner now: Azhrakkar, the Bristle Boar and the Grey Alpha.
Shown at true size, never blown up (Jay: "the monsters look a bit bad blown up like that"). A larger website render from the Blender model comes with roadmap N6.

| ✓ | Art name | What | Status |
|---|---|---|---|
| [x] | `azhrakkar` | Floor 10 boss | approved |
| [x] | `alpha` | Grey Alpha, Floor 1 elite | approved |
| [x] | `boar` | The "fire boar" is our red-crested Bristle Boar (Jay: "It might be named frenzied boar or just regular boar with the red on top") | approved |
| [x] | `gate_hound` | Floor 1 field boss (64x64) | approved |
| [x] | `axe_lord`, `axe_lord_blade` | Axe-Lord of the Stair, Floor 1 boss (64x64), both phases | approved |
| [x] | `underkeeper` | The Underkeeper, boss of the Underkeep: a towering skeletal jailer in a cage-helm with a ghost-teal lantern and a dragging chain and padlock | approved 2026-11-26 |
| [~] | `old_tusk` | Old Tusk, Floor 1 secret boss: the Bristle Boar grown ancient (grizzled, one great tusk, old arrows in his back) | drafted 2026-11-25, waiting for Jay |
| [~] | `hollowfang` | Hollowfang, Floor 1 hidden mini-boss: a night-black wolf with a pale mane and one great fang | drafted 2026-11-25, waiting for Jay |
| [~] | `briar_mother` | Briar Mother, Floor 1 hidden mini-boss: a thorny wine-purple mound with three snapping bud heads and a crown of rose petals | drafted 2026-11-25, waiting for Jay |
| [~] | `old_bristleback` | Old Bristleback, Floor 1 elite: the charcoal boar with the ember crest, a little grander (taller crest with glowing coal tips, ember cheek bristles, heavier tusks) | approved 2026-11-26 |
| [x] | `moonhowl` | Moonhowl, Floor 1 elite: a moon-white wolf with a midnight-blue saddle and a gold crescent on its brow, head high as if about to howl | approved 2026-11-26 |
| [x] | `vault_wraith` | Vault Wraith: a violet hooded wraith chained to a floating gold-banded strongbox, coins circling | approved 2026-11-26 |
| [ ] | `twin_fang_warden` | the Twin Fang trial boss (Floor 8) | not made |


Approved 2026-11-26 (Jay: "Approve all"), own looks in tools/make_creature_sheets.py: vanguard_f, ranger_f, arcanist_m, mystic_m (with addons), watchguard, dorrow, smith, alchemist, runewright, bix, crossbowman, hexer, cutthroat, crawler, blightwasp, ridgecat, bull, stonebull, grazer, strider, old_tusk, hollowfang, briar_mother.

## Batch 14 (2026-11-27): adventure layer, rare weapons and secret keepsakes (Priority: medium; placeholders work)
Still icons only (Grok). Rare weapons need a picture of their own so others can tell them from the ordinary weapon (`tools/gen_gear.py`); secret gear and keepsakes are things players show off. Until drawn, the game borrows the base item shown in brackets.

| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [ ] | `item_briarguard_sabre.png` (now item 3273) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a curved one-handed sabre with a dark green-bronze blade, a guard of twisted briar thorns wrapped around the grip, a single red berry set in the pommel, a faint red glint along the edge." |
| [ ] | `item_copsewood_bow.png` (now item 9378) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a short hunting bow carved from pale silver birch with dark knots, small living leaves still growing at both tips, a green-dyed string, a faint golden shimmer along the limbs." |
| [ ] | `item_wand_of_ember_script.png` (now item 3075) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a slim charred-black wand carved with glowing orange runes along its length, the tip a curl of ember-red light, tiny sparks drifting off it." |
| [ ] | `item_thornward_rod.png` (now item 3070) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a gnarled dark-wood rod wrapped in a spiral of thorny vine, topped with a closed white rosebud that glows softly pale green." |
| [ ] | `item_millrace_boots.png` (now item 3552) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a pair of soft brown leather boots with a blue-grey waterproof sheen, a small brass millwheel buckle on each, and a wet darker band around the soles as if they just ran through a mill stream." |
| [ ] | `item_shrinekeepers_pendant.png` (now item 3014) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a round weathered-stone pendant on a thin silver chain, a tiny shrine arch carved into it, a soft warm white light glowing from inside the arch." |
| [ ] | `item_wardens_signet.png` (now item 3063) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a heavy dark-iron signet ring with a square face engraved with a key crossed over a barred window, a dull blue stone set in the key's bow." |
| [ ] | `item_inn_tankard.png` (now item 2880) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a dented pewter tankard with a hinged lid, a little stamped hammer-and-anvil mark on its side, foam spilling over the rim." |
| [ ] | `item_brass_spyglass.png` (now item 23512) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a short brass spyglass, three telescoping sections, worn leather wrap in the middle, a glint of sky reflected in the lens." |
| [ ] | `item_plains_map.png` (now item 2823) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a half-unrolled parchment map, hand-drawn green plains with a tiny tower in the middle, ink blots, one corner torn, a red string tying the roll." |
| [ ] | `item_message_bottle.png` (now item 5802) | 32×32, 1 | "32x32 pixel-art item icon, Tibia style, transparent background: a small green glass bottle stoppered with a cork and red wax, a rolled-up note visible inside, a strand of river weed caught around its neck." |

## Batch 15 (2026-11-27): adventure layer Session B, rare roamers and treasure (Priority: medium; placeholders work)
Rare roamers (roadmap AD4) are made by Claude with the Blender pipeline; drafts are in `ART_FOR_JAY/` (start with
`RARE_ROAMERS_for_review.png`, plain grey). Until approved, the game shows a placeholder with a coloured glow. The
Frenzied Boar uses our approved red-crested boar.

| ✓ | Art name | What | Status |
|---|---|---|---|
| [x] | `goldback_toad` | Goldback Toad: a bottle-green, nearly black toad with a gold back studded with nuggets, a tiny gold crown and ruby eyes (Tibia's toad is orange-gold) | approved 2026-11-27 ("approved, put them in the game"), in the game |
| [x] | `pale_stag` | Pale Stag: an ash-white stag with a charcoal face, throat ruff and legs, great pale antlers with frost-blue tips (Tibia's deer is small and red-brown) | approved 2026-11-27 ("approved, put them in the game"), in the game |
| [x] | `paymaster` | The Paymaster: the bandits' banker in a black felt hat with a gold band and a green coat, hugging an iron-banded strongbox | approved 2026-11-27 ("approved, put them in the game"), in the game |
| [ ] | `deadeye_sorrel`, `page_thief`, `glasswing`, `ironpurse`, `the_unfinished` | addon-hunt targets and hidden beasts: borrow the crossbowman, hexer, prism shardling, a citizen and the granite warden for now | later |

Still item icons (Grok), 32×32, 1 frame, transparent background. Until drawn, the game borrows the item in brackets.

| ✓ | File name | Grok prompt |
|---|---|---|
| [ ] | `item_tattered_map.png` (now 5706) | "32x32 pixel-art item icon, Tibia style, transparent background: a torn, stained parchment treasure map folded in half, a red X and a dotted path, one corner burnt." |
| [ ] | `item_vault_key.png` (now 9172) | "32x32 pixel-art item icon, Tibia style, transparent background: a heavy black iron key with a round bow shaped like a coin, rust at the teeth." |
| [ ] | `item_stone_rubbing.png` (now 2819, 2833, 4831) | "32x32 pixel-art item icon, Tibia style, transparent background: a small sheet of rough paper with a charcoal rubbing of a carved mason's mark, smudged edges." |
| [ ] | `item_goldbacks_crown.png` (now 5799) | "32x32 pixel-art item icon, Tibia style, transparent background: a tiny three-pointed gold crown with a ruby, sized for a toad, a little dented." |
| [ ] | `item_frenzied_tusk.png` (now 3044) | "32x32 pixel-art item icon, Tibia style, transparent background: a curved ivory boar tusk with a red-black scorch mark at its root, mounted on a small dark wooden plaque." |
| [ ] | `item_pale_antlers.png` (now 12544) | "32x32 pixel-art item icon, Tibia style, transparent background: a pair of white branching stag antlers with frost-blue tips, mounted on a dark wooden shield." |
| [ ] | `item_paymasters_strongbox.png` (now 35571) | "32x32 pixel-art item icon, Tibia style, transparent background: a small dark oak strongbox with brass bands and a brass lock, lid ajar, empty." |
| [ ] | `item_smugglers_lantern.png` (now 10289) | "32x32 pixel-art item icon, Tibia style, transparent background: a shuttered tin signal lantern with a red glass pane, soot on top." |
| [ ] | `item_bandit_banner.png` (now 10415) | "32x32 pixel-art item icon, Tibia style, transparent background: a tattered mud-brown banner on a short pole, a red mask painted on it." |
| [ ] | `item_ruin_idol.png` (now 8146) | "32x32 pixel-art item icon, Tibia style, transparent background: a small weathered grey stone idol of a seated figure with a worn face, lichen in the cracks." |
| [ ] | `item_captains_sea_chest.png` (now 8773) | "32x32 pixel-art item icon, Tibia style, transparent background: a salt-stained blue-grey sea chest with rope handles and iron corners." |
| [ ] | `item_climbers_compass.png` (now 10302) | "32x32 pixel-art item icon, Tibia style, transparent background: an old brass compass whose needle points straight up, a cracked glass face." |
| [ ] | `item_wardwright_tablet.png` (now 28538) | "32x32 pixel-art item icon, Tibia style, transparent background: a small clay tablet covered in neat angular builders' marks, one corner broken off." |

## Batch FD-C (2026-11-27): the First Climb and the Oathroom (Priority: low; placeholders work)
Archivist Maren (an NPC, so she goes through the Blender pipeline, not Grok): an older woman in archive grey with ink-blue
sleeves, spectacles on a cord and a ledger under one arm. Until then she wears a grey citizen outfit.
The Oathkeeper (boss, Blender pipeline): the First Climb's oath-warden, a tall armoured knight in faded blue and bronze
with an unlit lantern on his belt; compare with Tibia's knight-type bosses and make him clearly ours (no helmet crest,
a cracked oath-stone on his chest). Until then a stand-in look is used.

| ✓ | File name | Grok prompt |
|---|---|---|
| [ ] | `item_fc_record_page.png` (now 2815) | "32x32 pixel-art item icon, Tibia style, transparent background: a single yellowed journal page with neat brown handwriting and a torn left edge." |
| [ ] | `item_fc_watch_log.png` (now 2821) | "32x32 pixel-art item icon, Tibia style, transparent background: a thick battered leather log book, its pages swollen, a faded tower stamped on the cover." |
| [ ] | `item_fc_unsent_letter.png` (now 2818) | "32x32 pixel-art item icon, Tibia style, transparent background: a folded letter sealed with dark red wax that was never broken, a soldier's seal of a stair." |
| [ ] | `item_agnas_wreath.png` (now 2981) | "32x32 pixel-art item icon, Tibia style, transparent background: a small round wreath of golden wheat stalks tied with a blue ribbon." |
| [ ] | `item_tams_pendant.png` (now 3039) | "32x32 pixel-art item icon, Tibia style, transparent background: a plain healer's pendant, a smooth green stone on a worn leather cord." |
| [ ] | `item_archive_seal.png` (now 2834) | "32x32 pixel-art item icon, Tibia style, transparent background: a cream certificate with a big ink-blue wax seal showing a quill over a tower." |
| [ ] | `item_oathbound_pack.png` (now 5801) | "32x32 pixel-art item icon, Tibia style, transparent background: a sturdy dark-blue backpack with bronze buckles and a small oath-stone sewn on the flap." |
| [ ] | `object_oath_stone.png` (now stone tile 429) | "32x32 pixel-art floor tile, Tibia style, top-down: a square flagstone with a carved ring and a raised hand in its middle, faint blue in the grooves." |

## Floor 1 depth: ground features, cooking, Town Works (FD2, FD4, FD5; nothing waits on these)
Placeholders work today. Creatures (Blender pipeline): the **Elder Sproutling** (now the sproutling look; a bigger, older
sproutling with a woody trunk and a crown of leaves), the **Nest Queen** (now the wasp look; a long-bodied wasp with a
gold-striped abdomen and torn wings) and the **Bandit Lieutenant** (now the bandit captain look; a red sash and a tin
badge on his chest).

| ✓ | File name | Grok prompt |
|---|---|---|
| [ ] | `object_ratcatcher_bell.png` (now a post 2117) | "32x64 pixel-art object, Tibia style, top-down 3/4 view: a green-bronze hand bell hanging from a short wooden post, rat silhouettes cast into the rim." |
| [ ] | `object_mole_mound.png` (now rock 1787) | "32x32 pixel-art object, Tibia style: a heap of fresh brown earth with a dark round tunnel mouth at its top." |
| [ ] | `object_howling_stone.png` (now stone 4850) | "64x64 pixel-art object, Tibia style: a tall grey standing stone worn into hollows by the wind, faint wolf scratches at its base." |
| [ ] | `object_chime_shard.png` (now crystals 7808-7811) | "32x64 pixel-art object, Tibia style: a tall thin pale crystal shard standing upright, with a soft glow at its tip." |
| [ ] | `object_wanted_poster.png` (now a sign) | "32x32 pixel-art object, Tibia style: a wooden post with a nailed parchment WANTED poster showing a rough bandit sketch." |
| [ ] | `object_signal_brazier.png` (now basin 2113) | "32x32 pixel-art object, Tibia style: a big iron signal brazier on three legs, cold and full of black coals." |
| [ ] | `object_ballista.png` (now 2065) | "64x64 pixel-art object, Tibia style: an old wooden siege ballista on a stone base, a long iron bolt in its groove." |
| [ ] | `object_lily_pad.png` (now 39548 on mud) | "32x32 pixel-art floor tile, Tibia style, top-down: three broad green lily pads with a white night flower on pond water." |
| [ ] | `object_turtle_nest.png` (now 14759) | "32x32 pixel-art object, Tibia style: a shallow scrape in wet sand with four leathery white eggs." |
| [ ] | `item_truffle.png` (now 3728) | "32x32 pixel-art item icon, Tibia style, transparent background: a knobbly black truffle with a little earth on it." |
| [ ] | `item_turtle_egg.png` (now 5678) | "32x32 pixel-art item icon, Tibia style, transparent background: one leathery off-white turtle egg." |
| [ ] | `item_lieutenant_badge.png` (now 9218) | "32x32 pixel-art item icon, Tibia style, transparent background: a dented tin badge shaped like a crossed dagger and key." |
| [ ] | `items_dishes_floor1.png` (13 dishes, now food items) | "A sheet of 13 32x32 pixel-art food icons, Tibia style, transparent background: grilled minnow, smoked perch fillet, seared meat, boar roast, roast truffle, baked turtle egg, carp steak, whiskers fish pie, hunter's roast with truffle, honey-glazed ham, truffle omelette, bramble berry tart, herb-crusted perch." |
| [ ] | `object_works_board.png` (now notice board 2597) | "32x64 pixel-art object, Tibia style: a tall wooden board with a carpenter's plan pinned to it and a coin slot box at its foot." |

## Batch ART-F1 (2026-11-27): Floor 1 creatures that still wore borrowed Tibia looks (art session)
Drawn by Claude with the Blender pipeline; each passes `check_creature.py` and had the DETAIL_RULES pass. Previews (sheet
and 4x walk loops on plain grey) are in `ART_FOR_JAY/<name>/`. Until Jay approves one, the game keeps its placeholder.

| ✓ | Art name | What | Status |
|---|---|---|---|
| [~] | `meadow_hare` | Meadow Hare: a silver-grey hare with a buff wash, very long black-tipped ears with pink insides, a white scut (Tibia's rabbit is plain brown) | drafted, waits for Jay's look |
| [~] | `dapple_fawn` | Dapple Fawn: a small dun-taupe fawn on long legs, a dark spine stripe with rows of cream dapples, big dark-rimmed ears (Tibia's deer is a red-brown grown deer) | drafted, waits for Jay's look |
| [~] | `thistle_hen` | Thistle Hen: a slate-blue ground hen freckled white, a rust breast, a spiky thistle-purple crest, a cocked bronze-black tail (Tibia's chicken is white with a red comb) | drafted, waits for Jay's look |
| [~] | `acorn_squirrel` | Acorn Squirrel: an ash-grey squirrel with a huge dark brush of a tail frosted russet at the end, russet ear tufts and a golden acorn in its mouth (Tibia's is red-brown with a pale tail) | drafted, waits for Jay's look |
| [~] | `nest_queen` | Nest Queen: a big queen wasp, a long honey-gold abdomen with burgundy-black bands, an ivory crown of horn spikes, wings torn into ragged strips, an amber venom drop (her wasps are amber and blue-black; Tibia's is lemon) | drafted, waits for Jay's look |
| [~] | `elder_sproutling` | Elder Sproutling: the sproutling grown old: a sage bulb face with amber eyes under bark brows and a cracked frown, a bark trunk with moss, twig arms with leaf hands, root feet, a crown of dark leaves with pink blossoms | drafted, waits for Jay's look |
| [~] | `bandit_lieutenant` | Bandit Lieutenant: the road bandit's body with a wine-black hood and cape, a mustard officer's scarf, two long knives, crossed knife belts with throwing knives and a bright tin badge (the captain keeps the red sash; Claude's call, Jay can veto) | drafted, waits for Jay's look |
