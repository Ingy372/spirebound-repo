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

### Quests and the Stair Key

### Bosses

### Economy and supplies

### Small things
- The Skills panel shows "XP Gain Rate 7290%" from level 1. A new player will not know what that means.

## Numbers
(table from `python tools/party_play.py report`)
