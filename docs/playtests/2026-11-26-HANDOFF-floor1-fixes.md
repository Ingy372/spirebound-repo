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
- **Done (fix session, 2026-11-26):** `SpireGear.make` now hands a player the piece ignoring carrying weight; with no free backpack slot it goes to the Store Inbox with a message, never the floor (`lib/spirebound/gear.lua`). Quest gold now goes to the bank (`SpireQuests.payGold`), the deliver-quest parcel uses `SpireGive.item`, and boss shards / chest prizes use the new `SpireGive.reward` (backpack, else Store Inbox). Lost barracks weapon: Garrick's existing `replace` (2000 gold) now also refunds if it can't hand it over, and the Journal says "lost: Garrick can replace it". Tests: `tests/test_party_playtest_fixes.lua` (P1-1 x2). Client check left for after the restart (ROADMAP PT1).

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
- **Done:** `tools/gen_npcs.py` never passes the tick on (`false`), and refuses a purchase heavier than free capacity with "You can't carry that much..." before the engine is asked; regenerated all 64 shop NPCs (`gen_npcs.py` + `gen_floor_content.py`). Test: "no shop passes the 'ignore capacity' tick on". Client check left (PT1).

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
- **Done:** new `SpireProgress.killCredit(key, killer, target)` (reuses `sharers`, credits each nearby party member once per kill even though onKill fires for both the top damage dealer and the last hitter). Used by kill quests (`SpireQuests.countKill`) and hunting tasks (`SpireTasks.countKill`). `daily.lua` has no kill counting; Season Path / Chronicle kill stats stay personal. Test: "a kill counts for every party member nearby, once each" (3 members, one 60 tiles away).

### 4. Auto-loot is off for every new character
- **Seen:** 23+ kills each and no gold reached the bag: Canary only auto-loots after `!autoloot on`, and nothing in
  the game says so (one FAQ line in the Journal). New players leave all loot in the bodies unless they open each one.
- **Fix:** switch the feature on at a character's first login (`player:setFeature(Features.AutoLoot, 1)`, see
  `data/scripts/talkactions/player/auto_loot.lua` in the Canary data), and mention `!autoloot off` in the Journal.
- **Check:** a fresh character's first kill puts the gold in the bag.
- **Done:** `SpireQuests.autolootDefault` switches autoloot on once per character at login (also for existing characters who never set it); `!autoloot off` sticks. Journal FAQ updated. Test: "autoloot is on for a new character, once, and !autoloot off sticks". Client check left (PT1: first kill puts the gold in the bank, see 7).

### 5. Mastery and weapon familiarity silently need the barracks weapon in hand
- **Seen:** the tank (weapon never held, then lost) has no Mastery points at level 21 ("Vanguard Mastery 0/10");
  the two who equipped theirs have points.
- **Cause:** `SpireProgress.countsPure` (`lib/spirebound/progress.lua`) requires a Spirebound weapon of your class.
- **Fix (pick one, Claude's call):** put Dorrow's weapon straight into the hand (old weapon to the bag), and/or show
  "Hold your Hearthguard Sword to grow Mastery" on the Journal's STYLE line when it isn't held.
- **Check:** fresh level-10 character: weapon in hand after Dorrow, Mastery points rise on kills.
- **Done (both options):** `SpireGear.equip` puts Dorrow's weapon (and Garrick's replacement) straight into the weapon hand, the old weapon to the backpack; falls back to backpack / Store Inbox if there is no room. Dorrow says where it went. The Journal's Upgrade view now says "not in your hand: hold it..." under WEAPON and "Mastery only grows while you hold your class's barracks weapon" under STYLE. Tests: two P1-5 tests + "upgrade view: a barracks weapon not in hand, or lost, is pointed out".

