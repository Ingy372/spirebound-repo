# Hand-off: fixes from the Floor 1 review (2026-11-26)

For the session that fixes these. The full reasoning, numbers and file references are in
`docs/reviews/floor1-review-2026-11.md` (finding ids like A4-2, B4-1 below point into it). Jay asked for this list to be
handed over while the review session keeps testing.

## UPDATE (review session, same evening): confirmed by test with a real character on commit `fff7d60b`

Do these first; they are worse than anything in Group 1.

- **T1. The weapon damage bonus never applies (was Group 2, B4-0). CONFIRMED.** 26 of 26 hits (20 real melee swings and
  `doTargetCombatHealth` with spell, melee and ranged origin) reached `SpireProgress.onDealt` as a negative amount and
  came back unchanged. A tier-5 awakened Stairlord's Edge (power 1.61) dealt the same as bare hands. Fix the sign
  handling there, in `SpirePerks.onDealt` and in any "damage taken" guard; test with a real hit. Then re-measure the
  Axe-Lord (his tuning today was measured without the bonus).
- **T2. Experience callbacks are ignored. CONFIRMED.** Canary 3.6.1 treats `playerOnGainExperience` as void (its own
  `data/scripts/eventcallbacks/README.md`). A Death Game character and a botting character (xpFactor 0.45) each gained
  exactly the normal 378 from a 56-experience kill. Affected: `difficulty_events.lua` (Hardcore, Death Game, cavebot,
  Siege, Hunting Focus), `beacons.lua`, `events.lua`, `boost.lua`. `playerOnGainSkillTries` is listed void too (double
  skill gain below 50, Hardcore skill debt): test it. Apply the factors in the engine's `Player:onGainExperience`
  (`data/events/scripts/player.lua`, via `server/core-overrides`), and check the `bonusXp` bookkeeping does not charge
  players for bonus experience they never got.
- **T3. The cavebot loot cut crashes on every kill. CONFIRMED.** `scripts/spirebound/cavebot.lua` line 46:
  `item:isStackable()` does not exist ("attempt to call method 'isStackable' (a nil value)"). Botting gave 42.1 coins
  a kill against 42.4. Use `ItemType(item:getId()):isStackable()`; test through the real drop; then check the cut runs
  before autoBank moves the coins.
- **Correction to Group 1 item 3 (Hardcore).** A level-15 Hardcore death lost 7.5% experience: the experience penalty
  works. Do not add one. Only the item risk is off below level 21 (blessings are handed back at each login); that is a
  question for Jay.
- **Numbers for item 15.** Real experience per kill = base x stage x 1.5 (below level 50) x 1.5 (stamina above 39 h):
  22.5x at levels 1-8, 9.0x at 9-20, 6.75x at 21-50; 4.5x at 21-50 with stamina below 39 h. Coins per Road Bandit: 42.3
  measured over 120 kills (loot rate 2), model 33.5.
- **A lesson for every fix here:** 281 in-game tests passed while T1-T3 were broken, because the tests call the pure
  rule with made-up inputs. Each fix needs a test that goes through the real event with a real creature
  (`tools/loadtest.py` + `tools/loadbot.py` can log a real character in on a test copy).

## Ground rules
- `CLAUDE.md` applies as always: change generators, not generated files; `python3 tools/check_names.py`; boot test after
  each task; plain-English commits; PROGRESS entry; anything cut becomes a ROADMAP task.
- **The review session is still running tests.** It uses its own test copy in WSL (`/root/sbreview`, ports 7471/7472,
  database `spirebound_review`). Don't touch those. Use `/root/sbtest` for your boot tests as usual.
- Don't edit `docs/reviews/floor1-review-2026-11.md` (the review session updates it). You may commit it as you find it.
- Don't restart Jay's live server for these unless a client check needs it (then back up first, as always).
- **Three groups below.** Do group 1 now. Group 2 items are suspected from reading the code: the review session is
  testing them and will message you with the result; start them only after that message, or after you have reproduced
  the problem yourself with a failing test. Group 3 needs Jay: write each as a question in `QUESTIONS.md` with the
  recommendation given here, and build nothing until he answers (except where it says "assume").
- Every fix gets an in-game test that goes through the real path (the real NPC, kill event or map spot).

---

## Group 1: confirmed by reading the code. Fix now, in this order.

### 1. Vanguard barracks weapons are weaker than shop swords (B4-1) — High
- Hearthguard Sword/Axe/Mace are built on plain `sword` (attack 14), `axe` (12), `mace` (16)
  (`lib/spirebound/gear_data.lua`, from `tools/gen_gear.py`). Garrick sells a longsword (17) for 160 gold and a spike
  sword (24) for 8,000 (`tools/gen_npcs.py`). Melee and sword skills scale with weapon attack
  (`scripts/spirebound/sword_skills.lua` line 30). A maxed, awakened barracks sword equals attack 22.5.
