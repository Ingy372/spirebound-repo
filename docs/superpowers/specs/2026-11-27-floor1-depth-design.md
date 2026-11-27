# Floor 1 depth: a story, grounds that differ, the big quest, cooking, and a world that changes

Design, 2026-11-27 (Fable session). Building is done by Opus sessions (section 6).

## 1. Why

Jay, 2026-11-27: "i still dont feel like there is enough content/systems/activities to keep players completely immersed in the spirebound world." The second review found Floor 1 has plenty to do, but nearly all of it is the same kind of thing (fight, get a reward, tick a list):

1. no story: the six story quests are kill counts;
2. every hunting ground plays the same (gate, hub, four loops);
3. no big group quest of the kind Tibia veterans remember;
4. fishing is the only thing to do besides fighting;
5. nothing players do changes the world.

Jay: "love 1-5." On the story: "i would lean in the direction of a place to conquer with a grand prize waiting at the top of the tower kinda thing. does that sound good, not the best story teller." The story below is Claude's, built on that; Jay can change any of it (Q101).

The sixth finding (the wait before the next floor opens) belongs to the floor-by-floor unlocks, which Jay put off: "lets finish floor 1 first. put the idea of the floor by floor unlocks into the roadmap and we will do that later" (roadmap FU1-FU3).

## 2. Goals, non-goals, anti-goals

**Goals**
- A new player can say, in one sentence, why everyone is climbing.
- No two hunting grounds are played the same way.
- One quest on Floor 1 that players plan for, talk about and show off.
- A full evening is possible without hunting.
- At least three places on Floor 1 look different in week 2 than on day 1, because of what the server did.

**Non-goals**
- No new reward loop with its own daily list (we have nine; Q58).
- No crafting bench, recipes window or material grind (Jay is "not a fan of crafting").
- Nothing on Floor 2 or above.
- No new art is required to ship: every piece works with sprites we have. Art wishes go to ART_REQUESTS.md.

**Anti-goals (these would make it a failure)**
- A quest step with no log line saying what to do next, or a puzzle longer than about 15 minutes once understood (pillar 6). Secrets keep their riddles; the story and the big quest are plain.
- Any story text, book or NPC line that gives away a secret's place (Jay's riddle rule, DESIGN 8.1).
- Power for the fastest only. Firsts are looks and titles.
- Anything that cannot be tested solo or as a pair with the Pilot party tools (DESIGN 3.4).

## 3. Approaches

**A. More of what we have** (more kill quests, more grounds, more secrets). Cheapest, and it is exactly what feels thin. Rejected.

**B. Big new systems** (professions, gathering, a crafting tree). Adds hours, but Jay dislikes crafting, it adds loops, and it is slow to build. Rejected.

**C. Depth on what exists (chosen).** One story thread that ties the existing places and monsters together; one small feature per ground built from existing map pieces; one hand-made quest; cooking on the fires that every hub already has; town works that swap map pieces. Each piece is small, reuses what is built, and none needs new art.

## 4. The design

### 4.1 The story: "The First Climb" (FD1)

**The premise (one paragraph every player meets in the Arrival Yard).** The Spire is older than anyone's records. Every tale agrees on one thing: at its summit waits the **Summit Wish**, one wish, granted to whoever reaches it. Nobody is trapped here. Everyone who walks through the gate came by choice, to win it. Hearthgate is the camp that grew at the foot of the stair.

**The mystery of Floor 1.** Climbers were here before. A company called the **First Climb** built Hearthgate's oldest walls, went up the stair, and never came down. Their names were on the Monument once; the top rows have been chiselled off. Nobody in town will say who did it. The story quest follows their trail across Floor 1.

**What the player learns, step by step** (this is also why Floor 1 looks the way it does):
- The ruins, the Old Quarry and the Old Watchtower are the First Climb's works: they quarried the stone for the stair and kept watch over it.
- The Ruin Guards and Ruin Archers are their garrison, still at their posts, still following the last order.
- The bandits on the Bandit Road are not just robbers: they are digging for the First Climb's pay chest.
- The Axe-Lord of the Stair was the First Climb's rearguard captain. His order was not to keep the monsters in. It was to let nobody follow.
- The last page, found after he falls: *"The Wish is real. We have seen what it costs. Hold the stair. Let no one climb after us."* And under it, in another hand: *"They went on anyway. Highlands, by the herd road."* It ends pointing up.

**Four of the First Climb are named** (one per path, original names, builder may adjust if the name check objects): Captain **Aldric Vane** (Vanguard, the rearguard: the Axe-Lord), **Sorrel Marsh** (Ranger, the scout), **Ione Castellan** (Arcanist, the record keeper whose pages we find), **Brother Tam** (Mystic, the healer who turned back). *Check against existing names first: the addon quest has a "Deadeye Sorrel"; rename ours if they clash, or make it the same family on purpose.*

