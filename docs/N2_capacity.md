# N2: how many players Floor 1 feeds (for the lead session's 10.4)

Written by the second session, 2026-11-26. Floor 1 only. Nothing on the map was changed; the map changes suggested
below are for the lead session (10.4, MAP_REQUESTS M1).

## In plain English

**Floor 1 feeds about 30 hunters at once at 200 kills an hour each, and only about 9 of them in the level 9-30
grounds.** The roadmap's target for a launch evening is 150 (10.4). The PC is not the limit (150 bots ran without lag,
`docs/LOAD_TEST.md`); monsters are. On every ground from Boar Meadow up, the whole ground's kills an hour barely rise
when more players arrive: monsters come back at a fixed pace, so every extra hunter just takes a share of the same kills.
The crowd system helps a little (20-60% more kills when a ground is busy or packed), not enough. Boar Meadow is under 200
kills an hour even for one player alone.

## How it was measured

- The same scripted players as the load test (`docs/LOAD_TEST.md`): real logins, a test-only brain that hunts like a
  player (nearest free monster, walk to it, the economy model's damage for that level and class, a 2-second pause after
  each kill, walk on to the next spot when nothing is in sight), the **crowd system on** (more monsters when a ground
  fills: 5+ players "busy", 8+ "packed").
- Every one of Floor 1's twelve walled grounds got the same number of bots at once: 1, then 2, 4, 6 and 8 per ground
  (12 to 96 bots in all; capped at 8 a ground because Jay was playtesting on the live server beside the test).
  Each step ran 10 minutes; the first 3 minutes were left out (the ground settles), kills counted over the last 7.
- Bots stayed online between steps, so each step starts from the ground the step before left behind (as an evening fills).
- "Kills per player per hour" = the ground's kills in those 7 minutes, scaled to an hour, divided by its bots.
- Rerun: `python3 tools/loadtest.py capacity --steps 1,2,4,6,8 --minutes 10 --warmup 3` on a test copy.

## The model, for comparison (tools/gen_economy.py)

