# Gear and Weapon Progression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved gear system for Floor 1 (and the Floor 2 weapon list): style tree, weapon tiers and familiarity, Hearth Shards, the Floor 1 checklist, the "Next upgrade" window, 4 hidden mini-bosses, shop starter gear and the shop-only Mastery Respec.

**Architecture:** One Python generator (`tools/gen_gear.py`) owns every number and name and writes Lua data files; `tools/balance.py --check` enforces the ceiling and shop rules. Pure rule functions live in `server/data-spirebound/lib/spirebound/` (tested by in-game `SpireTest` tests), and thin event scripts in `scripts/spirebound/` apply them. Weapon state is stored on the item (custom attributes, so it survives trades and restarts); style state on the character (`player:kv():scoped("spirebound")`). The window is a new Journal tab.

**Tech Stack:** Canary v3.6.1 Lua datapack, OTClient Redemption 4.2 Lua module, Python 3 generators.

**Spec:** `docs/superpowers/specs/2026-11-23-gear-progression-design.md` (read it with this plan; section numbers below point into it).

## Global Constraints

- Canary v3.6.1 (protocol 15.11), OTClient Redemption 4.2. No pin changes.
- No CipSoft or SAO names a player can see; `python3 tools/check_names.py` reports 0 banned hits before every commit.
- Numbers come from generators (`tools/gen_gear.py`, `tools/balance.py`, `tools/gen_economy.py`); never hand-edit generated Lua. Change the generator, rerun it, commit both.
- `python tools/balance.py --check` passes; `tools/test_boot.sh` passes (run inside WSL Ubuntu on Jay's PC) after every task.
- Every player command has a button (`tools/check_commands.py`, rule R19).
- Tick a roadmap task only after a test through the real game path.
- Player-facing text is plain English; every "Next" line names the thing and the place in one sentence (spec section 1).
- PvP rules from DESIGN 6.7 apply to every new ability.
- Commit messages plain English, ending with the co-author line; push to `main` after each task.

## Review Focus

1. **Item state through trade, death drop, depot and restart:** tier, familiarity, awakened flag and family stay on the item. Test in Task 2 (attributes survive `item:clone()`/moving into a container) and the restart check in Task 11.
2. **Kills that must not count:** PvP kills, kills with a non-class weapon, summons' kills, and Arrival Yard Pen Rats give no style or familiarity. Test in Task 3.
3. **Party kills:** each member gets its own share, never the full amount to everyone. Test in Task 3.
4. **Upgrading past the cap or with the wrong floor's shards:** refused with a plain message, nothing taken. Test in Task 4.
5. **Respec abuse:** a second respec inside 7 days is refused and the item is not used up; a respec keeps style points. Test in Task 9.

---

### Task 1: The gear generator and its balance checks

**Files:**
- Modify: `tools/gen_gear.py` (rewrite; keep the existing piece names where they fit)
- Modify: `tools/balance.py` (add `gear_problems()` and call it from `--check`)
- Create (generated): `server/data-spirebound/lib/spirebound/gear_data.lua`
- Remove: the generated table part of `server/data-spirebound/lib/spirebound/gear.lua` (it becomes the rules file in Task 2)

**Interfaces:**
- Produces Lua globals in `gear_data.lua`:
  - `SpireGearData.weapons` = list of `{ id, name, floor, vocation, family, source = "main"|"drop"|"boss_awaken", base, attack, awakenedName, awakenedAttack }` for Floors 1 and 2 (Floor 2: 2-3 weapons per class).
  - `SpireGearData.armour` = list of `{ id, name, floor, vocation, source = "quest"|"drop", base, armor }`.
  - `SpireGearData.shop` = per vocation `{ weapon = {base, attack, name}, armour = {base, armor, name} }`.
  - `SpireGearData.TIER_ATTACK[floor]` = attack per tier (number), `TIER_ARMOR[floor]`, `MAX_TIER = 5`.
  - `SpireGearData.FAMILIARITY_POINTS` = list of 10 thresholds (points for levels 1..10), `FAMILIARITY_BONUS = 0.015`.
  - `SpireGearData.tokens[floor]` = `{ rough = itemId, cut = itemId, flawless = itemId, names = {...} }`; `TIER_COST[t]` = `{ grade, count = 3, gold }` for t = 1..5.
  - `SpireGearData.style[vocation]` = `{ stage1 = {key, name}, paths = { {key, name, finals = { {key,name}, {key,name} } }, ... } }` with the names from spec 4.2; `STYLE_POINTS` = list of 30 cumulative thresholds; `PASSIVES[key]` = `{ kind, per_level }`.
- Produces Python: `gen_gear.weapon_power(floor, tier, familiarity, awakened) -> float` used by `balance.py`.

- [ ] **Step 1: Write the failing check.** In `balance.py` add `gear_problems()` returning a list of strings, and assertions:
  - new Floor 2 weapon (tier 0, fam 0) is 0.90-0.95 of maxed Floor 1 (awakened, tier 5, fam 10), for every class;
  - maxed Floor 1 < Floor 2 at tier 2, fam 5;
  - Floor 2 passes maxed Floor 1 after 2-3 hours of Floor 2 hunting (use `kills_per_hour` and the shard drop rates);
  - shop weapon < Floor 1 main weapon at tier 2, fam 0, and shop weapon > the NPC weaponsmith's best weapon for that class at level 15;
  - style stage 1 finishes at level 35-40 of modelled hunting, stage 2 at Floor 4-5, stage 3 at Floor 8;
  - a solo player saving every shard reaches tier 5 on Floor 1 by level 30-35.
- [ ] **Step 2: Run** `python tools/balance.py --check`. Expected: fails (no gear data yet).
- [ ] **Step 3: Write the generator** with the spec's values (4.2-4.4, 4.9) and choose base numbers until the checks pass. Token item ids: three unused small-gem items, renamed "Rough/Cut/Flawless Hearth Shard", each with a description naming where it drops.
- [ ] **Step 4: Run** `python tools/gen_gear.py && python tools/balance.py --check && python3 tools/check_names.py`. Expected: all pass, 0 banned hits.
- [ ] **Step 5: Commit** "Gear generator: weapons, tiers, familiarity, Hearth Shards and style trees, with balance checks".

### Task 2: Weapon rules on the item

**Files:**
- Modify: `server/data-spirebound/lib/spirebound/gear.lua` (rules only)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_gear_weapons.lua`
- Modify: `server/data-spirebound/scripts/spirebound/tests/test_r12.lua` (old ladder tests replaced)

**Interfaces:**
- Consumes: `SpireGearData` (Task 1).
- Produces:
  - `SpireGear.make(into, defId) -> Item|nil` (weapon, armour or shop piece by its `id`)
  - `SpireGear.state(item) -> { id, tier, fam, famPoints, awakened, shop }` or nil for non-Spirebound items
  - `SpireGear.setState(item, state)`; refreshes attack/armor and the description line ("Tier 2/5 - familiarity 6/10")
  - `SpireGear.famLevel(points) -> int` (pure), `SpireGear.damageBonus(state) -> number` (pure, 0 for shop items)
  - `SpireGear.mainWeapon(player) -> Item|nil` (the Spirebound weapon in hand), `SpireGear.defOf(item) -> def`

- [ ] **Step 1: Write the failing tests**

```lua
SpireTest.add("gear: familiarity levels follow the thresholds", function()
	local T = SpireGearData.FAMILIARITY_POINTS
	SpireTest.eq(SpireGear.famLevel(0), 0, "no points")
	SpireTest.eq(SpireGear.famLevel(T[1]), 1, "first threshold")
	SpireTest.eq(SpireGear.famLevel(T[10] * 5), 10, "capped at 10")
end)
SpireTest.add("gear: tier and familiarity live on the item and survive a move", function()
	local bag = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local w = SpireGear.make(bag, SpireGearData.weapons[1].id)
	SpireGear.setState(w, { tier = 2, famPoints = SpireGearData.FAMILIARITY_POINTS[6] })
	local copy = w:clone()
	SpireTest.eq(SpireGear.state(copy).tier, 2, "tier kept")
	SpireTest.eq(SpireGear.state(copy).fam, 6, "familiarity kept")
	SpireTest.eq(w:getAttribute(ITEM_ATTRIBUTE_ATTACK), SpireGearData.weapons[1].attack + 2 * SpireGearData.TIER_ATTACK[1], "tier adds attack")
	SpireTest.eq(SpireGear.damageBonus(SpireGear.state(w)), 6 * SpireGearData.FAMILIARITY_BONUS, "familiarity bonus")
	bag:remove()
end)
SpireTest.add("gear: shop pieces have no tiers and no familiarity", function()
	local bag = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local s = SpireGear.make(bag, "shop_weapon_3")
	SpireTest.eq(SpireGear.state(s).shop, true, "marked as shop gear")
	SpireTest.eq(SpireGear.damageBonus(SpireGear.state(s)), 0, "no familiarity bonus")
	bag:remove()
end)
```

- [ ] **Step 2: Run the boot test.** Expected: the three tests FAIL.
- [ ] **Step 3: Implement** with `item:setCustomAttribute("sb_gear", id)`, `"sb_tier"`, `"sb_fam"`, `"sb_awake"`; name and attack/armor via the existing `ITEM_ATTRIBUTE_*` calls. Delete the old `SpireGear.find/give` users or point them at the new table.
- [ ] **Step 4: Run the boot test.** Expected: PASS, no new errors.
- [ ] **Step 5: Commit** "Weapons keep their tier and familiarity on the item".

### Task 3: Kills fill familiarity and style; damage bonus in combat

**Files:**
- Create: `server/data-spirebound/lib/spirebound/style.lua` (pure style rules)
- Create: `server/data-spirebound/scripts/spirebound/progression.lua` (kill event, damage hook, login reminder hook point)
- Modify: `server/data-spirebound/scripts/spirebound/spells.lua:1469` (call `SpireProgress.onDealt` next to `SpirePerks.onDealt`)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_progression.lua`

**Interfaces:**
- Consumes: `SpireGear.*` (Task 2), `SpireGearData.style`, `STYLE_POINTS`, `PASSIVES`.
- Produces:
  - `SpireStyle.get(player) -> { points, stage = 1..3, level = 0..10, path = key|nil, final = key|nil }`
  - `SpireStyle.levelOf(points) -> stage, level` (pure)
  - `SpireStyle.addPoints(player, n)`; announces level ups and "choice ready" in plain English
  - `SpireStyle.choose(player, key) -> ok, message` (refuses unless stage level 10 and `key` is an option)
  - `SpireStyle.passiveBonus(styleState, context) -> number` (pure; context = `{ distance, isBoss, race }`)
  - `SpireProgress.killShare(rawXp, partySize) -> number` (pure), `SpireProgress.counts(player, target, weapon) -> bool` (pure-ish)
  - `SpireProgress.onDealt(attacker, target, amount) -> amount` (familiarity + style passive + trophies)

- [ ] **Step 1: Write the failing tests**: `levelOf` at 0, at each stage edge, past the end (3,10); `killShare(100, 1) == 100`, `killShare(100, 4) == 25`; `counts` is false for a player target, a Pen Rat, a non-class weapon and a summon's kill; `choose` refuses before level 10 and refuses a key from another class; after `choose`, `get().path` is the key and a second `choose` of the other path is refused; `onDealt` returns `100 * (1 + 0.09)` for a weapon at familiarity 6 with no style passives.
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement.** Points per kill = monster type's base experience (before stages and bonuses) split by party share; familiarity points go to the weapon in hand, style points to the character. Register the kill event for every player at login (like `quests.lua` does).
- [ ] **Step 4: Run the boot test.** Expected: PASS.
- [ ] **Step 5: Commit** "Kills raise weapon familiarity and the style tree, and both add damage".

### Task 4: Hearth Shards drop, and the Weaponsmith upgrades, reforges and re-issues

**Files:**
- Modify: `tools/gen_monsters.py` (shard loot per ground grade from `SpireGearData`/`gen_gear.py`: Rough on every Floor 1 monster except Pen Rat, Cut on the harder half, Flawless on group-ground monsters, the Old Watchtower and elites), rerun it
- Modify: `tools/gen_economy.py` (shard values and upgrade fees; every class still earns at its grounds)
- Modify: `tools/gen_npcs.py` entry `hearthgate_weaponsmith` (keywords `upgrade`, `reforge`, `replace`)
- Modify: `server/data-spirebound/lib/spirebound/gear.lua` (add rules)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_gear_weapons.lua`

**Interfaces:**
- Produces: `SpireGear.upgradeCheck(state, def, counts, gold) -> ok, cost|message` (pure; `counts` = shards the player holds by grade and floor), `SpireGear.upgrade(player, item) -> ok, message`, `SpireGear.reforge(player, item, family) -> ok, message` (tier kept, familiarity 0, fee), `SpireGear.reissue(player) -> ok, message` (main weapon at tier 0 for a fee, only if the player holds no main weapon of that floor).

- [ ] **Step 1: Write the failing tests**: upgrade 0→1 with 3 Rough and the fee succeeds and takes exactly 3 shards and the fee; 2→3 with Rough only is refused naming Cut shards and where they drop; tier 5 refused ("already at its best"); Floor 1 shards on a Floor 2 weapon refused; shop item refused; nothing taken on any refusal; reforge keeps tier and resets familiarity; reissue refused while holding the weapon.
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement**, regenerate monsters and NPCs, run `python tools/gen_economy.py --check` and `python tools/balance.py --check`.
- [ ] **Step 4: Run the boot test.** Expected: PASS. Also talk to the Weaponsmith in the client with the GM character (`upgrade`) once.
- [ ] **Step 5: Commit** "Hearth Shards drop on Floor 1 and the Weaponsmith turns three into a tier".

### Task 5: The Floor 1 path (Dorrow's weapon, the quests, Gate Hound, Axe-Lord awakening)

**Files:**
- Modify: `server/data-spirebound/lib/spirebound/quests.lua` (new reward kinds `weapon_choice`, `temper`, `armour`; re-order quests so Dorrow's level-10 offer, the temper quest (~15) and the armour quest (~20) form the story line; each `step`/`report` names giver and place)
- Modify: `server/data-spirebound/npc/quest_dorrow.lua` via `tools/gen_quest_npcs.py` (the family choice: "bow", "crossbow", "spear"...)
- Modify: `server/data-spirebound/scripts/spirebound/bosses_floor1.lua:224-227` (Gate Hound: 3 Cut shards once per credited character; Axe-Lord: awaken the Floor 1 weapon of every credited character; drop `lastTopFighter`)
- Modify: `server/data-spirebound/scripts/spirebound/gear.lua` (rare drops become alternative Floor 1 weapons; boss piece drop removed)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_floor1_path.lua`, update `test_r12.lua`, `test_quests.lua`

**Interfaces:**
- Consumes: `SpireGear.make/state/setState`, `SpireBoss.credited`.
- Produces: `SpireGear.awaken(item) -> ok` (sets `awakened`, awakened name and attack), `SpirePath.FLOOR1` = ordered list of `{ key, text, done(player) -> bool, where }` used by Task 6.

- [ ] **Step 1: Write the failing tests**: a level 9 character is refused by Dorrow, level 10 gets a weapon of the chosen family and the right vocation; finishing the temper quest raises that weapon one tier; the armour quest gives the class's Floor 1 armour; Gate Hound credit gives 3 Cut shards once (second kill gives none); Axe-Lord credit awakens a main weapon and a rare-drop weapon alike, for every credited name; every `SpirePath.FLOOR1` step's `where` is non-empty.
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run the boot test.** Expected: PASS.
- [ ] **Step 5: Commit** "Floor 1 weapon path: Captain Dorrow at level 10, two quests, the Gate Hound and the Axe-Lord's awakening".

### Task 6: The "Next upgrade" window

**Files:**
- Create: `server/data-spirebound/lib/spirebound/upgrade_view.lua` (pure text builder)
- Modify: `server/data-spirebound/lib/spirebound/journal.lua` (tab `upgrade`), `client/modules/game_spirebound/journal.lua` (tab `{ 'upgrade', 'Upgrade' }` first, pt/es labels, Commands entry `!upgrade`)
- Create: `server/data-spirebound/scripts/spirebound/upgrade_command.lua` (`!upgrade` opens the tab; `!style` shows the tree; `!style choose <path>` then `!style confirm`)
- Modify: `server/data-spirebound/scripts/spirebound/progression.lua` (login reminder: the "Next" line once per login)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_upgrade_view.lua`

**Interfaces:**
- Consumes: `SpireGear.state`, `SpireStyle.get`, `SpirePath.FLOOR1`, `SpireTrophies.found(player)` (Task 7; until then an empty list).
- Produces: `SpireUpgrade.lines(view) -> {string}` (pure; `view` = `{ weapon, armour, path, style, trophies }`), `SpireUpgrade.nextLine(view) -> string`.

- [ ] **Step 1: Write the failing tests**: with no weapon at level 4 the next line is "Reach level 10, then see Captain Dorrow at Hearthgate's north gate."; with a tier 1 weapon and 1 Rough shard it names "2 more Rough Hearth Shards" and "any Floor 1 hunting ground"; at tier 2 it names Cut shards and their grounds; with every step done and tier 5 it says to look at Floor 2's weapons; hidden mini-bosses never appear unless found; the window matches the spec 4.7 sections (WEAPON, ARMOUR, FLOOR 1 PATH, STYLE, TROPHIES); every line fits the window width (≤ 90 characters).
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement**; `!style choose` asks twice before it locks; `python3 tools/check_commands.py` passes.
- [ ] **Step 4: Run the boot test.** Expected: PASS. Open the Journal's Upgrade tab in the real client with the test Ranger and take a screenshot for Jay.
- [ ] **Step 5: Commit** "Next upgrade window: the Floor 1 checklist, your weapon, your style".

### Task 7: Four hidden mini-bosses and their trophies

**Files:**
- Modify: `tools/gen_monsters.py` (4 mini-bosses, original names, solo-at-level tuning), rerun
- Modify: `maps/floor1_plan.py` / `maps/scenery.py` (4 hidden spots off the roads, map rules from CLAUDE.md), `tools/mapgen.py` run; render with `python tools/maprender.py`
- Modify: `server/data-spirebound/lib/spirebound/secrets.lua` (each spot is a secret, tier medium)
- Create: `server/data-spirebound/lib/spirebound/trophies.lua`, `server/data-spirebound/scripts/spirebound/minibosses.lua` (respawn at a random 1-3 h, credit list, trophy once per character)
- Create: `docs/gm/floor1_minibosses.md` (GM only; spots and `/pos` lines)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_minibosses.lua`

**Interfaces:**
- Produces: `SpireTrophies.LIST` = `{ {id, boss, name, effect = {kind, value}} }`, `SpireTrophies.found(player) -> {ids}`, `SpireTrophies.grant(player, id) -> bool` (false if already had), `SpireTrophies.bonus(player, context) -> number` (read by `SpireProgress.onDealt`; speed and max-health trophies applied at login).

- [ ] **Step 1: Write the failing tests**: grant is once per character; each trophy's effect changes the number it promises; respawn delay is always within 3600-10800 s; each spot is a registered secret; no spot is within 2 tiles of a road (use the map plan data).
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement**, render each spot and look at it.
- [ ] **Step 4: Run the boot test.** Expected: PASS. Kill one mini-boss in the client with the GM character's test Ranger and check the trophy appears in the Upgrade tab.
- [ ] **Step 5: Commit** "Four hidden mini-bosses on Floor 1 that leave a permanent trophy".

### Task 8: Style signature abilities, stage 1

**Files:**
- Modify: `server/data-spirebound/lib/spirebound/sword_skills.lua` / `spells.lua` and `tools/gen_spellbook.py` (one stage-1 signature ability per class, unlocked at style stage 1 level 10, following DESIGN 6.7)
- Test: `server/data-spirebound/scripts/spirebound/tests/test_progression.lua`

**Interfaces:**
- Consumes: `SpireStyle.get`.
- Produces: `SpireStyle.hasAbility(player, abilityKey) -> bool`.

- [ ] **Step 1: Write the failing tests**: each class's ability is refused below stage 1 level 10 and works at it; it appears in the spellbook data.
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement.** Add two new roadmap tasks (rule: cut work becomes a task): "Style path abilities (8, stage 2)" and "Style final abilities (16, stage 3)"; they are reached on Floors 4-8, after the alpha.
- [ ] **Step 4: Run the boot test.** Expected: PASS. Cast each ability once in the client via the spell autopilot route.
- [ ] **Step 5: Commit** "Each class's first style ability".

### Task 9: Shop starter gear and the Mastery Respec

**Files:**
- Modify: `server/data-spirebound/lib/spirebound/shop.lua` (kinds `gear` and `respec`; catalog test allows stats only on `gear` items made from `SpireGearData.shop`)
- Modify: `server/data-spirebound/scripts/spirebound/shop.lua` (delivery; respec use)
- Modify: `server/data-spirebound/scripts/spirebound/tests/test_shop.lua`
- Add a GM command `/givegear <player> shop` for testing while the shop is off

**Interfaces:**
- Produces: `SpireStyle.respec(player, now) -> ok, message` (clears `path` and `final`, keeps `points`; refused if the last respec was < 7 days ago, item not used up on refusal).

- [ ] **Step 1: Write the failing tests**: the catalog test fails if any non-`gear` item has attack/defense/armor, and if a `gear` item beats the Floor 1 main weapon at tier 2; respec keeps points and stage, clears choices; a second respec within 7 days is refused and the respec item stays; respec is never in any loot table, NPC shop or quest reward (scan the generated data).
- [ ] **Step 2: Run the boot test.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run the boot test.** Expected: PASS.
- [ ] **Step 5: Commit** "Shop starter gear that Floor 1 weapons outgrow, and the shop-only Mastery Respec".

### Task 10: Crafting off the gear path; every material names its source

**Files:**
- Modify: `server/data-spirebound/lib/spirebound/crafting.lua` and `tools/gen_economy.py` (remove any gear recipes), `tools/junk_prices.py` and `server/data-spirebound/npc/hearthgate_junk_trader.lua` (drop stock materials no Spirebound monster drops, like poisonous slime)
- Create: `tools/check_materials.py` (every item in any Floor 1 loot table, recipe or NPC buy list has a description naming its monster and ground; no recipe or NPC asks for an item nothing drops); call it from `tools/test_boot.sh`

- [ ] **Step 1: Write the check** and run it. Expected: FAIL listing the stray materials.
- [ ] **Step 2: Fix the data**, rerun generators.
- [ ] **Step 3: Run** `python tools/check_materials.py` then the boot test. Expected: PASS.
- [ ] **Step 4: Commit** "Crafting is no longer a gear path, and every material says where it drops".

### Task 11: Whole-path check in the real game, docs, and Jay's checklist

**Files:**
- Create: `tools/autopilot_routes/floor1_gear_path.json` (fresh Ranger: level 10 at Dorrow, pick bow, temper quest, a shard upgrade at the Weaponsmith, open the Upgrade tab)
- Modify: `server/data-spirebound/scripts/spirebound/tests/test_e2e.lua` (restart check: tier and familiarity still on the weapon after a save and reload of the player)
- Modify: `ROADMAP.md` / `ROADMAP_DONE.md` (P1), `PROGRESS.md`, `WEEKLY_REPORT.md` (under-an-hour checklist for Jay), `BESTIARY.md` if it lists drops

- [ ] **Step 1: Run** `python tools/autopilot.py floor1_gear_path` with the server running. Expected: the report shows the weapon received, tier 1 after the upgrade, and the Upgrade tab screenshot.
- [ ] **Step 2: Run the boot test.** Expected: PASS including the restart check.
- [ ] **Step 3: Write** the playtest checklist and progress entry; tick P1.
- [ ] **Step 4: Commit and push** "Gear progression playable on Floor 1: checklist for Jay".
