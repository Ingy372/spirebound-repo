# Floor 1 review: can Spirebound compete? (2026-11-23, overnight playtest)

*Written by Claude for Claude, at Jay's request: "do a full run of the first floor and record every hole or place that we
can upgrade... act as if we were having to compete with cyntara, or another server on the top ot list... be as detailed
as possible." This is the work list for making Floor 1 alpha-ready. Each item has an id (F1-xx) so roadmap tasks can
point at it. Measured numbers come from the autopilot playthroughs (`tools/make_playthrough_routes.py`, routes
`playthrough_<class>`), map renders (`tools/maprender.py`) and reading the code.*

**How the playthroughs were run.** A fresh Pilot of each class gets the Registrar's starter kit, talks to Guide Pell,
does the rat pen, then hunts every Floor 1 ground at the middle of its level band (two routes, 75 s of hunting on each;
`/pilot level` jumps the level so the run tests places, not the hours of walking), gets Captain Dorrow's weapon at
level 10, and tries the Gate Hound, the Old Watchtower and the Axe-Lord. The autopilot only melee/auto-attacks and
drinks potions: **it casts no spells**, so kill speed is a floor, not what a good player gets. The server ran the code
from earlier on 2026-11-23 (the restart to load tonight's fixes was not allowed); see "Caveats" at the end.

---

## 0. The short answer

**Not yet.** Spirebound has more *systems* than most servers launch with (seasons, floors that open server-wide,
difficulty modes up to permadeath, SAO cursors, a fair-PvP rulebook, houses that do things, fishing, secrets with an
info broker, a second town, a hidden dungeon, a clear gear path, 126 spells). That is a real strength and a better
pitch than "another 8.6 Baiak". What it lacks is the **feel**: the moment-to-moment hunting, the look of the first
places a player sees, and the density of things to do per hour. Players judge a server in its first 30 minutes, and
our first 30 minutes are the weakest part of the game.

The fix is not more systems. It is **content density and polish on Floor 1**: monsters that fight differently,
grounds you remember, quests that aren't "kill 15 X", a town that looks lived-in, and a first hour that shows off
what makes us different (the tower, the floors, the cursors) instead of hiding it until level 35.

Ranked by how much each would move a new player's first evening (details in sections 2-9):

| # | Fix | Why it matters most |
|---|---|---|
| 1 | Give Floor 1 monsters real behaviour (F1-10) | Hunting is 80% of play time; 8 of 13 regular monsters only melee (first pass done overnight) |
| 2 | Make the first hour show the tower (F1-01..05) | The arrival yard is a plain rectangle; the hook (floors, race, SAO) is invisible |
| 3 | Replace kill-count quests with real quests (F1-20) | All 16 Floor 1 quests are "kill N of X" |
| 4 | Rebuild the seven boxy grounds and enlarge Toad Pond (F1-30) | Wolf Copse and six others are four square rings of trees |
| 5 | Bring a style choice into Floor 1 (F1-40) | The Mastery path, our best "choice" system, starts after Floor 1 |
| 6 | A lived-in Hearthgate (F1-50) | Jay's own note; town is a grid of identical boxes |
| 7 | Daily and repeatable reasons to log in (F1-60) | Cyntara's daily chests, weekly quest, events every few hours |

---

## 1. Who we are competing with (research, 2026-11-23)

- **The top of the lists is nostalgia and high rates.** tibiaservers.com (12 Nov 2026): 257 servers, 53,768 players
  online in total; Best Baiak (8.60, high-rate PvP) leads with ~3,856. RubinOT runs 18 worlds (real Tibia map, x80 on
  some). Miracle 7.4 (classic rates, real files) peaks ~1,740. A low-rate custom server with a streamer (Streamy z
  Nadinem) reached ~2,600 online.
- **Cyntara** (Jay's reference) is a high-rate custom server: staged custom exp, 15x skills; top players are level
  3,000-4,500 with rebirths; 150+ quests, most with a **daily reward chest** (once every 20 h); an artifact weapon from a
  level 700 quest that levels with "Artifact Power"; charms, dungeons with leaderboards and talismans, mining that feeds
  the artifact, transmogs, alchemy, enchanting, a weekly quest of seven goals, a season journey that teaches new
  players, automated events, a free-for-all Brawl, a siege every 6.5 h, an **hourly lottery**, a WANTED! bounty on the top
  online player every 6 h. Donations: coins (e.g. $200 = 26,000 coins) for cosmetics, a loot tracker, premium.
  Snapshot: 18 online (348 peak) when read, so even Cyntara is past its peak.
- **What forum veterans say keeps players** (OTLand threads; opinions, not data): a distinctive hook plus heavy
  advertising at launch; stability; numbers going up (level, damage, loot) all the time; not reaching the top too fast;
  optional rather than mandatory grind; anti-bot; and a population: servers die when a newer one opens.

**Where Spirebound fits.** We are not a high-rate server and should not try to be one: our pitch is "the tower opens
floor by floor, together, with real stakes" (DESIGN.md pillar 1). The closest comparison is a *low-rate custom RPG
server*: players there accept slower levels **if every hour has something new**: a quest, a boss, a drop, a secret, a
place. Our risk is a slow Floor 1 (11-15 h, Jay's Q30 decision, good for launch-day urgency) that is *thin*: the
hours are there, the variety isn't.

---

## 2. The first hour (arrival to level 10)

**What happens now** (Pilot runs, Guide Pell's real lines):
1. A new character lands in the Arrival Yard with a practice club. Message: "Follow the stone path east; Guide Pell
   will help you."
2. Pell: "Walk the stone path east and each stop teaches one thing. Take on my {quest}..." His quest: "defeat three of
   its rats". "hunt" gives a clear pointer: "Start with Field Rat (The Ratwarren, levels 1-4): west, about 80 steps
   from the city centre."
3. Four wall-gates teach kill, loot, spells, potion; the Registrar picks vocation and difficulty and gives the kit.
4. Hearthgate. From here the Upgrade tab's top line says "Reach level 10, then see Captain Dorrow..."

**Holes**
- **F1-01 The Arrival Yard has no wow.** Render: a grass rectangle, a dirt path, four pairs of plain walls, a box with a
  red carpet. Real Tibia gives Dawnport an island and a ship arrival. Ours should show **the tower**: arrive on a
  platform at the foot of the Spire, see the Floor 2 gate sealed by boulders, read a plaque of "first clears" (empty on
  launch day: the race starts now). This is the screenshot streamers and the website use.
  **Seen in the playthrough: the Pilot arrived at night and the first screen was almost black** (the day/night cycle
  dims the yard, which has no light sources). Light the yard (lamps along the path, a lit gate) or keep it always day. Detail: the yard already has 12 lamps
  (`S.lamp`, item 8659, `maps/layout_floor1.py`), none within 5 tiles of the spawn, and the ones in view look dark at
  night: check that 8659 is a lit lamp and give the arrival square two of its own.
- **F1-02 Levels 1-7 have no spells.** Every class's first attack spell is at level 8 (Ember Strike, Frost Strike,
  Piercing Shot, Heavy Strike). The first 30-45 minutes are auto-attack only. Give each class one starter attack at
  level 1 and one utility by level 4.
  **Done 2026-11-23 (overnight):** each class's first attack (Heavy Strike, Piercing Shot, Ember Strike, Frost Strike) now
  unlocks at level 1, the moment the Registrar gives you a path (he tells you to say !spells), and its first heal (Second Wind, Field Dressing, Mending Spark, Dewfall)
  at level 4; Guide Pell says so. In-game test added.
- **F1-03 The hook is hidden.** Nothing in the first hour mentions the race: that the first party to kill the Axe-Lord
  opens Floor 2 *for everyone* and goes on a monument. Add a world-state line to the login message and the Journal
  ("Floor 2: sealed. No one has reached the Axe-Lord yet.") and a server broadcast when the Gate Hound first falls.
  **Login line done 2026-11-23 (overnight):** every login now says e.g. "The tower: Floor 2 is sealed. No one has broken
  through the Pass on Floor 1 yet: the first party to defeat its guardian opens the way to the floor boss." Still to do:
  the Journal line and Portuguese/Spanish text.
- **F1-04 Pell's quest needs a "yes" that new players miss.** "Ready? Say {yes} or {no}." Fine for Tibia veterans; but
  the Journal should list the quest as soon as Pell offers it. (My own route forgot the "yes" and the quest silently
  didn't start: a new player would do the same.)
- **F1-05 The tutorial teaches mechanics, not the game's identity.** Add one gate for *cursors* (green/orange/red:
  who can attack you and why), one for *the Journal* (J), one for *sword skills* (the SAO hotbar).
- **F1-06 Pilot tests skip the Registrar** (test problem, fixed tonight by giving Pilots the kit): note for future
  routes.

---

## 3. Hunting: monsters (the biggest problem)

Hunting fills most of the 11-15 hours. **8 of the 13 regular Floor 1 monsters only melee** (as found; correction: the
wasp and the thornsnap's bites already poison, and the elite Grey Alpha and Bandit Captain summon helpers). Three have
one ranged bolt each (15% every 2 s). None of them set fields, heal, flee at low health, push, explode, hide, come back
to life, buff friends, or change as they get hurt.

| Monster | XP | HP | Attacks |
|---|---|---|---|
| Field Rat | 6 | 20 | melee |
| Hopper Toad | 9 | 28 | melee |
| Sproutling | 13 | 35 | melee, earth bolt (range 4) |
| Meadow Wasp | 17 | 45 | melee + poison |
| Bristle Boar | 28 | 90 | melee |
| Meadow Wolf | 36 | 85 | melee |
| Burrow Mole | 39 | 130 | melee |
| Reed Snapper | 39 | 150 | melee |
| Road Bandit | 50 | 160 | melee |
| Thornsnap | 56 | 140 | melee + poison |
| Field Shardling | 58 | 120 | melee, energy bolt (range 4) |
| Ruin Archer | 83 | 220 | melee, arrow (range 6) |
| Ruin Sentinel | 96 | 300 | melee |
| Stonehorn Ram (elite) | 480 | 900 | melee, charge, heals |

Tibia's own early monsters already do more: a wasp poisons, a rotworm is a tank, a troll flees, an orc shaman heals and
summons snakes, a spider webs, a cave rat runs. That variety is why hunting feels like a decision.

**F1-10 Give every Floor 1 monster one signature behaviour** (in `tools/gen_monsters.py`, which writes them):
- Meadow Wasp: poison sting (damage over time) → players buy antidote, Mystics' Cleanse matters.
- Bristle Boar: charge (a 2-tile dash + push) when you're at range: punishes Rangers who stand still.
- Meadow Wolf: howl that calls the nearest wolf; flees at 15% and comes back.
- Burrow Mole: burrows (invisible, untargetable) for 3 s and pops up behind you.
- Reed Snapper: drags you into the water tile next to it (slow).
- Hopper Toad: spits a slowing glob.
- Field Rat: steals a coin and runs (killing it gets it back): funny and memorable.
- Thornsnap: thorn field it leaves behind (earth field).
- Road Bandit: throws a smoke bomb (blind = shorter view), steals; bandits in pairs flank.
- Ruin Sentinel: shield wall (takes half damage from the front for 4 s): reward walking round it.
- Field Shardling: dies in a small energy burst (stand back) or splits into two shards.
- Sproutling: heals other Sproutlings.
This uses Canary's existing spell kinds (condition, field, push, invisible, summon, heal); no engine work. Check each
in `tools/balance.py` so XP per minute stays on target.

**First pass done 2026-11-23 (overnight)**, in `tools/gen_monsters.py`, with an in-game test that no regular Floor 1
monster only bites: Field Rat flees when nearly dead; Hopper Toad's sticky spit slows; Meadow Wasp darts (bursts of
speed); Bristle Boar charges; Meadow Wolf darts in and flees when badly hurt; Burrow Mole burrows out of sight; Reed
Snapper drags you down (slow); Road Bandit throws a smoke bomb (dizzy); Thornsnap's roots slow; Ruin Sentinel shield-bashes
in a line. **Not yet seen in the client** (needs the server restart), and still to do: the coin-stealing rat, the wolf's
call for help, the shardling's death burst, the sproutling healing friends, the sentinel's shield wall (these need
scripts, not just monster spells), and an economy pass on damage taken now that monsters do more.

**F1-11 One elite per ground.** Only the Watchtower has an elite (Stonehorn Ram). Add a named elite per ground that
spawns rarely, glows (an aura effect), and drops the ground's best loot and a flawless Hearth Shard chance. This is
the "something exciting might happen" Cyntara gets from champions.

**F1-12 Loot that matters.** Check the per-ground loot tables against the gear path: every ground should have one
thing worth picking up beyond gold and crafting stuff (a rare cosmetic, a ground-specific trinket, a book page of
lore).

---

## 4. Hunting: grounds

**F1-30 Seven of twelve grounds are still the old "four square loops".** Wolf Copse (render tonight): four square rings
of firs round four blocks, a bench, nothing to remember. Same layout: Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap
Hollow, Shard Fields, Bandit Road, Old Quarry (the H7-H8 roadmap rebuilds). Each needs a shape and a landmark a
player would describe to a friend ("the wolf den under the split rock").
**Measured: the Ranger Pilot died 5 tiles inside Boar Meadow's gate** at level 12 (10 boars in sight, 5 next to it,
1,556 damage in two minutes). The old loop layout keeps monster *homes* 8+ tiles from the gate, but boars wander and
chase down the 2-tile loops, so the gate isn't quiet in practice. (The Pilot had no weapon equipped: a test fault,
fixed for the other classes, but five boars at once would still kill most level 12s.) This makes H7 urgent: Boar
Meadow is the level 9-15 ground every new player reaches right after the starter grounds.
**Measured across Floor 1 (tools/hunt_check.py, 2026-11-23):** the six grounds still on the old loop layout (Wolf Copse,
Reedmarsh, Thornsnap Hollow, Shard Fields, Bandit Road, Old Quarry) let 19-32 monster-weight reach one player at once
against a budget of 6, have 0-3% quiet tiles (rule: 25%), and 72 monsters each; their party caves 24-31 against 12.
**Boar Meadow rebuilt overnight (H7, first of the six-plus-one):** a designed ground on three levels (a ring of glades
round Oak Ridge, the Ridge itself at z 6 up a ramp, the Wallows at z 8 down two holes), 12 loner boars plus crowd
spots, a quiet gate, Old Tusk's wallow now a dead-end chamber in the Wallows (GM list updated). Passes the checker on
every level, the walk test and the in-game tests. Not yet walked in the client (needs the restart). Its surface is
still a rectangle round the ridge: give it a more natural outline in the polish pass.
**Wolf Copse rebuilt overnight too (H7):** packs of 3 along the north and south firs, far apart, a quiet West Pass,
Howling Rock (z 6) with the Grey Alpha's pack at its west end, and the Alpha's Den (z 8 party cave, eight chambers of
four, two led by an Alpha). Crowd spots add two stragglers each (Claude's call: a whole extra pack broke every budget).
Checker, walk test and in-game tests pass; not yet walked in the client. Same caveat: it is also a ring round a ridge,
so Boar Meadow and Wolf Copse now share a shape; vary them in the polish pass.
**Reedmarsh rebuilt overnight too (H7):** mud causeways between open water, a middle island in the big pond reached by
two bridges, pairs of Reed Snappers with single Hopper Toads on the near islands, the far southern islands as the deep
part. Checker, walk test and in-game tests pass; not yet walked in the client.
**Thornsnap Hollow rebuilt overnight too (H7 done on paper):** a dirt rim curving round a bramble mass, a path from the
gate into the hollow's middle, sentries in ones and twos at the bends, the Rootcellar as the party cave (eight root
chambers of four). Its shape is its own (not a ring round a ridge). **H8 started:** Shard Fields rebuilt (gravel flats with
two lines of shardling pairs, the Terraces up the east side by a ramp, the Shard Grotto party cave). Bandit Road and Old
Quarry are the last grounds over budget (19-22 against 6); both need buildings (ruined lookouts, a built mine), so they
are the hardest two.

**F1-31 Toad Pond is too small** (Jay's playtest). Render: about 45 x 40 tiles of usable space, four ponds and an
island, boxed in by trees. Grow it to about 70 x 60 with a second lower level (the Sunken Grotto is the start) and the
crowd system's extra groups switching on with 3+ players.

**F1-32 Levelling speed** (measured: see section 10). Jay: "leveling would take forever and be boring." Keep the
11-15 h total (Jay's Q30), but make each hour denser: more kills per minute on the grounds a player is *meant* to be
on (respawn and density), and more XP from quests (each quest should be worth ~15-20 minutes of hunting, now most pay
gold only).

---

## 5. Quests

**F1-20 All 16 Floor 1 quests are "kill N of X".** (Bread for the Road: 15 boars; Tempered in the Field: 15 wolves;
Millstone: 20 Thornsnaps; ... The Alpha: 1 Grey Alpha.) Rewards are mostly gold. Pillar 6 says "plain to learn",
not "all the same". Mix in the quest types players remember, keeping every step written in the Journal:
- **A chest quest** per ground: a hard-to-reach chest (behind the elite, at the end of the lower level) with a fixed
  reward (Tibia's oldest joy). Cyntara's daily chest on top: open it again every 20 h for a small roll.
- **An escort / rescue**: the Lost Patrol becomes "find the patrol's survivor in the Bandit Vault and walk him home".
- **A delivery with a choice**: Millcross's miller and the Bandit Road (help the bandits or the miller: a different
  reward, a title).
- **A lever/door puzzle with the answer in the Journal after a short search** (pillar 6 allows puzzles that say what
  to do next).
- **A boss-access quest**: the Axe-Lord's room needs "the Stair Key" from a three-part chain (Gate Hound + Watchtower +
  Underkeep), so the floor boss is a goal you build to.
- **A lore chain**: book pages that drop on each ground and tell who built the tower; finishing the set gives a title
  and an outfit addon.

**F1-21 Quest rewards should include experience** (see F1-32) and at least one cosmetic per quest line.
**Experience done 2026-11-23 (overnight):** every Floor 1 quest now pays about 10 minutes of hunting experience at its
ground (3,400 for Wasp Nest up to 10,700 for Shard Hunt; 300 for Pell's rats; 92,150 in all), so quests shave roughly
two hours off the modelled 14.9 h climb, which stays inside Jay's 11-15 h. In-game test. Still to do: cosmetics.
**F1-23 The Journal never shows what a quest pays.** Add the reward line (gold, experience, title, gear) to each quest
in the Quests tab and to the NPC's offer. **Done 2026-11-23 (overnight):** "Reward: 600 gold, 4,950 experience." on every
offer and every quest row in the Journal (in-game test).

**F1-22 Quests are found by talking to the right NPC.** The Upgrade tab now points to the next gear step (built
today), but side quests still require walking into Hunter Brannoch. Put a "!" over NPCs with a quest you can take
(OTClient can draw a marker over a creature), and list "quests nearby" in the Journal by level.

---

## 6. Gear and progression on Floor 1 (built today; what is still missing)

Built today and checked in the real client: Dorrow gives the Trailwarden Bow ("Level 12! Every climber who gets this far
earns a weapon from the barracks..."), and the Upgrade tab names the next step and where. In the playthrough its top
line at level 12 read "Next: take 3 rough Hearth Shards and 500 gold to Weaponsmith Garrick: tier 1." (clear and
actionable).

**F1-40 The style choice comes after Floor 1.** Mastery 10 is around level 37, so an alpha tester on Floor 1 never
makes the permanent choice that makes the system exciting. Options: a small "stance" choice at Mastery 5 (Floor 1)
that previews the two paths and can be swapped freely until Mastery 10; or lower Mastery 10 to ~level 30 so it lands at
the Axe-Lord.

**F1-41 Familiarity is hard to see in play.** (Correction: the look text already showed "familiarity 3/10: +x% damage".)
**Done 2026-11-23 (overnight):** the look text now adds "(45% to the next)" and each new level flashes green on the
character. Still to do: a bar in the Upgrade tab.

**F1-42 Shards are rare and silent.** About 1 in 180 kills. When one drops, show a special loot message and an effect
on the corpse (the "rare drop" moment). Consider a pity counter so no one goes 600 kills without one.
**Done 2026-11-23 (overnight):** a shard is guaranteed at three times the expected wait (counted per player and grade), and a drop shows a sparkle on the corpse and "A rough Hearth Shard glints in the remains!" (in-game test; live after a restart).

**F1-43 The smith's gold check was broken** (fixed tonight: `getTotalMoney` doesn't exist in Canary 3.6.1; Garrick went
silent). Needs a server restart to be live; then rerun `floor1_gear_path` and tick roadmap P1.

---

## 7. Town and world feel

**F1-50 Hearthgate looks generated.** Render: a strict grid of same-sized square buildings on plain cobblestone; red
carpets as flat blocks; almost no trees, lamps, signs, market stalls, fountains, flower boxes, carts or water in the
streets. 24 NPCs, nearly all shops and services; no townsfolk.
- Add a market square with stalls and walking traders (`walkRadius` 3-4, ambient lines).
- 10-15 citizen NPCs who walk routes and say things that change with world state ("They say someone reached the
  Watchtower!").
- Vary building shapes and heights (two-storey corners, an L-shaped inn, a tower over the gate).
- Ambient effects: chimney smoke, fountain splash, fireflies at night, birds (a light script on a timer; nothing like
  this exists now: no `ambient` script in `scripts/spirebound`).
- A notice board that shows live server events, bounties and first-kill records (`boards.lua` exists: put a board in
  the square).

**F1-51 NPCs wander out of earshot** (fixed tonight in the generators: town NPCs now wander 1 tile, not 2; live after
restart). Garrick walked 4 tiles away behind his counter and ignored "upgrade".

**F1-52 One NPC reply vanished in the client** (fixed tonight, and `tools/check_npc_text.py` now guards it in the boot
test): a `{keyword}` followed by `)` makes OTClient's chat window throw and drop the whole message.

---

## 8. Reasons to log in every day

Spirebound has seasons, a **Season Path** (daily and weekly goals for points, a cosmetic every 100 points: this is
the daily/weekly loop, and it was switched **off** for the friends test; switched on overnight so testers see it),
tasks, a task shop, arena, siege, world events every 3 h (Frenzy, Incursion, Fishing Frenzy, Wandering Champion),
fishing, houses, boards. Missing compared with Cyntara and other top servers:
- **F1-60 A daily reward** (login streak; small, cosmetic-leaning, never power). **Done 2026-11-23 (overnight):** day n
  of 7 pays 100 x n gold to the bank, day 7 pays 1,000 gold and 5 health potions; a missed day restarts the week
  (`lib/spirebound/daily.lua`, rules tested in game; the login itself not yet seen in the client). Later: swap the
  day-7 prize for a cosmetic once shop outfits exist.
- **F1-61 Daily chests** on quest ends (see F1-20).
- **F1-62 A weekly goal list**: exists as the Season Path's weekly goals (`!path`). Add "finish 2 quests" as a goal, and
  show the goals in the Upgrade tab so players don't have to know the command.
- **F1-63 An hourly lottery or "lucky player" broadcast**: cheap to build, makes chat move. **Done 2026-11-23
  (overnight):** every hour one climber online (level 8+, not staff, not last hour's winner) gets 20 gold a level (max
  5,000) in the bank and a server-wide shout-out (rules tested in game).
- **F1-64 A bounty on the top player online** (we have the bounty system; tie it to the top-level player every 6 h).
- **F1-65 Leaderboards on the website and in town** (first kills, Death Game survivors, fish records).

---

## 9. Shop and money (launch-readiness)

**F1-13 Rangers with arrows lose money on every Floor 1 ground** (ECONOMY.md, NPC-only net per hour: Ratwarren -586,
Toad Pond -368, Glade -178, Waspgrass -109, Boar Meadow -483, Burrow Hills -300, Wolf Copse -751). They only profit by
selling materials to other players, which a small alpha (or a quiet launch hour) won't have. Spears break even but are
used up and clumsy. Jay played a Ranger. Fix: cheaper arrows on Floor 1 (or a recoverable share, as Tibia's arrows
sometimes drop back), and/or Floor 1 monsters pay Rangers' ammo through slightly better NPC prices for materials.
Check after with `tools/gen_economy.py` that no class runs at a loss on its own floor by NPC selling alone.
**Done 2026-11-23 (overnight):** arrows 1 gold and bolts 2 in Hearthgate; `gen_economy.py` now fails if any class loses gold selling to NPCs alone. Arrow Rangers now net +414 (Ratwarren) to +929 (Waspgrass) an hour.

- Shop prices are placeholders (300 starter set, 500 respec scroll): set before alpha ends (roadmap 7.3).
- Cosmetics carry Cyntara's shop (title shaders, outfit effects, loot tracker). We have outfits and mounts in the art
  pipeline: plan at least 6 shop outfits and 2 mounts for launch; a loot tracker is a cheap, popular convenience.
- Premium: decide what it gives (Cyntara: faster stamina regeneration). Keep it convenience only (pillar 5).

---

## 10. Measured numbers (autopilot playthroughs)

Each ground: two routes, 75 s of hunting on each, at the middle of its level band. "XP/h" is experience per hour over
the whole visit (walking included), with the real experience stages; the economy model (ECONOMY.md) predicts
18,000-36,000 for these grounds. Kills are counted from loot messages, so they undercount; trust the XP.

**Vanguard** (Registrar kit: sword, wooden shield, leather set; Dorrow's Hearthguard Sword at level 10):

| Place | Level | XP/h | Damage taken | Lowest health | Most in sight / next to you | Result |
|---|---|---|---|---|---|---|
| Tutorial pen | 2 | 26,500 | 0 | 100% | 3 / 3 | Pell's quest: offered, done, 100 gold paid (real NPC) |
| Ratwarren | 3 | 21,000 | 0 | 100% | 2 / 2 | |
| Toad Pond | 5 | 26,700 | 0 | 100% | 3 / 2 | |
| Sproutling Glade | 7 | 27,900 | 10 | 96% | 2 / 1 | |
| Waspgrass Fields | 9 | 28,400 | 35 | 83% | 4 / 4 | |
| Boar Meadow (old map) | 12 | - | 1,708 in 62 s | 0% | 10 / 7 | **died 5 tiles inside the gate** |

**Ranger** (ran without a weapon equipped by a test fault; worst case):

| Place | Level | XP/h | Damage taken | Lowest health | Most in sight / next to you | Result |
|---|---|---|---|---|---|---|
| Ratwarren | 3 | 12,600 | 0 | 100% | 2 / 2 | |
| Toad Pond | 5 | 19,700 | 0 | 100% | 3 / 2 | |
| Sproutling Glade | 7 | 18,200 | 57 | 69% | 2 / 2 | |
| Waspgrass Fields | 9 | 13,500 | 55 | 72% | 4 / 4 | |
| Boar Meadow (old map) | 12 | - | 1,556 in ~2 min | 0% | 10 / 5 | **died at the gate** |

**What the numbers say**
- The four rebuilt starter grounds work: steady experience at the model's rate, little damage, never more than 4
  monsters in sight. A new player's first two hours are fine to play, just plain (section 3).
- **The step from the starter grounds to the level 9-15 ground killed two of two Pilots on the old map.** A real new
  player who survives it will still meet a wall of monsters on six of the next seven grounds (section 4). The rebuilds
  done overnight (Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow, Shard Fields) are meant to fix exactly this, but
  they are only live after a server restart and are not yet walked in the client.
- Experience per hour matches the economy model, so the 11-15 hour Floor 1 (Jay's Q30) holds for a steady hunter.
  Levelling is not *slow* by the numbers; it *feels* slow because each hour is the same thing (Jay's "boring").

*(Arcanist and Mystic results are added below when their runs finish.)*

---

## Caveats

- **Found and fixed overnight: the boot test was writing into Jay's game database.** `tools/test_boot.sh` used the
  same database (`spirebound`) as the game Jay plays, so its in-game tests (which open floors, reset test accounts and
  save the world on shutdown) touched Jay's world. A test of mine failed half-way at 21:22 and left Floors 1-2 marked
  as "boss defeated" there; I removed those three records at 21:25 (before that, no floor had a boss kill). The boot
  test now uses its own database, `spirebound_test`, refuses to run on `spirebound`, and the scope test puts its
  changes back even when a check fails.

- The autopilot auto-attacks and drinks potions; it casts no spells and doesn't pick routes like a player. Kill speed
  and damage taken are for comparing grounds and classes, not absolute.
- `/pilot level` raises the level but not skills (a level 26 Pilot has level-2 skills plus what it trained on the way),
  so later grounds are harder for the Pilot than for a real player who climbed there.
- The live server ran code from before tonight's fixes; the smith upgrade and NPC wander fixes need a restart.

## Sources
- [tibiaservers.com live OTS list](https://tibiaservers.com/), [nostalgic.gg most popular 2026](https://nostalgic.gg/en/blog/most-popular-tibia-private-servers-2026-en), [nostalgic.gg top 10 April 2026](https://nostalgic.gg/en/blog/2026-04-top-10-tibia-servers-en)
- [Cyntara home](https://cyntara.org/), [Cyntara newcomer guide](https://cyntara.org/library/newcomer), [Cyntara wiki](https://wiki.cyntara.org/), [Cyntara server info](https://cyntara.org/library/serverinfo), [Cyntara artifacts](https://cyntara.org/library/artifacts)
- OTLand: [what holds players in your server](https://otland.net/threads/what-do-you-think-holds-players-in-your-server.304027/), [why oldschool servers don't last](https://otland.net/threads/why-do-oldschool-servers-not-last.297821/), [getting players to join and stay](https://otland.net/threads/how-to-getting-players-to-join-and-stay-on-your-ot.28570/latest)