### 5b. Young Normal climbers DO lose experience on death (levels 22-49), while being told they didn't
(added 17:15, after a party wipe on the Bandit Road)
- **Seen:** Pilot Fern (Mystic, Normal) died at level 25. Server log: "You lost 19757 experience. You were
  downgraded from Level 25 to Level 24." Ten seconds later our own message: "Your death cost you no experience (you
  would have lost 19757): climbers below level 50 on the Normal rules are spared." The database confirms the loss
  (experience 195,178 = before minus 19,757; level 24). Same for Pilot Wick (25 -> 24).
- **Cause (likely):** `lose.playerOnLoseExperience` (`scripts/spirebound/difficulty_events.lua` ~22) returns 0 via
  `Difficulty.finalDeathLoss`, but Canary 3.6.1 still applies the engine's loss: either the callback's return value is
  not used, or another `playerOnLoseExperience` callback (Canary's own data, or ours) runs after it and wins. Below
  level ~21 the engine's adventurer's blessing hides the bug, which is why the G12 tests passed.
- **Fix:** find how Canary 3.6.1 really uses that callback's return (search the Canary data folder for other
  `playerOnLoseExperience` callbacks; check `Player::death` / `onLoseExperience` in the engine source on GitHub at
  tag v3.6.1). If the return can't zero the loss, give the experience back after the respawn
  (`player:addExperience(kept, false)` at login/respawn where the youngGrace message is sent, without a level-up
  message spam).
- **Check:** a Normal test character at level 30 dies to a monster -> level and experience unchanged after respawn,
  and the message is still shown. In-game test plus one real death in the client.
- **Done:** the loss hook now also writes down the experience the player should end with (`deathExpTarget`); at the next login (the respawn) `SpireDifficulty.settleExperience` gives back what the engine took (or takes the extra for Hardcore / skulls, which the engine was ignoring too). If the engine ever honours the return, nothing changes. The engine's own "You lost N experience" line at death can't be stopped from Lua; the "spared" line after the respawn is now true. Test: "party fixes P1-5b". Real death in the client: PT1.

### 5c. At levels 22-49 a death loses the whole backpack and some gear (the free blessings stop at 21)
(added 17:20)
- **Seen:** all three characters had all five blessings at level 21 (database `blessings1-5 = 1`). Their first death
  (level 23-25) used them up; at the second death they had only `blessings1`, and each lost its whole backpack
  (every potion, the gold coins in it, the loot) and roughly one piece of equipment in ten: the tank lost his
  longsword and backpack (respawned with a plain "bag"), the Arcanist her studded armour, the healer all her health
  potions. Meanwhile our message says "climbers below level 50 on the Normal rules are spared".
- **Why it matters:** a level-22+ party that wipes once loses its pocket gold, potions and some gear with no warning,
  right at the hardest part of Floor 1 (Bandit Road, Gate Hound, Axe-Lord). Players will feel cheated by the
  "spared" line.
- **Fix (Claude's call, Jay can veto):** match the promise: Normal climbers below 50 keep their items too (give them
  full blessings at login and after each death while level < 50 and Normal, or skip the drop in the death hook), and
  keep `Difficulty.ITEM_DROP_BASE` for 50+. If Jay prefers real item risk before 50, then the death message and the
  Registrar's "normal" pitch must say so, and the priest should be pointed out at level 20 ("blessings keep your
  backpack").
- **Check:** a Normal test character at level 30 with no blessings dies -> keeps backpack and gear (or, if the rule
  is kept, is told clearly before and after).