**The chain** replaces the kill counts as the Floor 1 story. Eight chapters, given by a new NPC, **Archivist Maren**, at the Monument. Each has a level floor so the story paces the whole climb. Every step has a quest-log line that names the next place in plain words.

| # | Level | Chapter | What the player does |
|---|---|---|---|
| 1 | 4 | The Missing Names | Read the Monument's scraped rows. Maren asks for proof the First Climb was real: find their supply mark in the Old Granary cellar (use the wall). |
| 2 | 8 | The Quartermaster's Trail | Three supply stones, one each in three starter grounds, each read on the spot. Each gives a line of the tally; the third names Millcross. |
| 3 | 12 | Bread for the Climb | Miller Agna's family baked for the First Climb. Her grandmother's ledger is in the mill loft; the mill is overrun (thornsnaps or the ground's own monsters). Clear the loft, bring the ledger. |
| 4 | 15 | The One Who Turned Back | Brother Tam came down alone and is buried in the marsh. Find the grave. **A choice:** bring his pendant to Maren for the archive, or leave it and plant the marker Agna gives you. Two different keepsakes (a title each); the look line shows which you chose. |
| 5 | 19 | The Pay Chest | Captain Dorrow's lost patrol was following the same trail. Bandit Captains carry pages of Ione's record (this absorbs "The Lost Patrol": 2 captains). The pages show the bandits are digging in the wrong place. |
| 6 | 24 | The Watch That Never Ended | In the Old Quarry, read the garrison's standing order on the wall of the guard post; in the Old Watchtower, reach the top room and read the watch log (the last entry is decades of the same line). |
| 7 | 28 | The Rearguard | With the Stair Key (existing quest), find Aldric Vane's field desk at the foot of the labyrinth. His unsent letter says who he is and what he was told to do. |
| 8 | 30 | The Last Page | Defeat the Axe-Lord (first kill or any repeat kill; credit as the boss system gives it). The last page drops into the quest log. Title **"Heir to the First Climb"**, the Floor 1 perk choice (moved here from "finish all six"), and Maren restores the names on the Monument for that player's view (a readable plaque). |

**Rules for the builder**
- The six old story quests stay in the game as **jobs** (side quests, same pay), so no work is lost. Only the perk moves to chapter 8. "The Lost Patrol" becomes chapter 5; "The Last of the Patrol" stays as its follow-up job.
- Nine **readable books and letters** carry the lore (Ione's pages, the ledger, the order, the watch log, the letter). They are real items the player keeps; reading one marks it on the Discoveries page under a new "Records" row group. Three more records are loose in the world, not in the chain, for explorers (not secrets: no riddle, no purse, just lore and a row).
- Town NPCs get one line each about the First Climb, and they disagree (a hero's company; fools; "my grandfather said they were paid to go"). Guide Pell tells the premise in the yard; the `!guide` letter opens with it.
- The Chronicle (DESIGN 4) chapter 1 "a quest" and chapter 3 "a floor boss" keep working; chapter 2's "a secret" is untouched.
- Text in English first; the i18n files get keys with English fallbacks.

### 4.2 One thing only that ground has (FD2)

Rule: each ground gets **one feature** that is used, not just seen; built from existing items and the map tools; never on the gate side of the hub (the gate stays quiet); works for one player unless marked; never the best experience in the game (it adds variety, not a new farm). `python tools/balance.py --check` and `tools/hunt_check.py` must still pass.

| Ground | Feature |
|---|---|
| Ratwarren | **The Ratcatcher's Bell** in the hub: ring it and a swarm pours out of the walls for 60 seconds. Once per player per 20 minutes. |
| Toad Pond | **Night lilies:** at night a lily path rises to the island in the middle, which has its own toads and a fishing spot that only exists at night. |
| Sproutling Glade | **Seedlings:** dead sproutlings leave a seedling. Stamp it out, or leave it two minutes and it grows into an Elder Sproutling (tougher, better loot). |
| Waspgrass Fields | **Nests:** use a torch on a nest to burn it out. The swarm and a Nest Queen come out; the burnt nest gives honeycomb. Nests regrow. |
| Boar Meadow | **Truffles:** an unharmed boar sometimes roots at the ground. The spot it leaves can be dug with a shovel for a truffle (cooking, 4.4). Kill it too early and there is none. |
| Burrow Hills | **Mole tunnels:** open holes link the four loops underground (a shortcut network); mounds collapse behind you for a minute, so a chase can be cut off. |
| Wolf Copse | **The Howling Stone:** use it and every wolf on that loop comes at once; at night the pack is bigger. A party trick and a dare. |
| Reedmarsh | **The tide:** every 30 minutes the water drops for 10 and sandbars appear with turtle nests (eggs for cooking) and a washed-up chest spot. |
| Thornsnap Hollow | **Vine walls:** vines close some trails; cut them (a blade) or burn them (a fire rune, takes over J15b). They grow back, so the maze is never the same twice. |
| Shard Fields | **Chimes:** four tall shards ring different notes when struck. Strike them in the order the wind plays them (shown by a sparkle every few minutes) and the grotto cache opens. Once per player per day. |
| The Bandit Road | **Wanted posters** at the gate: one named Bandit Lieutenant is out on the road each hour, on a random loop. The poster pays on his badge. |
| The Old Quarry | **The lift:** one player turns the winch, the other rides up to the upper ledge (a small spawn and a view). Needs two. |
| The Old Watchtower (apex) | **The signal fire:** light the brazier on the roof and hold the roof for 3 minutes of waves. While it burns (20 minutes) everyone in the ground gets a small loot bonus, and the server is told who lit it. It is a Contested zone, so others can come and put it out. |
| The other grounds in `maps/floor1_plan.py` (the Fallen Bastion and any not listed) | The builder designs one each by the same rule and writes it in FLOOR1.md. |

Each feature's first use marks a row on the Discoveries page ("Ground lore"), so a player can see which grounds they have not really played yet. The signpost in each hub gets one plain line about the feature (these are not secrets).

### 4.3 The big quest: "The Oathroom" (FD3)

The First Climb swore their oath in a sealed hall under the Old Quarry. It is Floor 1's one hand-made group quest: the thing a veteran asks a newcomer about.

- **Entry:** level 30, four players (any paths), each on one of four oath tiles; one pulls the lever. One team inside at a time; 25 minutes, then everyone is put out. Leaving or dying puts you outside; the team can go on without you. No experience loss inside for Normal characters below 50 as everywhere; Death Game rules apply as everywhere (warn at the door).
- **Where:** the door is found in story chapter 6 (the player reads about it on the garrison wall), so it is known and plain, not a secret.
- **Four halls, one for each of the four who swore:**
  1. *The Captain's hall:* a held line. Waves come down a corridor for 3 minutes; the door behind opens only if nobody was pushed past the line.
  2. *The Scout's hall:* the team splits in two. Each pair has a lever that opens the other pair's next door; four levers, in the order shown on the wall at the entrance.
  3. *The Keeper's hall:* a floor of rune tiles. The safe path is written in Ione's record in the hall before; one player reads it out, the others walk it. Wrong tiles hurt, they do not kill outright.
  4. *The Healer's hall:* the Oathkeeper (boss). He heals from four braziers; each must be put out by someone standing on it, which takes that player out of the fight for a few seconds.
- **Reward room: four chests, take one, once per character per season.** Everyone can see which you took (look line and a Discoveries row):
  - the **Captain's chest:** one free tier step on a Floor 1 weapon you own (the only power choice, and it stays inside the gear system);
  - the **Scout's chest:** the Oathbound Pack, a backpack with its own look;
  - the **Keeper's chest:** 10,000 gold;
  - the **Healer's chest:** the Oathkeeper's Mantle, an outfit piece or aura (uses an existing effect until art exists).
- First team each season goes on the Monument (through the existing season-firsts system; looks and a title only).
- Tuned for four level 30s with ordinary Floor 1 gear to pass on a second or third try. Tested with four Pilots in a party through the real door.

### 4.4 Something besides fighting: cooking (FD4)

Every hunting-ground hub already has a fire. Cooking uses it. There is no bench, no window, no recipe list to buy.

- **How:** use a raw ingredient on a fire (a hub fire, a house hearth, the Hearth in town) and it cooks. Use a second ingredient on a cooked dish while it is on the fire and it becomes a combined dish, if that pair is a recipe.
- **Ingredients come from playing:** fish (fishing), boar meat, honeycomb (wasp nests), truffles (Boar Meadow), turtle eggs (Reedmarsh tide), mushrooms and herbs as loot where they already drop. This gives monster materials a use without crafting (answers part of Q57).
- **About twelve dishes on Floor 1.** Each is food with one small, slow, out-of-fight comfort: regeneration, a little more carrying strength, a longer light, walking speed in town. **No damage, defence, experience or loot** (DESIGN 8.2). One dish at a time; numbers through `tools/balance.py`.
- **Recipes are found, not sold:** the first time a player makes a dish, it is written in their **Cookbook** (a row group on the Discoveries page, so no new window). Unfound dishes show "???". Three are hard to guess; NPC lines and one of the loose records hint at them plainly (they are not secrets).
- **Feasts:** a combined dish can be set down by a fire as a feast; party members who eat from it share its comfort for longer than eating alone. This is the reason to sit at the hub fire together.
- Titles: Camp Cook (5 dishes), Hearth Cook (all of Floor 1). The legendary fish has its own dish.
- Selling dishes to other players is fine (market). NPCs buy them for little.

### 4.5 A world that changes: Town Works (FD5)

A **Works Board** beside the notice board in Hearthgate shows one project at a time. The whole server gives gold and materials toward it at the board. When it fills, the map changes for the rest of the season, and the next project opens.

| # | Project | What changes |
|---|---|---|
| 1 | The River Bridge | The broken bridge is rebuilt: a short way to the marsh side. |
| 2 | The Road Lanterns | The road to Millcross is lit at night. |
| 3 | The Stair Camp | Tents, a fire, a healer and a supply seller at the foot of the labyrinth. |
| 4 | The Watchtower Stair | The collapsed stair in the Old Watchtower is repaired: a second way to the roof. |
| 5 | The Monument Garden | Flower beds and benches round the Monument, and a plaque with every giver's name. |

- **Size** follows the number of accounts active in the last week, so five testers and five hundred players both finish a project in roughly three to five days. Gold given is destroyed (a sink; `tools/balance.py` counts it).
- **Who gets what:** everyone who gave anything is on the project's plaque. The top giver gets a title for the season (Bridgewright, Lamplighter, Campmaster, Stairwright, Gardener); looks only. A cap per account per day stops one rich player from finishing it alone.
- **How it is built:** each project is a set of map pieces placed by the server when the project is done and placed again on every start (kept in the season's saved state). Before it is done the unfinished state stands there (the broken bridge, unlit posts, an empty camp site). Season reset clears them.
- **Also:** after the Axe-Lord's first death each season, banners hang on Hearthgate's gates for the rest of the season.
- Works progress and finishes are announced through the existing finds line, and the board shows the next project so there is always one to look forward to.

## 5. What it touches that already exists

- `DESIGN.md` 8.3 says each floor's story quests unlock the perk: unchanged in meaning; on Floor 1 "the story" is now The First Climb.
- Q57 (crafting): cooking is not a crafting system and adds no crafter NPC. The Fletcher and Alchemist question stays open.
- Q58 (too many loops): none of this is daily. The Bandit Road poster is hourly and local to one ground.
- Roadmap J15b (fire runes burn vines) is taken over by Thornsnap's vine walls. MR5's "tower base at the labyrinth's foot" meets the Stair Camp: build the camp site where MR5 would put it.

## 6. How the build sessions share the work

**Session C (story and the big quest): FD1, FD3.** Owns `lib/spirebound/quests.lua`, `perks.lua` (the perk trigger), `hunting_guide.lua` and Guide Pell's text, new `first_climb.lua` and `oathroom.lua` with their scripts, the new NPC, new map module `maps/floor1_story.py` (record spots, the grave, the field desk, the Oathroom).

**Session D (grounds, cooking, town works): FD2, FD4, FD5.** Owns new `ground_features.lua`, `cooking.lua`, `works.lua` with their scripts, `crafting.lua`, `fishing.lua` (ingredients only), `boards.lua` (the Works Board), `tools/balance.py` and `tools/gen_economy.py`, `tools/gen_monsters.py` (Nest Queen, Elder Sproutling, Bandit Lieutenant), new map module `maps/floor1_features.py`.

**Shared**
- Both add rows with the existing `SpireDiscoveries.register` / `mark` and announce with `SpireFinds.announce`, guarded as before. Neither edits `discoveries.lua` or `finds.lua` beyond adding a row group; if both need the same file, Session D makes the edit and Session C asks for it in a message.
- `maps/layout_floor1.py` gets one hook line from each session calling its own module. The generated map is never merged by hand: after a pull, rerun `tools/mapgen.py`. Check `git status` and `git log` for the Hearthgate clean-up session's files before the first map change, and leave `maps/hearthgate*.py` alone; the Works Board, the banners and Archivist Maren are placed from the sessions' own modules.
- Commit only your own files (`git add <paths>`, `git pull --rebase --autostash`, push). ROADMAP, PROGRESS, QUESTIONS, FLOOR1.md and ART_REQUESTS get small appended edits right before a commit.
- The boot test runs in `/root/sbtest` one at a time (`flock /root/sbtest.lock`). The live server is restarted only when a client check needs it, and the other session is told first.
- A task is ticked only after a test through the real game path (CLAUDE.md), with the autopilot or `claude_play` on a fresh character for the new-player parts.

## 7. Left to the builders

All wording (plain English, original names, name check clean); the exact spots; monster and dish numbers inside the balance checks; the Oathroom's floor plan and tuning; which existing items stand in for books, dishes and chests; the three loose records; the features for grounds not in the table; what goes in ART_REQUESTS.md.
