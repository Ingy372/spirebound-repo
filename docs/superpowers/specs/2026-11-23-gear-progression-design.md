# Gear and weapon progression (design, 2026-11-23)

Status: approved by Jay on 2026-11-23 ("agree on everything... everything is good to build"), with one change: mastery respecs are sold in the donation shop (4.2, 4.9).
Lines marked **(Claude's call)** are mine and Jay can veto them. Everything else is Jay's decision, in his words where quoted.

---

## 1. Why we are doing this

Jay's playtest on a level 12 Ranger (2026-11-23): "floor 1 is boring." The biggest reason was gear: "there doesnt seem to be any progression for gear or weapons outside of crafting, which im not a fan of myself." Players hear they need a material (his example: "venomous slime") with no idea where it drops.

What Jay wants, in his words:
- "the games that got my attention and held it with there weapons systems had a pretty clear progression path for players. it wasnt murky whatsoever. once i lost my 'mission' of how to progress my character, the fun quickly died."
- From Cyntara he liked: damage built from quests, the best weapon from a quest that opens at a certain level, and that weapon then gaining **mastery** as you use it.
- From another server he liked: monsters drop a tier item, **three combine into the next tier**, and you choose between selling it (good money) or saving it to tier up your own gear.
- "im also big on secret information too": 3 to 5 **hidden mini-bosses** on Floor 1 that give a small boost.
- Mastery with **permanent choices**: "once a max mastery level is achieved, then one more choice and another mastery to max out. weapons cannot be respected. this should create a sense of choice as well and give players reason to replay certain classes, continue playing multi seasons, and create diverse roles in the game."
- It should feel like Sword Art Online: weapons are replaced floor by floor, and the choice is "take a temp reduction switching to the new more powerful weapon, or decide to stick with old faithful and keep leveling masteries."
- The shop: "the shop should have some gear that gets outclassed later. i believe that was a good idea and another chance for the server to make money."

**The one test for every part of this design:** at any level, can a player say what their next upgrade is and where to get it, in one sentence, without leaving the game? If not, the design has failed even if everything works.

## 2. Goals, non-goals, anti-goals

**Goals**
1. A clear, always-visible upgrade path from level 1 to the end of Floor 1, repeating on every floor.
2. Two kinds of progress: **style** (permanent, belongs to the character, built from choices) and **weapon** (temporary, replaced floor by floor).
3. Hunting always has a gear reason: tier tokens drop in every hunting ground and are worth selling or keeping.
4. Secrets pay: hidden mini-bosses give permanent boosts.
5. The Floor 1 gear quests become the Floor 1 quest line, so "I can't find any quests" is fixed by the same work.
6. Shop starter gear that is useful early and clearly outclassed later.

**Non-goals (not in this project)**
- Crafting as a gear path. Crafters stay, but only for ammo, potions, supplies and cosmetics. No player ever needs a crafter to progress.
- Durability and repairs (still task R10b).
- Floors 2 to 10 content in full. This project builds the system and Floor 1 completely, and writes the Floor 2 weapon list so the "switch or stay" choice can be tested. Floors 3 to 10 get their weapon lists from the same generator later.
- The other notes from Jay's playtest (Hearthgate too empty, Toad Pond too small, levelling too slow) are separate roadmap tasks.

**Anti-goals (would make this a failure even if it works)**
- A murky path: hidden requirements, materials with no source, or "go ask around" for the main path.
- Pay-to-win: shop gear must never beat gear earned by playing, past the early levels.
- One right answer: if one style path or one weapon is clearly best, the choices are fake.
- "Old faithful forever": if a maxed old weapon is never beaten, nobody switches. If it is beaten instantly, nobody cares about familiarity.
- A respec that can be earned in game. Respecs exist only in the donation shop (Jay, 2026-11-23).

## 3. Approaches we considered

| | Approach | Trade-off |
|---|---|---|
| A | One quest weapon per floor that grows with mastery (Cyntara style) | Simplest and clearest, but nothing to chase once mastered and nothing to trade |
| B | Tier tokens only: three tokens raise an item one tier | Every kill matters and tokens trade well, but no big "I got the weapon" moment and risks feeling grindy |
| **C** | **Both: quest weapons at set levels as the backbone, tier tokens to improve them, mastery for the long term** | Most work, but gives both moments Jay described and fills Floor 1 with quests. **Jay picked C ("C for sure").** |

Within C we also weighed "one weapon for life that evolves every floor" against Jay's own SAO version. Jay pushed back on his first idea: "are we sure one weapon for life is the strongest idea?" We picked his SAO version: style is permanent and belongs to the character, weapons are swapped (section 4). It matches the show (the player's skill grows and locks in; blades are replaced floor by floor) and keeps the "switch or stay" decision on every floor.

