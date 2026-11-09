# Art requests (for Jay + Grok's pixel-art generator)

Base Tibia sprites stand in for all of these until your art arrives, so nothing here blocks the build. Make them in any order; the "Priority" column says what's most visible.

## How to use this file
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
| [ ] | `outfit_vanguard_{s,e,n,w}_{0,1,2}.png` | 32×32, 12 | A sturdy armored sword knight in steel plate with a blue tabard and a kite shield, short cape, helmetless with short hair. Walking cycle, 4 directions. |
| [ ] | `outfit_ranger_{s,e,n,w}_{0,1,2}.png` | 32×32, 12 | A nimble ranger in green leather and a hooded cloak, quiver on the back, bracers. Walking cycle, 4 directions. |
| [ ] | `outfit_arcanist_{s,e,n,w}_{0,1,2}.png` | 32×32, 12 | A battle mage in deep red robes with gold trim and a high collar, glowing runes on the sleeves. Walking cycle, 4 directions. |
| [ ] | `outfit_mystic_{s,e,n,w}_{0,1,2}.png` | 32×32, 12 | A nature mystic in pale green and white robes, leaf-shaped shoulder pieces, wooden beads. Walking cycle, 4 directions. |
| [ ] | `mon_field_rat_*` | 32×32, 12 | A plump brown field rat with a pink tail, harmless-looking. |
| [ ] | `mon_hopper_toad_*` | 32×32, 12 | A fat green-and-yellow toad with big eyes, mid-hop pose for walking frames. |
| [ ] | `mon_sproutling_*` | 32×32, 12 | A small walking plant creature, a bulb body with two leaf arms and a sprout on its head. |
| [ ] | `mon_bristle_boar_*` | 32×32, 12 | A wild boar with dark bristly fur, short tusks, angry red eyes. |
| [ ] | `mon_meadow_wolf_*` | 32×32, 12 | A lean grey-brown wolf with a pale belly. |
| [ ] | `mon_grey_alpha_*` | 32×32, 12 | A bigger silver-grey wolf with a scarred face and a darker mane (elite version of the wolf). |
| [ ] | `mon_field_shardling_*` | 32×32, 12 | A small creature made of floating pale-blue crystal shards around a glowing core. |
| [ ] | `mon_road_bandit_*` | 32×32, 12 | A human bandit with a brown hood, a face scarf and a short sword. |
| [ ] | `mon_bandit_captain_*` | 32×32, 12 | A bandit leader with a red sash, a feathered hat and a curved sabre. |
| [ ] | `mon_thornsnap_*` | 32×32, 12 | A snapping plant with a thorny jaw-like flower head on a crawling vine body. |
| [ ] | `mon_ruin_sentinel_*` | 32×32, 12 | An old animated stone guard statue, cracked and mossy, holding a stone spear. |
| [ ] | `mon_ruin_archer_*` | 32×32, 12 | A skeletal archer in rotted leather with a bow. |
| [ ] | `mon_stonehorn_ram_*` | 32×32, 12 | A mountain ram with huge curled stone-grey horns and thick wool. |
| [ ] | `boss_gate_hound_*` | **64×64**, 12 | A huge three-headed hound with black fur and ember-orange eyes, spiked collar on each neck. |
| [ ] | `boss_axe_lord_*` | **64×64**, 12 | A towering armored warlord in rusted bronze plate with a horned helm and a giant double-bladed axe. |
| [ ] | `boss_axe_lord_blade_*` | **64×64**, 12 | The same warlord (rusted bronze plate, horned helm) now holding a long curved blade instead of the axe, battle-damaged armor. |
| [ ] | `npc_registrar.png`, `npc_priest.png`, `npc_vesper.png`, `npc_banker.png`, `npc_merchant.png` | 32×32, 1 frame each (facing south) | Town NPCs: a clerk with a ledger; a temple priest in white; a sly information broker in a dark purple coat with a feathered hat and a small notebook; a banker with spectacles; a merchant with an apron. |

## Batch 1b — added overnight 2026-11-08 (Priority: medium)

| ✓ | File names | Size / frames | Grok prompt (after the style lock) |
|---|---|---|---|
| [ ] | `mon_old_tusk_*` | 32×32, 12 | A huge old wild boar with one broken tusk, grey-streaked bristles and scars, angry and battle-worn (secret mini-boss). |
| [ ] | `npc_bounty_warden.png`, `npc_guildwarden.png`, `npc_quartermaster.png` | 32×32, 1 frame each (facing south) | Town NPCs: a stern bounty warden in a dark red coat with a wanted-poster scroll; a guild official in blue robes holding a banner staff; a quartermaster in a leather apron with a crate of arrows and potions. |
| [ ] | `summon_ember_sprite_*`, `summon_wolf_companion_*` | 32×32, 12 each | A small floating fire spirit with a bright core; a loyal grey wolf with a green leaf collar (friendly spell summons). |

## Batch 2 — UI (Priority: high, small)

| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [ ] | `ui_cursor_green.png`, `ui_cursor_orange.png`, `ui_cursor_red.png`, `ui_cursor_black.png` | 16×16, 1 each | A small downward-pointing diamond cursor marker floating above a character, glossy, colored green / orange / red / dark red with black outline. |
| [ ] | `ui_floor_badge.png` | 96×32, 1 | A sleek fantasy UI banner plate for showing "Floor 1" text, dark metal with a thin glowing cyan edge, empty center. |
| [ ] | `ui_skill_frame.png`, `ui_skill_frame_ready.png` | 36×36, 1 each | A square skill-slot frame, dark metal; the "ready" version has a soft cyan glow. |
| [ ] | `ui_difficulty_hardcore.png`, `ui_difficulty_deathgame.png` | 12×12, 1 each | A tiny flame icon; a tiny skull-with-crossed-blade icon. |

## Batch 3 — Sword skill icons (Priority: medium)
24 icons at 32×32, 1 frame each, file names `skill_<name>.png`: arc_slash, riposte_line, fourfold_rend, split_earth, hewing_turn, executioners_drop, bell_ringer, crushing_arc, tremor_blow, quickdraw, pinning_shot, arrow_storm, bolt_lance, ratchet_shot, siege_bolt, skewer, javelin_arc, comet_spear, spark_edge, flame_script, starfall_rite, thorn_edge, frost_script, verdant_burst.
Prompt: *"A square fantasy skill icon showing <one-line description of the move>, bold readable silhouette, glowing effect, dark background."* (Claude will add per-icon descriptions when task 1.14 is built.)

## Batch 4 — Azhrakkar, the Cerulean Ruin (Priority: later, phase 5, but worth starting early)
| ✓ | File names | Size / frames | Grok prompt |
|---|---|---|---|
| [ ] | `boss_azhrakkar_{s,e,n,w}_{0,1,2}.png` | **64×64**, 12 | A giant muscular blue-skinned horned fiend with glowing pale-cyan eyes, dark ridged armor plates on the shoulders, wielding an enormous jagged greatsword taller than itself. Menacing, original design. |
| [ ] | `boss_azhrakkar_attack_{s,e,n,w}_{0,1,2}.png` | **64×64**, 12 | The same blue fiend mid-swing with the enormous greatsword, blue fire trailing the blade. |
| [ ] | `fx_cerulean_sweep_{0..5}.png` | 32×32, 6 | A wide blue-fire sword-sweep slash effect, 6-frame animation, transparent background. |