- Fix: give the three barracks weapons one attack and defence of their own, written onto the item in
  `SpireGear.setState` the way armour already is (suggest attack 20 at tier 0, +1 per tier, defence 15; Claude's call,
  note it in QUESTIONS.md for Jay's veto). Same for the shop "Climber's Sword" (keep it below the barracks weapon).
  Remove the spike sword from the Floor 1 Weaponsmith.
- Test: no weapon a Floor 1 shop sells out-damages the tier-0 barracks weapon of the same class.

### 2. Rare-drop weapons: perks not built, drop far too common (B4-2) — High
- `perk` / `perkValue` (life leech, crit, mana leech, heal) exist only as data; nothing reads them. The Briarguard
  Sabre's base (sabre, attack 12) is below the main sword. `DROP_CHANCE` 3% applies to Ruin Sentinels (48 spawns) and
  Stonehorn Rams (42) as well as elites, random class, no pity.
- Fix: build the four perks (small, as specified in the gear spec 4.5) or remove them from the data and the item text;
  same base attack as the main weapon; drop 0.5% from Grey Alpha, Bandit Captain and Stonehorn Ram only; the looter's
  own class twice as likely as each other class.

### 3. Hardcore has no downside before level 21 (A8-1) — High
- The engine's adventurer's blessing (all blessings up to level 21) means a Hardcore death costs no experience and no
  items, while Hardcore still gets +25% experience and +15% loot.
- Fix: Hardcore and Death Game characters do not keep the starter blessing (remove it at login / after it is given);
  Hardcore's loss applies from level 8. Test: a level-15 Hardcore death loses experience; a level-15 Normal death
  still loses nothing.

### 4. Death Game characters can be made unkillable (A8-2) — High
- `SpireDeathGame.judge` (`lib/spirebound/deathgame.lua`) saves a character when (a) the killing monster hit any
  non-party, non-guild, other-IP player in the last 30 s, or (b) such a player did 15% of the victim's health in the
  last 60 s. Two friends hunting side by side unpartied trigger (a) all day; in boss rooms a friend can do (b).
- Fix: (a) no "dragged in" save when the victim had also damaged that monster (it is on the monster's damage map);
  (b) outside damage only saves when the outside player was the aggressor (the victim had not attacked them first in
  that window) or is skulled. Tests for both, and the existing R5 tests must still pass.

### 5. The floor unlock can silently never fire (A4-5) — Medium
- `Floors.onlyTesters` decides by name prefix ("Pilot ", "Spell "); real players can use those names. Decide by the
  test account's e-mail instead (as `/pilot` does), or reserve the prefixes in `tools/name_rules.py` and the sign-up.
- `SpireBossDeath` returns early when the boss has no fight record (after a script reload): no credit, no unlock, and
  the boss is never scheduled to return. Rebuild a record from the damage map, log loudly, always schedule the return.

### 6. Gate Hound is a launch-day queue (A4-3) — Medium
- 30-minute return, at most 20 credited, 2% share needed; every climber needs the credit for the Stair Key.
- Fix: return after 10 minutes (`SpireBoss.REPEAT_RESPAWN` is shared with the floor boss: give the field boss its
  own), credit at 1% for field bosses.

### 7. Axe-Lord coins go to one player (A4-6) — Low
- One body. Pay each credited fighter directly (suggest 10 platinum each via the bank) and shrink the body's coins.

### 8. Labyrinth spawns (A1-1) — High, map work
- 4 Ruin Sentinels, 4 Ruin Archers, 5 Ruin Sentinels across three 43x31 mazes (`maps/layout_floor1.py` ~890-892).
- Fix: about 12 per level in mixed packs (sentinel + archer + hexer), away from the teleports; render and check.
  Then roadmap N1 still has to walk it.

### 9. Three new grounds have no trail in the plan (A1-2) — Medium, map work
- `python tools/wilds_plan_check.py` prints "NO TRAIL TO" for the Bramble Run, Smugglers' Ridge and the Fallen Bastion
  gates. Add trails and junction signposts; done when it prints "problems 0". (That checker rewrites
  `docs/FLOOR1_WILDS_PLAN.png`; `tools/hunt_check.py` rewrites `docs/previews/*.png`.)

### 10. Small money and reward leaks — Low, one commit each or together
- Sealed Shrine pays 1,000 gold to every character (`scripts/spirebound/secrets.lua` REWARDS.sealed_shrine): use the
  once-per-account rule the other secrets use.
- Secret item rewards and the Underkeep strongbox gem use plain `player:addItem` (can land on the floor when
  overloaded): use `SpireGive.reward`. Same for the fishing catch (`scripts/actions/tools/fishing.lua` land()).
- Underkeep strongbox and the daily login streak pay per character: make them per account.
- "Tempered in the Field" gives +1 tier at any tier, so it can be saved to skip tier 5 (3 flawless shards + 6,000
  gold): the temper only works below tier 2 (say so in Dorrow's line).
- `SpireGear.reforgeWith` takes the fee before creating the new weapon and keeps it if creation fails: refund.
- Flawless shards: the Stonehorn Ram drops them at the elite rate (3.52%) and there are 42 Rams. Give the Ram its own
  lower rate (suggest 1%) in `tools/gen_gear.py`.

### 11. Fishing (A7-1, A7-2) — Medium/Low
- Night fish use the real clock (`os.date`) while secrets use the game's hour: use `SpireSecrets.gameHour()`.
- No delay between casts and a 5-platinum purse make fishing a safe, macro-friendly gold source: 2 s between casts,
  purse 2 platinum at weight 1. (The review session is measuring the real rate; adjust if it messages other numbers.)

### 12. Text that misleads new players (A5-2, A9) — Low
- Quest directions disagree with the map: the Bandit Road is north-east (four quests say east); use one wording each
  for Wolf Copse and the Old Quarry (`lib/spirebound/quests.lua`; positions in `maps/floor1_plan.py` CAMPS).
- A one-line message at level 9 that experience now comes slower (10x to 4x), and the Journal says which grounds and
  Stair Key steps need a group (Bandit Road, Gate Hound, Old Watchtower).

### 13. Donation items must survive a season (S-1) — do before the shop opens
- Outfits and mounts are re-granted from the account at login; furniture, decorations and the Spire Manor deed are
  plain items / a house and are wiped. Re-deliver owned shop items to the Store Inbox at a new character's first
  login; last owner of the Manor gets first refusal. Add to the season rehearsal check.

### 14. Dev commands ship in the live datapack (A6-2) — Low
- `/pilot` and the load-test commands are locked only by account e-mail. Load `dev_*.lua` only when a test-server
  switch is set (as `dev_loadbot.lua` already does with `SPIRE_LOADTEST`), without breaking the autopilot on Jay's PC.

### 15. Make the models tell the truth (E-1, A3-1) — Medium, tools only
- `tools/gen_economy.py` `drop_value` ignores `rateLoot = 2` (the engine doubles every chance, capped at 100%).
- The levelling ladder ignores the engine's stamina bonus (1.5x) and low-level bonus
  (Canary `data/events/scripts/player.lua` ~597-601).
- Put both in, regenerate `ECONOMY.md` / `BALANCE.md`, and list what no longer passes. **Do not retune drops or
  stages yet**: that is Jay's choice (group 3, questions 3 and 4).

---

## Group 2: suspected. Wait for the review session's test result.

- **B4-0 The weapon damage bonus may be skipped on most hits.** `SpireProgress.onDealt`
  (`lib/spirebound/progress.lua` ~85) returns the amount unchanged when it is `<= 0`, but damage reaches that hook as
  a negative number for most hits (see the comment at `scripts/spirebound/bosses_floor1.lua` ~145 and
  `scripts/spirebound/spells.lua` ~1440). `SpirePerks.onDealt` beside it may share it. If confirmed: work on the size
  and keep the sign; test with a real monster, with and without a tier-5 weapon.
- **CB-2 Are a cavebot user's coins halved before `autoBank` moves them to the bank?**
- **A2-4 Can Underkeep wings be reached without their teleport** (Skystep, rope spots)?
- **A6-1 The "2 hours of play-time protection"** from DESIGN.md 6.4: not found in the PvP scripts.
- **A3-1 size of the engine's experience bonuses** at levels 2-50.

## Group 3: needs Jay. Put in QUESTIONS.md with these recommendations; don't build.

1. **PvP inside boss rooms below level 50** (A4-2): today anyone can attack anyone in the Pass arena and the
   Axe-Lord's hall (`lib/spirebound/pvp.lua` lines 154, 161). Recommendation: boss-room PvP from level 50 only.
2. **Q78 the Axe-Lord's party size** is still unanswered; roadmap N1 (a real run) proves him.
3. **Floor 1's length**: keep the engine's experience bonuses (shorter floor) or the 11-15 hours?
4. **Loot rate 2**: keep the richer real game, or trim drops to match the documents?
5. **Item names**: do Tibia's item names ("magic plate armor", "wand of vortex") fall under "no CipSoft names"?
6. **Upgraded gear tradable to any level** (B4-9): add a level requirement by tier?
7. **Mastery respecs only in the donation shop**: add a steep in-game gold route?
8. **Spear Rangers have no barracks weapon** (B4-3): add a Trailwarden Spear (recommended) or drop spears?
9. **Underkeep Wing 1 size** (A2-1): about 18 monsters today; recommendation about 50, three kinds, one mini-boss, one
   secret inside each wing.
10. **Solo players and the Stair Key** (A3-2, A5-1): 30 Road Bandits on a group ground. Recommendation: pairs on the
    Bandit Road's outer loops (assume this; it also needs Q73's answer for Boar Meadow).
11. **A guild can fill the 20-player boss hall** (A4-4): cap per guild, or a second hall?
12. **Private boss hall without the Stair Key** (A4-7): keep as a catch-up or require the key?

## Not for this hand-off (already on the roadmap)
PT3 (Burrow Hills pays 3x; solo pace), N1 (the real full run), Q73 / 10.4 (Boar Meadow), R10b (a gold sink such as
repairs), server-side cavebot detection, fishing's unbuilt pieces (message bottles, hidden spots, a buyer for fish).
