# Playtest notes (Jay writes here)

Write anything: bugs, "this feels slow", "I love this", "change X". Claude reads this at the start of every session and fixes notes before new work. Newest at the top. Date each session.

Template:
```
## 2026-11-15
- What I tested:
- Bugs:
- Felt good:
- Felt bad / change this:
```

---

## To try next (from Claude, 2026-11-25, evening)
- **Weapon skill keys are now Ctrl+1, 2, 3** (Shift+1-3 typed "!@#" into chat). Try them with chat on and off. Does Enter still fire a skill after you click one of its buttons?
- **Switch chat tabs, then type a line straight away:** does the first line get sent?
- **Make a new character:** you should leave the yard at level 2. Does the Registrar's door stand out now? Say `!hunt` in town and follow the directions: do the signposts help?

## To try next (from Claude, 2026-11-24, night)
- **Make a brand-new character** and go through the Arrival Yard to the Registrar. After you pick a path you land in the Proving: try your spells on the rats (they are on your action bar, buttons 3 and 4), then step on the glowing stone and fight Bramblejaw alone. Is it too easy or too hard at your level? Is the red-smoke stomp clear?
- Does the Quest Tracker show Pell's quest now when you take it?

## 2026-11-25 (Claude's own playtest: a fresh Ranger, about 25 minutes)
- Full report: `docs/playtests/2026-11-25-claude-ranger.md`. Played move by move with the new `tools/claude_play.py` (Claude reads every screenshot and picks the next move itself; no shortcuts).
- Good: Pell's quest, the Ranger kit (bow, quiver and armour all arrive), the Registrar's lines, Bramblejaw at level 5 (health got down to 42% once), the `!hunt` tip leading to wasps.
- Bugs, now roadmap C1-C3: closed tutorial gates can be walked through after bumping them (and the hint repeats on every bump); `!spells` marks style abilities as learned; small text and kit clean-ups.
- Confirms G7: I left the yard at level 5.

