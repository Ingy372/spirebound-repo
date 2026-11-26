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
| [ ] | `boss_gate_hound_*` | **64×64**, 12 | A huge three-headed hound with black fur and ember-orange eyes, spiked collar on each neck. |
| [ ] | `boss_axe_lord_*` | **64×64**, 12 | A towering armored warlord in rusted bronze plate with a horned helm and a giant double-bladed axe. |
| [ ] | `boss_axe_lord_blade_*` | **64×64**, 12 | The same warlord (rusted bronze plate, horned helm) now holding a long curved blade instead of the axe, battle-damaged armor. |
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
