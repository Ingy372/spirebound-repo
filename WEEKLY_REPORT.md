# Update, 2026-11-24: the overnight Floor 1 playtest and review

(The 2026-11-23 gear report is in git history. The full review is `FLOOR1_REVIEW.md`; this page is the short version.)

## The answer to "do we stand a chance?"
Not yet, but it's fixable on Floor 1 alone. Our systems and our pitch (floors that open for everyone, a monument for
first clears, permadeath if you dare, fair PvP) are stronger than most servers'. What loses players today is the feel
of the first evening: a plain start, monsters that only bite, kill-count quests, a generated-looking town, and grounds
that swarm. Section 9b of the review has the scorecard and the order to fix things in.

## What changed overnight (all live after one server restart)
- **Hunting grounds:** Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow and Shard Fields rebuilt: calm gates,
  monsters spread out, two or three levels each, a party cave under four of them, faster respawn so the kill rate
  holds. Two test characters died at Boar Meadow's old gate before this. Only Bandit Road and Old Quarry are still the
  old swarming kind (they need buildings, next session).
- **Monsters fight differently:** rats flee, toads slow you, boars charge, wolves dart and run when hurt, moles
  burrow, snappers drag you down, bandits throw smoke, thornsnaps root, sentinels shield-bash.
- **Five rare glowing elites** (one per rebuilt ground), and a **treasure chest** hidden in every rebuilt ground (a
  first-time prize with a Hearth Shard, then a daily chest every 20 hours).
- **First hour:** first attack spell the moment you pick a class, a heal at level 4; the street lamps are lit (every
  lamp on Floor 1 was the unlit kind); every login says where the tower's race stands.
- **Quests:** every Floor 1 quest pays experience now, and offers and the Journal show the reward.
- **Gear:** the smith's upgrade was broken (fixed), the Gate Hound now comes back after a kill (your checklist needs
  it), the checklist and a sign at the Pass say to bring a party, shards have a pity counter and a sparkle.
- **Reasons to come back:** a daily login reward, a lucky climber every hour, and the Season Path's daily and weekly
  goals switched on for the friends test.
- **Money:** arrows cost 1 gold on Floor 1, so a Ranger no longer loses money hunting.
- **Safety:** the automatic test was writing into your game's database; it has its own now. A half-failed test had
  marked Floors 1-2 as cleared in your world; I removed that.

## Before you play (one step)
Restart the server: double-click `windows\Stop-Spirebound.bat`, then `windows\Start-Spirebound.bat`.

## Playtest checklist (about 45 minutes)
1. **New character (10 min):** make a new character. Is the yard lit? Can you cast your first spell right after the
   Registrar? Does the login message mention the tower's race?
2. **Boar Meadow (10 min, level 9-12):** walk in. Is the gate calm? Do boars charge? Try Oak Ridge (the ramp) and the
   Wallows (the holes in the south). Can you find the chest?
3. **Wolf Copse or Reedmarsh (10 min):** does it feel like a place, or still like a grid? Did you meet an elite?
4. **Weaponsmith (5 min):** with your Ranger, hold your bow, say `hi`, `upgrade`, `yes` to Garrick. Does it work now?
5. **Quests (10 min):** take a quest from Dorrow or Brannoch. Does the offer say what it pays? Does finishing it
   give experience?

## Open questions (my recommendation is assumed until you answer; QUESTIONS.md)
- **Q46:** a free "stance" at Mastery 5 so Floor 1 players feel the style choice coming? Recommended: yes.
- **Q47:** rebuild the arrival yard and Hearthgate before inviting alpha testers? Recommended: yes.
- **Q48:** the Gate Hound comes back after it dies (so everyone can finish the checklist). Built that way.
- Still open: Q45 (spear for Rangers), shop prices.

## Art and map requests
- `ART_REQUESTS.md` Batch 7: the elites use their ground's monster sprite for now; variants later.
- No map requests: I built the grounds. The last two (Bandit Road, Old Quarry) need ruined buildings and a mine.
