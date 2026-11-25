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
