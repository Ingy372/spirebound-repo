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

## Also new since the wilds rebuild (Phase R, same day)
- **Logging in is safer (R4):** the login hands out a random one-day token, never your password back; the login service only listens on this PC; there is a sign-up page at http://localhost:8080/signup; starting the server no longer resets the test account (use `windows\Make-Test-Accounts.bat` if you need it back).
- **Death Game is fair (R5, R6):** only a real PvE death retires a character; a one-hit "tag" from another player no longer saves you, but real damage (15% of your health) does, and so does a monster dragged onto you. Retiring frees the house, guild, market offers and the slot. GMs can `/restore` after a server crash. The Hardcore item drop now respects blessings.
- **Fair PvP (R7):** everyone who did real damage shares a kill (skulls, Sanctuary, bounties split by damage). Healing a murderer costs your protection for 5 minutes. Murderers wake in the new Outlaw Camp far west.
- **Saves (R8):** the server saves at once after a first kill, a floor clear, a retirement, a shop buy or a secret sale, and every 10 minutes.
- **Bosses (R9):** healers and tanks earn credit; token hits don't; offline players get their titles at next login; 20 players per room; hits that can kill give a full second of warning; after the floor is cleared, a party of 1-5 can say `!private` for its own Axe-Lord fight once a day. Each floor's hall can unseal on its day of the season (`/calendar start`).
- **Balance for all ten floors (R10):** one table (`BALANCE.md`) that the monsters are built from; the climb now rises gently from 14 to 45 hours per floor. Floor 1 tasks paid far too much and now pay sanely; task points buy things (`!taskshop`). The Fortune Hall's 5% is really destroyed now.
- **The Arrival Yard (R11):** four gates (beat a rat, loot it, `!spells`, drink a potion), then the Registrar. The Journal has a "How do I..." page.
- **Things to earn (R12):** a named gear ladder for every path on Floors 1-2 (boss pieces for the top fighter), two quest lines that reward gear, and all twenty floor perks now really work.
- **Friends-test scope (R13):** Floors 1-2 only; arena, siege, shop and Season Path off (`/scope test` or `/scope launch`). Floor 2's monsters each have a trick.
- **Moderation (R14):** `!report`, `!rules`, GM `/mute`, `/reports`, `/gmlog`, and a chat filter in three languages. Rules and punishment ladder: `docs/RULES.md`.
- **Bots (R15):** hunting on one spot for 10 minutes counts as botting; followers of a botter share the penalty; the client's attack helper and script editor are gone.

## Extra playtest (about 15 minutes)
1. Log in with a fresh account from http://localhost:8080/signup. Walk the Arrival Yard: each gate should stop you until you've done its step.
2. As Jay, say `!rules`, `!report Jay, testing the report box`, then `/reports`.
3. Say `!taskshop` and `!hunt` on any character.

## Also done later the same day
- **Houses (R16):** Open House puts your real guest list back afterwards (even after a restart), once a day; the Summoning Circle opens onto its own small arena; no portals into labyrinths or Contested ground.
- **Secrets (R17):** trigger the moment you step on them; gold once per account; night secrets follow the game's night; real hints on Floors 6-10.
- **Tests on GitHub (R18, part):** a GitHub workflow now runs the full boot test on every push (please glance at the repository's Actions tab once: I can't see it from here), plus end-to-end tests for the headline rules.
- **Commands (R19):** the Journal (J, or the new top-bar button) has a Commands tab with a button for every player command. Your client was restarted to load it.
- **Small fixes (R20):** memory freed at logout, offline Derby winners paid, the Rapid Respawn weekend added.
- **Twin Fang (R21):** a 22% off-hand edge instead of 50%, one-handed swords only, combos on real monsters, a solo trial.

## Still open
- **R22** (prove the custom art pipeline: one of your sprites in the client) and **R18**'s first green GitHub run.
- New tasks found on the way: **R10b** (repairs and floor travel fees), **R10c** (house prices per floor), **R13b** (Floor 2's own hand-built map), **W12** (walk every hunting ground in the client).
- Your direction-list jobs **J5b, J5c, J6, J9, J10** (J10 still waits on Q27).
- **R0** is yours: play the first hour.

## Open questions (my recommendation is assumed until you answer)
- **Q33 (new):** do the walled grounds look the way you want? I recommend keeping the layout and letting the Cowork polish soften the outlines.
- **Assumed this session:** Q13 (season calendar), Q14 (stepping down costs the bonus), Q16 (bot rules), Q18 (Twin Fang 22%), Q19 (warning time), Q22 (friends-test scope). Each is noted in QUESTIONS.md.
- **Q26-Q29** (Spire Manor price, the forge, the account vault, the junk buyer) and **Q13-Q25** are still open. Nothing in this update depends on them.

## Art and map requests
- No new sprites were needed: everything uses existing Tibia pieces.
- `MAP_REQUESTS.md` M1 (the real Floor 1) is now mostly built by me; what's left is the finishing polish you planned for Cowork near the end.
