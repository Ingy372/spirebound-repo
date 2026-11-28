# Cooking as a levelled skill (design, 2026-11-27)

Replaces section 4.4 of `2026-11-27-floor1-depth-design.md` and DESIGN.md 8.2's "dishes never help in a fight".

## Jay's brief

- Q102: "players will steal from each other. make it so that fish are used with crosshairs and then from there used on a fire to cook. that or a special fire needs to be created with stations so that players cooking wont have there stuff stolen"
- Q111: "cooking should have fighting boosts behind it. i love the idea of different effects from different meals. that will also give unoffical roles to people outside of combat. if it is possible to add it as a skill that can be leveled i think i would prefer it. that would also preserve better boosts for players who have grinded the skill."
- On this design's outline: "make it so".

## 1. The skill

- **Cooking, level 0 to 100.** Tibia's own skill list can't be extended, so Cooking is saved by the server the way Mastery is, and our client shows it in the Journal's character page next to Mastery (and `!cooking` in chat).
- **Raised by cooking.** Every dish gives cooking experience; harder dishes give more. A dish you have outgrown by 20 levels gives none (no farming the cheapest fish forever).
- **Pace (Claude's call, tuned in playtests):** a player who cooks what they hunt reaches about Cooking 25 on Floor 1; Cooking 100 is a season-long goal for a dedicated cook.
- **Burning:** a dish at exactly your level burns 20% of the time (ingredients lost, a little experience still gained); the chance falls to 0 by 10 levels above it. This is what makes a high Cooking level worth something.

## 2. Cooking without theft: the cooking station

Jay offered two ways; the station is the one we can promise works, because it lives entirely in our own server and client code.

- **Cooking stations** stand at every hunting-ground camp fire, the Hearth in Hearthgate, the Cook's kitchen in town, and house hearths. They look like a spit or a pot over the fire.
- **Use the station** and the **cooking window** opens: the dishes you know, which ones your backpack has the ingredients for, your chance to burn, and what each does. Pick one and press Cook. Ingredients go straight from your backpack to the finished dish in your backpack. **Nothing is ever put down on the ground, so nobody can take it.**
- Several players can use one station at once.
- "Use with" (crosshair) from a raw ingredient onto a station or fire also opens the window with that ingredient's dishes selected, for players who try that first.
- Raw fish and other raw food stay edible as in Tibia.

## 3. Recipes

- **Found by trying, then remembered.** In the window, "Try a new combination" lets you pick two or three ingredients; if they make a dish, it goes in your **Cookbook** for good. Unfound dishes show "???" with the Cooking level they need.
- **The Cook** (an NPC in Hearthgate's kitchen) hints at a few recipes per floor in plain words and sells nothing that gives power.
- About **12 dishes per floor**. Higher floors' ingredients make the higher tiers, so cooks stay useful all season.

## 4. What meals do: the fight boosts

- **One meal at a time**, shown as a "Well fed" icon. It lasts **30 minutes of play** and **ends when you die**. Eating another meal replaces it.
- **Meal families** (each dish belongs to one):

| Family | Boost | Who wants it |
|---|---|---|
| Hearty | more max health | tanks, Death Game players |
| Spiced | more melee and distance damage | Vanguards, Rangers |
| Broth | more magic damage, faster mana regeneration | Arcanists, Mystics |
| Ironskin | less damage taken | tanks, boss groups |
| Mender's | stronger healing done | healers |
| Keen | higher critical hit chance | damage dealers |
| Warding (four kinds) | resist one element: fire, ice, earth or energy | boss fights |
| Trail | faster walking | everyone, travelling |

- **Tiers by Cooking level:** tier 1 dishes from Cooking 0, tier 2 from 20, tier 3 from 40, tier 4 from 60, tier 5 from 80. A tier-1 damage dish gives about +2%, a tier-5 about +8%; resist dishes 4% to 15%. **Food never beats gear:** `tools/balance.py` keeps every meal under a fixed share of what a floor's gear gives.
- **Skill shows in the dish:** a dish made by a cook 20 or more levels above its tier is "Fine" (+25% of its effect); 40 or more above, "Masterwork" (+50%). The cook's name is on it ("Spiced Boar Haunch, Fine, cooked by Aldra"). This is what keeps the best boosts for players who ground the skill: a Masterwork tier-5 meal can only come from a top cook.
- **Feasts:** a combined dish can be set out at a camp fire for your party. Everyone who eats from it gets its boost for 60 minutes instead of 30. Only party members can eat from it, so a feast can't be stolen either.
- **PvP:** meals work the same in PvP. Their numbers are small next to gear and styles.

## 5. The cook as a role

- Dishes are **tradeable and sell on the market**, and carry the cook's name, so a known top cook can make a living.
- Hunters sell ingredients (meat, fish, honeycomb, truffles, eggs, herbs) to cooks; fishermen get a real customer.
- Titles: **Camp Cook** (Cooking 25), **Hearth Cook** (50), **Master of the Hearth** (100), plus "every Floor 1 dish found".
- NPCs buy dishes only for little, so cooks sell to players.

## 6. What changes in the game

- DESIGN.md 8.2: dishes now give fight boosts (Jay, Q111). The "never helps in a fight" line is replaced.
- `lib/spirebound/cooking.lua` (today: use on a fire, comforts only) is rebuilt around the station, the skill and the meal families; numbers from `tools/gen_depth.py`.
- New client window in `client/modules/game_spirebound` (the cooking window) and a Cooking line on the Journal's character page.
- The station is a map object placed by the Floor 1 builder at every camp fire.

## 7. Done when

- A fresh character raises Cooking by cooking at a camp station in the real game, unlocks a tier-2 dish, and its meal's boost is seen to change damage in a fight (in-game test).
- A second character next to the station can never take the first one's ingredients, dish or feast (in-game test).
- A dish by a cook 20 levels above it shows "Fine" and gives the larger boost.
- Burn chance and experience follow section 1; `balance.py --check` passes with the meal ceiling.
- The cooking window is seen in the client.
