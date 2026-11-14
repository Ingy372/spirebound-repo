# Spirebound spells: design (2026-11-13 overhaul)

This is the design behind the spell table in `server/data-spirebound/lib/spirebound/spells.lua`. The table is the
source of truth for numbers; this page explains them. Everything here is **(Claude's call, Jay can veto)** except the
rules marked (Jay).

Rules kept from Jay:
- Spells unlock by level on their own, no trainer, no gold (Jay, 2026-11-08).
- Every vocation gets utility and support spells, not only damage (Jay, 2026-11-08).
- Ammunition is never conjured (Jay).
- Rangers and Vanguards have an attack spell at level 8 (Jay's playtest, 2026-11-13).
- Original names and words only. No Tibia spell names or incantations.

---

## 1. Audit: what we had before this overhaul

**Where spells live.** One data table (`lib/spirebound/spells.lua`) and one builder
(`scripts/spirebound/spells.lua`) that turns each row into a Canary "instant" spell. Tibia's own spells are deleted at
build time (`tools/build_server.py`), and the engine's "learn spells first" switch is off. There are no spell NPCs or
spellbooks: `!spells` lists your spells and the "New spell" message appears on level up. Runes (fire, strike,
healing, paralysis) are Canary's own rune scripts; our conjure spells only make them. The client has no spell data of
its own; the sword-skill bar is separate (`client/modules/game_spirebound`).

**Vocations and their Tibia counterparts** (DESIGN.md 5.2):

| Spirebound | Tibia | Weapons | Role |
|---|---|---|---|
| Vanguard (id 4) → Blade Warden | Knight | sword, axe, club + shield | tank, front line |
| Ranger (id 3) → Far Warden | Paladin | bow, crossbow, spear | ranged damage, some healing |
| Arcanist (id 1) → High Arcanist | Sorcerer | wand | area damage, big spells |
| Mystic (id 2) → Elder Mystic | Druid | rod | healer, support, nature damage |

**What each had (54 rows):** 8 shared spells all at the same level for everyone (Kindle, Wayfinder, First Aid,
Cleanse, Skystep, Hearth Ration, Quickstep, Beacon), then Vanguard 12, Ranger 12, Arcanist 11, Mystic 11 of their own
(2 Lost Arts each). Vanguard: Heavy Strike 8, Second Wind 10, Whirlwind 16, Rally Cry 20, Charge 25, Iron Hide 30,
Intimidate 35, Battle Hymn 45, Guardian Stance 50, Bulwark Aura 60, Recovery 70, Iron Will 80. Ranger: Piercing Shot
8, Keen Sight 13, Field Dressing 15, Scatter Shot 16, Tracker's Mark 20, Disengage 25, Swift Foot 30, Snare 35,
Radiant Shot 40, Camouflage 45, Eagle Eye 55, Sanctified Ground 70. Arcanist: Ember Strike 8, Volt Strike 12, Mana
Ward 14, Fireburst Wave 23, Conjure Fire Rune 27, Arc Beam 35, Blink 40, Conjure Strike Rune 45, Summon Ember Sprite
50, Arcane Empower 60. Mystic: Frost Strike 8, Thorn Strike 14, Mend Other 18, Purify 20, Conjure Healing Rune 24,
Barkskin 30, Rejuvenate 35, Mass Mend 36, Entangle 40, Summon Wolf Companion 50.

**Problems found:**
1. **The Vanguard was not the hardest solo class.** Whirlwind (level 16) hit all 8 tiles around you with 70–130% of
   the melee scale on a 4 s cooldown: about as strong as the Ranger's Scatter Shot and close to the Arcanist's wave,
   and it came before either mage's area spell.
2. **No class rhythm.** Every vocation got 8 identical shared spells at identical levels, and all four own lists
   followed the same "one every 5 levels until 50, then stop" pattern. Almost nothing unlocked after level 80 although
   floors run to 400+ and the season has no level cap.
3. **Every spell looked the same.** Nearly all non-attack spells used the same blue or green sparkle
   (`MAGIC_BLUE`/`MAGIC_GREEN`), so you could not tell who cast what.
4. **Conjuring was free.** Conjure spells made runes from nothing, but `tools/gen_economy.py` assumes a blank rune
   (10 gold from the Runewright) per conjure. Mages were richer than ECONOMY.md says.
5. **Vanguard heals scaled with magic level**, which Vanguards barely train, so Second Wind healed ~30 HP at level 30.
6. **Every spell shared a 1 s group cooldown**, so a mage could fire an attack spell and a sword skill back to back
   with almost no gap, and healing and attacks blocked each other the same way.
7. **Arcanist and Mystic had only 10 own spells to level 60**, and the "about 20 per vocation" in DESIGN 5.3b only
   held by counting the shared ones.
8. Placeholders/duplicates: Beacon was a second, bigger Kindle; First Aid duplicated each vocation's own first heal;
   "Entangle" said one thing and did another (it conjured a paralysis rune).
9. Still Tibia-named: the **rune items** our spells make keep Canary's item names (great fireball rune, sudden death
   rune, ultimate healing rune, paralyze rune). Those are item names, not spells; renaming them is a separate task
   (QUESTIONS.md).

**Sword skills and spells, so they don't overlap.** Sword skills (DESIGN 5.3) are free (0 mana), tied to the weapon
in hand, chain into combos (Opener → Link → Finisher) and use a 1 s shared cooldown in the "attack" group. Spells now
cost mana and use Tibia's 2 s attack group cooldown, which **is the same group**: a spell and a sword skill cannot be
fired in the same second, so you weave them. Spells cover what sword skills don't: healing, defense, movement,
party buffs, crowd control, runes, and (for mages) the big elemental areas. Weapon-class attack spells (Vanguard,
Ranger) scale with the weapon skill, like sword skills, but are single big hits or kit tools rather than combo pieces.

## 2. How Tibia does it (what we copy, what we don't)

- **Unlocks are spread out and front-loaded.** In Tibia every vocation gets light, find person, a small heal and
  haste in the first 15 levels; then each vocation's real kit appears in steps. Classic 8.6 knights got their only
  area attack, Berserk, at level 35 and Fierce Berserk at 90, with very little in between; Groundshaker came at 33
  and Brutal Strike at 30 ([TibiaWiki](https://tibia.fandom.com/wiki/Fierce_Berserk), [TibiaWiki Knight](https://tibia.fandom.com/es/wiki/Knight)).
  Sorcerers and druids get strikes and waves in the teens and twenties, beams around 23–38, then the big areas
  around 55–60. Modern Tibia filled the gaps with more mid-level spells, but kept the shape.
- **Why it feels good:** a new tool every few levels, plus a few **power-spike levels** you look forward to (the
  first area spell, the first ultimate). Utility spells sit between the damage spells, so even "quiet" levels give
  you something (haste, levitate, invisibility, runes).
- **Solo difficulty:** knights are the slowest solo levellers because they have almost no area damage and must
  stand in melee; sorcerers and druids are in the middle (strong areas, fragile, mana-hungry); paladins are easiest
  (strong ranged damage, a usable area spell, self-healing, and they can kite).

What we change: Spirebound has no level cap and 20–30 floors per season (floor bands 1–35, 35–60 ... 350–400+), so
unlocks continue to level 200+, and each vocation's curve has its own rhythm instead of sharing one.

## 3. The new system

### 3.1 Unlock curves (one rhythm per vocation)

| Vocation | Shape | Own spells before 30 / 30–100 / after 100 (not counting Lost Arts) | Power-spike levels |
|---|---|---|---|
| **Vanguard** | Slow burn. Few early spells, big gaps, defense first; the late game is where it shines. | 5 / 7 / 3 (+2 Lost Arts) | 33 (Whirlwind), 90 (Skyrend), 200 (Undying Oath) |
| **Ranger** | Steady. Something new every 4–8 levels from 8 to 65, then slower; kiting tools early. | 7 / 8 / 1 (+2) | 16 (Scatter Shot), 45 (Sunburst Volley), 80 (Dawnpiercer) |
| **Arcanist** | Front-loaded glass cannon. Most attacks by 30, then big jumps. | 8 / 8 / 1 (+2) | 18 (Fireburst Wave), 55 (Stormcall), 80 (Inferno Core), 100 (Cinder Lance) |
| **Mystic** | Healer's rhythm. Heals first, party tools in the 30s–60s, damage a step behind the Arcanist. | 7 / 9 / 1 (+2) | 16 (Mend Other), 36 (Mass Mend), 55 (Thornfield), 100 (Verdant Renewal) |

Shared utilities still exist, but **each vocation learns them at its own level** (the Ranger finds people and runs
earlier, the Mystic cleanses and makes food earlier, the Vanguard gets light and haste last).

Lost Arts (★) are never unlocked by level alone: the first needs every story quest on Floor 5 and level 120, the
second every story quest on Floor 8 and level 250 (levels moved from 100/150 to match those floors' bands).

### 3.2 How the kits create Tibia's solo curve

- **Vanguard (hardest solo).** One area attack only, Whirlwind, at level 33: adjacent tiles only, 40–70% of the melee
  scale, 8 s cooldown. Measured as "tiles × average hit ÷ cooldown" it is about **a quarter** of the Ranger's Scatter Shot
  and about **40%** of the Arcanist's Fireburst Wave at the same level (level 40: Whirlwind ≈ 48 damage/s, Mystic
  Frost Wave ≈ 106/s, Arcanist Fireburst ≈ 125/s, Ranger Scatter Shot ≈ 190/s). Its strength is surviving and
  protecting others (Iron Hide, Guardian Stance, Rally Cry, Undying Oath), which pays off in parties, not solo.
  Single-target damage is good (Heavy Strike, Rending Blow, Skyrend), so it can still kill one thing at a time.
- **Arcanist and Mystic (middle).** Strong area spells from 18–21 and big rings from 55, but they are fragile and pay
  mana for everything. The Arcanist hits harder (Inferno Core, Cinder Lance) and has Mana Ward; the Mystic hits
  softer (Frost Wave also slows) but heals itself and others very well.
- **Ranger (easiest solo).** Its attack spells scale with distance skill, which Rangers train fast, so Scatter Shot is
  the strongest early area spell; it heals itself (Field Dressing), and it has the best kiting kit in the game
  (Quickstep at 10, Snare 20, Disengage 24, Swift Foot 32, Camouflage 50) so it rarely has to stand and take hits.
  Its weakness is party value: its buffs are smaller and its heals are single-target.

The in-game test `spells: the Vanguard has one weak area attack...` fails the build if the Vanguard's area spell ever
reaches half the strength of any other vocation's first area spell, or comes earlier.

### 3.3 Visual identity (who cast it, at a glance)

Every spell can use three layers: a **cast** effect on the caster, a **projectile** to the target, and an **impact** on
each tile it hits. Area spells use a real shape (wave, beam, ring, or an area around the target).

| Vocation | Palette | Signature effects (existing Canary effects) |
|---|---|---|
| Vanguard | crimson and gold, steel | red hit (`HITAREA_RED`), slash, gold burst (`OUTBURST_YELLOW`), yellow rings, block sparks, challenge banner (`CHIVALRIOUS_CHALLENGE`), golden empowerment |
| Ranger | daylight white-gold and forest green | sniper arrow / flash arrow / earth arrow projectiles, green hit (`HITAREA_GREEN`), green whirl, holy light (`HOLYDAMAGE`, `HOLYAREA`, `DIVINE_DAZZLE`, `DIVINE_GRENADE`), sparkles, roots |
| Arcanist | ember orange and storm violet | fire projectile + fire hits, orange sparks, purple lightning (`PURPLE_ELECTRIC_SPARK`), purple teleport, storm cloud (`STORM`), explosions |
| Mystic | frost teal and living green | ice projectile + ice hits, ice tornado, giant ice, green star projectile, green rings, plant bursts (`BIGPLANTS`, `PLANTATTACK`), green pulse |

Shared utilities use neutral effects (sparkles, white smoke, teleport) so they never get confused with a vocation.

### 3.4 Groups and cooldowns

- Group cooldowns follow Tibia: **attack 2 s**, **healing 1 s**, **support 2 s**. Attack spells share the attack
  group with sword skills (see section 1).
- Each spell also has its own cooldown (column "CD"). Big spells have long ones so they feel like events.
- Damage/healing: `level/5 + S × a + base` to `level/5 + S × b + 2 × base`, where **S** is the scaling stat:
  **ML** magic level (mages, Ranger heals), **Melee** best of sword/axe/club (Vanguard attacks), **Dist** distance
  skill (Ranger attacks). Vanguard heals use **Lvl**: `level × a + base` to `level × b + 2 × base`. Shown below as
  `S a–b +base`.

## 4. Spell lists

Words are what you say (always the spell name in lower case, without apostrophes). Visuals are cast → projectile →
impact; "—" means that layer is not used.

### 4.1 Shared utilities (each vocation at its own level)

| Spell | Words | A / M / R / V level | Mana | CD | What it does | Visuals |
|---|---|---|---|---|---|---|
| Kindle | kindle | 8 / 8 / 9 / 10 | 20 | 2 s | light radius 7 for 10 minutes | fire sparkles |
| Wayfinder | wayfinder *name* | 10 / 10 / 8 / 8 | 20 | 2 s | direction and distance to a player | blue sparkle |
| Cleanse | cleanse | 12 / 10 / 11 / 12 | 30 | 6 s | removes poison, burning, bleeding, slows etc. from you | white smoke |
| Skystep | skystep up / down | 12 / 12 / 12 / 14 | 50 | 2 s | climb one level where there is a gap | teleport |
| Hearth Ration | hearth ration | 14 / 11 / 14 / 14 | 120 | 2 s | makes a piece of food | green sparkle |
| Quickstep | quickstep | 14 / 14 / 10 / 16 | 60 | 2 s | haste (+30%) for 30 s | white whirl |

### 4.2 Vanguard (17 own, 23 in all): the shield

| Lvl | Spell | Words | Type | Mana | CD (group) | Numbers | Area / range | What it does | Visuals |
|---|---|---|---|---|---|---|---|---|---|
| 8 | Heavy Strike | heavy strike | attack | 20 | 2 s (attack) | Melee 0.8–1.5 +5 | target, melee | hard blow | — → — → red hit |
| 9 | Second Wind | second wind | healing | 30 | 1 s (healing) | Lvl 1.0–1.6 +20 | self | heal | — → — → gold burst |
| 16 | Rending Blow | rending blow | attack | 35 | 6 s (attack) | Melee 0.9–1.6 +5, bleed 5×12% | target, melee | hit plus bleeding | — → — → slash + blood |
| 20 | Rally Cry | rally cry | support | 40 | 4 s (support) | — | radius 3 | taunt: monsters turn on you | challenge banner → — → red shout on each |
| 25 | Charge | charge | utility | 70 | 12 s (support) | — | 3 tiles | dash to your target | bloody steps → — → ground shake |
| 30 | Iron Hide | iron hide | support | 80 | 20 s (support) | 30% less damage, 6 s | self | defensive stance | yellow rings → — → block sparks |
| 33 | Whirlwind | whirlwind | attack | 60 | 8 s (attack) | Melee 0.4–0.7 +5 | 8 tiles around you | the only (weak) area attack | white whirl → — → red hits |
| 40 | Intimidate | intimidate | support | 90 | 16 s (support) | slow 4 s | radius 2 | slows monsters around you | red shout → — → stun |
| 50 | Battle Hymn | battle hymn | support | 150 | 30 s (support) | +10% melee, 2 min | party, radius 5 | party buff | gold burst → — → red sparkle |
| 60 | Guardian Stance | guardian stance | support | 120 | 24 s (support) | adjacent allies −20%, you −10%, 8 s | adjacent | protect allies | yellow rings → — → block sparks |
| 70 | Recovery | recovery | healing | 120 | 2 s (healing) | Lvl 2.0–3.0 +60 | self | strong heal | red sparkle → — → gold burst |
| 90 | Skyrend | skyrend | attack | 160 | 12 s (attack) | Melee 2.2–3.4 +20 | target, melee | the big single hit (power spike) | orange hit → — → explosion + critical |
| 110 | Iron Will | iron will | utility | 80 | 12 s (support) | — | self | break free of slows and paralysis | red sparkle |
| 140 | Bulwark Aura | bulwark aura | support | 200 | 60 s (support) | party −8%, 2 min | party, radius 4 | party armour | yellow rings → — → block sparks |
| 200 | Undying Oath | undying oath | support | 250 | 120 s (support) | 4 s | self | for 4 s nothing can take you below 1 HP | golden empowerment → — → gold burst |
| ★120 | Last Bastion | last bastion | healing | 250 | 60 s (healing) | Lvl 1.6–2.4 +100, ×up to 3 when low | self | heal that grows as HP drops (Floor 5 Lost Art) | golden empowerment → — → gold burst |
| ★250 | Unbroken Line | unbroken line | support | 400 | 90 s (support) | party −15%, 10 s | party, radius 4 | emergency wall (Floor 8 Lost Art) | challenge banner → — → block sparks |

### 4.3 Ranger (18 own, 24 in all): the hunter

| Lvl | Spell | Words | Type | Mana | CD (group) | Numbers | Area / range | What it does | Visuals |
|---|---|---|---|---|---|---|---|---|---|
| 8 | Piercing Shot | piercing shot | attack | 20 | 2 s (attack) | Dist 0.8–1.5 +5 | target, 5 | strong shot | — → sniper arrow → green hit |
| 10 | Field Dressing | field dressing | healing | 40 | 1 s (healing) | ML 1.2–1.9 +15 | you or a named ally | heal | — → small holy → sparkles |
| 13 | Keen Sight | keen sight | utility | 40 | 10 s (support) | — | radius 6 | reveals invisible monsters | white burst → — → blue sparkle |
| 16 | Scatter Shot | scatter shot | attack | 45 | 4 s (attack) | Dist 0.7–1.3 +5 | wave in front | spread of arrows (power spike) | green whirl → — → green hits |
| 20 | Snare | snare | support | 60 | 10 s (support) | root 3 s (players 1 s, slowed) | target, 7 | pins a monster | — → earth arrow → roots |
| 24 | Disengage | disengage | utility | 60 | 12 s (support) | — | 2 tiles | leap away from your target | green whirl → — → poff |
| 28 | Tracker's Mark | trackers mark | support | 60 | 15 s (support) | +10% damage taken, 15 s | target, 7 | party deals more to it | — → flash arrow → red smoke |
| 32 | Swift Foot | swift foot | utility | 100 | 2 s (support) | haste +70%, 22 s | self | strong haste | green whirl |
| 38 | Radiant Shot | radiant shot | attack | 70 | 4 s (attack) | Dist 1.1–1.8 +10, holy | target, 5 | holy shot | — → small holy → holy hit |
| 45 | Sunburst Volley | sunburst volley | attack | 110 | 6 s (attack) | Dist 0.9–1.5 +5, holy | 3×3 around target | holy burst on a group | — → holy orb → holy area |
| 50 | Camouflage | camouflage | utility | 120 | 30 s (support) | 10 s | self | monsters lose you | green smoke |
| 55 | Eagle Eye | eagle eye | support | 180 | 60 s (support) | +10% crit chance, 2 min | party, radius 5 | party buff | divine dazzle → — → sparkles |
| 65 | Sanctified Ground | sanctified ground | healing | 220 | 30 s (healing) | ML 0.6–1.0 +20 each second, 6 s | radius 2 | healing zone for you and party | divine dazzle → — → holy area |
| 80 | Dawnpiercer | dawnpiercer | attack | 160 | 10 s (attack) | Dist 1.5–2.4 +10, holy | 7-tile line | long holy beam (power spike) | divine dazzle → — → holy hits |
| 100 | Hunter's Focus | hunters focus | support | 150 | 60 s (support) | +15% distance, 20 s | self | burst window | golden empowerment → — → sparkles |
| 160 | Lightrain | lightrain | attack | 300 | 15 s (attack) | Dist 1.6–2.6 +20, holy | 5×5 around target | rain of light | divine dazzle → holy orb → holy area |
| ★120 | Hawk's Path | hawks path | utility | 150 | 20 s (support) | — | 6 tiles | long dash forward (Floor 5 Lost Art) | white whirl → — → white burst |
| ★250 | Volley of Dawn | volley of dawn | attack | 500 | 40 s (attack) | Dist 2.6–4.0 +30, holy | ring of 21 tiles around you | huge holy area (Floor 8 Lost Art) | divine dazzle → — → divine grenade |

### 4.4 Arcanist (19 own, 25 in all): the destroyer

| Lvl | Spell | Words | Type | Mana | CD (group) | Numbers | Area / range | What it does | Visuals |
|---|---|---|---|---|---|---|---|---|---|
| 8 | Ember Strike | ember strike | attack | 20 | 2 s (attack) | ML 1.2–2.0 +5, fire | target, 5 | fire bolt | — → fire → fire hit |
| 9 | Mending Spark | mending spark | healing | 25 | 1 s (healing) | ML 1.0–1.6 +10 | self | small heal | — → — → violet energy |
| 12 | Volt Strike | volt strike | attack | 20 | 2 s (attack) | ML 1.2–2.0 +5, energy | target, 5 | lightning bolt | — → energy → purple lightning |
| 14 | Mana Ward | mana ward | support | 50 | 14 s (support) | 3 min | self | damage drains mana first | purple teleport |
| 18 | Fireburst Wave | fireburst wave | attack | 80 | 4 s (attack) | ML 1.3–2.1 +5, fire | wave in front | fire wave (power spike) | orange sparks → — → fire area |
| 23 | Arc Beam | arc beam | attack | 110 | 4 s (attack) | ML 1.6–2.6 +5, energy | 5-tile line | lightning beam | purple lightning → — → energy hits |
| 26 | Gale Step | gale step | utility | 100 | 2 s (support) | haste +70%, 22 s | self | strong haste | purple smoke |
| 27 | Conjure Fire Rune | conjure fire rune | conjure | 300 | 2 s (support) | 1 blank rune → 4 fire runes | self | area attack runes | fire sparkles |
| 30 | Blink | blink | utility | 80 | 14 s (support) | — | 3 tiles | short teleport forward | purple teleport → — → purple teleport |
| 35 | Searing Brand | searing brand | attack | 60 | 8 s (attack) | ML 1.0–1.6 +5, burn 6×12% | target, 5 | fire hit that keeps burning | — → fire → fire hit |
| 45 | Conjure Strike Rune | conjure strike rune | conjure | 600 | 2 s (support) | 1 blank rune → 3 strike runes | self | strong single-target runes | violet energy |
| 50 | Summon Ember Sprite | summon ember sprite | summon | 300 | 30 s (support) | one at a time | beside you | a fire spirit fights for you | orange teleport |
| 55 | Stormcall | stormcall | attack | 300 | 16 s (attack) | ML 2.2–3.4 +10, energy | ring of 21 tiles | storm around you (power spike) | storm cloud → — → energy area |
| 60 | Arcane Empower | arcane empower | support | 220 | 60 s (support) | +10% magic level, 2 min | party, radius 5 | party buff | purple teleport → — → violet energy |
| 80 | Inferno Core | inferno core | attack | 400 | 20 s (attack) | ML 2.6–4.0 +20, fire | ring of 21 tiles | fire ring around you (power spike) | explosion → — → fire area |
| 100 | Cinder Lance | cinder lance | attack | 250 | 30 s (attack) | ML 3.2–4.8 +30, fire | target, 5 | the ultimate single hit (power spike) | — → explosion bolt → explosion + sparkles |
| 130 | Arc Cataclysm | arc cataclysm | attack | 500 | 12 s (attack) | ML 2.4–3.6 +20, energy | 3-wide, 6-long beam | great lightning beam | storm cloud → — → purple lightning |
| ★120 | Meteor Rain | meteor rain | attack | 600 | 40 s (attack) | ML 3.2–5.0 +30, fire | 5×5 around target | meteors (Floor 5 Lost Art) | explosion → fire → fire area |
| ★250 | Mirror Image | mirror image | utility | 300 | 60 s (support) | 5 s | beside you | a decoy monsters attack (Floor 8 Lost Art) | purple teleport |

### 4.5 Mystic (19 own, 25 in all): the warden of life

| Lvl | Spell | Words | Type | Mana | CD (group) | Numbers | Area / range | What it does | Visuals |
|---|---|---|---|---|---|---|---|---|---|
| 8 | Frost Strike | frost strike | attack | 20 | 2 s (attack) | ML 1.2–2.0 +5, ice | target, 5 | ice bolt | — → ice → ice hit |
| 9 | Dewfall | dewfall | healing | 25 | 1 s (healing) | ML 1.1–1.8 +12 | self | heal | — → — → green rings |
| 13 | Thorn Strike | thorn strike | attack | 20 | 2 s (attack) | ML 1.2–2.0 +5, earth | target, 5 | thorn bolt | — → earth → carniphila |
| 16 | Mend Other | mend other | healing | 70 | 1 s (healing) | ML 1.6–2.6 +20 | named ally or you | heal another player (power spike for groups) | — → green star → green sparkle |
| 21 | Frost Wave | frost wave | attack | 70 | 4 s (attack) | ML 1.0–1.7 +5, ice, slow 2 s | wave in front | ice wave that slows | ice tornado → — → ice area |
| 24 | Conjure Healing Rune | conjure healing rune | conjure | 400 | 2 s (support) | 1 blank rune → 1 healing rune | self | rune anyone can use | green rings |
| 28 | Purify | purify | support | 90 | 6 s (support) | — | party, radius 4 | removes harmful conditions | green rings → — → white smoke |
| 32 | Barkskin | barkskin | support | 150 | 30 s (support) | party −10%, 2 min | party, radius 4 | party armour | green rings → — → small plants |
| 36 | Mass Mend | mass mend | healing | 160 | 2 s (healing) | ML 1.0–1.6 +20 | party, radius 4 | group heal (power spike) | green rings → — → green sparkle |
| 42 | Rejuvenate | rejuvenate | healing | 100 | 6 s (healing) | heal every second, 10 s | named ally or you | heal over time | — → green star → green pulse |
| 48 | Conjure Binding Rune | conjure binding rune | conjure | 500 | 2 s (support) | 1 blank rune → 1 paralysis rune | self | crowd-control rune | roots |
| 50 | Summon Wolf Companion | summon wolf companion | summon | 300 | 30 s (support) | one at a time | beside you | a wolf fights at your side | green smoke |
| 55 | Thornfield | thornfield | attack | 300 | 16 s (attack) | ML 1.8–2.9 +10, earth | ring of 21 tiles | thorns erupt around you | big plants → — → plant attack |
| 65 | Lifeward | lifeward | support | 120 | 12 s (support) | −25% damage, 6 s | named ally or you | shield one player | — → green star → green rings |
| 80 | Glacier Core | glacier core | attack | 400 | 20 s (attack) | ML 2.2–3.4 +20, ice | ring of 21 tiles | ice storm around you | giant ice → — → ice tornado |
| 100 | Verdant Renewal | verdant renewal | healing | 400 | 4 s (healing) | ML 2.0–3.0 +40 | party, radius 5 | big group heal (power spike) | big plants → — → green pulse |
| 130 | Mana Bloom | mana bloom | support | 200 | 60 s (support) | mana every 2 s, 30 s | party, radius 5 | party mana regeneration | green rings → — → blue sparkle |
| ★120 | Wellspring | wellspring | healing | 400 | 45 s (healing) | ML 1.0–1.6 +40 each second, 8 s | radius 3 | healing spring (Floor 5 Lost Art) | water splash → — → green pulse |
| ★250 | Winter's Breath | winters breath | attack | 600 | 40 s (attack) | ML 3.2–5.0 +30, ice | ring of 21 tiles | huge ice area (Floor 8 Lost Art) | giant ice → — → ice area |

## 5. Retired or changed

| Old | What happened | Why |
|---|---|---|
| First Aid (shared, 8) | removed | each vocation has its own first heal at 9 (Second Wind, Field Dressing at 10, Mending Spark, Dewfall) |
| Beacon (shared, 20) | removed | duplicate of Kindle; Kindle now lasts 10 minutes |
| Entangle (Mystic, 40) | renamed Conjure Binding Rune, level 48 | the name now says what it does |
| Whirlwind (Vanguard, 16) | moved to 33, weaker, 8 s cooldown | Vanguard is the hardest solo class (section 3.2) |
| Vanguard level 16 | new Rending Blow (single target + bleed) | keeps an early second attack spell (Jay's playtest) without an area spell |
| Conjure spells | now use up one blank rune | matches ECONOMY.md |
| Lost Arts | level 100/150 → 120/250 | match Floor 5 and Floor 8 level bands |
| New spells | Rending Blow, Skyrend, Undying Oath, Sunburst Volley, Dawnpiercer, Hunter's Focus, Lightrain, Mending Spark, Gale Step, Searing Brand, Stormcall, Inferno Core, Cinder Lance, Arc Cataclysm, Dewfall, Frost Wave, Thornfield, Lifeward, Glacier Core, Verdant Renewal, Mana Bloom | fill the long gaps after level 60 and give each class its spikes |

Characters who had hotkeys for First Aid or Beacon will see "unknown spell"; nothing else is lost (spells are not
stored per character).

## 6. Art requests

None of these block anything: each spell already uses the best existing effect (marked "placeholder" below). They are
also copied to `ART_REQUESTS.md`.

| For | What | Placeholder now |
|---|---|---|
| Whirlwind (Vanguard) | A single 3×3 spinning steel arc, crimson edge, 6 frames, 32×32 per tile (or one 96×96) | white whirl + red hits |
| Skyrend (Vanguard) | A tall golden-crimson downward sword slash on one tile, 7 frames | orange hit + explosion |
| Undying Oath (Vanguard) | Gold halo/shield ring that loops around the character, 8 frames | golden empowerment |
| Dawnpiercer (Ranger) | A white-gold light arrow projectile (distance effect), 8 directions | none (beam of holy hits) |
| Lightrain (Ranger) | Falling light-needles on a tile, 6 frames | holy area |
| Stormcall (Arcanist) | Violet lightning strike from above on a tile, 6 frames | storm cloud + energy area |
| Arc Cataclysm (Arcanist) | Thick violet lightning beam segment (horizontal and vertical), 4 frames | purple lightning |
| Thornfield (Mystic) | Green thorn spikes bursting out of the ground, 6 frames | plant attack |
| Lifeward (Mystic) | Translucent leaf-green bubble around a character, 8 frames | green rings |

## 7. Balance questions for playtesting

These are assumed as written until Jay says otherwise (also in `QUESTIONS.md`):
1. Is the Vanguard too hard solo now (no area spell until 33)? If yes, the first fix is Whirlwind to level 25, not more
   damage.
2. Ranger Scatter Shot is the strongest early area spell. Good ("easiest class"), or too strong?
3. Conjuring now costs a blank rune (10 gold). Does rune-making still feel worth it?
4. Are the big ring spells (Stormcall, Thornfield, Inferno Core, Glacier Core) flashy enough, or do they need the
   custom art in section 6 first?
5. Should the rune items get Spirebound names (they still use the engine's item names)?
