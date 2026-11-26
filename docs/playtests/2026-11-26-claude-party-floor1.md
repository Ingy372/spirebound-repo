# Claude's Floor 1 party playtest, 2026-11-26

Asked by Jay: "do a playthrough and use 2-4 characters... clear the entire first floor and make detailed notes about
what can be improved... make sure the characters are using everything the game provides". These notes are for the
Fable review and final Floor 1 audit, then Jay's own solo playtest.

## The party
Three brand-new characters, made at level 1 in the Arrival Yard, played through the real path (no `/pilot` shortcuts):

| Tag | Character | Path | Role |
|---|---|---|---|
| tank | Pilot Bram | Vanguard | front line, taunts |
| heal | Pilot Fern | Mystic | heals the party |
| dps | Pilot Wick | Arcanist | damage, area spells |

They are named "Pilot ..." on purpose: a test character can never open a floor or claim a first clear, so the
Axe-Lord kill can't spoil the real race.

## How it was played (method)
- Arrival Yard, Registrar and the Proving: move by move with `tools/claude_play.py` (now runs several clients at once,
  `--as <tag>`), reading the screenshots.
- The hunting: `tools/party_play.py` (new). All three walk the same planned path as a pack through each ground's loop
  points, surface and cave, fight, and every lap is logged (experience, gold, potions, food, deaths) to
  `.local/claude_play/party_laps.jsonl`. When supplies run low the party walks to town and really trades: sells loot
  to Trader Osric, buys potions from Alchemist Ivo and food from Innkeeper Roan.
- The test client was taught to play like a player for this: eats food (and casts Hearth Ration when out), drinks the
  best potion it has, heals party members (Mend Other, Mass Mend...), casts taunts and party buffs, buys and sells
  through the trade window, and gets back up after a death.

## Findings (most important first)
(filled in as the run goes)

### Needs Jay
1. **The floor race already looks won on your server.** Every login says "Floor 3 is sealed. No one has broken
   through the Pass on Floor 2 yet". That is left over from the overnight test kill (PROGRESS, 2026-11-26 midday).
   Fix: with your GM character, type `/floor reset 2` then `/floor reset 1` (about a minute). Must be done before
   any real player logs in.

