# Floor 1 test results (2026-11-26)

For Jay. These are tests of everything the Floor 1 review (`docs/reviews/floor1-review-2026-11.md`) could not check.
Every result comes from real characters logged in to a private copy of the server, not from made-up inputs.
This session tested and reported only. It changed no game code or maps.

**How I tested.** I used a private copy of `main` in WSL (`/root/sbreview`, ports 7471/7472, database
`spirebound_review`). It was first built from `1dcedca2`. Once the fix session had landed its changes, I rebuilt it
from `46016cc7` and re-ran everything that those changes touch. At the end I re-tested every broken item on
`c654cde3`, the newest `main` at the time of writing. Scripted test characters log in over the real game
protocol (`tools/loadbot.py`) and send what a client sends: talk, NPC talk, the attack packet, fight modes and
use-item packets. A temporary test script, which is not in the repo, moves them one real step at a time with the
engine's own `player:move`, so stairs, teleports, secrets and doors fire exactly as they do for a player. It also has
monsters and players hit them through the real damage events. Then I read what the server logged. The test files and
logs are kept outside the repo, in WSL `/root/tester_logs/` and this session's scratchpad.

Each result says which commit it was tested on. **(fixed since)** means it was broken on the old commit, works on the
new one, and I re-tested it myself.

## Needs fixing (most serious first)

Everything in this list was still broken on `c654cde3`, except the Pass gate, which the map work has fixed (item 1).

1. **Anyone with a floor perk errors on every hit and loses their weapon bonus (item 7).** Once you choose a perk from
   Registrar Maelis, every hit on a monster gives "Lua Script Error ... perks.lua:57: attempt to call method 'isBoss'".
   The perk does nothing, and the error also stops the weapon power and the rare-weapon perk for that hit. A perked
   climber hits like bare hands. Still on current `main`. Sent to the fix session.
2. **A Death Game character can still be saved by a friend in a boss room (item 9).** An unpartied friend starts the
   fight and hits the victim for 20% in the Axe-Lord's hall (PvP is open there below level 50). A monster then kills
   the victim: "saved, not retired". The fix session closed the other two tricks, but not this one. Sent. It may be a
   question for Jay: recommendation below.
3. **PvP damage is never recorded (item 8).** The script that notes who hurt a player drops every hit, because damage
   arrives as a negative number. So the "10% of the damage" kill credit and the outnumbered shield never count anyone
   but the killer. Sent.
4. **`!private` lets a character without the Stair Key fight the Axe-Lord (item 10).** Once Floor 2 is open, a keyless
   character standing by level 3's teleport says `!private` and is put in the private hall with the boss. It is no
   route to Floor 2 (the hall only leads back to level 3), but it hands out repeat boss kills. Sent.
5. **The "2 hours of play-time protection" in DESIGN.md 6.4 does not exist (item 8).** Only the level-50 rule exists.
   A design gap, not a bug: build it or drop it from DESIGN.md.
6. **Small money leaks still open (items 11, 13):**
   - Ground chests pay their first-time reward to every character on an account. A second character on the same
     account got the full 3,450 gold and items again. That is 34,500 gold plus potions and shards per extra character.
   - The Well Vein secret gives 10 platinum (1,000 gold) as an item, so it skips the "secret gold once per account"
     rule. A second character on the same account got the 1,000 again.
   - Hunting-task gold is put in the backpack (`addMoney`), not the bank. With a full backpack part of it is lost:
     Rhen said "490 gold" and the character received 400, twice in two tries.
7. **Death Game loot bonus looks bigger than designed (item 6):** +45% coins measured against +30% designed (300
   kills each). Worth a longer measurement before changing anything.
8. **Smaller things:** after a reforge the new weapon goes to the backpack, not the hand, so "upgrade" and !upgrade
   see no weapon until you move it back (item 12). The fishing collection log is kept per character, though
   DESIGN.md 8.2 says account-wide (item 4). A Mastery Respec Scroll bought in the shop is lost in a season wipe,
   unlike the shop's outfits, mounts and furniture (item 15): probably fine, since it is used up on a character, but
   worth one line in the shop text.

