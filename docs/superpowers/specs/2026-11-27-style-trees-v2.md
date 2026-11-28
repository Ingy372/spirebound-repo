# Style trees, second version (design, 2026-11-27)

**Jay reviewed this on 2026-11-27; sections 7, 8 and 9 at the end hold his changes and override anything above them (the later section wins).**

Replaces the path and final-style table in `2026-11-23-gear-progression-design.md` 4.2. Everything else in 4.2 stays the same: 3 stages of 10 levels, 2 permanent choices, the stance from Mastery 5 (P11), pacing (stage ends around levels 37 / 110 / 275), the shop respec. This file only changes **what the choices are**.

## 1. Jay's brief (2026-11-27)

- **Vanguard:** "one style to be a classic sword and shield tank that can split off into an even tankier tree that heavily sacrifices offensive ability for defense or a less drastic slightly more offensively balanced option."
- **Mystic:** "one style to be damage focused with crowd control elements. from there you decide the next fork for this path. for the secondary path it will be support/healing and the fork from there will be heavy support/buffing/healing/ or slightly less healing than normal, but higher offensive capability."
- **Arcanist and Ranger:** "i leave it to you to examine and find roles that would fit best."

## 2. What was wrong with version 1

1. **The forks were mostly flavour.** Rootcaller and Frostwarden both did damage plus crowd control. Emberwright and Stormbinder split by element (fire or lightning), not by what you do in a group.
2. **No real trade-offs.** Every style level gave a small plus and nothing cost anything, so a "tank" choice never cost you damage. Jay wants the heavy tank to *give up* offence.
3. **Hidden mismatches.** Cinderheart was "huge single bursts", but its ability (Heart of Cinders) hits a ring around you.

## 3. The rule for every tree (Claude's call)

Each class splits first into **two jobs** (path), then each job splits into **the extreme version or the balanced version** (final). For example: tank, then full fortress or fighting tank. The extreme final always pays for its strength with a **minus** somewhere. The balanced final never has a minus. This makes the second choice a real decision, as Jay asked for the Vanguard, and the same pattern works for all four classes.

Each class still keeps a solo-capable option at every choice (gear spec 4.2).

## 4. The trees

Each style level gives the passive shown "per level", so a full stage gives 10 times it. Numbers are Claude's call and get tuned after playtests; they live in `PASSIVES` in `tools/gen_gear.py`. The ability is the signature skill you unlock by finishing that stage.

### 4.1 Vanguard: the shield or the blade

```
Vanguard Mastery (+0.5% damage per level)
 ├─ Bulwark: the shield tank  (only with a shield in hand)
 │    ├─ Ironwall: the fortress   (extreme: much tougher, much weaker hits)
 │    └─ Bladeward: the knight    (balanced: tough and still hits)
 └─ Reaver: the melee damage dealer  (unchanged)
      ├─ Bloodedge: life-steal, single target
      └─ Stormbreaker: cleaving area hits
```

| Style | Per level | Full at 10 | Signature ability |
|---|---|---|---|
| **Bulwark** (path) | -0.6% damage taken, **only while a shield is equipped** | -6% taken | **Shieldwall Vow** (kept): the party near you takes 20% less damage for 8 s |
| **Ironwall** (final, extreme) | -1.2% damage taken, +1.5% max health, **-2% damage dealt** | -12% taken, +15% health, **-20% damage** | **Iron Bastion** (reworked): 6 s of 50% less damage taken, and every monster within 3 tiles turns to attack you (a taunt). You can't be pushed while it lasts |
| **Bladeward** (final, balanced) | -0.5% damage taken, +0.6% damage dealt | -5% taken, +6% damage | **Riposte Guard** (new): a 6 s stance; every melee hit you block or dodge strikes back at 60% of your weapon damage |
| Reaver, Bloodedge, Stormbreaker | unchanged | | Red Reckoning, Crimson Verdict, Thunder Cleave (kept) |

A finished **Ironwall** overall (all three stages): 18% less damage taken, 15% more health, and 15% *less* damage than a Vanguard with no style. A finished **Bladeward**: 11% less taken, 11% more damage. A finished **Bloodedge**: 23% more damage, no defence.

