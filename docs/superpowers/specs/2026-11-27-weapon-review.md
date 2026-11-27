# Weapon system review and redesign (2026-11-27)

Status: **designed, not built.** Written by the Fable design session from Jay's notes of 2026-11-27. Building goes to Opus sessions (roadmap tasks WA1 to WA7).
It changes sections 4.3 to 4.6 of `2026-11-23-gear-progression-design.md` (the built system). It does **not** touch section 4.2 (the style tree), which is being redesigned in `2026-11-27-style-trees-v2.md`.
Lines marked **(Claude's call)** are mine and Jay can veto them. Jay's own words are quoted.

---

## 0. The short version (for Jay)

1. **More weapons.** Every class gets **six weapons on every floor** instead of one main weapon and a rare drop. They are the same strength overall, but each fights differently: steady, fast, heavy, elemental, lucky (rare drop) and secret (from a hidden beast). Each one comes from a different place, so every kind of player has one to chase.
2. **Familiarity resets when a weapon changes hands.** Tier stays on the weapon. Familiarity belongs to the character who earned it. When a **different character** first fights with the weapon, its familiarity drops to 0 and starts counting for them.
3. **A second awakening: "Ascended".** If you beat the next floor's boss still using your awakened weapon from the floor below, it ascends: a new name, your name carved on it forever, a small new trick, a title and a server announcement. It does **not** get stronger, and it only happens once per weapon. I'm pushing back a little here: extra power would make switching weapons pointless. I explain why in section 5.

---

## 1. What I reviewed

- `DESIGN.md` 5.2, 5.3, 5.6 and the gear paragraph in 8.3.
- The gear spec, sections 4.3 to 4.10 (the built system).
- `tools/gen_gear.py` (weapons, power formula, shards), `tools/balance.py` (`gear_problems`: the ceiling rule), `tools/gen_economy.py`.
- The Lua: `lib/spirebound/gear.lua` (item state, perks, Weaponsmith, awakening), `scripts/spirebound/gear.lua` (drops, Weaponsmith and Dorrow talk), `lib/spirebound/progress.lua` (`SpireProgress.credit`: where familiarity grows), `lib/spirebound/trophies.lua` (the four hidden beasts), `scripts/spirebound/secret_gear.lua` (how a bound item blocks trade and moving).

How the built system works today:
- A weapon's power is one number that multiplies all its holder's damage: `(1 + base + tier x step + awakening) x (1 + 1.5% x familiarity)`.
- Floor 1: base +10%, +4% per tier, awakening +10%. Fresh = **1.10**. Maxed (tier 5, familiarity 10, awakened) = **1.61**.
- Floor 2 (from the ceiling rule): base +48.9%, +6% per tier, awakening +15%. Fresh = **1.49**.
- Tier, familiarity points and awakening are stored on the item as custom attributes (`sb_tier`, `sb_fam`, `sb_awake`, with the weapon's id in `sb_gear`). Familiarity grows in `SpireProgress.credit` each time the holder gets a kill share.
- Per class on Floor 1: one main weapon from Captain Dorrow (Vanguard sword, axe or mace; Ranger bow or crossbow; Arcanist wand; Mystic rod) and one rare drop (0.5% from two elites and the Stonehorn Ram) with a small perk: life leech, crit, mana leech or stronger heals.

## 2. What works (keep it)

1. **The checklist is clear.** Level 10 weapon, temper quest, Gate Hound shards, tiers, boss awakening. It passes the section 1 test ("say your next upgrade in one sentence").
2. **The ceiling numbers are right.** A fresh Floor 2 weapon is 92.5% of a maxed Floor 1 weapon and passes it after about 2.1 hours of hunting. "Stay" is right for a couple of hours, then "switch" is. That is what makes the choice real.
3. **Upgrades never fail.** Shards have pity timers, rewards wait for a fighter who died before the boss did, and lost weapons are re-issued. Nothing gambles with gear.
4. **One power number.** Every weapon's strength is a single multiplier, so the generator can prove it follows the ceiling rule. The new weapons keep that and add their differences on top (section 3.3).
5. **Item-stored state** survives the depot, trades and restarts. The new rules build on it.

## 3. What to change

| # | Problem | Fix |
|---|---|---|
| C1 | **Too few weapons** (Jay's note 1). Arcanists and Mystics have exactly one weapon family, so on Floor 1 their whole choice is "the rod, or a 0.5% lucky rod". | The weapon array in section 3.1: six weapon kinds per class per floor. |
| C2 | **The rare drop is a free upgrade.** It has the main weapon's exact power **plus** a perk. The anti-goal "one right answer" applies: if you have one, you always use it. | Every weapon gets a **rating** (section 3.3). A rare drop may sit up to 2% above the steady weapon because luck should feel good, but no higher. The steady weapon keeps its own advantages: it can be reforged and re-issued, and it gets the free temper. |
| C3 | **The Ranger has no spear weapon**, although DESIGN 5.2 lists the spear family and spec 4.5 step 1 offers it. | Add the Trailwarden Spear as a third steady weapon for Rangers (WA4). |
| C4 | **Familiarity survives trade** (Jay's note 2). | The bond rule in section 4. |
| C5 | **The market is untested for our gear.** Canary's market may refuse items with custom attributes, or strip them (a tier 5 weapon would come out plain). The spec says gear must survive the market. Nobody has tried it yet. | WA2: list a tiered weapon on the real market and buy it with another character. If the engine strips or refuses it, block Spirebound weapons from the market with a clear message ("trade it in person") so nothing is ever silently lost. |
| C6 | **The boss awakens "a Floor 1 weapon you hold or carry".** With six weapons a player may carry three, and the code picks the one in hand, else the first in the bags. | Rule: the boss awakens the weapon **in your hand**. A fighter who was dead at the kill gets the reward later (as today), and it goes to their Floor 1 weapon with the most familiarity bonded to them. One awakening per kill, so awakening a second weapon means another boss kill (the private repeat portal, R9, gives that a purpose). |
| C7 | **Trying a new weapon means losing your tiers.** If the variants start at tier 0, nobody at level 28 will try one. | **Retune** at the Weaponsmith (section 3.4): move tiers from one of your Floor 1 weapons to another, minus one tier, for a fee. |

### 3.1 The weapon array: six kinds per class, every floor

Each kind fills a different player's wish, and each has its own source, so no two are got the same way.

| Kind | How it fights | Where it comes from (Floor 1) | Who it's for |
|---|---|---|---|
| **Steady** (today's main weapon) | Even damage, no tricks. Can be reforged into another family, re-issued if lost, tempered free. | Captain Dorrow at level 10 (as today) | Everyone; the safe pick |
| **Swift** | Hits **8% softer**, sword skills recharge **20% faster**: more combos, more skill effects. Ranger version: shorter range (5 tiles). | **Weaponsmith commission** from level 15: gold plus Rough Hearth Shards (price set in `gen_economy.py`) | Players who like pressing buttons and chaining combos |
| **Heavy** | Hits **5% harder**, Finishers **+20%**, sword skills recharge **20% slower**: fewer, bigger moments. Vanguard version is **two-handed** (no shield, see 3.3). Ranger version: longer range (7 tiles). | The **Gate Hound** (field boss): each credited fighter has a 15% personal chance per kill for their own class's Heavy weapon **(Claude's call)** | Players who like big numbers, and a reason to keep killing the Gate Hound |
| **Elemental** | A quarter of each hit becomes an element (fire, ice, earth or energy). Hits harder against monsters weak to it, softer against resistant ones. | A **side quest** around level 18-20, one per class, named in the Next-upgrade window | Players who learn monsters and pick the right weapon for the hunt |
| **Rare** (today's rare drops) | Its perk: life leech (Vanguard), crit (Ranger), mana leech (Arcanist), stronger heals (Mystic). Up to 2% above Steady. | **Elites** and the Stonehorn Ram, 0.5% (as today, own class twice as likely) | Grinders; the "a rare weapon lies in the remains!" moment everyone hears about |
| **Relic** | A **skill line**: it improves one named sword skill (see 3.2). Up to 2% above Steady. | A **hidden beast**: each of the four drops one class's relic, 8% per kill for each credited fighter of that class **(Claude's call)**. Never listed in the Next-upgrade window. | Explorers; the secret weapon others ask about |

**Why six and not more (Claude's call):** six is one per kind of player (follower, button-presser, big-hitter, thinker, grinder, explorer), and each comes from a different part of the game we already have (quest giver, Weaponsmith, field boss, side quests, elites, hidden beasts). More than six means two weapons from the same source doing nearly the same thing: bloat. Fewer than six leaves a kind of player with nothing to chase. Across ten floors that is 24 weapons per floor, about 240 in all, but a player only ever looks at their own class's six on their floor.

**Every floor keeps the six kinds but changes the details**, so it isn't the same list repainted: the element follows the floor's theme (Floor 2's Mesa: energy), the skill lines touch different sword skills, and the sources move to that floor's quest giver, field boss, elites and hidden beasts. A floor with no hidden beasts has no Relic.

**Families:** Steady comes in every family of the class (Vanguard sword, axe, mace; Ranger bow, crossbow, spear). The other kinds come in **one** family each, spread so every family appears **(Claude's call)**. Example for the Floor 1 Vanguard: Swift = sword, Heavy = two-handed axe, Elemental = mace.

### 3.2 Floor 1 weapon list (draft names, Claude's call; all pass `tools/check_names.py`)

| Class | Steady (Dorrow) | Swift (Weaponsmith) | Heavy (Gate Hound) | Elemental (side quest) | Rare (elites) | Relic (hidden beast) |
|---|---|---|---|---|---|---|
| **Vanguard** | Hearthguard Sword / Axe / Mace | **Millcross Shortsword**: *Fourfold Rend* strikes five times | **Gatebreaker Greataxe** (two-handed): *Executioner's Drop* bonus below 40% health instead of 30% | **Emberforged Mace** (fire): *Tremor Blow* leaves burning ground for 3 s | Briarguard Sabre (life leech) | **Old Tusk Cleaver** (from Old Tusk): *Split Earth* reaches one tile further |
| **Ranger** | Trailwarden Bow / Crossbow / **Spear (new)** | **Reedmarsh Shortbow** (range 5): *Quickdraw* fires two arrows | **Quarry Arbalest** (range 7): *Siege Bolt* pierces to a second target | **Frostfletch Bow** (ice): *Pinning Shot* slows 1 s longer | Copsewood Bow (crit) | **Hollowfang Bow** (from Hollowfang): *Arrow Storm* covers one more tile |
| **Arcanist** | Wand of Hearth Sparks | **Wand of Quick Sparks**: *Spark Edge* recharges at once after a combo | **Wand of Kindled Stone**: *Starfall Rite* hits 15% harder at the centre | **Wand of Stormglass** (energy): *Flame Script* also chains to one more monster | Wand of Ember Script (mana leech) | **Drowned Warden's Wand** (from the Drowned Warden): *Flame Script* covers one more tile |
| **Mystic** | Reedroot Rod | **Willowswitch Rod**: *Thorn Edge* recharges at once after a combo | **Oakheart Rod**: *Verdant Burst* heals the party 25% more | **Rod of Mire Frost** (ice): *Frost Script* slows 1 s longer | Thornward Rod (stronger heals) | **Briar Mother's Rod** (from the Briar Mother): *Verdant Burst* reaches one more tile |

The skill lines are examples. The builder sets the final ones in the generator, but each must stay small and touch **one named sword skill** (Jay's "skill-bonus hook"). They live in the sword-skill code (`sword_skills.lua`), **not** in the style tree. Arcanist and Mystic sword skills ("spellblade arts") work the same way.

Every weapon is awakened by the floor boss like today (awakened name: `<name>, Awakened`, or its own name for the steady ones). Every weapon uses the same tiers, shards and familiarity.

### 3.3 Keeping it fair: the weapon rating

The trade-offs must not make one weapon the right answer. `tools/gen_gear.py` gets a **rating** for every weapon: its expected damage compared with the Steady weapon of the same floor, tier and familiarity, in a simple model that `balance.py` checks.

- **Model (Claude's call):** 35% of a fighter's damage comes from sword skills, 65% from normal attacks and spells; a third of skill damage comes from Finishers; elements are averaged over that floor's monsters' weaknesses (the `elements` in `tools/gen_monsters.py`).
- Swift: 0.92 x (0.65 + 0.35 x 1/0.8) = **1.00**. Heavy: 1.05 x (0.65 + 0.35 x (1/1.2) x 1.067) = **1.01**. Steady = 1.00.
- **The band:** every weapon's rating must be between **0.98 and 1.02**. Perks (leech, crit, heal) and skill lines count inside the band at a price set in the generator.
- **The one exception: two-handed Vanguard weapons** get +10% on top (rating up to 1.12), paid for by giving up the shield. **(Claude's call, Q105.)**

**Checked against the ceiling rule** (numbers from `gen_gear.weapon_power`, run 2026-11-27):

| Check | Rule (spec 4.3) | Result |
|---|---|---|
| Fresh Floor 2 vs maxed Floor 1, same kind (Swift vs Swift...) | 90-95% | **92.5%** (unchanged) |
| Fresh Floor 2 Steady vs the best possible maxed Floor 1 weapon (rating 1.02) | 90-95% | **90.7%** |
| Worst fresh Floor 2 weapon (0.98) vs best maxed Floor 1 (1.02) | loose check: at least 88% | **88.9%** |
| Hours for a fresh Floor 2 Steady to pass the best maxed Floor 1 | 2-3 h | **2.45 h** (7 familiarity levels) |
| Worst Floor 2 at tier 2, familiarity 5 vs best maxed Floor 1 | must beat it | **1.695 vs 1.642** (passes) |
| Two-handers | compared only with the floor below's two-hander | **92.5%** |

So the ceiling rule still holds. `balance.py --check` gets the like-for-like checks plus the loose cross-kind ones (WA3). One edge: the very worst Floor 2 weapon takes about 3.15 h to pass the very best Floor 1 weapon. That's acceptable for a cross-kind comparison, and it is why the cross-kind check is looser.

### 3.4 Retune: trying a weapon without losing everything

At the Weaponsmith (**Claude's call**): "retune" moves the tier of one of your Floor-n weapons to another Floor-n weapon you own. The target gets the source's tier **minus one** (never below its own), the source drops to tier 0, and you pay a gold fee. Familiarity is not moved: it belongs to each weapon and you. Awakening is not moved. This lets a level 28 player try the Heavy weapon they just got without throwing away fifteen shards, and it is still a gold and shard sink.

### 3.5 Shards and the economy

No change to drop rates. The array creates more demand for shards (a second weapon to tier, the Swift commission costs Rough shards), which makes Jay's "sell or save" choice stronger: the market for shards gets more buyers. Tier 5 on **one** weapon still lands around level 30-35 for a solo player who keeps every shard (the existing check). Tiering a second weapon is meant to be a long goal or a market purchase.

## 4. Familiarity resets when a weapon changes hands (Jay's note 2)

Jay: "i love the idea of the mastery sticking with the weapon, but i feel like familiarity should be reset upon trade. also that will increase the uniqueness of each play through."

### 4.1 The rule

- **Tier stays on the weapon. So do awakening and ascension** (they are the weapon's story, see 5).
- **Familiarity belongs to the character who earned it.** Each Spirebound weapon carries a **bond**: the character it is familiar with.
- **When a different character fights with it**, familiarity goes to 0 and the bond moves to them. They see: "Copsewood Bow doesn't know you yet: its familiarity starts again with you."
- The item's look text shows the bond: "familiarity 6/10 with Aldra".

### 4.2 What counts as a change of owner

**A different character fights with it** (gets a kill share while holding it), or **puts it in their weapon hand**. That one test covers every route:

| Situation | Resets? |
|---|---|
| Traded to another player, then used | **Yes** |
| Bought on the market, then used (if the market allows our gear, see C5) | **Yes** |
| Looted from your corpse by your killer (Hardcore drops, PvP) and used | **Yes** |
| Lent to a friend for one hunt and given back | **Yes, twice**: the friend starts at 0, and when you take it back it starts at 0 again for you. A weapon remembers one fighter. |
| Passed to **your own other character** (same account) | **Yes (Claude's call, Q104).** Otherwise a level 200 alt could level familiarity for a new character, which is the "farm it for someone else" Jay wants to stop. |
| You drop it, store it in the depot, house or mail, and pick it up yourself | No |
| You get it back from your own corpse | No |
| A friend only **carries** it in their bag and never holds it | No |
| Reforged into another family | Already resets (today's rule); the bond stays with you |
| Re-issued by the quest giver after a loss | A new weapon, bonded to you, familiarity 0 |
| Weapons already in the game with no bond (from before this change) | The first character to fight with it becomes its bond, with no reset |

Jay said "reset upon trade". I recommend resetting **on first use by the new owner**, not at the moment of the hand-over (Q104). The result is the same for every real trade, and it is far simpler and safer to build. There is only one place to check (instead of trade, market, corpse, floor, mail and house separately), and a weapon handed over only to be carried keeps its numbers.

### 4.3 How the engine detects it

- Store the bond on the item as a new custom attribute, `sb_bond` = the character's id number (`player:getGuid()`), next to `sb_fam`. It survives restarts, the depot and trades, like the other attributes. The character's name for the look text comes from the id.
- **Set it** when `SpireGear.make` gives a weapon to a player (Dorrow, quests, re-issue, reforge) and whenever an unbonded weapon is first used.
- **Check it** in two places:
  1. `SpireProgress.credit` (`lib/spirebound/progress.lua`), the only place familiarity grows. If `sb_bond` is someone else, set `famPoints` to 0 and the bond to this player **before** adding the share. This alone makes the rule hold in every case, because familiarity cannot grow anywhere else.
  2. When a weapon is moved into a hand slot (a `playerOnMoveItem` callback, like `scripts/spirebound/secret_gear.lua`), so the player sees the reset at once and not on their first kill. This is only for the message: rule 1 is the safety net.
- Nothing needs the trade, market or corpse events, which is why this is reliable.

## 5. Awakening on later floors: the "Ascended" weapon (Jay's note 3)

Jay: "should it continue to grow if the player manages to make it floor 2 with the same weapon and secure a boss kill? if so how should it grow? i feel like that would be a unique challenge so it should provide a unique reward. feel free to push back."

### 5.1 My recommendation: yes, once, as a trophy, not as power

**It's a real challenge.** At the Floor 2 boss, a player who switched would hold a Floor 2 weapon around tier 5 and familiarity 10 (power about 2.06). A maxed, awakened Floor 1 weapon is 1.61: **about 78% of the damage**. Beating the boss with the old weapon is hard, possible in a good group, and worth celebrating.

**Why the reward shouldn't be power (the push-back):** any power you give at the moment of the kill only matters afterwards, which means on Floor 3. There, a fresh Floor 3 weapon is already 2.06 and the old Floor 1 weapon is 1.61 (78%). To matter on Floor 3, the lift would have to be enormous, and then nobody would ever switch: the anti-goal "old faithful forever". A small lift does nothing. So power is either pointless or game-breaking, and the reward should be **pride, story and a small side-grade**.

### 5.2 How Ascension works

**Requirements** (all checked at the boss kill):
1. The weapon in your hand is from **the floor just below** this boss's floor (a Floor 1 weapon at the Floor 2 boss).
2. It is **awakened**.
3. It is at **familiarity 10, bonded to you** (section 4). This ties the two notes together: you can buy someone's awakened weapon, but you must earn its familiarity yourself before it can ascend, so the journey is yours.
4. You are on the boss's credit list **and dealt at least 10% of its damage yourself** **(Claude's call)**, so a group cannot carry a passenger to an ascension.

**What it gives:**
1. **A new name:** `<awakened name>, Ascended` (e.g. "Stairlord's Edge, Ascended").
2. **Your name carved in it, for good:** "Ascended by Aldra at the Floor 2 boss, Season 1." The line stays if the weapon is traded or sold later, so an ascended weapon is a piece of server history. (Its familiarity still resets for the next owner.)
3. **A legacy line (side-grade):** your sword-skill combos stay open **one second longer** (5 s instead of 4) while you hold it **(Claude's call)**. It is fun and visible, and it counts inside the rating band, so its overall power stays the same.
4. **A look:** a small sparkle on its hits; later its own icon (an art request for Grok).
5. **For the character:** the title **Unbroken**, an entry on the Discoveries page and the website, and a server-wide announcement ("Aldra brought the Stairlord's Edge to the top of Floor 2!").
6. **Heirloom (once):** at the Weaponsmith you can **lay it to rest**: the ascended weapon becomes a house trophy (it can't be wielded again), and your **current** weapon gains **2 familiarity levels** at once. The stubborn path then pays you back when you finally switch: a fresh Floor 3 weapon passes the old one after about 1.4 h instead of 2.45 h. It's a small, one-off reward for a hard thing. **(Claude's call, Q106.)**

**Where it stops:** **once per weapon, one floor up.** A Floor 1 weapon can ascend at the Floor 2 boss and nowhere else. Two floors up (Floor 1 weapon at the Floor 3 boss) the old weapon does about 56% of the damage of a proper Floor 3 weapon. That fight is mostly being carried, and the 10% damage rule would fail it anyway. I'd leave a "Legend" mark for that out of launch and revisit when Floor 3 is real.

**Against "switch or stay" (spec 4.6):** On Floor 2, staying with the old weapon is the right call for the first ~2.5 hours (unchanged), and the wrong call for raw power after that, as designed. Ascension adds a third choice for the stubborn: **stay on purpose, hunt about 20% weaker, and earn a trophy and a title.** That is a challenge run, not the best path, so switching keeps its point. On Floor 3 everyone switches (the ascended weapon is two floors old), and the heirloom makes that switch a little sweeter.

**Ceiling rule:** unchanged. Ascension adds no power, the legacy line sits inside the rating band, and the heirloom only touches familiarity (it shortens one switch, once per ascended weapon). The ceiling check doesn't need to change; WA6 adds a check that ascension never changes a weapon's power number.

**Building it:** the rule, its checks and its tests can be built now on Floor 1 data (WA6), but it only switches on when the Floor 2 boss exists (Floor 1 first, Jay 2026-11-26).

## 6. What changes in code (for the builders)

- `tools/gen_gear.py`: a `kind` per weapon (steady, swift, heavy, elemental, rare, relic), with its source, hit factor, cooldown factor, finisher factor, element and share, skill line, two-handed flag and range. The rating model from 3.3. The Floor 1 list from 3.2, with the Ranger spear.
- `tools/balance.py` (`gear_problems`): the rating band, the like-for-like ceiling checks and the loose cross-kind checks from 3.3, and a check that ascension adds no power.
- `tools/gen_economy.py`: the Swift commission price (gold plus Rough shards) and the retune fee. Every class still earns at its grounds.
- `lib/spirebound/gear.lua`: `sb_bond` (set, check, look text), the hit, cooldown and element effects (through the existing damage hook `SpireGear.onDealtPerk`, which already changes hit size), awakening only the weapon in hand (C6), retune, and ascension (`sb_ascended`, `sb_ascended_by`).
- `lib/spirebound/progress.lua`: the bond check in `SpireProgress.credit`.
- The sword-skill code: the per-weapon skill lines, the Swift and Heavy cooldown factors, and the ascended combo window. **Not** the style tree or mastery files (another session owns those).
- The Gate Hound, the four hidden beasts, the Weaponsmith (commission, retune, lay to rest), and three to four side quests for the elemental weapons.
- The Next-upgrade window: an "Other Floor 1 weapons" list with sources (Relics never shown until found).
- Market: the WA2 test, and a block if needed.
- Art: one still icon per new weapon (Grok prompts in `ART_REQUESTS.md`), 15 for Floor 1.

## 7. Questions for Jay (in QUESTIONS.md)

- **Q104** Familiarity reset: on the new owner's first use (recommended) rather than at hand-over; your own other characters count as new owners.
- **Q105** Six weapon kinds per class per floor; Vanguard two-handers get +10% for giving up the shield.
- **Q106** Ascension: yes, once per weapon, one floor up, for pride and a side-grade but no power, with the heirloom.