Fixed during this session and re-tested here: the Pass gate (item 1), a boss dying with no fight record (item 10),
"Spell"/"Pilot" names (item 10), the Death Game hit-back and dragged-monster tricks (item 9), and the Underkeep
strongbox, Sealed Shrine and login streak paying once per account (items 2, 11, 13).

## Results by item

### 1. The labyrinth: WORKS now (the gate was broken until the map work)
Tested on `1dcedca2`; the gate re-tested on `c654cde3`.
- **The three levels can be walked.** A real level-60 character went from the Pass arena to level 1's teleport
  (1250,1040,7), arrived on level 2 (1212,1013,6), walked to level 2's teleport, arrived on level 3, walked to level 3's
  teleport and landed on the hall door (1231,1035,4). Each level is one connected area: level 1 has 13,391 walkable
  tiles, levels 2 and 3 have 836 each. Each level's only exits are its teleports up and back.
- **The Stair Key door turns a keyless character back:** it lands on the door and 0.1 s later stands at 1251,1040,5,
  beside level 3's teleport.
- **The door can't be bypassed:**
  - Teleporting straight onto the door tile: sent back.
  - Logging in while standing on the door tile (the character was saved there): it came in at 1251,1040,5, sent back.
  - Skystep: no tile on level 3 has a Skystep spot at all. All 544 tiles of the hall are inside the boss-room zone,
    which Skystep refuses. The hall's only exit is the teleport back to level 3.
  - `!private`: see item 10. It lets a keyless character in once Floor 2 is open.
- **The Pass gate (fixed since).** On `1dcedca2` the gate boulders (1232,1070 and 1233,1070) were in place and
  `Floors.isLabyrinthOpen(1)` was false. Even so, the shortest path from the arena to level 1 goes round them and
  crosses the gate's row at **1244,1070**: 116 steps, through 1233,1088, 1244,1083, 1244,1053 and 1234,1043. The
  character really walked it. On `c654cde3`, with the boulders back in place, there is **no path** from the arena to
  level 1: fixed.

### 2. The Underkeep: WORKS
Tested on `1dcedca2`.
- **The grate secret:** a real step onto the grate (1182,1303,7) recorded the secret and put the character at the
  Underkeep entry (1180,1250,8).
