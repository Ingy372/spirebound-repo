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
