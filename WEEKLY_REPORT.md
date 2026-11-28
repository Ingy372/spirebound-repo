# Update, 2026-11-28 morning: Floor 1 depth is in, and a night of fixes

(The 2026-11-26 report is in git history. Details per task: `PROGRESS.md`, `ROADMAP_DONE.md`.)

## The short version
Four sessions worked on Floor 1 at once without getting in each other's way. Floor 1 now has a story, one thing to do in
every hunting ground, a big four-player quest, cooking, and a town project everyone builds together. The night session
brought Floor 1 back to 11-15 hours, made the Axe-Lord a raid again, closed a real PvP hole, added room for more players
at levels 19-30, and drew the labyrinth's own monster. An art session drew most of the creatures that still wore borrowed
Tibia looks. What's left before Floor 1 is complete is still the real thing: you playing it, then a party clearing it (N1).

## What's new
**Floor 1 depth (the story and depth sessions):**
- **The story, "The First Climb":** Archivist Maren at the Monument tells eight chapters about the company that climbed
  before you and never came back. The Floor 1 perk now comes at the end of chapter 8.
- **The Oathroom:** a four-player quest at level 30 under the Old Quarry: four halls and a boss, then each player takes one
  of four chests, once a season. Four test characters cleared it through the real door.
- **Every hunting ground has its own thing to do** (a bell, night lilies, wasp nests, truffles, a tide, a ballista...).
- **Cooking:** drop food on any campfire; about a dozen dishes, found by trying, kept in a Cookbook.
- **Town Works:** a board in Hearthgate where everyone gives gold to one project at a time (a bridge, road lanterns...).
  When it fills, the map changes for the season. The River Bridge is already finished on your server from a test.

**Night session:**
- **Floor 1 is back to 11-15 hours** (your answer to Q83). The engine was secretly giving 1.5x experience below level 50.
  That's switched off; Tibia's normal "rested" bonus stays.
- **The Axe-Lord is a raid again** (your answer to Q78): 60,000 health (was 20,000), harder hits, four guards at 60%.
  Five level-30 test characters in a real party wiped after taking him to about half in four minutes; a raid of about
  nine kills him in roughly 2.5-3 minutes.
- **New characters are protected for their first 2 hours of play**, at any level, even in boss rooms. Checked with two
  characters in the client.
- **A real PvP hole closed:** class spells (Iron Reach and the rest) ignored every PvP protection, so a high level could
  hit a protected player with a spell. Now spells follow the same rules as normal attacks.
- **Two new party caves for levels 19-30:** the Ridge Tunnels under Smugglers' Ridge and the Bastion Cellars under the
  Fallen Bastion (the surface had no room left for whole new grounds). Floor 1 now holds about 117 players hunting at
  once against my target of 150; the last ~30 need more map space (see Questions).
- **Quieter server:** every kill used to write 8 warning lines to the log (about 150,000 an hour at 100 players). Now none.
- **The map now builds the same on any computer** (it used to fail on water grounds under Linux).
- **Smaller finishes:** Trader Osric buys cooked dishes (for little); fire spells and fire runes burn Thornsnap Hollow's
  vine walls; Burrow Hills has its fourth mole mound (down in the Molework); the Road Lanterns now line the road from
  Millcross to the bridge; the Underkeep's drain grate warns that only seasoned climbers come back up.
- **Still to be seen in the game client** (the test clients were busy all evening with the Oathroom tests): selling a
  the Underkeep's flooded hall and the full pace measurements. (Osric's dishes, the fire rune on the vines, the two
  new caves and the Stairwarden were all seen in the client in the end.)

## Playtest checklist (under an hour)
1. (10 min) Make a new character and walk out of the Arrival Yard. Does the first thing Guide Pell says make you want to
   climb (the Summit Wish)?
2. (10 min) Talk to Archivist Maren at the Monument and do chapter 1 of "The First Climb". Is the story worth reading?
3. (10 min) In any hunting ground you reach, find its one special thing (ask an innkeeper for a rumour if stuck).
4. (5 min) Drop raw meat or a fish on a campfire, then drop a second ingredient on the dish. Did you find a recipe?
5. (5 min) Look at the Works Board in Hearthgate: is it clear what everyone is building and why you'd give gold?
6. (10 min) Look at the new drawings in `ART_FOR_JAY/` (list below) and say "approved" or what to change.
7. (5 min) Tell me if anything felt too fast or too slow. Floor 1 should now take a normal player 11-15 hours.

## Questions (my recommendation is assumed until you answer)
- **Q102** (Session D's smaller calls on cooking, ground features and Town Works). Recommendation: keep them all.
- **Q101 / Q100** (the story and the secrets): still open from yesterday. Recommendation: keep.
- **Floor 1 for launch night:** about 117 players can hunt at once; 150 needs more land. Recommendation: wait until after
  your playtest; if the friends test shows crowding, I add a second open area to Floor 1 (a few hours of map work).
- **The Underkeep's first wing is too crowded in two halls:** even a level-60 test character in top gear died alone in
  the collapsed hall and the column hall (8-9 monsters come at once). Recommendation: thin the column hall from three
  packs to two, so a strong solo player or a pair can get through. (The drain grate already warns that only the
  seasoned come back up.)
- **The Axe-Lord as a raid** means you can't test him alone or as a pair. A solo or pair playtest stops at the Gate Hound,
  unless you bring my five test characters.

## Art waiting for your OK
New drawings in `ART_FOR_JAY/`, each with a walk animation: the **Stairwarden** (the labyrinth's guard: an empty suit of the
First Climb's armour with a cold light inside and a halberd), the four lawn animals (**Meadow Hare, Dapple Fawn, Thistle Hen,
Acorn Squirrel**), the **Nest Queen**, the **Elder Sproutling**, the **Bandit Lieutenant**, and the Underkeep's **Mire Toad** and
**Sluice Warden**, plus the **Oathkeeper** (the Oathroom boss), **Bramblejaw**, the **Wolf Companion** and the **Drain Matron**.
Until you approve them, they wear borrowed Tibia looks in the game.

## Map requests
None. All map work this week was done by Claude.
