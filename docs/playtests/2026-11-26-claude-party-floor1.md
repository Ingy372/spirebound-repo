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

### Hunting grounds
(per ground: experience and gold per hour, supplies, deaths, feel)

### Quests and the Stair Key

### Bosses

### Economy and supplies

### Small things
- The Skills panel shows "XP Gain Rate 7290%" from level 1. A new player will not know what that means.

## Numbers
(table from `python tools/party_play.py report`)