## 4. The design

### 4.1 Two layers

**Layer 1: Style (the character's, permanent).** Each class has one style tree. It fills from fighting with any of that class's weapons. Choices in it are permanent for that character. It never resets when you change weapons. **(Claude's call: it is per character, not per account, so a player can try a different style on another character; Jay said "account", and we agreed in chat that per character keeps the replay reason.)** It resets with the character at a season end, like levels do, so every season is a new set of choices.

**Layer 2: Weapon (the item's, temporary).** Each weapon has its own **tier** (from tokens) and **familiarity** (from use). Both stay on that item, even if it is traded. When you take a new weapon, its tier and familiarity start low, but its base power is higher.

### 4.2 Style tree

```
Stage 1: <Class> Mastery 1-10
            |  at 10, choose one (permanent)
   +--------+--------+
 Path A            Path B         Stage 2: Path Mastery 1-10
   |  at 10, choose      |  at 10, choose
 +-+--+               +--+--+
 A1   A2              B1    B2    Stage 3: Final Mastery 1-10
```

- 3 stages x 10 levels = 30 style levels. 2 choices. 4 end styles per class, 16 in the game.
- **Each style level** gives a small passive bonus that fits the path (example: Marksman +1% damage at range 4 or more; Bulwark +1% shielding).
- **Finishing each stage** (level 10) unlocks one **signature ability** for that path: a sword skill or spell no other path has. So a finished character has 3 signature abilities.
- **Choices are permanent, except by a shop respec.** Jay, 2026-11-23: "i want to sell mastery respec's in the donation shop. that will be the only way to acquire one." No NPC, quest, drop or GM command undoes a choice (GMs can fix bugs only, logged). A **Mastery Respec** from the shop lets the character re-pick its choices; how far back it goes and what happens to points is in 4.9.
- **How style fills (Claude's call):** style points come from the experience of monsters you kill while holding a weapon of your class, counted before XP stages and bonuses, so a fast-levelling weekend does not skip it. Party kills count for each member's share. Players never fill style from other players (no PvP farming).
- **Pacing (Claude's call, numbers in `tools/balance.py`):** Stage 1 finishes around the end of Floor 1 / start of Floor 2 (around level 35 to 40), so the first choice comes at the first floor change. Stage 2 finishes around Floor 4 to 5. Stage 3 finishes around Floor 8. That spreads the three big moments across a season.
- **Showing it:** the style window (section 4.7) shows both options of the next choice before you reach it, with what each does, so a player can plan. Choosing asks twice ("This is permanent. Choose Marksman?").

**Replaced 2026-11-27:** the paths and finals below are superseded by `2026-11-27-style-trees-v2.md` (Jay's brief for the Vanguard and Mystic; extreme-or-balanced finals for every class). The table is kept for history.

**Draft path names (Claude's call, Jay can veto; all must pass `tools/check_names.py`):**

| Class | Path A → finals | Path B → finals |
|---|---|---|
| Vanguard | **Bulwark** (tank, protects the party) → Aegis Warden (party shields) / Ironwall (solo tank) | **Reaver** (melee damage) → Bloodedge (life-steal, single target) / Stormbreaker (area cleaves) |
| Ranger | **Marksman** (long-range single target) → Deadeye (big crits) / Volley Captain (multi-target volleys) | **Trapper** (slows, ground control) → Snareweaver (roots and traps) / Pathfinder (speed, party support) |
| Arcanist | **Emberwright** (fire, burst) → Cinderheart (huge single bursts) / Ashwalker (burning ground, area) | **Stormbinder** (lightning, chains) → Tempest (chain area damage) / Spellbreaker (counters other casters, PvP) |
| Mystic | **Lifebinder** (healing) → Dawnmender (group heals) / Wardkeeper (shields and barriers) | **Wildcaller** (nature damage) → Rootcaller (roots and thorns) / Frostwarden (ice, slows) |

Every class keeps a solo-capable option at each choice. Each final should have a clear party role, so groups want a mix (Jay: "create diverse roles").

### 4.3 Weapons

**Familiarity (per weapon, 0 to 10).** Fills from kills with that weapon held, faster than style. Each level adds a small damage bonus (Claude's call: +1.5% per level, so +15% at 10). Familiarity 10 on a weapon takes about 3 to 4 hours of hunting at that floor's level (Claude's call).

**Tier (per weapon or armour piece, 0 to 5).** Raised with tier tokens (section 4.4). Each tier adds attack (weapons) or armour (armour pieces).

**Ceiling rule (what makes "switch or stay" a real choice).** Every weapon has a base power by floor. Numbers live in `tools/balance.py` and its check enforces:
- A brand-new next-floor weapon (tier 0, familiarity 0) is about **90 to 95%** of a maxed weapon from the floor below (tier 5, familiarity 10).
- It passes the old weapon after about **2 to 3 hours** of hunting on the new floor (some familiarity and a tier or two).
- A maxed weapon is never better than a tier 2, familiarity 5 weapon from the floor above.
So old faithful is the right call for a few hours and the wrong call after that, and familiarity always matters.

**Armour** has tiers but no familiarity (Claude's call: keeps it simple; armour comes from quests, drops and the boss, and is tiered with tokens).

### 4.4 Tier tokens

- Every hunting ground drops **tier tokens** for its floor. Floor 1's token is the **Hearth Shard** (Claude's call on the name).
- Three grades (Claude's call): **Rough** (any Floor 1 ground), **Cut** (the harder half of Floor 1's grounds and caves), **Flawless** (group grounds, the apex Old Watchtower, elites like the Grey Alpha and Bandit Captain).
- **Upgrade costs:** tier 0→1 and 1→2: 3 Rough. 2→3 and 3→4: 3 Cut. 4→5: 3 Flawless. Done at the **Weaponsmith** in each floor's town, with a gold fee that rises per tier (a gold sink).
- **Upgrades never fail and never lose the item** (Claude's call: no gambling on your gear; it keeps the path clear).
- A floor's tokens only upgrade that floor's gear. Floor 1 tokens cannot upgrade Floor 2 gear.
- Tokens are tradable on the market and sell to NPCs for little. Selling to players is where the money is, so Jay's "sell or save" choice is real. Drop rates are set in `tools/gen_economy.py` so a solo player who saves every token can reach tier 5 on their Floor 1 weapon around level 30 to 35, and a player who sells them all earns a good extra income.
- **Every token's description says where it drops** ("Rough Hearth Shard. Dropped in every Floor 1 hunting ground."). Same rule for every material in the game (fixes the "venomous slime" problem).

### 4.5 The Floor 1 path (the checklist)

Each class gets one **main weapon** for Floor 1, and the checklist upgrades it. Jay's examples: "reach level 10", "complete the quest from [insert npc]", "kill floor boss 1".

| Step | Level | What happens | Where |
|---|---|---|---|
| 0 | 1 | Starter weapon from the Registrar (as today) | Arrival Yard |
| 1 | **10** | **Reach level 10.** The Floor 1 quest giver offers your Floor 1 main weapon, and you pick its family (Ranger: bow, crossbow or spear; Vanguard: sword, axe or club; Arcanist wand; Mystic rod). | Captain Dorrow, Hearthgate barracks (Claude's call on giver) |
| 2 | ~15 | **Quest 1** (story quest line, part 1): your weapon is "tempered", +1 tier free and a small bonus. | Quest NPC named in the window |
| 3 | ~20 | **Quest 2**: your Floor 1 armour piece (today's quest piece in `tools/gen_gear.py`). | Quest NPC named in the window |
| 4 | ~25 | **Kill the Gate Hound** (field boss): everyone on its credit list gets 3 Cut Hearth Shards, once per character (see note) | The Pass |
| 5 | 12-35 | **Tier tokens** raise weapon and armour to tier 5 | Every hunting ground, Weaponsmith |
| 6 | ~30-35 | **Kill the Axe-Lord of the Stair** (floor boss): your Floor 1 weapon is **awakened** (new name and look, its final base power). Everyone on the credit list gets it, not only the top fighter. | Top of the labyrinth (or the private repeat portal, R9) |

Note on step 4 **(Claude's call)**: 3 Cut Hearth Shards are exactly one tier step, simple to explain and useful at that point.

**Rules around the main weapon (Claude's calls):**
- **"Maxed" means awakened, tier 5, familiarity 10.** That is the weapon the ceiling rule in 4.3 compares with.
- **The boss awakens whichever Floor 1 weapon you hold**, the main weapon or a rare-drop one.
- **Changing family mid-floor** (say bow to spear): the Weaponsmith reforges your weapon into another family of your class for a gold fee. Tier carries over, familiarity goes back to 0.
- **Losing it on death** (normal Tibia death rules and Hardcore drops still apply; blessings protect as usual): the quest giver re-issues the main weapon at tier 0, familiarity 0 for a gold fee. Death can hurt, but it never blocks the path.
- **Kills that count** for style and familiarity: any kill (melee, arrow, spell, sword skill) while a weapon of your class is equipped. Arcanists and Mystics fill them with spells while holding their wand or rod.

The existing **rare drop** pieces (Briarguard Sabre, Copsewood Bow...) stay as alternative Floor 1 weapons: they start with a slightly different trade-off (Claude's call: same base power as the main weapon, a different small bonus) and use the same tiers and familiarity, so a lucky drop is a real choice, not a strict upgrade.

The quests in steps 1 to 3 are the **Floor 1 story quest line**. The existing 12 quests (`server/.../lib/spirebound/quests.lua`) are reused and re-ordered where they fit (The Lost Patrol, Wasp Nest, Pelts for the Hall...). Each quest-giver NPC is named in the window with its town and a map mark.

### 4.6 Floor 2 and later: the "switch or stay" choice

Each floor from 2 up offers, per class, **2 or 3 new weapons**: a quest weapon (as step 1 above, opened at the floor's first level), a rare drop, and the floor boss's awakened weapon. Each has its own small trade-off (for example faster attacks vs bigger hits), so the choice is about style as well as power. They follow the ceiling rule in 4.3. For this project, Floor 2's list is written and testable; Floors 3 to 10 come from the same generator later.

### 4.7 The "Next upgrade" window

A client window (new module, also opened by `!upgrade` and by talking to the Weaponsmith, so no one needs the chat command; rule R19). It shows:

```
WEAPON  Copsewood Bow            tier 2/5   familiarity 6/10
  Next: 1 more Rough Hearth Shard -> tier 3 needs 3 Cut Hearth Shards
        (Cut shards: Wolf Copse, Reedmarsh, Thornsnap Hollow and harder)
ARMOUR  Trailwarden Greaves      tier 1/5

FLOOR 1 PATH
  [x] Reach level 10 - Captain Dorrow gave you your weapon
  [x] The Lost Patrol (Captain Dorrow, Hearthgate barracks)
  [ ] Pelts for the Hall (Hunter Brannoch, Hunters' Hall)   <- next
  [ ] Defeat the Gate Hound (the Pass, north of Millcross)
  [ ] Defeat the Axe-Lord of the Stair (top of the labyrinth)

STYLE   Ranger Mastery 7/10   (next choice at 10: Marksman or Trapper - click to read both)
TROPHIES 2 found
```

- The **top "Next" line is always one sentence** naming the thing and the place (the test in section 1).
- Hidden mini-bosses are never listed or hinted at here. Only found trophies show, by name.
- A **login reminder** prints the "Next" line once per login (Claude's call).
- The window also lists the Floor 1 quest line, which answers "I can't find any quests".

### 4.8 Hidden mini-bosses (secrets)

- **4 on Floor 1** (Claude's call, inside Jay's 3 to 5). Each lives in a hidden spot that is itself a secret in the existing secrets system: finding the spot is a discovery you can sell to Vesper (DESIGN 8.1).
- Each one gives a **permanent style trophy** the first time a character helps kill it (on the credit list): a small bonus that works with every weapon, so switching weapons never loses it. Examples (Claude's call): +2% damage against one monster race; +1 style level's worth of points; +5 movement speed; +3% max health.
- Respawn: 1 to 3 hours, random within that range (Claude's call), so a found spot is not camped empty forever but is not farmed either. The trophy is once per character; later kills give normal loot.
- They are tuned for a solo player at the right level or a small group below it, and are never needed for the main path.
- Placement: off the roads, in places that reward exploring (a cave behind a waterfall, a ruin cellar, a hollow tree in the Glade...). Map rules from `CLAUDE.md` apply. The 4 are listed in a GM-only file, never in player docs or the website.

### 4.9 Shop gear

- Jay changed the shop rule (2026-11-23): "the shop should have some gear that gets outclassed later." `DESIGN.md` 1 (pillar 5) and 11 are updated with his words.
- The shop sells a **starter set per class**: weapon plus armour, a bit better than NPC shop gear, for levels 1 to 15 (Claude's call on the band).
- Shop gear **cannot be tiered, has no familiarity and cannot be awakened**. The Floor 1 main weapon at tier 2 already beats it (checked by `balance.py`).
- No shop gear for Floor 2 and up at launch (Claude's call; adding any later is Jay's decision, one floor at a time, always outclassed by that floor's quest weapon at tier 2).
- Shop gear can be sold to other players on the market, like other shop items (DESIGN 11).
- **Mastery Respec** (Jay, 2026-11-23: "that will be the only way to acquire one"): sold only in the donation shop, never dropped, earned or given by NPCs. **(Claude's calls:)** it resets both style choices; style points already earned are kept, so the character lands at the same stage and picks again (no grind back); one use per item; it can be sold to other players on the market like any shop item, so the shop is still the only source; a 7-day wait between respecs on one character, so players can't swap style per fight.
- The shop only opens at public launch, so during friend tests the starter set is given by a GM command for testing.

### 4.10 What changes in existing systems

- `tools/gen_gear.py` grows into the generator for weapons, armour, tiers, ceilings and tokens for all floors (Floors 1 and 2 filled in); `tools/balance.py --check` enforces the ceiling rule and the shop rule.
- `tools/gen_economy.py` adds token drops and upgrade fees, and keeps every class making money at its grounds.
- Crafting: gear and weapon recipes, if any, are removed; crafters keep ammo, potions, supplies, cosmetics. Every material's description names where it drops.
- The stock Tibia items and NPC lines that mention materials we do not have (like "venomous slime") are found and removed or renamed.
- The floor boss reward changes from "top fighter gets the boss piece" to "everyone on the credit list gets the awakening" (the boss can still drop the rare piece).
- Sword skills: today they unlock at levels 60, 100 and 150 (DESIGN 5.3). The style signature abilities are new skills on top; the level unlocks stay.

## 5. Constraints

- Canary v3.6.1, protocol 15.11, OTClient Redemption 4.2. Item data must survive server restarts, trading and the market.
- No CipSoft names visible to players; `check_names.py` covers every new name.
- Numbers come from generators (`tools/balance.py`, `tools/gen_economy.py`, `tools/gen_gear.py`), never hand-edited tables.
- Every task is ticked only when tested through the real game (an in-game test or autopilot run), per CLAUDE.md.
- Pillar 6 (plain to learn) and the section 1 test.
- PvP: style abilities follow DESIGN 6.7 (only the Vanguard moves players, short roots with immunity, and so on).

## 6. Left to the builder

- How tier, familiarity and awakening are stored on items (custom item attributes, or Canary's own item tier field if it fits and shows in the client).
- The exact passive per style level and each signature ability, within section 4.2's roles and DESIGN 6.7.
- Exact numbers for drop rates, fees, ceilings and pacing, set in the generators and checked by `balance.py`.
- Which existing quests become steps 2 and 3, and the hidden mini-bosses' looks, spots and loot.
- The client window layout, within section 4.7.
- The order of work (the plan comes next).