- **Ironwall** is the wall a large group puts in front of the Axe-Lord. Solo, it survives anything but kills slowly. That is the heavy sacrifice Jay asked for.
- **Bladeward** is the classic sword-and-board knight who can hunt alone.
- **(Claude's call) The shield, not the sword, is the rule.** Bulwark works with any one-handed Vanguard weapon (sword, axe or club) plus a shield, so axe and club players can tank too. Twin Fang (DESIGN 5.6) needs an empty shield hand, so a Bulwark's bonuses switch off while they dual-wield. That is fair: Twin Fang is the offensive path.
- **Retired:** Aegis Warden and its Warden's Oath (a party shield). The party-protector role stays in Bulwark's Shieldwall Vow, which every shield tank gets.

### 4.2 Mystic: thorns and ice, or the healer

```
Mystic Mastery (+0.5% damage per level)
 ├─ Wildcaller: damage with crowd control   (Jay's path A)
 │    ├─ Blightcaller: the damage dealer    (extreme: big damage, little control)
 │    └─ Frostwarden: the controller        (balanced: holds a fight in place)
 └─ Lifebinder: support and healing          (Jay's path B)
      ├─ Dawnmender: the lifeline           (Jay: "heavy support/buffing/healing")
      └─ Briarmender: the battle healer     (Jay: "slightly less healing than normal, but higher offensive capability")
```

| Style | Per level | Full at 10 | Signature ability |
|---|---|---|---|
| **Wildcaller** (path) | +0.8% damage, roots and slows last +2% longer | +8% damage, +20% control time | **Bramble Maw** (kept): thorns burst around you and root monsters for 2 s |
| **Blightcaller** (final) | +1.2% damage | +12% damage | **Worldvine Grasp** (reworked): a bigger hit, a shorter 1 s root, and the thorns stay in the ground poisoning anything inside for 6 s |
| **Frostwarden** (final) | +0.5% damage, roots and slows last +4% longer | +5% damage, +40% control time | **Hoarfrost Prison** (kept, root 2 s raised to 3 s): a telegraphed ice field that freezes a group in place |
| **Lifebinder** (path) | +1% healing | +10% healing | **Sanctuary Bloom** (kept): a healing zone for 10 s |
| **Dawnmender** (final, extreme) | +1.5% healing, party buffs +3% stronger, **-1.5% damage dealt** | +15% healing, +30% buffs, **-15% damage** | **Second Dawn** (reworked): the big party heal now also leaves everyone near you with +10% damage and 10% less damage taken for 10 s |
| **Briarmender** (final, balanced) | -0.5% healing, +1% damage | -5% healing, +10% damage | **Verdant Lash** (new): an earth bolt; 60% of the damage it deals heals the most hurt party member near you |

- **Why Blightcaller vs Frostwarden (Claude's call, Jay left it open):** the old fork was two kinds of the same thing. The new fork is *kill it* or *hold it*. Blightcaller is the Mystic who out-damages most styles but barely stops anything. Frostwarden keeps a group pinned so the party can work, which makes it the safest solo style and the one large groups want for pulls.
- **"Slightly less healing than normal":** "normal" here means a Lifebinder's healing. A finished Briarmender heals 5% more than a Mystic with no style (+10 from Lifebinder, -5 from Briarmender), while a Dawnmender heals 25% more. Briarmender hits 15% harder in total; Dawnmender hits 10% weaker.
- **Party buffs +3% stronger** means Barkskin, Mana Bloom, Lifeward and the new Second Dawn buff give more (Barkskin's -10% becomes -13%). The same party buff still never stacks with itself (DESIGN 5.3b).
- **Retired:** Wardkeeper and its Grove Ward. Its party shield is folded into Second Dawn. Rootcaller is renamed Blightcaller because the style is no longer about roots.

### 4.3 Arcanist: the destroyer or the storm-binder (Claude's call)

The Arcanist is "the destroyer" (spells.md 4.4): area damage and big flashy spells. So both paths deal damage, but they do different jobs in a group: **raw destruction**, or **control and making everyone else hit harder**.

```
Arcanist Mastery (+0.5% damage per level)
 ├─ Emberwright: raw destruction (fire)
 │    ├─ Cinderheart: the boss-breaker   (extreme: one huge hit, weak on crowds)
 │    └─ Ashwalker: the wildfire         (balanced: burning ground for hunting)
 └─ Stormbinder: control and tempo (lightning)
      ├─ Tempest: the skirmisher         (balanced: chains and speed, best solo)
      └─ Spellbreaker: the hexer         (extreme: weak alone, makes the party hit harder)
```

| Style | Per level | Full at 10 | Signature ability |
|---|---|---|---|
| **Emberwright** (path) | +0.8% damage | +8% damage | **Cinderfall** (kept) |
| **Cinderheart** (final, extreme) | +2% damage against a single target, **-1% damage with area spells** | +20% single, **-10% area** | **Heart of Cinders** (reworked to fit the role): a 2 s charge with a warning sigil, then the biggest single hit in the Arcanist's kit. It used to be a ring around you, which did not fit a boss-breaker |
| **Ashwalker** (final, balanced) | +1% damage | +10% damage | **Ashen Path** (kept): dash 5 tiles, leaving burning ground |
| **Stormbinder** (path) | +0.6% damage, slows and knock-backs last +2% longer | +6% damage, +20% control time | **Arc Cascade** (kept): lightning that jumps 5 times |
| **Tempest** (final, balanced) | +1% damage, +1 speed | +10% damage, +10 speed | **Eye of the Tempest** (kept) |
| **Spellbreaker** (final, extreme) | +0.4% damage; your marks make monsters take +0.5% more damage from everyone | +4% damage, marks +5% stronger | **Sundering Bolt** (reworked): the monster takes 20% more damage from everyone (was 15%) for 8 s, and is slowed. In PvP it also drains the target's mana |

- **Why this split:** a big group wants one Spellbreaker (everyone deals more) and one Cinderheart (the boss melts). A solo player or a hunting pair picks Ashwalker or Tempest. Spellbreaker's job was "counters other casters, PvP" before. That is too narrow for a server that is mostly PvE, so it becomes the group debuffer and keeps a PvP bonus.
- Elements stay as before: the destruction path is fire and the control path is lightning, so the look of each style doesn't change.

### 4.4 Ranger: the sharpshooter or the warden (Claude's call)

The Ranger is "the hunter": ranged damage with some healing (DESIGN 5.2), and it already owns heals (Field Dressing, Sanctified Ground) and party tools (Eagle Eye, Tracker's Mark). So the split is **damage**, or **control and support**.

```
Ranger Mastery (+0.5% damage per level)
 ├─ Marksman: the sharpshooter
 │    ├─ Deadeye: one target, huge crits    (extreme: the best boss damage, weak on crowds)
 │    └─ Volley Captain: many targets        (balanced: the hunting Ranger)
 └─ Huntwarden: control and support   (was "Trapper")
      ├─ Snareweaver: the trapper            (balanced: the solo kiting expert)
      └─ Pathfinder: the scout and field medic (extreme: party speed and heals, low damage)
```

| Style | Per level | Full at 10 | Signature ability |
|---|---|---|---|
| **Marksman** (path) | +1% damage at range 4 or more | +10% at range | **Farshot** (kept) |
| **Deadeye** (final, extreme) | +1.2% damage at range 4+, +0.5% critical chance, **-1% damage with area attacks** | +12% at range, +5% crit, **-10% area** | **Last Light** (kept) |
| **Volley Captain** (final, balanced) | +1% damage | +10% damage | **Arrow Squall** (kept) |
| **Huntwarden** (path) | +0.5% damage, +1% healing | +5% damage, +10% healing | **Snarefield** (kept) |
| **Snareweaver** (final, balanced) | +0.6% damage, roots and slows last +4% longer | +6% damage, +40% control time | **Web of Briars** (kept) |
| **Pathfinder** (final, extreme) | +2 speed, +1.5% healing, party buffs +3% stronger, **-1% damage** | +20 speed, +15% healing, +30% buffs, **-10% damage** | **Wayfarer's Stride** (reworked): the party haste now ends with a heal pulse for everyone it touched |

- **Why "Huntwarden" instead of "Trapper":** the path now covers the Ranger's healing and party tools as well as traps, and "Trapper" only told half of it.
- **Pathfinder is the support Ranger** a group brings when it has no Mystic. Snareweaver kites anything alone.

## 5. The whole picture: one job each

| | Extreme final (has a minus) | Balanced final (no minus) |
|---|---|---|
| Vanguard, Bulwark | Ironwall: the wall | Bladeward: the knight |
| Vanguard, Reaver | (both balanced, unchanged) Bloodedge | Stormbreaker |
| Mystic, Wildcaller | Blightcaller: pure damage *(no minus: damage is its own price, it has little control)* | Frostwarden: control |
| Mystic, Lifebinder | Dawnmender: the lifeline | Briarmender: the battle healer |
| Arcanist, Emberwright | Cinderheart: the boss-breaker | Ashwalker: the wildfire |
| Arcanist, Stormbinder | Spellbreaker: the hexer | Tempest: the skirmisher |
| Ranger, Marksman | Deadeye: the boss sniper | Volley Captain: the hunter |
| Ranger, Huntwarden | Pathfinder: the support | Snareweaver: the kiter |

The Reaver path is left as it was. Jay didn't ask to change it, and it is already "damage or more damage". It is the one fork without an extreme/balanced split. **(Claude's call; changing it is a later question.)**

**Groups want a mix** (Jay: "create diverse roles"): a large group on the Axe-Lord ideally brings an Ironwall, a Dawnmender, a Spellbreaker, a Cinderheart or Deadeye, and a Frostwarden for the guards.

## 6. Notes for the builder

- **Keep saved characters safe.** Keys that keep their meaning keep their key (`bulwark`, `ironwall`, `reaver`, `bloodedge`, `stormbreaker`, `wildcaller`, `frostwarden`, `lifebinder`, `dawnmender`, `emberwright`, `cinderheart`, `ashwalker`, `stormbinder`, `tempest`, `spellbreaker`, `marksman`, `deadeye`, `volley_captain`, `snareweaver`, `pathfinder`). `trapper` keeps its key and only changes its display name to Huntwarden. Three keys change because their meaning changed: `aegis_warden` → `bladeward`, `rootcaller` → `blightcaller`, `wardkeeper` → `briarmender`. A character holding a retired key gets its final choice cleared and a message telling it to pick again (free; this is not a respec and doesn't start the 7-day wait).
- **New passive kinds** for `lib/spirebound/style.lua` (today it knows damage, taken, far_damage, heal, speed): `max_health`, `cc` (longer roots, slows and knock-backs; for monsters only, PvP roots stay as they are), `buff` (stronger party buffs), `crit`, `single_damage` / `area_damage` (by spell or attack shape), `mark` (stronger vulnerability marks), and a `shield_only` flag on Bulwark's passive. Negative values per level must work (the extreme finals use them).
- **New or reworked abilities:** Iron Bastion (adds a taunt), Riposte Guard (new: counter on block or dodge), Worldvine Grasp (shorter root, adds poison ground), Second Dawn (adds a party buff), Verdant Lash (new: damage that heals an ally), Heart of Cinders (single target with a charge), Sundering Bolt (20%, slow, PvP mana drain), Wayfarer's Stride (adds a heal pulse), Hoarfrost Prison (3 s root). Each needs its effect checked against spells.md 3.3 (the class palette). Retire Warden's Oath and Grove Ward.
- **The stance (P11)** keeps working: it gives a taste of a *path*, and the paths keep their keys.
- `tools/balance.py --check` should gain one check: no finished style deals more than about 25% extra damage, and every extreme final has a minus.
- Names: all new names (Bladeward, Riposte Guard, Blightcaller, Briarmender, Verdant Lash, Huntwarden) pass `tools/check_names.py`.
- Tests: the p1b/p1c autopilot routes cover each class's abilities. Update them for the new and renamed ones.

## 7. Jay's review (2026-11-27) and the changes it made

Jay: "i like it but it can be a lot to swallow at first." Everything in this section replaces the matching parts above.

### 7.1 Showing it to players without overwhelming them

- **Only ever show the next choice, never the whole tree.**
- **Pre-framing at class pick:** the Registrar ends with one line, repeated in the Journal: "At Mastery 10 (around level 37) your class trainer will send for you. You will choose your path then, and your style later." Nothing else about styles is shown yet.
- **The summons (Jay: "a message appears in there bag telling them they have been summoned by there vocation specialist for special training"):** at Mastery 5 a sealed letter appears in the backpack from the class trainer (Vanguard: Captain Dorrow; Ranger: Hunter Brannoch; Arcanist: Vesper; Mystic: Fisher Corwin). Visiting the trainer lets you try both paths for free (the stance). At Mastery 10 a second letter: "come and choose". Talking to the trainer opens **the choice window**: two cards side by side, each with the name, one line on the role ("the shield tank"), what you gain, what you give up, and the signature ability. Choose, then a confirm ("this is permanent"). The final style (Mastery 20) works the same way with a third letter.
- The Journal's "Calling" page shows your current path and only the next choice.
- Jay was fine with either a pop-up or the summons (Claude's call): the summons, because it makes the choice a moment and reuses the trainers players already know, and the window still gives the clear side-by-side.
- When the first choice lands (level 37 or earlier) is still Q46, part of this conversation.

### 7.2 Respec

Jay: "i want class mastery to reset with in game donation only." The Mastery Respec Scroll stays shop-only, as built. (QA10's gold respec is cancelled; there is no separate weapon mastery to reset.)

### 7.3 Reaver: the off-hand fighter (Jay: "reaver should be able to equip a second weapon to forgo defense in favor of damage")

```
Reaver: no shield, an off-hand blade instead (or a two-handed weapon)
 ├─ Bloodedge: the berserker      (extreme: the hardest-hitting Vanguard, takes more damage)
 └─ Stormbreaker: the cleaver     (balanced: hits everything around it)
```

- **Off-hand blades** are a new kind of item that goes in the shield hand: daggers, short swords, hatchets and cudgels with an attack value and no defence. Tibia's client can't hold two weapons, so the off-hand blade is a shield-hand item our scripts treat as a second weapon (the same trick Twin Fang uses). Ordinary ones keep a Tibia dagger look; rare ones get our own art.
- **Reaver (path):** +0.8% damage per level while no shield is held, and after every melee hit the off-hand blade strikes for 20% of its damage, +1% per level (30% at Mastery 10). A Reaver holding a two-handed weapon gets the same share as extra two-hander damage instead, so two-handed axe and club users still fit. Signature: **Red Reckoning** (kept).
- **Bloodedge (final, extreme):** +1.2% damage and +2% off-hand strike per level (50% at 10); off-hand strikes heal you for a little of the damage; below half health you hit 10% harder. **Minus: you take 1% more damage per level (+10%).** Signature: **Crimson Verdict** (kept).
- **Stormbreaker (final, balanced):** +1% damage per level, and each melee hit also strikes monsters standing next to your target for 3% per level of its damage (30% at 10). No minus. Signature: **Thunder Cleave** (kept).
- **Is it balanced? (Claude's honest check):** yes, if two rules hold: off-hand blades are clearly weaker than main weapons (about two thirds of a main weapon's attack on the same floor), and the off-hand strike is a share of that. A finished Bloodedge then deals roughly 35-40% more than an unstyled Vanguard and takes 10% more damage with no shield, which is a real trade against Ironwall's 18% less damage taken. `balance.py` gets a ceiling for it.
- **Twin Fang (Q56 overlaps):** if every Reaver can dual-wield, Twin Fang's "only 3 per season get dual wielding" no longer makes sense. Recommendation: Twin Fang becomes the rare prize **on top of** the Reaver: the first 3 each season to beat the Floor 8 trial get the Twin Fang title, a glowing off-hand look and its three sword skills as looks-only versions. No extra power, so late joiners aren't weaker.

### 7.4 Dawnmender: is +25% healing too much?

Jay: "is 25% to extreme of a heal boost?" A heal of 400 would become 500. In monster hunting that is fine; the risk is player fights, where one healer could keep a friend alive against a whole team. **Change:** Lifebinder +10% and Dawnmender **+10%** (was +15%), so **+20% in total**. Dawnmender's real strength is its party buffs and Second Dawn, which stay. Briarmender stays at Lifebinder's +10% minus 5% (+5% in total).

### 7.5 Spellbreaker, explained and fixed

- **Monsters have no mana in Tibia**, so the mana drain only does anything against players. Against monsters, the Spellbreaker's job is the **mark**.
- **The worry about the slog:** the Spellbreaker is the *final* style, chosen around level 110. Until then the player is a Stormbinder (+6% damage, longer slows and knock-backs), which hunts like any Arcanist.
- **Rework so it is good solo, not only in groups:**
  - **Sundering Bolt** marks one monster: it takes **20% more damage from everyone, the Spellbreaker included**, for 8 seconds, and is slowed.
  - **The mark jumps:** when a marked monster dies, the mark moves to the nearest monster, so solo hunting flows from one to the next.
  - **Hex Spread** (its area spell) puts a weaker 10% mark on up to 3 monsters.
  - **Minus: 10% less damage against unmarked targets.**
  - So solo, the Spellbreaker hits the marked monster about 25% harder than an unstyled Arcanist and the rest about 10% softer: strong on bosses and big single monsters, slower on large crowds. In a group the whole party gets the 20%. Against players the mark also drains mana.

### 7.6 Pathfinder: support in its own way, not a backup Mystic

Jay: "it should support the party in its own unique way." The Mystic **restores** health, the Ironwall **absorbs** hits, the Pathfinder **makes the party avoid them and move**.

- **Pathfinder (final, extreme):** party members near you get **+0.5% chance per level to dodge an attack completely** (5% at 10), **+2 speed per level**, **0.3 seconds more warning before a boss's big hit**, and you see invisible monsters and hidden traps for the party. Its heals are gone. **Minus: 10% less damage.**
- **Wayfarer's Stride (signature, reworked):** party haste plus 6 seconds of +15% dodge for everyone it touches.
- The Huntwarden path keeps its small +10% healing (the Ranger's field dressing).

### 7.7 Snareweaver: crowd control that can't be abused

Jay: "careful, this can be a hard concept to balance when it comes to pvm. does tibia have any approach to this concept?" Tibia mostly avoids freezing monsters: bosses and many strong monsters are immune to being slowed or held, and its main control tool is the magic wall, which blocks where monsters can walk instead of stopping them. We follow that:

- **Walls and slows over freezes.** Signature **Web of Briars** becomes a briar wall: a short line of thorns that blocks a path for 4 seconds (players know this from Tibia's magic wall) and slows anything that touches it.
- **Roots stay short, and wear off:** holding the same monster again within 10 seconds gives half the time; a third time it is immune for 10 seconds.
- **Bosses and elites can't be held at all**, only slowed a little.
- **A held monster still casts and shoots**, so kiting is never free.
- Control time at full Snareweaver drops from +40% to **+25%**.
- Frostwarden (the Mystic controller) follows the same rules.

## 8. Jay's second review (2026-11-28)

Jay: "i love pretty much everything thats been created for styles ... all of the balances look good to me." Section 7 is approved except where this section changes it.

### 8.1 When the choices come

Jay: "the 1st style choice should come upon players arriving to floor 2. the second can happen at mastery level 10 as planned."

- **First choice (the path): when a player first arrives on Floor 2.** The summons letter arrives as they step into Floor 2's town, and the trainer's choice window opens from there. Mastery 10 lands around level 37, about when players reach Floor 2 anyway, so the two line up. A player who reaches Floor 2 early still chooses on arrival; the path's bonus then fills as their Mastery climbs.
- **The free try-out (stance) at Mastery 5 stays on Floor 1**, so players feel the choice coming.
- **Second choice (the final style): Mastery 20, around level 110**, as planned. (Claude's reading: Jay's "mastery level 10" means "the second choice as planned". Checked in Q46.)

### 8.2 Briars stay with the Mystic

Jay: "originally briars were going to the mystics property ... thats unexpected for the tibia community. they are use to druids (mystics) being the ones who control wild growth."

- **The briar wall goes to the Mystic** (Frostwarden, the controller), like Tibia's druid wild growth. Its PvP version (vine walls that fire burns, DESIGN 6.7) was already the Mystic's.
- **Snareweaver becomes the Ranger's trapper with Ranger tools:** set traps on the ground that snap shut on the first monster to step in, nets fired from the bow, and slowing shots. Signature **Web of Briars** is renamed **Hunter's Snare**: a ring of traps around the Ranger.

### 8.3 Holding monsters: an emergency button, not a way to win (approved)

Jay: "i am in favor for the monsters building snare or slow immunity and it only working for so long ... it provides a timing aspect to boss fights and harder monsters. they cant just be stun kited the whole fight. but its there as an emergency button to save the party, or used to get the monster into certain positions."

- Every monster builds resistance: a second hold within 10 seconds lasts half as long, a third does nothing for 10 seconds.
- **Bosses and hard monsters are no longer simply immune** (Claude's change, from Jay's "timing aspect to boss fights"): they can be held once, then are immune for a long time (30 seconds on bosses). So a hold is a button the party saves for the right moment.
- A held monster still casts and shoots.

### 8.4 A summoner (Jay: "one of the style choices could be a summoner? ... this is a mechanic that already exists in tibia and we could have a lot of fun with it")

Claude's view: a good fit, if its known problems are handled from the start. Open in Q113.

### 8.5 Twin Fang and the hero weapons

Jay likes a "hero" in each class: one special weapon per class, held by one player per season, with power that "helps to create FOMO" but is "nothing crazy or game breaking", and either no PvP use or a PvP nerf. Open in Q114.

## 9. Jay's third review (2026-11-28)

### 9.1 The second choice comes sooner

Jay: "the time gap between first choice and second choice is a little too big. maybe mastery level 15? im shooting for the second choice to be around level 80-90 ... less burn out before arriving to their final class."

- **Claude's call on how:** keep three stages of 10 Mastery levels (the passives and the choice window stay simple), and speed up stage 2 so **Mastery 20 lands around level 85** instead of 110. Stage 3's end (around level 275) stays. The Mastery experience curve in `tools/gen_gear.py` changes; `balance.py` checks level 80-90 for Mastery 20.

### 9.2 The try-out becomes a sealed trial at the trainer

Jay: "the only way i see that working is the player being put into a 'quest' where they are given the power for a short period. the quest would need to be blocked off so there is no exited or teleporting."

- **The free stance at Mastery 5 is removed.**
- **The Path Trial (Claude's design from Jay's idea):** when the trainer's summons brings a player to choose (first choice on Floor 2, final style at Mastery 20), the trainer offers a trial for each option. The player steps into a sealed training yard alone, holding that option's full Mastery 10 power and its signature ability, with training dummies and a few monster waves for about 5 minutes. No exits, no Waycrystals, no logging out to escape (logging out ends the trial). When it ends they are back at the trainer. Each option can be tried once per choice.
- **Why it is worth building, not just a test tool:** the class Mastery respec is shop-only (Jay's rule), so a wrong pick costs real money. The trial is what lets a free player choose with confidence. It reuses the private-room system the Proving and the boss rooms already use, so it is one small yard, not a new system.

### 9.3 Control bonus

Jay: "thats game logic. you decide on it." **Claude's call:** the paths with control (Wildcaller, Stormbinder) make holds and slows last up to 20% longer; the control finals (Frostwarden, Snareweaver) up to 25%. Monster resistance (section 8.3) applies on top, so it never adds up to a frozen fight.

### 9.4 No summoner

Jay: "if its already been tested and tibia caused trouble in tibia, maybes its a system we should just exclude and avoid then." **Excluded.** Blightcaller stays as designed.

### 9.5 Hero weapons: Claude's input (Q114)

Jay: "im loving the hero weapon idea ... but i dont want to see a good handful of players throw a fit and quit because they didnt get the hero weapon." Benefits: the race, stories, something for streams, a goal that lasts the season. Risks: four winners out of hundreds; one big guild taking all four every season; everyone else feeling locked out. Recommended guards, all three together:

1. **Small power, monsters only** (as in Q114): about 10% above the floor's best weapon, the rally in boss fights, normal strength against players.
2. **Echo weapons for everyone after the first:** the first to beat a trial gets the true hero weapon (the power, the rally, the server announcement, their name on it). Everyone who beats the same trial later that season gets an **echo**: the same look and special moves, but without the extra power or the rally. Nobody is locked out of the trial; only the first is the hero.
3. **One hero weapon per guild and per account each season,** so four different groups can be heroes and one guild can't sweep them.

With those, Claude thinks the benefits clearly outweigh the risks.
