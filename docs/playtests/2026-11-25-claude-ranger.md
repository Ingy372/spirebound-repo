# Claude's playtest, 2026-11-25: a brand-new Ranger, about 25 minutes

New character "Claude Climber" (level 1, no path), played one move at a time with `tools/claude_play.py`. I looked at
every screenshot and decided each move myself, with no `/pilot` shortcuts. Screenshots and the full transcript are in
`.local/claude_play/2026-11-25_1636/` (on Jay's PC only).

## What I did
Arrival Yard: Pell, the pen, his quest, back to report. Then the stone path to Registrar Maelis, Ranger + Normal, the
Proving (hall rats, then Bramblejaw alone), Hearthgate, and the `!hunt` tip to Waspgrass Fields (killed wasps to level 8).

## Worked well
- Pell's intro and quest are clear; the Quest Tracker showed "0 of 3" straight away.
- The Ranger kit really arrives now: bow in hand, quiver on, armour worn (this morning's fix holds on the real path).
- The Registrar's pitch and mode questions read well; the messages after choosing say exactly what to do next.
- Bramblejaw is about right for a level-5 Ranger: the stomp warning is clear, my health dropped to 42% once, one potion.
- Arriving in Hearthgate gives a `!hunt` tip with directions, and following it led to wasps. Level 8 unlocked Wayfinder
  with a clear message.

## Bugs
1. **Closed tutorial gates can be passed (serious).** Walking into the "spells" gate kept pushing me back, but after
   about 20 seconds of bumping I was through it, and through the potion gate as well, without saying `!spells` or
   drinking the potion. The fence next to the gates is solid, so I went through the gate tiles, not around them.
2. **Gate hint spam.** Each bump repeats the hint at the bottom of the screen: 65 copies in 20 seconds.
3. **`!spells` says the Ranger already knows abilities it doesn't have.** At level 8 with no style path, the list marks
   Farshot, Snarefield, Last Light, Arrow Squall, Web of Briars and Wayfarer's Stride as "(learned)". Those come
   from style paths and final choices, so they are not learned yet.
4. Small things:
   - Every hit message has a double space: "due to your  attack".
   - Coming back to Pell with the quest done, "hi" gives the normal greeting. Nothing tells you to say "report".
   - Maelis's speech bubble is still floating in the Proving after you arrive.
   - The area label in the Proving still says "Hearthgate Plains [Guarded]".
   - After the Registrar the backpack holds two shovels and two ropes (the yard kit plus the Ranger kit).
   - The gap in the pen's fence counts as a safe zone, so attacking from it says "This action is not permitted in a
     protection zone". A new player standing in the gateway won't know why.

## Balance notes
- I left the yard at level 5 and the Proving at level 7, which confirms G7 (target: level 2 to 3).
- Distance skill went from 10 to 25 by level 8 (skills are 10x by design; Jay may want to look at this).
- `!hunt` sent my Ranger to Waspgrass Fields, which the plan lists as an Arcanist class ground. It works fine for a
  Ranger, but class grounds were meant to suit one class.

## Testing tools
- My test helper (not the game) walked me into the forest once, and a walk aimed at the Registrar's own tile reported
  "stuck". `claude_play.py` now has a `walk_to` with planned paths; use it rather than raw coordinates.