- **The strongbox can be reached on foot** from the entry (it walked to 1240,1251,8). It pays: +1,333 gold by a real
  click (use-item packet), and nothing for a second character on the same account (since `5fec5bd4`, also checked by
  the fix session's own test).
- **No wing can be reached without its teleport.** I mapped every walkable tile of each wing: wing 1 3,005 tiles,
  wing 2 2,187, wing 3 2,763, wing 4 1,810, wing 5 1,431, wing 6 1,621. Each wing has exactly one way out (its return
  teleport), and no wing reaches another on foot, although wings 1 and 2 share level 8. There are no stairs, holes,
  rope spots or ladders inside any wing. I checked every tile of every wing for a Skystep spot (up or down, every
  direction, with the spell's own rules): there are none.
- **The boulder/teleport swap:** with Floor 2 opened in the test database, wing 2's door turned from a boulder into a
  teleport to 1250,1255,8 within the 60-second check. It turned back into a boulder within 60 s of closing Floor 2.
  A restart with Floor 2 open also comes up with the teleport.
- Note: wings 3-6 need Floors 4, 6, 8 and 10, and those are sealed by the friends-test scope, so they stay boulders for
  now. That is as designed.

### 3. The newest grounds on foot, and spawns: WORKS
Tested on `1dcedca2`.
- **On foot from the Hearthgate temple, with real steps:** the Bramble Run gate took 27 s (271 steps), Smugglers'
  Ridge 36 s (354 steps), the Fallen Bastion 26 s (257 steps). A path search also found a walking route from the
  temple to every one of the 15 Floor 1 ground gates, the Pass arena (211 steps) and the Old Watchtower (395 steps).
- **Spawns (monsters alive at startup against the plan's number):** Reedmarsh 23/23, Bramble Run 21/21, Thornsnap
  Hollow 15/15, Old Quarry 24/24, Smugglers' Ridge 17/17, Fallen Bastion 16/16, and every other ground at or above
  its number. The startup log has no spawn or monster errors. The Old Watchtower is the Stonehorn Ram's apex spot and
  is not a walled ground: its three Rams are in the spawn file and the path to it exists.
- Small note: Boar Meadow shows 28 alive against 16 planned and Toad Pond 71 against 66, because neighbouring
  monsters stand inside their boxes.

### 4. Fishing: WORKS (measured with real use-item packets, not the drawn client)
Tested on `46016cc7` (after the fishing fix `b15bd927`). Two characters used a real rod on the river by Millcross
(rod at 1121,1213, water at 1124,1213) every 2.1 s for 5 minutes, which is how fast an attentive player or a macro
can go now.
- **Skill 10** (it rose to 19 during the test): 24 catches in 5 minutes, about **290 an hour**: 10 minnows, 10 perch,
  1 carp, 1 mudskipper, 2 trout.
- **Skill 52:** 29 catches in 5 minutes, about **350 an hour**: 17 minnows, 6 perch, 4 carp, 2 mudskippers, 2 old
  boots.
- **Gold an hour:** only the sunken purse pays gold (2 platinum, weight 1 of about 107). That comes to about 550-650
  gold an hour at either skill. No NPC buys fish from players (the innkeeper only sells "fish" for 6), so the fish
  themselves are worth nothing in gold. The two samples had no purse and no pearl.
- **Delay between casts:** since `b15bd927` a new cast needs 2 s. The fix session's own test showed a recast 0.7 s
  later refused and one 2.7 s later going out. On my copy that test once failed: the 2.7 s cast hit "your line is
  already in the water" from the first cast's bite. That is the test's timing, not a bug.
- **Night fish:** they now follow the game's clock, not the PC clock. That clock runs fast: in my 5 minutes the game
  hour went from 22 to 10, so a game day lasts about 10 real minutes and "night" (20:00-05:00) about 4 of them. The
  night secret uses the same clock.
- Note: the fishing collection log is stored on the character, though DESIGN.md 8.2 says it is account-wide.

### 5. Skill gain: WORKS
Tested on `46016cc7`.
- **Twice as fast below level 50:** the engine's own skill path (`Player:onGainSkillTries`, fixed in `41a83ef8`)
  gives 20,000 tries for 1,000 at level 30 against 10,000 at level 55. That is the engine's 10x skill rate, then x2
  below 50. Real sword fighting agreed: every real hit of a level-30 character counted double.
- **Hardcore skill debt:** a real Hardcore death at level 30 with sword 63 cost a level (29) and a sword level (62).
  At the next login it set a sword debt of 1,406 tries. A character with a 3,000-try debt then fought for real for
  40 s: its 20 tries all went to the debt (3,000 -> 2,980), and its sword tries did not move.

### 6. Loot bonuses: WORKS (Death Game looks high)
Tested on `1dcedca2`. The loot code did not change after that. Each character killed 300 Road Bandits through the
real kill path, and I counted the coins that reached its bag and bank:

| Character | Coins | Per kill | Against Normal | Designed |
|---|---|---|---|---|
| Normal | 13,190 | 44.0 | - | - |
| Hardcore | 15,195 | 50.7 | +15% | +15% |
| Death Game | 19,071 | 63.6 | **+45%** | +30% |
| Normal, all 4 Beacon fires lit | 16,077 | 53.6 | +22% | +20% |

The extra loot roll (`monsterOnDropLoot`) really fires. Death Game is 4-5 times further from its design than the
random spread of 300 kills would explain. Worth a 1,000-kill check before anyone changes it.

### 7. Damage hooks: PARTLY (damage taken works; any floor perk breaks damage dealt)
Tested on `1dcedca2`; the perk error is still in `perks.lua` on current `main`.
- **Damage taken, with exact hits of 100 from a monster:** plain 99 (1 for armour). With the maxed Bulwark/Ironwall
  style 83 (factor 0.84, as designed). With Iron Will 91 (-8% physical); a fire hit stays 99, also as designed. With
  both, 76. Real Road Bandit swings arrive negative (6 of 8 hits; the other 2 were zero) and are reduced the same way.
- **BROKEN: damage dealt with any floor perk.** Without a perk a 100 hit dealt 100. With Executioner, a 100 hit on a
  monster at 20% health dealt 100, not 110, and every hit logged "attempt to call method 'isBoss' (a nil value)" at
  `scripts/spirebound/perks.lua:57`. Canary 3.6.1's MonsterType has no `isBoss`. The perk hook runs before the weapon
  bonus and the rare-weapon perks in the same damage event, so the error skips those too. That means **every player
  who takes a perk loses their weapon bonus.**

### 8. PvP: PARTLY
Tested on `1dcedca2` and `46016cc7`.
- **Below level 50, in the Pass arena and the Axe-Lord's hall: yes, they can hurt each other.** Both places are
  "boss room" zones. Spirebound's rule allowed the attack (30 against 30, `canAttack` true), and a real hit landed
  (49 of a 100 hit; the engine halves PvP damage). In town no damage got through. In the open the rule refused 30
  against 30, as designed.
- **BROKEN: PvP damage is never recorded.** Right after a hit of 49 the PvP damage record showed 0, every time.
  `scripts/spirebound/pvp.lua` does `math.max(0, primaryDamage)` on a negative number.
- **The "2 hours of play-time protection" (DESIGN.md 6.4) does not exist.** The PvP rules check only the level-50 line,
  and no script tracks play time.
- Could not test: a full fight with real auto-attacks between two players. My scripted characters send the client's
  attack packet with secure mode off, and the rule allowed it, but the engine dropped the target and no hit landed.
  Against a monster the same packet works. The cause is probably my scripted client, not the game, but only the real
  client can confirm. A 5-minute check for Jay: two characters below 50 hit each other in the Pass arena.

### 9. Death Game "saved" loopholes: PARTLY
Tested on `46016cc7`, after the fix `da66e020`. Death Game victims were killed by a real monster hit after the setup:

| Setup | Result | Right? |
|---|---|---|
| The victim fought the monster, and the monster also hit an unpartied friend | retired | yes (the trick is closed) |
| The victim never touched the monster, which had hit another player | saved (dragged in) | yes, as designed |
| The victim hit the friend first and the friend hit back for 20% (boss room) | retired | yes (closed) |
| **An unpartied friend starts the fight and hits the victim for 20% in the Axe-Lord's hall** | **saved** | **no** |
| No other player involved (control) | retired | yes |

On the old commit (`1dcedca2`) the first trick did not save the victim either, because the friend's hit was too small
to count. The fix session's own test reproduced it and closed it. **The boss-room trick is still open:** two friends
can arrange for one to "attack" the other in any boss room, where PvP is allowed below 50, and the victim then can't
die for good. Recommendation: in boss rooms, damage from an unskulled player should not save a Death Game character.
Or ask Jay.

### 10. Boss edge cases: PARTLY
- **A boss that dies with no fight record (as after a script reload): fixed since.** On `1dcedca2` the Gate Hound
  never came back after such a kill (a normal kill came back on time). On `46016cc7` it is credited from the engine's
  damage list and comes back. (Respawn was shortened to 15 s on the test copy to see it.)
- **A party whose names all start with "Spell ": fixed since.** The name checker (`tools/name_rules.py`) accepts
  "Spell Breaker" and "Pilot Jones". On `1dcedca2` such a party killed the Gate Hound, got credit, and the labyrinth
  stayed shut. On `46016cc7` test characters are known by their account, and the same names on normal accounts opened
  the labyrinth.
- **Gate Hound credit and the Stair Key piece:** both party members who hit got the credit and their first key piece.
  The first real kill opened the gate (boulders gone, announced). A third party member who stood by and did nothing
  got no credit. Since `7cfaeb6e` you need 1% of the fight, from damage, healing or soaking hits. Being in the party
  is not enough. That looks intended.
- **BROKEN: `!private` without the Stair Key.** Tested on both commits. With Floor 2 open, a keyless character (0 of 3
  pieces) said `!private` by level 3's teleport and landed in the private hall (1229,1062,4) with the Axe-Lord. The
  private hall's only exit is the teleport back to level 3.

### 11. Secrets: WORKS (one small leak)
Tested on `46016cc7`. A character stepped onto each of the 12 trigger tiles from the tile next to it (a real step):
- **All 12 fired** and were recorded. Payouts the first time: Miller's Race 800 gold, Inn Smith 3 strong potions,
  Sealed Shrine 1,000 gold (plus two Bandit Captains), Dye Well 1,200, Empty Camp 300 plus the diary note, Well Vein
  10 platinum, Coward Pup 5 items, Gate Balcony 400. Firefly Hollow (night) gave its lit lamp when the game hour was
  night. The Underkeep and North Crack teleported, and Old Tusk woke his boss. A second visit paid nothing.
- **A second character on the same account:** the secret gold was not paid again (Miller's Race, Dye Well, Sealed
  Shrine 0). Exception: **Well Vein paid its 10 platinum again**, because it is an item reward.
- **Selling to Vesper:** "sell dye well" paid 3,000 gold straight to the bank. Selling it again: "Everyone knows that
  one already. Loadbot 1101 sold it." The sale is announced to everyone; the announcement is not logged, so I checked
  the public flag instead. A second character who had found Well Vein could still sell that one (3,000), as designed.

### 12. Gear at the Weaponsmith: WORKS (one rough edge)
Tested on `46016cc7`, through Garrick's real NPC talk (hi, upgrade, yes...):
- **Upgrade through all five tiers:** tier 1 for 3 rough shards and 500 gold, up to tier 5. Weapon power went 1.14,
  1.18, 1.22, 1.26, 1.30. Asking again at tier 5: "already at its best: tier 5".
- **Reforge:** "reforge axe", yes: "Reforged into Hearthguard Axe, tier 5. Its familiarity starts again." The tier
  is kept and the fee is paid. Rough edge: the new axe lands in the backpack and the weapon hand is empty.
- **Replace:** with no weapon left, "replace", yes gave a new tier-0 Hearthguard Sword in the hand for its fee. With
  the reforged axe still in the backpack it correctly refused ("You still carry your weapon").
- **The free temper at tier 4:** changed by the fix session (`5fec5bd4`): the field temper now works only below tier 2,
  which closes the "save it for tier 5" trick. I did not run Dorrow's 15-wolf quest itself.

### 13. Chests, login streak, hunting tasks
Tested on `46016cc7`.
- **The 15 ground chests: WORKS, but they pay per character.** Opened by real clicks: all 15 opened, first time
  +34,500 gold in total, plus potions and a rough shard each. After moving their timer back 21 hours the daily refill
  paid +460, +240 and +340 (the three tested). **A second character on the same account got the full first-time reward
  again** (chest 1: +3,450).
- **Login streak: WORKS.** Day 1 paid 100 gold to the bank. Logging in again the same day paid nothing. A second
  character on the same account the same day got nothing, which is right since `5fec5bd4`. With the day moved back,
  the next login paid day 2 (+200, streak 2; tested on `c654cde3`). Note for testers: my scripted client only really
  logs out from inside town. Elsewhere it stays in the game and the next login just reconnects without a new "login".
  That also explains why the fix session's own daily case failed on my copy.
- **Hunting tasks: WORK, per character.** Taskmaster Rhen gave "Hunt 60 Road Bandits". 60 real kills counted, the
  report paid ("490 gold and 2 task points"), and taking it again the same day was refused ("Come back tomorrow").
  **Leak:** the gold goes into the backpack, and with a full bag 90 of the 490 were lost (twice).

### 14. Every Floor 1 NPC: WORKS
Tested on `46016cc7`. All 33 Floor 1 NPCs were found on the map. Each was greeted with "hi" and asked "job", "trade",
"quest" and "bye" through the real NPC channel:
- **Every one answered "hi".** All 14 traders opened their shop on "trade". The quest givers (Dorrow, Brannoch, Agna,
  Corwin, Marrow, Vesper) answered "quest" with their quest, or "no work right now".
- **No Lua errors** from any NPC conversation, the Weaponsmith and Taskmaster runs included.
- Dead keywords: none for the words each NPC itself offers. Non-traders ignore "trade" without answering (normal for
  Tibia NPCs). Patrolman Teodric (an escort) answers only "hi"/"bye", as written.

### 15. Season wipe rehearsal: WORKS
`tools/season_wipe.sh rehearse` on a copy of the newest backup (`spirebound_2026-11-26_19-11-26`). Jay's real database
was not touched: the rehearsal loads the backup into a scratch database and drops it afterwards.
- Before: 34 characters, 2 staff, 11 accounts, 123 saved house tiles, 1,684 character records, 5 account rewards.
- After: 0 characters, 2 staff, 11 accounts, 0 house tiles, 0 character records, **5 account rewards kept**.
- **Donation-shop items across a wipe (tested on `c654cde3`, shop switched on as at launch):** a character bought the
  Hearth Cloak outfit, the Stone Hound mount, a harp kit, a candelabrum and a Mastery Respec Scroll with the real
  `!shop buy`. I moved the season on, ran the wipe on my test database, and logged in a new character on the same
  account. Result: the unspent shop coins were kept (1,460), the outfit and the mount were granted again, and the harp
  kit and candelabrum were waiting in the Store Inbox (since `d289490d`). The Respec Scroll was gone with the old
  character.

### 16. Re-tests of the landed fixes: WORKS
On `46016cc7` I ran the fix session's whole real-character suite (`tools/loadtest.py review`, 28 cases) on my own
copy. 26 pass:
- **Weapon bonus:** a 100 hit deals 90 bare-handed (Ruin Sentinels take 10% less) and 145 with a maxed Stairlord's
  Edge.
- **Experience:** 453 plain, 680 Death Game (+50%), 566 Hardcore (+25%), 203 with the cavebot on (45%).
- **The cavebot's loot cut:** 60 Road Bandits gave 1,730 coins with the cavebot against 3,256 without. Coins are
  counted in the bag and the bank together, so the cut happens before autoBank moves them. If it happened after, the
  bank would hold the full amount.
- **Beacon loot:** +22% with four fires lit (item 6). **Beacon experience** was not measured separately. It uses the
  same fixed experience hook the suite proves for the other factors.
- The two failures are timing problems in the tests, not game bugs. The daily-reward case has the same logout problem
  as my own streak test (item 13), and the streak itself works. The fishing case is explained under item 4.

### 17. General crash scan: WORKS
Tested on `1dcedca2`: `python3 tools/loadtest.py ramp --steps 10,24 --minutes 4`. 10 bots, then 24 bots, 4 minutes
each, hunting across every Floor 1 ground (about 4,300 monsters alive).
- **0 "Lua Script Error" lines** in the whole log. Lag averaged 0.3 to 0.5 ms (worst 15 ms). CPU was 9-18% of one
  core and memory 233 MB.
- My other runs found two errors the bots never trigger, because bots take no perks and don't talk: the perk `isBoss`
  error (item 7, real) and an error from my own test script, which I fixed.
- Harmless startup warnings: 27 Tibia wheel spells not found (an engine feature we don't use), and "no boosted
  boss / boosted creature" from the engine (Spirebound has its own boost script).

## What I could not test, and why

- **A real auto-attack fight between two players (item 8).** My scripted client's attack on a player was accepted by
  Spirebound's rules but dropped by the engine. Direct hits prove that damage gets through in the arena and the hall.
  A 5-minute check in the real client settles it.
- **How things look on screen** (PvP cursor colours, NPC dialogue windows, the fishing splash): the real client only.
  The live server was not restarted, so none of today's fixes are on Jay's server yet.
- **Dorrow's 15-wolf temper quest end to end (item 12)**: only the rule change was checked.
- **Beacon experience on its own (item 16)**: only the loot side was measured. The experience side uses the same hook
  that the suite proves works for Hardcore, Death Game and the cavebot.
