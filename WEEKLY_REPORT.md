# Update, 2026-11-13: Floor 1 outside the walls is rebuilt

## What's new
- **Every hunting ground is now a proper place.** All twelve grounds were rebuilt from `FLOOR1_WILDS_PLAN.md`:
  - a wall of trees, rock, thorns or swamp, with **one gate** off a road;
  - a **hub** inside the gate with a sign, a fire and a bench;
  - **four hunting loops**: ring trails round a grove, a pond, a rock pile or a bandit camp, with monster groups at fixed spots. One loop is one player's hunt (or two sharing), and one lap is a cavebot route.
  - Each has its own look: thicket mounds (Ratwarren), four ponds (Toad Pond), fern groves (Sproutling Glade), hedged flower beds (Waspgrass), oak groves (Boar Meadow), rock hills (Burrow Hills), dark firs (Wolf Copse), a swamp with pools (Reedmarsh), thorns (Thornsnap Hollow), boulder fields (Shard Fields), fenced bandit camps (Bandit Road), rubble (Old Quarry).
- **Old Tusk's wallow:** Boar Meadow's south-east grove is hollow, a mud clearing reached through a one-tile gap. Old Tusk and the secret moved in there.
- **Six caves for parties** under the harder grounds, each a ring of eight chambers with 32 monsters. The cavebot is refused in them (your Q32).
- **Tibia-style respawn:** fewer monsters, back after 2 to 3.5 minutes, so you walk your loop instead of standing still. I also found that our engine really waits about twice the number in the spawn file, so the files now hold half of it.
- **Your crowd system (Q31):** 5 or more players in a ground bring out extra groups, 8 or more bring out all of them, and 12 or more on a starter ground makes them come back three times as fast. `!hunt` tells you how busy your grounds are, for example "Boar Meadow: busy (6 players, extra monsters are out)".
- **Slower levels (Q30):** 10x to level 8, 4x to 20, 3x to 50 (was 25x). Monster experience was retuned so every step of the ladder is better than the last. By the model Floor 1 now takes about 9.5 hours to level 35 by hand, so roughly 13 hours in real play. Bandits and the Quarry pay more coins.
- **Roads and signs:** no road runs through a ground any more. There are new trails to every gate, the Copse Road, the Watch Road to the Old Watchtower (it had none), and signposts at ten junctions naming each ground and its levels.
- **Under the hood:** the map build now refuses to finish if any gate can't be reached from the Hearthstone, a loop isn't a closed ring, a wall has a hole, or a monster group stands on a road or near a gate. Rock walls use Tibia's real mountain tiles, learned from Canary's hand-made map. Boot test: 105 in-game checks, all passing.

## Playtest checklist (about 50 minutes)
Log in as Jay (your GM character). Type `/pos x, y, 7` in chat to jump, then press Escape before walking. Make a normal character too for step 1.
1. **New character, signs only (15 min):** from the Arrival Yard, go to Hearthgate and find the Ratwarren, Toad Pond, Sproutling Glade, Waspgrass Fields and Boar Meadow using only the signposts. Note any junction where you didn't know which way to go.
2. **Boar Meadow (10 min):** jump to `/pos 1159, 1341, 7` (the hub). Walk each of the four loops once. Do they feel like places? Is one lap a good length? Walk into Old Tusk's wallow in the south-east grove.
3. **Toad Pond and Waspgrass (5 min):** `/pos 1314, 1276, 7` and `/pos 1224, 1211, 7`. Can you see where the trails go on grass?
4. **Reedmarsh and Wolf Copse (5 min):** the marsh hub is `/pos 1070, 1326, 7` and Wolf Copse's hub is `/pos 1083, 1282, 7`.
5. **A cave (10 min):** `/pos 1273, 1206, 7`, walk south onto the hole into the Molework, go round the ring of chambers and back up the stairs. If a friend is around, try a fight down there together.
6. **`!hunt` (2 min):** say `!hunt` on a low-level character. You should get the advice and a busy line for your grounds.
7. **Look and feel (3 min):** see Q33. Do the grounds look right to you, or too regular?

## Open questions (my recommendation is assumed until you answer)
- **Q33 (new):** do the walled grounds look the way you want? I recommend keeping the layout and letting the Cowork polish soften the outlines.
- **Q26-Q29** (Spire Manor price, the forge, the account vault, the junk buyer) and **Q13-Q25** are still open. Nothing in this update depends on them.

## Art and map requests
- No new sprites were needed: everything uses existing Tibia pieces.
- `MAP_REQUESTS.md` M1 (the real Floor 1) is now mostly built by me; what's left is the finishing polish you planned for Cowork near the end.