- **Done (Claude's call, Jay can veto: Q77):** `SpireDifficulty.youngBlessings` gives Normal climbers below level 50 every missing blessing at each login, so also after each respawn: no backpack or gear loss before 50. Hardcore and Death Game keep their item risk. The "spared" message now says "no experience and none of your items". Test: "party fixes P1-5c". Real death in the client: PT1.

---

## P2: new-player traps and economy

6. **Meat fills your capacity.** Autoloot picks up meat (wolves, boars, moles), no Hearthgate NPC buys it, and at
   13 oz each it put the tank over capacity by level 15 (then purchases and loot failed: "The loot you are trying to
   pick up is too heavy for you to carry"). Let Innkeeper Roan buy meat (a few gold), or keep it out of autoloot.
   - **Done:** Innkeeper Roan and Innkeeper Bess buy meat (2 gold) and ham (3 gold); Roan's greeting says so; Journal line "My backpack is too heavy!". Test checks Roan's shop.
7. **Coins fill the backpack.** Looted gold arrives as stacks of 100 gold coins: by level 15 nine of the tank's 20
   slots were coins and the next purchase failed. Options: set `autoBank = true` in `server/config-overrides.lua`
   (Canary: "the dropped coins from monsters will be automatically deposited to your bank account"; default false),
   or have Pell's {gold} topic and the Journal teach "deposit all" at the bank. (Shops already take
   the price from the bank: checked.)
   - **Done:** `autoBank = true` in `server/config-overrides.lua` (test checks the engine reads it); Journal "Where is my gold?" now says coins go to the bank. Whether the engine applies autoBank to autoloot (not only quick loot) needs the client check (PT1).
8. **Dorrow's weapon lands in the backpack with no word.** The Journal then ticks "[x] get your weapon" while its
   WEAPON line says "none yet". With item 5 above, put it in the hand or say "it's in your backpack: drag it into
   your hand". The barracks weapons and the quest armour also share their base item's name and look ("sword",
   "snakebite rod", "brass armor"), so a bag with two looks like two of the same thing: give them their own names
   in the bag view if possible (market name / look).
   - **Done:** see 5 (in hand + Dorrow says where). Own names in the bag view: not done (the engine shows the base item's look; custom names already show on look). Left as is.
9. **Dorrow asks "Which kind: {rod}?" with one choice** for Mystics and Arcanists, and "yes" isn't an answer. With
   one family, just hand it over.
   - **Done:** with one family Dorrow hands it over at once (`scripts/spirebound/gear.lua` dorrowTalk).
10. **Early money is very tight.** After the Proving each character had ~250 gold (one restock); at levels 7-9 each
    had 0-6 gold. At Boar Meadow a level-10 party of three earned ~430 gold per hour in total (before the autoloot
    fix in our run, so partly item 4). Re-check after 4 and 6; compare with potion prices (health 45, mana 50).
   - Not changed (balance): re-check after 4, 6 and 7 in the next playtest. ROADMAP PT3.
11. **The Proving is pitch-black.** It is underground and new characters have no light: half the screenshot is solid
    black. Light the hall and pits, or put a torch in every starter kit (only some kits have one).
   - **Done:** `SpireProving.light` gives 20 minutes of light when the Registrar sends a character down, on entering a pit, and on logging in inside the hall.
12. **`!spells` before a path.** The yard gate says "Say !spells to see the skills and spells each path will teach
    you", but before the Registrar the answer is "Choose a path... first". Make `!spells` show each path's first
    spells there, or change the gate's line.
   - **Done:** before a path, `!spells` shows each path's spells up to level 10 (`SpireGuide.previewLines`). Test added.
13. **Burrow Hills' quiet gate side.** Walking only the west side near the gate gave 5k experience per hour (the
    gate is quiet by design); the monsters are all east. A sign at the gate ("the warrens are east") would stop
    players deciding the ground is empty.
   - **Done:** the gate sign now ends "The warrens are east: follow the hollows away from the gate." (`maps/floor1_plan.py` BURROW `sign_hint`, map regenerated).
14. Small: the Skills panel shows "XP Gain Rate 7290%" from level 1 (confusing); the Registrar's walk-to point is
    outside his door, where talking to him gives "Come back when you are ready to choose."
   - Not done: the skills panel number is the stock client module (ROADMAP PT2). The Registrar walk-to point lives in the playtest tools, which this session may not edit.

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
