# Adventure and FOMO on Floor 1 (design, 2026-11-27)

Status: Jay approved building it on 2026-11-27 ("yes lift the rule from the 25th"). Roadmap Step 4b, tasks AD1 to AD7.
Lines marked **(Claude's call)** are mine and Jay can veto them. Everything else is Jay's, in his words where quoted.

## 1. Why

Jay, 2026-11-27: "is there enough 'adventure' element to keep players hooked and engaged all the way through the first floor? i dont want there to be any point in the player experience where their interest falls off. i want it to feel like an A+ adventure MMORPG. always something to do, something to explore, and lots of FOMO that someone might find something or get something that you dont have."

The audit (same day) found: levels 1-5 and 10-20 are good; levels 20-28 are flat (kill counts in the money grounds, no new hidden beast, weapon already earned); and almost nothing is scarce or visible. Nine of 13 secrets paid only coins, a rare weapon looked like the ordinary one and nobody was told, trophies could not be seen, every player of a class ended with the same addons.

**The two tests for every part of this design:**
1. At any level from 5 to 35, can a player name three different things to do next that are not a kill count?
2. Can a player standing in the Hearth Plaza see or hear that someone else has something they do not?

## 2. Goals, non-goals, anti-goals

**Goals:** finds are heard and seen by others; secrets pay things you keep; a few things each season belong only to the first finders; rare monsters worth dropping everything for; levels 20-28 as full as 10-20; a page that shows what you are missing; rumours that point without telling.

**Non-goals:** Floors 2-10 content (the systems must be floor-ready, only Floor 1 is filled in); new crafting; anything in the donation shop.

**Anti-goals:**
- Power only the first finders can have. Firsts are looks and titles only **(Claude's call, Jay did not object)**.
- Secret gear that beats the quest weapon path (gear spec, 2026-11-23). Secret gear lives in other slots.
- Chat spam. Announcements are rate-limited and never give a location away.
- Unexplained puzzles (DESIGN 8.3). Every hunt says what to do next.
- Anything on a ground's quiet gate or over its danger limits (`hunt_check.py`, `balance.py --check` must pass).

## 3. Approaches

| | Approach | Trade-off |
|---|---|---|
| A | Reward and visibility changes on what exists (announce, keepsakes, page) | Cheap, no art; fixes FOMO but not the 20-28 dip |
| B | New content only (roamers, maps, hidden places) | Fills the dip, but new finds would still be silent and invisible |
| **C** | **Both, A first** | Most work. Picked: Jay asked for both "something to explore" and FOMO |

## 4. The design

### 4.1 Secrets pay keepsakes (AD2)

Jay, 2026-11-27: "i feel like 1-3 secrets per floor should give gear, the rest can give special cosmetics or titles. players wont know what gives what so it will be up to them to decide if the secrets worth keeping, or rolling the dice to get an exclusive item."

Rules:
- **Three gear secrets per floor** (inside Jay's 1 to 3). **(Claude's calls:)** secret gear is a ring, an amulet or boots, never a weapon or armour; it cannot be traded, dropped, or put on the market (a worn piece proves you found the place); once per character; small bonuses checked by `balance.py`.
- **The rest give a cosmetic or a title**, plus a smaller purse (about a third of today's gold, still once per account).
- **Nobody is told what a secret pays.** Hints, Vesper's public list and the Discoveries page never name a reward. Only the finder sees it.
- **Keep or sell is unchanged** (DESIGN 8.1): selling pays gold and makes the directions public, so the finder of a gear secret chooses between gold now and staying one of the few who has it. Vesper pays the large tier for gear secrets without saying why.
- Which secrets hold gear is reshuffled each season (roadmap 8.4).

Cosmetics that need no new art **(Claude's call)**: titles; house trophies (placeholder items, renamed, each with a line in ART_REQUESTS for a Grok icon); and **auras**, a small magic effect that plays on the character every few seconds, visible to everyone, switched with `!aura <name|off>`.

Floor 1 table **(Claude's call on every row; numbers for the generator to tune)**:

| Secret | Pays now | Pays after |
|---|---|---|
| s1 The Underkeep | the way in | the way in, title "Underkeeper" |
| s2 Old Tusk | beast, trophy | unchanged (trophy now visible, 4.2) |
| s3 Miller's Race | 800 gold | **gear: Millrace Boots** (+5 speed), 250 gold |
| s4 Inn Smith | 3 potions | the hidden shop stays; title "Regular"; house trophy "Inn Tankard" |
| s5 North Crack | shortcut | shortcut, title "Cragfinder" |
| s6 Firefly Hollow | a lamp | **aura: Fireflies**, the lamp |
| s7 Sealed Shrine | group fight | **gear: Shrinekeeper's Pendant** (amulet, +3% maximum health and mana), everyone on the credit list |
| s8 Dye Well | 1,200 gold | **aura: Dyer's Drift** (slow coloured sparks), 400 gold |
| s9 Empty Camp | beast, trophy | unchanged |
| s10 Well Vein | beast, trophy | unchanged |
| s11 Coward Pup | beast, trophy | unchanged |
| s12 Gate Balcony | 400 gold | title "Skywatcher", house trophy "Brass Spyglass", 150 gold |
| s13 Forgotten Cell | 900 gold | **gear: Warden's Signet** (ring, +1 to the class's main skill), 300 gold |
| s14 Smugglers' Vault (new, 4.5) | | beast, trophy |
| s15 The Sealed Cut (new, 4.5) | | beast, trophy |

Characters who already found a secret get the new reward at their next login.

### 4.2 Rare finds are loud and visible (AD1)

Server-wide lines (orange event text) and a notice-board entry, kept for 7 days:

| Event | Line | Who is named |
|---|---|---|
| Rare weapon drop | "<Name> found a Copsewood Bow on a Grey Alpha!" | finder |
| Legendary fish | "<Name> landed Old Whiskers (17.4 kg)!" | finder |
| A secret's first find of the season | "Someone has found a secret in the Wolf Copse." | nobody, ground only |
| A hidden beast's first kill of the season | "A hidden beast has fallen somewhere on Floor 1." | nobody |
| Rare roamer sighted / killed (4.4) | "A Frenzied Boar has been sighted in the Boar Meadow!" / "<Names> brought down the Frenzied Boar!" | killers |
| Treasure keepsake (4.5) | "<Name> dug up a Smuggler's Lantern!" | finder |

- Later finds of the same secret or beast are silent (so a kept secret stays kept). A player can hide their name from find lines with `!finds anonymous`.
- At most one find line every 20 seconds; extra lines go to the board only **(Claude's call)**.
- **Rare weapons get their own item picture** (a different placeholder now; four Grok icon requests in ART_REQUESTS) and a "Rare:" line.
- **Looking at a player** shows: title, "Trophies: Old Tusk's Tusk, Hollowfang's Pelt", "Secrets found: 7", and "First finder (3)" if any. Beast trophies are named there, so others learn the beast exists but not where.

### 4.3 Season firsts (AD3)

- Every secret, hidden beast, rare roamer and the legendary fish records its **first finder of the season** (name, time). Shown on the notice board ("First finds") and on a new face of the Monument. Not shown: where it is.
- First-finder prizes are looks only: the title "First Finder", which becomes "Trailblazer" at 3 firsts and "Pathbreaker" at 6; at 3 firsts the **aura: Trailblazer's Wake**, which nobody else that season can earn.
- A first is credited to everyone on the credit list of a beast, and to one character for a secret. Staff and Pilot test characters never take a first (same rule as floor clears).
- Carries across seasons as account history (like other titles, DESIGN 4).

### 4.4 Rare roaming monsters (AD4, takes over N6)

Jay, 2026-11-25: "monsters that vets will look forward to running into once in the game. Bosses, the fire boar, and a few others that haven't been made yet."

- One roamer per level band. Every 25 to 45 minutes (random) one band's roamer appears at a random monster spot in one of its grounds, never within 8 tiles of a gate and never in a party cave. It stays 15 minutes, then is gone ("The Frenzied Boar has slipped away").
- **Sighted** line when a player first comes within 7 tiles; **killed** line with names. So the server hears "it's out there" and people run.
- Tuned like an elite: one player at the top of the band, or two below it. Counted by the danger checks.
- Loot: a purse worth about 10 minutes of the ground's income, 2 rough Hearth Shards, 25% a Beacon Ember, and **4% its keepsake**: a house trophy and a title, with the 3x pity rule shards use. Kills count on the Discoveries page.

| Band | Roamer | Grounds | Behaviour | Keepsake |
|---|---|---|---|---|
| 5-12 | Goldback Toad | Toad Pond, Sproutling Glade, Waspgrass | hops away from attackers, must be cornered | "Goldback's Crown" trophy, title "Toadcatcher" |
| 9-18 | Frenzied Boar (our red-crested boar; Q63) | Boar Meadow, Burrow Hills | charges, speeds up as it is hurt | "Frenzied Tusk" trophy, title "Boarbane" |
| 14-24 | Pale Stag | Wolf Copse, Bramble Run, Thornsnap Hollow | flees at speed, turns and gores when cornered | "Pale Antlers" trophy, title "Staghunter" |
| 19-30 | The Paymaster | Bandit Road, Smugglers' Ridge, Fallen Bastion | a bandit with the payroll chest and two guards; runs for the ground's edge | "Paymaster's Strongbox" trophy, title "Payday" |

Art: the boar exists. The other three use a recoloured placeholder until Blender sprites are approved (art workflow in CLAUDE.md; requests in ART_REQUESTS). Names are **(Claude's call)**.

### 4.5 Levels 20-28 filled (AD5)

**Treasure maps.** "Tattered map" drops from Road Bandits, Crossbowmen, Hedge Hexers, Ruin Sentinels and Ruin Archers (1%) and Bandit Captains (10%). Tradeable.
- Using it picks one of about 24 dig spots across the level 12-30 grounds (fixed once picked, kept on the map item) and reads a clue naming the ground and a landmark: "Shard Fields: where the gravel meets the old cart, south of the hub fire."
- Using it again inside the ground gives warmer/colder help: "far to the north-east", "close", "right here". Then use a shovel (General Store).
- The dig: gold worth 5 to 10 minutes of that ground, a chance of shards and an Ember, and 4% one of six keepsakes (house pieces: Smuggler's Lantern, Bandit Banner, Ruin Idol, Captain's Sea Chest, Old Climber's Compass, Wardwright Tablet). Ten maps dug: title "Treasure Hunter". Half the time 2 to 3 guards rise from the dig.
- Dig spots are placed at start-up from walkable points (as `quest_objects.lua` does), so no map edit is needed.

**Two hidden places** (new secrets s14, s15; real map work, built last, map rules in CLAUDE.md apply):
- **Smugglers' Vault**, below the Smugglers' Cellar. A barred door; the bar lifts for a Vault Key (2% from Bandit Captains, tradeable, used up). Inside: a short loop of guards and **Ironpurse**, the smugglers' banker. Trophy "Ironpurse's Tally": +2% gold from kills.
- **The Sealed Cut**, a walled-up working in the Old Quarry. Three marked stones (Old Quarry, Fallen Bastion, Shard Fields) each give a rubbing; with all three the wall opens for that player's party. Inside: **the Unfinished**, a half-carved stone giant. Trophy "Unfinished Hand": +1 armour.
- Both follow the hidden-beast rules (gear spec 4.8): once per character, 1 to 3 hours' rest, solo at the top of the band or a small group below, never needed for the main path, listed only in `docs/gm/floor1_minibosses.md`.

**Addon quests that were kill counts** become a hunt for a named target that appears after 15 kills of its kind in the ground (the Journal says so) **(Claude's call; Q71 covers the quest choices)**:
- Ranger addon 2: outshoot **Deadeye Sorrel** on Smugglers' Ridge (was 40 Crossbowmen).
- Arcanist addon 2: take the book from **the Page-Thief** on the Bandit Road (was 30 Hexers).
- Mystic addon 2: calm **Glasswing**, the oldest shardling, in the Shard Fields (was 40 Shardlings).

### 4.6 Floor 1 Discoveries page (AD6)

A Journal tab "Discoveries" (and `!finds`). Categories with a count each and a floor total: secrets (15), hidden beasts (6), elites (6), ground chests, fish (7 kinds), builders' stones (6), rare roamers (4), treasure keepsakes (6).
- Unfound rows read "???". A rumour (4.7) turns a row into "??? (rumoured: Boar Meadow)". Found rows show the name and the date, never a reward for secrets.
- Milestones: 25% title "Wanderer of the Plains"; 50% house trophy "Plains Map"; 100% title "Cartographer of the Plains" and the **aura: Cartographer's Compass**.
- Built from one registry so each floor later adds its rows.

### 4.7 Rumours (AD7)

- Innkeepers and townsfolk answer "rumour": one per player every 20 hours. It picks something that player has not found, in their level band first, and names the ground, never the spot: "A trapper swears something big wallows in the south of the Boar Meadow."
- Rumours cover secrets, hidden beasts, chests, stones and dig-map grounds. The rumour marks the row on the Discoveries page.
- Fishing can land a **message bottle** (weight 1 on the Floor 1 table): a rumour about a secret, whatever your level (DESIGN 8.2 already promises this).

## 5. How the two build sessions share the work

**Session A (rewards and visibility): AD1, AD2, AD3, AD6, AD7.** Owns: `lib/spirebound/secrets.lua`, `trophies.lua` (existing rows), `gear.lua`, `journal.lua`, `boards.lua`, `fishing.lua`, `townsfolk.lua`, their scripts, the client Journal module, new `finds.lua`, `discoveries.lua`, `auras.lua`, `rumours.lua`.

**Session B (new things to find): AD4, AD5.** Owns: `tools/gen_monsters.py` and generated monsters, `art/`, `lib/spirebound/quests.lua`, new `roamers.lua`, `treasure_maps.lua`, `floor1_adventure.lua` (adds s14, s15 and their trophies with `table.insert`, as `floor_content.lua` does), and, last, the map files for the two hidden places.

**The seam (Session A builds, Session B calls, always guarded with `if SpireFinds then`):**
- `SpireFinds.announce(kind, names, thing, groundName)`: the server-wide line, the board entry and the rate limit. `kind` is one of `rare_weapon`, `fish`, `secret`, `beast`, `roamer_seen`, `roamer_killed`, `keepsake`.
- `SpireFinds.first(category, id, players)`: records a season first; returns true if this was the first.
- `SpireDiscoveries.register(category, id, name, floor)` and `SpireDiscoveries.mark(player, category, id)`: rows on the page.
- `SpireAuras.give(player, id)` and titles through the existing `SpireBoss.grantTitle`.

**Shared rules:** commit only your own files (`git add <paths>`, then `git pull --rebase`, then push); ROADMAP, PROGRESS, QUESTIONS and ART_REQUESTS are appended to in small edits right before a commit; the map belongs to the Hearthgate clean-up session until its work is committed, so Session B does map work last and checks `git status` and `git log` first; the boot test runs in `/root/sbtest`, one at a time (wrap it in `flock /root/sbtest.lock`).

## 6. Left to the builders

Exact bonus numbers and drop rates (inside the checks), aura effect ids, placeholder item ids, the 24 dig spots and their clue lines, the two hidden places' floor plans, the roamers' stats, and the wording of every line (plain English, original names, `tools/check_names.py` clean).