### Serious bugs
1. **Buying from a shop with "Ignore capacity" ticked takes the gold and gives nothing.** Checked in the database
   after a logout: 3 health potions (135 gold) and 5 ham (40 gold) paid for, nothing in the bag, inbox or stash.
   A clean retest: one bread with the box ticked vanished; with it unticked it arrived. The engine (Canary 3.6.1,
   `npc:sellItem` with ignoreCap) makes the item and then charges, and the item is lost somewhere in between. Every
   Spirebound shopkeeper passes the player's tick straight through (`npc:sellItem(player, itemId, amount, subType, 0,
   ignore, inBackpacks)` in every `server/data-spirebound/npc/*.lua`). **Fix: pass `false` for `ignore` in all of
   them** (players then simply can't overbuy past their capacity, as in real Tibia), then retest a purchase with the
   box ticked. Until then any player who ticks the box loses money with no sign of why.
2. **Auto-loot is off for every new character.** Canary only loots for you after `!autoloot on`. Nothing in the yard
   says so (one line in the Journal's FAQ). My party killed 23 monsters each before I noticed that no gold or loot
   was reaching the bag: everything stays in the bodies unless you open each one. DESIGN.md 15 lists autoloot as a
   feature, and Jay's level-12 note ("no gear progression") fits a player who never loots. **Fix: switch it on for
   every new character** (set the feature at the first login, or at the Registrar), and teach `!autoloot off`.

### Arrival Yard and first hour
- **Launch crowding: one pen, three Proving pits, one Registrar.** Three players in the pen at once took turns on
  the same few rats (kill credit is shared, so nobody got stuck, but it was slow). The Proving has three pits with a
  5-minute limit each. A launch evening with 50+ new players at once will queue here. Check with the load test (N2/9.2).
- **The Proving is nearly pitch-black.** It is underground and a new character has no light: in the screenshot the
  bottom half of the screen is solid black. Give the hall and pits their own light, or hand out a torch with the kit.
- **`!spells` before a path says nothing useful.** The gate says "Say !spells to see the skills and spells each path
  will teach you", but saying it before the Registrar answers "Choose a path with Registrar Maelis... first". The gate
  opens anyway. Either show each path's first spells, or change the gate's line.
- **The walk-to point for the Registrar is outside his door.** A player standing there who talks to Maelis gets
  "Come back when you are ready to choose." Inside, it works.
- Good: Pell's quest and report work for three players at once; every attacker gets the kill credit; the starter kits
  (5 health and 5 mana potions, 5 ham, path weapon) arrive; Bramblejaw took each character down to 36-44% health
  with one potion each and died in about a minute: about right.

### Level 10: Captain Dorrow's weapon
- **The barracks weapon lands in the backpack, and nothing says to equip it.** After Dorrow hands it over, the
  Journal's Upgrade tab ticks "[x] Reach level 10 and get your weapon" but its WEAPON line still says "none yet:
  Captain Dorrow gives one at level 10". A new player will think it didn't work. Put it in the hand (the old starter
  weapon into the bag), or have Dorrow say "it's in your backpack: drag it into your hand".
- For Arcanists and Mystics, Dorrow asks "Which kind: {rod}?" with only one choice, and "yes" is not an answer.
  With one family, just hand it over.
- The new weapon has the same look and market name as the starter one (the bag shows two "snakebite rod"s), so a
  player can't tell which is which without looking at each one.
- **ROOT CAUSE FOUND: quest gear drops on the floor when you are over your carrying limit, with no message.**
  `SpireGear.make` (lib/spirebound/gear.lua) uses `into:addItem(d.base, 1)`; for a player, Canary's `addItem`
  defaults to `canDropOnMap = true`, so when the character is over capacity the item lands on the floor under them.
  Proven: Hunter Brannoch's reward "Hearthward Mail" did not appear in the tank's bag (he was over capacity from
  looted meat); the test client then found it lying on the tile at his feet and picked it up. This is almost
  certainly also what happened to his Hearthguard Sword at level 10 (it would have rotted away on the floor of the
  north gate). Every caller is affected: Dorrow's weapon (gear.lua:174), quest armour, boss rewards, shop sets
  (shop.lua:15-16), reforges (gear.lua:261). **Fix:** call `addItem(d.base, 1, false)` and, when it returns nil,
  send it to the player's store inbox or refuse with "Make room or lighten your load first" (Dorrow's handler already
  has that line for the nil case). Then retest with a character carrying too much.
- **The tank's Hearthguard Sword vanished (cause above, details kept for the record).** Dorrow gave it at level 10 ("It's
  yours"), tempered it at level 17 ("one tier stronger"), but at level 21 the Journal says "WEAPON: none yet" and
  the saved character has no Spirebound-tagged item anywhere (bag, hand, inbox, depot): only the plain starter sword
  and a looted mace. In between: a solo death on the Bandit Road at level 21 (with all five blessings, so no item
  drop expected) and several sell trips (Trader Osric doesn't buy plain swords). Dorrow only hands it out once, so
  a player who loses it is stuck without the Floor 1 weapon path. Worth a log line whenever a Spirebound item is
  removed, and a way to get it back from Dorrow.
- **Jay watching (2026-11-26): "he still has the basic sword and gear that he started with".** True up to level 21:
  my test script bought only potions and food, never armour, so the party played under-geared (partly the test,
  partly that nothing in the game nudges you to the armorer). Fixed from level 21 on: the script now buys the best
  affordable gear each town trip and wears anything better found in the bag. The tank went from leather to brass
  armour and legs, chain helmet, brass shield and longsword for about 920 gold. The armorer's best is brass at
  level 21; nothing between brass and the 8,000-gold spike sword for a Vanguard's weapon.

- **Mastery and weapon familiarity only grow while the barracks weapon is in your hand** (`SpireProgress.countsPure`
  needs a Spirebound weapon of your class). The tank never held his (it went to the bag, then vanished), so at level
  21 he has no Mastery points at all: "Vanguard Mastery 0/10", no stance at Mastery 5, nothing. The healer and the
  damage dealer, who equipped theirs, are earning points. A player who leaves the weapon in the bag silently gets
  no style progress for the whole floor. Show "equip the Hearthguard Sword to grow Mastery" in the Journal's
  STYLE line when it isn't held.

### Test method note (so the numbers are read right)
- Up to level 21 the test client cast mostly its first, cheapest attack spell plus weapon skills: the Arcanist never
  cast forked arc, ember barrage or fireburst wave, the Mystic never cast hailshards or frost wave, the Vanguard
  never cast shield bash or rending blow. Experience per hour up to level 21 is therefore a floor, not a ceiling.
  Fixed at level 21 (Jay asked: "is everyone using all the best spells?"): the client now picks an area spell for
  crowds and the strongest affordable spell otherwise, and the healer keeps a mana reserve. Gear was fixed at the
  same point (see above).

### Money in the first hours
- **Characters are broke at levels 3-10.** After the Proving they had ~250 gold each; one restock (5 health potions
  at 45) took it all. At level 7-9 each had 0-6 gold. At Boar Meadow (level 10, party of 3) the party earned 67 gold
  in a 9-minute lap, about 430 gold an hour for three players, while a health potion costs 45. Part of this is the
  auto-loot problem above (the first ~25 kills each were never looted). Re-check gold per hour after the fix, but
  early loot looks thin next to potion prices.
- Loot goes to the character who gets the kill credit, so in a party the healer and the tank-swapping damage dealer
  earned nothing while the tank got everything (heal +0, dps +0, tank +67 in one lap). Normal for Tibia (players
  split by hand), but unless the party splits, the healer is the poorest member. Worth a thought: an optional
  shared-loot party setting, or check whether one exists and teach it.

### Party play
- **The Stair Key can't be earned in a party (blocks the floor's main path).** The Axe-Lord's hall needs each
  character's own Stair Key, and one of its three pieces is Hunter Brannoch's "Iron for the Stair" (25 Burrow Moles,
  then 30 bandits), credited per kill. Hunting as a party, the tank lands the kills: after a lap of 79 moles the
  tank's count was done, the healer's 8/25 and the damage dealer's 0/25. A real party that hunts together will
  find two of its members locked out of the floor boss. (The test party split up to finish it, as real players
  would once they work it out.) Same fix as below, and it matters more here than anywhere. The other two pieces are
  already party-friendly: the Stonehorn Ram and the Gate Hound credit everyone on the boss's damage map
  (`scripts/spirebound/stair_key.lua`, `SpireGear.giveBossReward`); only the Iron quests use per-kill credit.
- **Quest kills don't count for the party.** `SpireQuestKill` (scripts/spirebound/quests.lua) credits only the
  character the engine gives the kill to (most damage / last hit). After hunting together, Dorrow's wasp quest stood
  at 12/12 for the tank, 4/12 for the healer and 0/12 for the damage dealer. Floor 1 tells players to group up, but a
  party has to farm each kill quest three times over, and the healer (who never lands the kill) almost never finishes
  one. **Fix: credit every party member within ~30 tiles who shares experience**, like the experience itself.
- **Gold piles up on one character.** Loot goes to the kill credit, so the tank had 1,250 gold while the healer had
  56 and could not buy mana potions. The bank's "transfer X to name" works (used it to share), but a new party won't
  know it. Teach it, or offer a party loot split.
- **Coins fill the backpack.** Looted gold arrives as stacks of 100 gold coins; by level 15 the tank's 20-slot bag
  held nine of them plus loot, and the next shop purchase failed ("There is not enough room"). Canary can send
  looted gold straight to the bank; worth switching on, or teaching the banker's "deposit all" early (Pell's {gold}
  topic could say it).
- **"Bought 0x health potion for 0 gold coin."** When a player can't carry what they buy, the engine prints that
  instead of saying why. With 25 looted meat the tank was over his carrying limit. Replace it with "You can't carry
  that much" if the NPC script can check first.

### Hunting grounds
(per ground: experience and gold per hour, supplies, deaths, feel)
- **Boar Meadow, party of 3 at level 10:** 9.4-minute lap (surface loops and the cave), ~25,900 experience per hour
  each with shared experience, no deaths, one health potion used in the whole lap. Comfortable for a party; the
  boars drop 1-13 gold plus meat and ham. A second lap at level 11: 7.8 minutes, 25-28k experience per hour each,
  no potions, no deaths: the party never felt pressure here.
- **Waspgrass Fields, party at level 12 (top of its band):** 9-minute lap, 13-16k experience per hour each, no
  potions, no deaths. Half of Boar Meadow's rate at the same level; fine as a ground the party has outgrown.
- **Wolf Copse, party at level 13:** 8.6-minute lap, 47-51k experience per hour each, one mana potion, no deaths.
  Nearly twice Boar Meadow. A party of three is never in danger on the solo grounds; Jay's "challenge, not calm"
  note (2026-11-25) can only be judged on the group grounds (Bandit Road, Old Quarry, the Watchtower) and solo.
  A later lap gave one kill worth 7,425 experience each (an elite, Grey Alpha by the `!hunt` tip), plus a rough
  Hearth Shard drop.
- **Burrow Hills, party at level 16-19, through its east end and caves:** 17-minute lap, **138-143k experience per
  hour each**, 79 moles and one boar, a handful of potions, no deaths. That is almost three times Wolf Copse for the
  same party, on a ground banded 11-16, with no elite. **Likely over-rewarding** (maybe today's faster respawns,
  commit 558b8779, on a ground built as a swarm). Re-measure solo before changing. (A first lap that only walked the
  quiet west side near the gate gave 5k per hour: the gate area is quiet by design, so a player who doesn't explore
  east will think the ground is empty. A sign at the gate pointing east would help.)
- **Levelling speed:** the party went from level 3 to 19-20 in about 2 hours 45 minutes of play, including town
  trips and quest walks. The balance target is about 12 hours to level 35 solo; a party with shared experience runs
  far ahead of it.

- **Bandit Road solo (Vanguard level 21):** died twice. First in starter leather. Second in brass armour, legs,
  shield and a longsword, starting at 25% health: four Road Bandits at once dealt 40-50 damage every 2 seconds while
  he drank a health potion every 2 seconds and cast Second Wind; dead in about 20 seconds. The ground is "mixed" and
  its packs are clearly meant for groups, which matches the design; but a health potion's heal looks small next to
  a 4-bandit pack's damage at that level. Worth checking potion strength against Floor 1's late-band damage.
- **Healer and damage dealer as a pair at Burrow Hills (level 19-21):** 16-minute lap, 81-92k experience per hour
  each, no deaths, the healer used 10 mana potions keeping both up, both earned their own loot (+565, +281 gold).

- **The Bandit Road, full party at level 23-25 (first real challenge of the run):** 20.6-minute lap, 119-151k
  experience per hour each, the healer and the tank died once each in the cave; the healer used 21 mana potions,
  the damage dealer 23 mana and 9 health potions. The healer died to the **Bandit Captain** (elite) with 8
  monsters in sight and 4 on her: the Captain hit a 260-health Mystic for 55-61 per swing. This is what Jay's
  "challenge, not calm" asks for. Caveats: the test party walks as a clump, so the healer stood in front instead
  of behind the tank, and the damage dealer had been split off upstairs; a well-played party would do better. Still,
  a 2-elite group ground for levels 19-27 that kills a level-25 party of three looks about right for "group" content.
  Note "From level 50 on, a death costs experience": below 50 these deaths cost nothing, so the challenge has no
  sting until Floor 2.
- **Second Bandit Road lap: full party wipe** (levels 23/25/25, on the surface by the road at about (1352, 1181)).
  The Bandit Captain again: the Arcanist died first, out of mana, taking 39-52 per Captain hit; the healer next with
  four bandits on her (Dewfall healing 39 against 27-per-hit bandits); the tank last, to the Captain, while drinking
  strong health potions. Two Captain fights, two losses. Dorrow's "The Lost Patrol" asks for two Bandit Captains
  from level 19 (`quests.lua` q1_2): at 19 that looks out of reach for a normal party; consider minLevel 24-25, a
  weaker Captain, or saying "bring a group of four" in the offer. (Same caveat: the test party clumps, so the healer
  stands in reach.)

### Weight and junk
- **Autoloot fills your capacity with meat.** Moles, boars and wolves drop meat (13 oz each), autoloot takes it, and
  no Hearthgate NPC buys it. By level 15 the tank carried 25 meat, couldn't buy potions ("Bought 0x"), and then
  couldn't loot ("The loot you are trying to pick up is too heavy for you to carry"). Either let an NPC buy meat
  (the innkeeper, for the stew pot), or keep food out of autoloot.

### Quests and the Stair Key

### Bosses

### Economy and supplies

### Small things
- The Skills panel shows "XP Gain Rate 7290%" from level 1. A new player will not know what that means.

## Numbers
(table from `python tools/party_play.py report`)