What one player could kill alone with no one else there ("solo", the economy model's cap is 300), and what the
ground's monsters can give back in an hour if every monster were killed the moment it came back ("supply", designed
levels only, before the crowd system's extra monsters).

| Ground | Levels | Solo kills/h (model) | Supply kills/h (model) | Crowd spots (extra monsters) |
|---|---|---|---|---|
| The Ratwarren | 1-4 | 300 | 4,582 | 12 (12) |
| Toad Pond | 3-7 | 300 | 2,160 | 14 (14) |
| Sproutling Glade | 5-10 | 300 | 2,651 | 12 (12) |
| Waspgrass Fields | 7-12 | 300 | 5,302 | 12 (12) |
| Boar Meadow | 9-15 | 264 | 504 | 12 (12) |
| Burrow Hills | 11-16 | 232 | 2,378 | 12 (24) |
| Wolf Copse | 12-18 | 277 | 669 | 12 (24) |
| Reedmarsh | 14-19 | 232 | 828 | 12 (12) |
| Thornsnap Hollow | 14-20 | 252 | 566 | 12 (12) |
| Shard Fields | 17-24 | 277 | 612 | 12 (12) |
| The Bandit Road | 19-27 | 248 | 411 | 15 (15) |
| The Old Quarry | 23-30 | 233 | 408 | 15 (15) |

## Measured

Kills per player per hour, by players on the ground (all twelve grounds filled at once; at 6 the crowd system was "busy" and at 8 "packed" on every ground).
Run of 2026-11-26 13:09-14:00 on the test copy (`.local/loadtest_capacity.json`); the server stayed at 1.2 ms average
lag with 96 bots.

| Ground | Levels | 1 | 2 | 4 | 6 (busy) | 8 (packed) | Whole ground at 8, kills/h |
|---|---|---|---|---|---|---|---|
| The Ratwarren | 1-4 | 617 | 602 | 311 | 270 | 243 | 1,946 |
| Toad Pond | 3-7 | 291 | 187 | 146 | 166 | 146 | 1,166 |
| Sproutling Glade | 5-10 | 420 | 416 | 212 | 150 | 148 | 1,183 |
| Waspgrass Fields | 7-12 | 728 | 636 | 409 | 363 | 200 | 1,603 |
| Boar Meadow | 9-15 | 171 | 170 | 58 | 63 | 64 | 514 |
| Burrow Hills | 11-16 | 343 | 314 | 186 | 204 | 181 | 1,449 |
| Wolf Copse | 12-18 | 334 | 216 | 122 | 106 | 104 | 831 |
| Reedmarsh | 14-19 | 249 | 182 | 131 | 121 | 110 | 883 |
| Thornsnap Hollow | 14-20 | 249 | 199 | 81 | 94 | 60 | 480 |
| Shard Fields | 17-24 | 309 | 178 | 101 | 87 | 71 | 566 |
| The Bandit Road | 19-27 | 231 | 127 | 90 | 84 | 88 | 703 |
| The Old Quarry | 23-30 | 240 | 191 | 94 | 74 | 64 | 514 |

What this shows:
- **From Boar Meadow up, a ground is "supply-limited".** The last column is close to the model's supply figure above
  (Boar Meadow 514 measured against 504 modelled, Reedmarsh 883 against 828, Shard Fields 566 against 612): the model's
  supply number is a good planning number for 10.4.
- **The starter grounds are big enough today.** The Ratwarren and Waspgrass Fields still give 200+ each to 8 players;
  their limit is walking between monsters, not monsters coming back.
- **One player alone gets 230-340 kills an hour on most grounds** (the economy model assumes 230-300), so the bots hunt
  at a realistic pace. Real players with area spells may kill a little faster where monsters bunch up, but that cannot
  beat the supply limit.
- Small numbers are noisy (a ground's 7-minute count is 30-200 kills), so treat each figure as plus or minus about 15%.

## Players per ground before each drops under 200 kills an hour

"Fits" = the most players measured with every one still at 200 kills an hour or more.

| Ground | Levels | Fits today | Whole ground's kills/h at 8 players | To feed 12, multiply the monsters by |
|---|---|---|---|---|
| The Ratwarren | 1-4 | 8 or more (not tried above 8) | 1,946 | 1.2 |
| Toad Pond | 3-7 | 1 | 1,166 | 2.1 |
| Sproutling Glade | 5-10 | 4 | 1,183 | 2.0 |
| Waspgrass Fields | 7-12 | 8 (just) | 1,603 | 1.5 |
| Boar Meadow | 9-15 | 0 (171 alone) | 514 | 4.7 |
| Burrow Hills | 11-16 | 2 (6 just about, with the crowd system) | 1,449 | 1.7 |
| Wolf Copse | 12-18 | 2 | 831 | 2.9 |
| Reedmarsh | 14-19 | 1 | 883 | 2.7 |
| Thornsnap Hollow | 14-20 | 1 (2 at 199) | 480 | 5.0 |
| Shard Fields | 17-24 | 1 | 566 | 4.2 |
| The Bandit Road | 19-27 | 1 | 703 | 3.4 |
| The Old Quarry | 23-30 | 1 | 514 | 4.7 |
| **Floor 1 total** | | **about 30 at once** (about 9 in levels 9-30) | | |

"Multiply the monsters by" = 12 players x 200 kills / today's whole-ground kills: how much more the ground must give
back each hour. It can come from more monsters at the same return time, shorter return times, or more ground (new grounds
for the same levels); the effect is the same.

## Suggested map changes for 10.4 (for the lead session)

Target from 10.4: 150 players at once over levels 1-35 (Claude's call, still to check against Jay's launch hopes).
A launch evening starts with everyone at level 1 and spreads upward; after a few hours most players are in levels 9-30.
So the mid grounds need the most work. Suggested, roughly in order of payoff:

1. **Plan with "supply = players x 200 kills an hour".** Each monster with a return time of R seconds gives back about
   3,600 / R kills an hour (the measurement agrees with that within about 15%). Example: Boar Meadow's boars return
   after 100 s, so each boar gives 36 kills an hour; feeding 8 players (1,600 an hour) takes about 45 boars on its solo
   levels, against about 14 today.
2. **Boar Meadow first:** it can't feed even one player at 200. It needs roughly three to four times its boars (or a
   second animal there) before anything else.
3. **The level 14-30 grounds (Reedmarsh, Thornsnap Hollow, Shard Fields, the Bandit Road, the Old Quarry) need about
   three to five times their supply each** to hold 12 players. That is too much for more density alone (the calm rules,
   H14 budgets). Better: a second ground for each level band (10.4's "add grounds and levels"), e.g. two more grounds for
   levels 14-20 and two for 20-30, each built like today's.
4. **The party caves are not counted here, on purpose.** The caves under six grounds are for parties (Jay, Q32) and
   sit below the ground's own levels, so solo capacity can't lean on them. If 10.4 wants a cave level for solo players,
   it must be one of the ground's own levels (`zs`), so the crowd system counts the players there.
5. **Toad Pond (1 player) and Sproutling Glade (4)** need about twice their supply for a launch, where everyone starts:
   a bigger pond or a second starter ground for levels 3-10.
6. **Burrow Hills is the best mid ground today** (1,449 kills an hour at 8 players; its moles come in groups of two):
   its layout is the one to copy.

Not a map change, for Jay to decide: the crowd system lets harder grounds grow only to 1.5 times (Jay's answer to Q31:
"good spots stay worth competing for"). Measured, it adds 20-60%. If Jay wants a launch-evening boost on the mid grounds
without more map, letting them reach 2-3 times for the first week of a season would close part of the gap (question
Q72).

The test can be rerun after the map changes to check (task 10.4's "N2 rerun meets the target"):
`python3 tools/loadtest.py capacity --steps 4,8,12,16 --minutes 10 --warmup 3` on a test copy.

## After 10.4 (rerun 2026-11-26 14:20-15:02, main at faf337be)

What changed in 10.4: Floor 1 monsters return after 40% of the old wait (at least 40 s), and three new grounds:
Bramble Run (14-20), Smugglers' Ridge (19-26) and the Fallen Bastion (23-30), so 15 grounds. Same method as above,
4, 8, 12 and 16 bots on every ground at once (60 to 240 bots). The economy model's estimate was about 125 at once,
about 80 in levels 9-30.

Kills per player per hour (crowd state: 4 quiet, 8 packed, 12-16 packed; the four starter grounds go to "rush" at 12):

| Ground | Levels | 4 | 8 | 12 | 16 | Whole ground at 16, kills/h | Fits now (before) |
|---|---|---|---|---|---|---|---|
| The Ratwarren | 1-4 | 718 | 685 | 608 | 502 | 8,040 | 16 or more (8) |
| Toad Pond | 3-7 | 392 | 289 | 209 | 191 | 3,060 | 12 (1) |
| Sproutling Glade | 5-10 | 555 | 288 | 321 | 291 | 4,654 | 16 or more (4) |
| Waspgrass Fields | 7-12 | 703 | 702 | 641 | 508 | 8,134 | 16 or more (8) |
| Boar Meadow | 9-15 | 81 | 89 | 61 | 57 | 909 | 0 (0) |
| Burrow Hills | 11-16 | 394 | 223 | 205 | 170 | 2,726 | 12 (2) |
| Wolf Copse | 12-18 | 122 | 136 | 82 | 67 | 1,071 | fewer than 4 (2) |
| Reedmarsh | 14-19 | 163 | 199 | 109 | 104 | 1,663 | fewer than 4, 8 at 199 (1) |
| Bramble Run (new) | 14-20 | 276 | 216 | 121 | 102 | 1,637 | 8 (new) |
| Thornsnap Hollow | 14-20 | 144 | 66 | 46 | 37 | 600 | fewer than 4 (1) |
| Shard Fields | 17-24 | 126 | 138 | 94 | 87 | 1,389 | fewer than 4 (1) |
| The Bandit Road | 19-27 | 135 | 151 | 104 | 83 | 1,329 | fewer than 4 (1) |
| The Old Quarry | 23-30 | 135 | 126 | 82 | 61 | 977 | fewer than 4 (1) |
| Smugglers' Ridge (new) | 19-26 | 184 | 141 | 109 | 72 | 1,149 | fewer than 4 (new) |
| The Fallen Bastion (new) | 23-30 | 105 | 112 | 78 | 57 | 917 | fewer than 4 (new) |

**Floor 1 now feeds about 100 at once at 200+ kills an hour each (it was about 30), about 40 of them in levels 9-30
(it was about 9).** The economy model said 125 and 80. Counted: the six grounds that fit 8 or more add up to about 80
(the four starter grounds, Burrow Hills and Bramble Run); the other nine grounds give each of 4 players 105-185 kills an
hour, so they fit about 2-3 each (about 20-25 more). The starter grounds have room to spare: 500+ each at 16 players.

**Still short (each player under 200 with 4 on the ground):** Boar Meadow, Wolf Copse, Reedmarsh (just), Thornsnap
Hollow, Shard Fields, the Bandit Road, the Old Quarry, Smugglers' Ridge and the Fallen Bastion. That is every level
12-30 ground except Burrow Hills and Bramble Run.

**Why, measured** (a 5-minute check with 4 bots on each ground, counting the monsters alive on the ground every
minute): on the short grounds half or more of the monsters are standing alive while the hunters are there (Boar
Meadow 11-16 alive, Wolf Copse 13-24, Shard Fields 12-14, the Bandit Road 8-11, Bramble Run 12-15). So monsters coming
back is no longer the limit there: the hunters lose their time **finding and walking to** monsters that are spread
thinly over a big area and two or three levels. Only the Old Quarry (4-7 alive) and Thornsnap Hollow (6-9 alive) also
run low on monsters. Burrow Hills, the best mid ground, keeps about 120 monsters alive on its levels; Boar Meadow about 15.

**Suggested next map changes (for the lead session):**
1. **Density, not respawn time, on the level 12-30 grounds:** more monsters per stretch of loop (packs and pairs
   along the walking route, as Burrow Hills does), fewer monsters off on separate levels, shorter loops between groups.
   Shorter return times won't help these grounds any more.
2. **Boar Meadow:** its boars are loners spread over three levels; it stays the weakest ground (57-89 each). Pairs, or
   a second animal in between, on its main level.
3. **The Old Quarry and Thornsnap Hollow** also need more monsters (they run low as well as being spread out).
4. A caveat in the bots' favour of the real game: the bots don't know the map; real players learn where groups stand
   and walk tighter loops, so real players will do somewhat better on the spread-out grounds than these numbers.

**Server load after 10.4** (same run): faster respawns mean more monsters to run. 60 bots: 1.1 ms average lag;
120: 4 ms with a few hiccups up to 0.7 s; 180: 9 ms with about one hiccup of more than 0.1 s every 8 seconds (worst
1.1 s); 240: 14 ms, about one every 4 seconds. Up to about 120 at once is still smooth; from about 180 players feel
small stutters now and then. See `docs/LOAD_TEST.md`.

## After 10.4, pass 2 (rerun 2026-11-26 15:16-15:40, main at 4f810bad)

What changed: the mid grounds repeat their clearing groups as often as each ground's danger limits allow, and Boar
Meadow has two more lone boars (Reedmarsh unchanged). Steps 4 and 8 per ground on all 15 grounds (60 and 120 bots, kept
near 120 because of the stutter found in pass 1). "Alive" = monsters standing on the ground's own levels, counted each
minute (the last count of the step).

| Ground | Levels | 4 (pass 1) | 8 (pass 1) | Alive at 4 / 8 | Whole ground at 8, kills/h | Fits now |
|---|---|---|---|---|---|---|
| The Ratwarren | 1-4 | 716 (718) | 644 (685) | 120 / 112 | 5,151 | 8+ (16+ in pass 1) |
| Toad Pond | 3-7 | 424 (392) | 305 (289) | 51 / 61 | 2,443 | 8+ (12 in pass 1) |
| Sproutling Glade | 5-10 | 480 (555) | 538 (288) | 60 / 52 | 4,303 | 8+ (16+ in pass 1) |
| Waspgrass Fields | 7-12 | 711 (703) | 671 (702) | 142 / 127 | 5,366 | 8+ (16+ in pass 1) |
| Boar Meadow | 9-15 | 148 (81) | 79 (89) | 14 / 25 | 634 | fewer than 4 |
| Burrow Hills | 11-16 | 347 (394) | 317 (223) | 131 / 132 | 2,537 | 8+ (12 in pass 1) |
| Wolf Copse | 12-18 | 244 (122) | 171 (136) | 22 / 23 | 1,371 | 4 (was fewer than 4) |
| Reedmarsh | 14-19 | 276 (163) | 209 (199) | 17 / 13 | 1,671 | 8 (unchanged map: noise) |
| Bramble Run | 14-20 | 236 (276) | 190 (216) | 13 / 17 | 1,517 | 4-8 (8 in pass 1) |
| Thornsnap Hollow | 14-20 | 171 (144) | 77 (66) | 13 / 12 | 617 | fewer than 4 |
| Shard Fields | 17-24 | 204 (126) | 149 (138) | 8 / 15 | 1,191 | 4 (was fewer than 4) |
| The Bandit Road | 19-27 | 144 (135) | 144 (151) | 12 / 10 | 1,149 | fewer than 4 |
| The Old Quarry | 23-30 | 189 (135) | 148 (126) | 12 / 17 | 1,183 | fewer than 4 (189 at 4) |
| Smugglers' Ridge | 19-26 | 176 (184) | 151 (141) | 10 / 9 | 1,209 | fewer than 4 |
| The Fallen Bastion | 23-30 | 152 (105) | 118 (112) | 10 / 9 | 943 | fewer than 4 |

**Floor 1 now feeds about 110 at once at 200+ kills an hour each (pass 1: about 100), about 50 in levels 9-30 (pass 1:
about 40).** Counted from the starter grounds and Burrow Hills at their pass 1 sizes (about 72), Reedmarsh 8, Wolf Copse
4, Shard Fields 4, Bramble Run about 6, and about 3 on each of the six grounds still under 200 with 4 players.

What the pass changed:
- **The denser grounds gained clearly at 4 players**: Wolf Copse doubled (122 to 244 each), Shard Fields 126 to 204,
  the Old Quarry 135 to 189, the Fallen Bastion 105 to 152, Boar Meadow 81 to 148. At 8 players the gains mostly shrink
  back (Wolf Copse 171, Shard Fields 149): the extra groups are used up and the walk between them returns.
- **Still under 200 with 4 players:** Boar Meadow, Thornsnap Hollow, the Bandit Road, the Old Quarry (just), Smugglers'
  Ridge and the Fallen Bastion. Thornsnap Hollow is the weakest mid ground now (77 each at 8): it keeps about 12
  monsters alive and its thornsnaps stand still as sentries, so hunters walk a long way between them.
- **Live monsters on the mid grounds stayed about where they were (10-25)**, against about 130 on Burrow Hills. The
  danger limits (the H14 budgets) cap how many groups a clearing may repeat, so density can't rise much more inside
  today's grounds. Burrow Hills fits more players because its moles live as a colony (many small groups close together),
  which the colony habit's budget allows.
- Run-to-run noise is about plus or minus 15-20% at these small counts (Reedmarsh, unchanged, read 163 then 276 at 4).

Suggestions if 10.4 needs more (for the lead session):
1. **More ground, not more density, for levels 17-30:** the budgets stop density, so a fourth and fifth ground for
   levels 19-30 (or a bigger area for Smugglers' Ridge and the Fallen Bastion) is the remaining lever.
2. **Thornsnap Hollow:** a second, walking monster between the sentries (or the sentries closer to the loop).
3. **Boar Meadow:** Q73 (boars in twos) would help most; with lone boars it stays under 200.

Server load in this pass: 60 bots 1.1 ms average (worst 0.31 s), 120 bots 3.5 ms (6 beats over 0.1 s in 7 minutes,
worst 0.55 s), the same as pass 1. Smooth.
