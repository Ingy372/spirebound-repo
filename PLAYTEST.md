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