## 2026-11-25 (Grok play tester, session 3: Ranger on Grok Fourth, Vanguard on Grok Third, Arcanist on Grok Second, Mystic on Grok Tester; written down by Claude)
- Full report: `docs/playtests/2026-11-25-grok-session3.md`. Grok started at 09:35, before the client package was rebuilt (09:46), and described the stock client (Store button showing), so the client fixes since Monday weren't on its screen. That's the second session running. From now on the server tells anyone on an old client to download it again.
- Liked: Arc Slash hitting two rats, the Journal's Quests tab with directions, Vesper's six-stone hunt, Little Bix, the clear [Open PvP] message.
- *Fixed 2026-11-25 (checked against the database and the real Registrar):*
  - *New Ranger with nothing to shoot (worst bug): a level 3 character can't carry the whole starter kit, so the game dropped the last pieces (the torch, then the quiver with its 100 arrows) on the Registrar's floor. Starter items now ignore carrying weight, the quiver goes on before the rest, and the armour is worn instead of sitting in the backpack. Rangers who lost theirs get a quiver with arrows at their next login.*
  - *Can't log out for minutes: the engine kept "in a fight" on while any monster had picked you as its target, even pen rats behind the fence. Now the lock lifts 15 seconds after the last hit given or taken (never during a fight with players).*
  - *Cheese gate held an Arcanist for good: from the second rat on, a character who hasn't looted gets the cheese straight into the backpack. The old "third try" fallback reset on every login and only counted walking in from one side.*
  - *Every closed yard gate now says why in the Server Log, not just at the bottom of the screen; "sword skills" now reads "skills"; the potion hint says "Use with..., then click yourself".*
  - *Action bar: the stock client keeps one bar per class, pre-filled with Tibia spells, and swapped it in when the class changed. Our client now replaces those stock spells with the path's attack and heal at every login, without touching buttons a player set up.*
  - *Bramblejaw's stomp says what to do: "step two tiles away from it, out of the red smoke". The skip swirl now says the fight stone is "4 steps south of this swirl".*
  - *The Journal crashed for characters with no path yet (server error at Grok Fourth's first login).*
- Left for later: roadmap G8-G12 (Registrar door, walking every `!hunt` route, retesting the client-side items on the current client, Vesper's second visit, small clean-ups).

## 2026-11-24 evening (Grok play tester, session 2: Arcanist on Grok Second, Vanguard on Grok Third; written down by Claude 2026-11-25)
- Full report: `docs/playtests/2026-11-24-grok-session2.md`. Grok's client was still the 19:00 package, so the evening's client fixes (clean speech bubbles, spells put on the action bar, quest auto-tracking) were not on its screen. The package is rebuilt (2026-11-25 morning).
- Liked: the new class pitches, the Registrar hall, Warden Ketta, Pell's cheese warning, the "you need a target" line, and `!hunt` (true directions, works in town, real class kills).
- *Fixed 2026-11-25 (checked in the client with the `s2_fixes` autopilot route):*
  - *Cheese gate hard-lock (top bug): the body decayed before the cheese reached the backpack. The gate now hands over a cheese on the third try (the first two still teach opening a body), and the hint says "if the body is gone, beat another rat".*
  - *The Proving's fight stone and the skip portal both glowed blue: the fight stone now glows red; the skip is a blue swirl that warns once ("this skips Bramblejaw...") and only sends you on if you step on it again.*
  - *Two sets of attack names: the row at the bottom is now labelled "Weapon skills (from the weapon in your hand)", and it stays empty before a path is chosen (no club skills in the yard). Arriving in the Proving explains both rows and warns about the hall's rats.*
  - *"a Arcanist" now reads "an Arcanist" (Registrar and Ascendancy). "No" to a mode goes back to the modes, not to the class choice.*
  - *No level-up hunting or spell tips before a path is chosen (the level 3 Toad Pond tip in the yard).*
  - *Esc no longer switches chat off; it clears what you were typing.*
- Not changed, and why:
  - *Magic Level 0 after many casts: the weapon skills (Spark Edge...) cost no mana, so they don't train Magic Level; the spells (ember strike...) do. It rises with spell casting.*
  - *Character list showing level 1 / None: the client reuses the list from your last login; logging in again shows the saved level and path.*
  - *"There is not enough room" on walls, left-click walking to a monster, a wand on the action bar asking "use with": the game's standard behaviour (right-click or the Battle List attacks).*
  - *Fast early levels (1 to 4 in three yard rats): Q52.*

## 2026-11-24 (Grok play tester, first-time Mystic, about an hour; written down by Claude)
- Full report: `docs/playtests/2026-11-24-grok-session1.md`. Grok's PC was overloaded, so lag-type items wait for a rerun (G6).
- Liked: Pell's intro, the stone-path stops, the Journal tip and especially `!hunt`.
- Headline: an hour in, level 5, no kill as a Mystic.
- *Fixed the same day:*
  - *Club skills on a Mystic's bar: the yard's practice club stayed in the hand, and the bar follows the weapon. The Registrar now takes the club back and puts the path's weapon in the hand.*
  - *Maelis's bubble showed `{yes? or {no??}`: a bug in the stock client's bubble code (any line with a comma or question mark). Fixed in our copy of the chat module.*
  - *"No confirmation after normal": the Registrar did reply, but only in that broken bubble. Registering now also writes "You are now a Mystic, living by the Normal rules." and your first two spells in the Server Log.*
  - *Thin pitches: each path now says how it plays, how hard it is and its first spells; the mode question explains normal, hardcore and death game in one line each.*
  - *`!hunt` "south, about 80 steps" hit a tree wall: directions now name the town gate and the ground's entrance ("leave Hearthgate by the south gate, then about 30 steps west to its north entrance").*
  - *[Open PvP] on Floor 1: real, but nobody under level 50 can attack or be attacked. The first time you walk into it, the Server Log now says so.*
  - *Pell's quest now says the pen's way in is the gap in the fence and that the next gate wants a rat's cheese. The yard signs say "Stop 1 of 3" etc.; stop 2 is "Skills and spells".*
- Still open: G1-G6 in ROADMAP.md (first spells on the action bar, a fast first class fight, Pell's quest in the tracker, "you need a target", client clean-up, a calm rerun).

## 2026-11-23 (Jay, level 12 Ranger; written down by Claude from chat)
- Verdict: "floor 1 is boring."
- No quests, or none that are easy to find.
- Hearthgate is low on NPCs and visual effects.
- Toad Pond is "ok i guess, but its way to small now." Levelling would take forever and be boring.
- No gear or weapon progression except crafting, and Jay is not a fan of crafting. Players hear they need "venomous slime" but have no idea how to get it or where the monster is.
- Jay: "i would lean towards another system outside of crafting for weapon/gear progression and improvement."
- Claude's findings: Floor 1 has only 3 named pieces per class (a 3% drop from the hardest monsters, a quest reward, the boss), so a level 12 sees none. 12 Floor 1 quests exist but only the Arrival Yard points to them. "Venomous slime" is not one of our materials; it comes from a stock engine item or NPC.

## To try next (from Claude, 2026-11-14)
- **The new Ratwarren** (levels 1-4, west of Hearthgate): walk in from the gate, hunt the Yard, take a hole down into the Warren, then follow the long tunnel south to the Deep Warren. Does it still feel like a flood? Too empty? Write what you think below.
- **The new Burrow Hills** (levels 11-16, north-east of Hearthgate, gate on the west side): walk the north hollow, climb a ramp onto the Crown (the hill in the middle), come down the other ramp, then take a hole down into the Molework. The far east end and the Crown's east side are meant to be the hard part. Use "Test Vanguard" or a character around level 14. Too calm? Too hard? Write it below.
- **Toad Pond, Sproutling Glade, Waspgrass Fields** (levels 3-12): Toad Pond has four ponds and an island you reach by bridges; the Glade has a ring of old trees with a hole down in the middle; Waspgrass has Hive Knoll, a hill you climb by ramps from the south meadow. Each has a cave below with more monsters. Calm enough? Too empty on top? Write it below.
- **The new spawn habits** (all five rebuilt grounds, 2026-11-16): rats now come in clumps of 5 to 8 below the Ratwarren, toads in pairs, wasps in clumps with a cloud of 9 at the hive, sproutlings thick round a nest in the Root Hollow, boars alone. Does each ground feel different from the others? Is any clump too much for its level? Write it below.

(no playtests yet: the first one comes at the end of Phase 1)

## 2026-11-11 (Jay, first look)
- What I tested: logging in, walking Hearthgate, the Arcanist path. Not the boss.
- Felt bad / change this:
  - Content is very thin (matches REVIEW.md). Quests or a tutorial are needed so players know where to go.
  - Hearthgate is too spread out; walking between places takes 2-3 minutes. Travel speed matters a lot in Tibia, so starting speed must be higher.
  - Idea: new characters spawn with a sheet of paper: lore, their mission, and the first few objectives.
  - Arcanist is broken: the wand needs level 6, so the player fist-fights to get there.
  - Couldn't find the NPC who sells spells, so couldn't test spells.
- Done the same day: mage starter wand and rod usable from level 1; base walking speed 110 → 170 for every vocation; starter letter (Registrar gives it; `!guide` re-reads it); `!spells` lists your spells (nobody sells them, they unlock by level); town compacted (depot beside the temple, shops just outside the temple door, monument closer). Still open: real quests and the Arrival Yard tutorial (ROADMAP R11, R12), more Hearthgate tightening in the real map.

## 2026-11-13 (Jay, Arrival Yard on Climber)
- Bug: killed 3-4 rats and still couldn't pass a gate. *Fixed the same day: the kill was counted (gate 1 was open); the gate that blocked was the loot gate. Pen Rats dropped only a few coins (nothing one time in five) and autoloot didn't count as looting, so it could be impossible. Pen Rats now always drop a cheese, and carrying it opens the loot gate.*
- Bug: "Only the worthy may pass" at the first gate. *Fixed the same day: the fence doors were the engine's own quest doors, which refuse everyone. The gates are now open gaps; the yard's own check stops you until the step is done.*
- Bug: the potion gate let me through before I drank. Wish: something visible at each gate. *Fixed the same day: ordinary health regeneration was being counted as the potion. Now the gate opens only when the potion has really left your backpack. Each gap now shows a harmless shimmering wall of energy.*
- (Ranger run) No attack spells early: nothing to attack with but basic hits after level 8. *Done the same day: Rangers get Piercing Shot (level 8) and Scatter Shot (16); Vanguards get Heavy Strike (8) and Whirlwind (16). They grow with the weapon skill, not magic level.*
- (Ranger run) No way to equip arrows. *Fixed the same day: in this game version a bow only fires from a quiver worn in the shield hand. New Rangers get a quiver with their 100 arrows inside; existing Rangers get a quiver at their next login; Fletcher Tamsin sells quivers (150 gold).*
