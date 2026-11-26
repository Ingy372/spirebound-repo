# Hand-off: Floor 1 fixes from Claude's party playtest (2026-11-26)

For the Opus session that fixes these. Jay will have Fable audit everything afterwards, so each item says how to
check it. Full notes and numbers: `docs/playtests/2026-11-26-claude-party-floor1.md` (still being written by the
playtest session, which is playing on toward the Gate Hound and the Axe-Lord).

**Source of the findings.** Three brand-new characters (Pilot Bram, Vanguard; Pilot Fern, Mystic; Pilot Wick,
Arcanist) played from level 1 in the Arrival Yard to level 23-25 on Jay's live server, through the real path,
real shops and real quests, no `/pilot` level or teleport shortcuts. Played with `tools/claude_play.py --as` and
`tools/party_play.py` (new: a party that hunts laps, banks, shops, heals and takes quests on its own).

**Ground rules while the playtest is still running.**
- Don't restart Jay's live server (`/root/sb`) until the playtest session says it is done; use `tools/test_boot.sh`
  (it boots a copy on shifted ports) for checks.
- Don't edit `tools/party_play.py`, `tools/claude_play.py`, `client/modules/game_autopilot/` or the playtest notes
  file: the playtest session is using them.
- Rules from CLAUDE.md apply as always (plain-English commits, `check_names.py`, boot test, PROGRESS entry,
  ROADMAP tasks for anything cut).

---

## Needs Jay (not code)
1. **The floor race already looks won.** Every login says "Floor 3 is sealed... No one has broken through the Pass on
   Floor 2 yet" (left over from the overnight test kill, PROGRESS 2026-11-26 midday). Jay types `/floor reset 2`
   then `/floor reset 1` with his GM character before any real player logs in. Remind him in the weekly report.

---

## P1: bugs that break the game for real players

### 1. Quest gear drops on the floor when the player is over capacity (silently)
- **Seen:** Hunter Brannoch's reward "Hearthward Mail" never reached the tank's bag; it was lying on the tile at
  his feet (the test client picked it up from there). The tank's Hearthguard Sword from Captain Dorrow vanished the
  same way at level 10 (the saved character has no Spirebound-tagged item anywhere). The tank was over his carrying
  limit both times (looted meat, see 6).
- **Cause:** `SpireGear.make` (`server/data-spirebound/lib/spirebound/gear.lua` ~133) calls `into:addItem(d.base, 1)`.
  For a Player, Canary's `addItem` defaults to `canDropOnMap = true`, so an item that can't be carried lands on the
  floor and later decays. Callers: Dorrow's weapon (`gear.lua` ~174, `scripts/spirebound/gear.lua` ~150/169),
  quest armour, boss rewards (`giveBossReward`), shop sets (`scripts/spirebound/shop.lua` 15-16), reforges (~261).
  Check `quests.lua` rewards and any other `player:addItem` used for important rewards too.
- **Fix:** when `into` is a player, call `addItem(d.base, 1, false)`; if it returns nil, send the item to the
  player's store inbox (or refuse and say "Make room or lighten your load first, then ask again": Dorrow already
  has that line for the nil case). Also tell the player where it went.
- **Also:** Dorrow hands out the weapon only once. Give players a way to get a lost barracks weapon back (Dorrow
  re-issues it for a fee; `SpireGearData.REISSUE_FEE` = 2000 already exists).
- **Check:** in-game test: a character over capacity gets Dorrow's weapon -> it is in the inbox (or refused), never
  on the floor. In the client: overload a test character, take a quest reward, look at the floor and the bag.

### 2. Buying with "Ignore capacity" ticked takes the gold and gives nothing
- **Seen:** health potions (135 gold) and ham (40 gold) paid for, nothing in the bag, inbox or stash (database
  checked after a logout). Clean retest: one bread with the box ticked vanished; unticked, it arrived.
- **Cause:** Canary 3.6.1 `npc:sellItem(... ignoreCap ...)` creates the item and then charges; the item is lost in
  between. Every Spirebound NPC passes the player's tick straight through:
  `npc:sellItem(player, itemId, amount, subType, 0, ignore, inBackpacks)` in 64 files under
  `server/data-spirebound/npc/`, written by `tools/gen_npcs.py`: fix the generator and regenerate.
