# Style trees, second version (design, 2026-11-27)

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