- **Fix:** pass `false` for `ignore` everywhere.
- **Check:** in the client, buy with the box ticked: item arrives or "not enough capacity", never money lost.
  Related: when a player can't carry the purchase the engine prints "Bought 0x health potion for 0 gold coin";
  if the NPC script can check capacity first, say "You can't carry that much" instead.

### 3. Iron for the Stair (part of the Stair Key) can't be earned while hunting as a party
- **Seen:** after a lap of 79 Burrow Moles hunted together, the mole quest (Iron for the Stair 1 of 2) stood done
  for the tank, 8/25 for the healer and 0/25 for the damage dealer. Same for Dorrow's wasps (12 / 4 / 0). The
  Stair Key needs Iron 2 of 2 for each character, so two of three party members are locked out of the Axe-Lord.
- **Cause:** `SpireQuestKill` (`server/data-spirebound/scripts/spirebound/quests.lua` top) only fires for the
  engine's killer (most damage / last hit).
- **Fix:** credit every party member who shares experience and is on the same floor within ~30 tiles of the kill
  (`SpireProgress.sharers` in `lib/spirebound/progress.lua` already computes exactly this set: reuse it). Apply to
  all kill quests, tasks and bounties that count kills the same way (check `tasks.lua`, `daily.lua`).
- **Check:** in-game test with a 3-Pilot party: each member's count goes up on a kill. The Ram and Gate Hound pieces
  already credit the whole damage map (`scripts/spirebound/stair_key.lua`), no change needed there.

### 4. Auto-loot is off for every new character
- **Seen:** 23+ kills each and no gold reached the bag: Canary only auto-loots after `!autoloot on`, and nothing in
  the game says so (one FAQ line in the Journal). New players leave all loot in the bodies unless they open each one.
- **Fix:** switch the feature on at a character's first login (`player:setFeature(Features.AutoLoot, 1)`, see
  `data/scripts/talkactions/player/auto_loot.lua` in the Canary data), and mention `!autoloot off` in the Journal.
- **Check:** a fresh character's first kill puts the gold in the bag.

### 5. Mastery and weapon familiarity silently need the barracks weapon in hand
- **Seen:** the tank (weapon never held, then lost) has no Mastery points at level 21 ("Vanguard Mastery 0/10");
  the two who equipped theirs have points.
- **Cause:** `SpireProgress.countsPure` (`lib/spirebound/progress.lua`) requires a Spirebound weapon of your class.
- **Fix (pick one, Claude's call):** put Dorrow's weapon straight into the hand (old weapon to the bag), and/or show
  "Hold your Hearthguard Sword to grow Mastery" on the Journal's STYLE line when it isn't held.
- **Check:** fresh level-10 character: weapon in hand after Dorrow, Mastery points rise on kills.

---

## P2: new-player traps and economy

6. **Meat fills your capacity.** Autoloot picks up meat (wolves, boars, moles), no Hearthgate NPC buys it, and at
   13 oz each it put the tank over capacity by level 15 (then purchases and loot failed: "The loot you are trying to
   pick up is too heavy for you to carry"). Let Innkeeper Roan buy meat (a few gold), or keep it out of autoloot.
7. **Coins fill the backpack.** Looted gold arrives as stacks of 100 gold coins: by level 15 nine of the tank's 20
   slots were coins and the next purchase failed. Options: set `autoBank = true` in `server/config-overrides.lua`
   (Canary: "the dropped coins from monsters will be automatically deposited to your bank account"; default false),
   or have Pell's {gold} topic and the Journal teach "deposit all" at the bank. (Shops already take
   the price from the bank: checked.)
8. **Dorrow's weapon lands in the backpack with no word.** The Journal then ticks "[x] get your weapon" while its
   WEAPON line says "none yet". With item 5 above, put it in the hand or say "it's in your backpack: drag it into
   your hand". The barracks weapons and the quest armour also share their base item's name and look ("sword",
   "snakebite rod", "brass armor"), so a bag with two looks like two of the same thing: give them their own names
   in the bag view if possible (market name / look).
9. **Dorrow asks "Which kind: {rod}?" with one choice** for Mystics and Arcanists, and "yes" isn't an answer. With
   one family, just hand it over.
10. **Early money is very tight.** After the Proving each character had ~250 gold (one restock); at levels 7-9 each
    had 0-6 gold. At Boar Meadow a level-10 party of three earned ~430 gold per hour in total (before the autoloot
    fix in our run, so partly item 4). Re-check after 4 and 6; compare with potion prices (health 45, mana 50).
11. **The Proving is pitch-black.** It is underground and new characters have no light: half the screenshot is solid
    black. Light the hall and pits, or put a torch in every starter kit (only some kits have one).
12. **`!spells` before a path.** The yard gate says "Say !spells to see the skills and spells each path will teach
    you", but before the Registrar the answer is "Choose a path... first". Make `!spells` show each path's first
    spells there, or change the gate's line.
13. **Burrow Hills' quiet gate side.** Walking only the west side near the gate gave 5k experience per hour (the
    gate is quiet by design); the monsters are all east. A sign at the gate ("the warrens are east") would stop
    players deciding the ground is empty.
14. Small: the Skills panel shows "XP Gain Rate 7290%" from level 1 (confusing); the Registrar's walk-to point is
    outside his door, where talking to him gives "Come back when you are ready to choose."

## P3: balance (measure solo before changing; Jay decides big moves)

15. **Burrow Hills pays far too much.** Through its east end and caves a level 16-19 party made 138-143k experience
    per hour each (79 moles, no elite), almost 3x Wolf Copse (47-56k) at the same levels, on a ground banded 11-16,
    with no danger. Suspect today's faster respawns (commit 558b8779) on a swarm ground. Measure solo with the
    autopilot, then tune Burrow Hills' density/respawn or mole experience in the generators (`tools/gen_monsters.py`,
    `maps/floor1_plan.py`), never the tables by hand.
16. **Levelling is fast for parties.** Level 3 -> 19 in about 2h45m of play including town trips; the target is ~12
    hours to level 35 solo. Fine if parties are meant to race ahead; check the solo pace with the autopilot.
17. **The solo/class grounds never threatened a party** (no deaths from level 3 to 21; the healer's party heal was
    never needed below 65%). The first deaths came at the Bandit Road (group ground, Bandit Captain elite: 55-61 per
    swing on a 260-health Mystic, 8 monsters in sight). That matches the design; just confirm with Jay that the solo
    grounds are meant to be this safe for groups.
18. **Health potions look weak late in the band.** A level-21 Vanguard in brass gear, drinking every 2 seconds and
    casting Second Wind, lost to a pack of four Road Bandits in ~20 seconds (40-50 damage per 2 s). Check potion
    strength against Floor 1's 19-30 band damage (`tools/balance.py`).
19. **No sting to dying below level 50** on Normal (no experience lost, by design: `Difficulty.youngGraceText`). Note
    for Jay's "challenge" goal: Floor 1 deaths cost only the walk back.

## P4: party play

20. **Loot goes to the kill credit**, so the tank ends up with all the gold (1,250 vs 56 for the healer, who then
    can't buy mana potions). The bank's "transfer X to name" works (the test party used it), but nobody will know.
    Teach it, or add a shared-loot party option.

## Things checked and fine (no work needed)
- Guide Pell's quest and report with three players at once; every attacker in the pen gets First Blood credit.
- Starter kits (5 health, 5 mana potions, 5 ham, path weapon) arrive; the Registrar handles three players.
- Bramblejaw: each character dropped to 36-44% health, one potion, about a minute: about right.
- NPC trading (with "ignore capacity" off), bank deposit/transfer, NPC purchases paid from the bank balance.
- Wolf Copse's Grey Alpha elite (7,425 experience each), Rally Cry, Mend Other, Hearth Ration all work in play.
- Death and respawn at the temple, and the "young climber" no-loss message.

## Not yet tested (the playtest session is doing these now)
Stonehorn Ram, Gate Hound, the labyrinth, the Axe-Lord, Old Quarry, Fallen Bastion, Smugglers' Ridge, Bramble Run,
the Watchtower, the escort quest, the Old Sluice puzzle. Their findings will be added to the playtest notes file.
