# Update, 2026-11-25 morning: what got done overnight

(The 2026-11-24 report is in git history. Details per task: `PROGRESS.md`, `ROADMAP.md`.)

## The short version
Almost everything from your "Floor 1 is boring" list now has a first version in the game: monsters that fight in
different ways, quests that aren't "kill 10 of X", quests you can find, a livelier Hearthgate, a bigger Toad Pond, a
style choice on Floor 1, and your approved monster art in the real client. The server is running all of it (restarted after Grok's playtest), and I checked nearly everything in the real client
with the autopilot: quests, monsters, the new abilities, the art, the townsfolk, Toad Pond.

## What's new
- **Your art is in the game.** The rat, boar, mole, toad, wasp, snapper, thornsnap, shardling, wolf, grey alpha,
  ram, sproutling and Azhrakkar now show in the client instead of the borrowed Tibia sprites. NPCs and class outfits
  are next (they need a small server change).
- **Monsters fight differently:** field rats steal a few coins and run (kill the thief to get them back), hurt wolves
  howl for the pack, sproutlings heal each other (kill the healer first), ruin sentinels raise a shield (walk round
  them). Wolf packs now stick together and join each other's fights.
- **New kinds of quest:**
  - *The Builders' Stones* (Vesper): six carved stones in the wilds tell who built the tower. Title "Stonereader".
  - *The Old Sluice* (Fisher Corwin): three levers in Reedmarsh; the order is carved on a stone nearby.
  - *Flour for the Gate* (Miller Agna, level 12+): take the flour to the guards, or sell it to Fence Marrow on the
    road south of the Bandit Road. Different reward and title each way.
  - *The Stair Key*: the Axe-Lord's hall now opens only for climbers who helped kill the Gate Hound, helped kill the
    Stonehorn Ram, and finished Iron for the Stair. (The review suggested the Underkeep as one piece, but it's a secret,
    and secrets stay off the main path.)
- **Quests you can find:** the Journal and quest log say where every quest giver stands ("about 40 steps north of the
  temple"), and a "!" on the minimap marks anyone with work for you. The Quest Tracker bug Grok found is fixed (half
  the quests were missing from the game's quest list).
- **Hearthgate feels alive:** six townsfolk walk the Hearth Square, chat, and give tips when greeted; a town crier
  calls out the tower's news; the fountain sprays.
- **Toad Pond** is 12 tiles wider with a fifth pond and a new route (the Reed Beds).
- **A style choice on Floor 1:** from Mastery 5, `!style marksman` (or your class's other path) gives a free,
  swappable taste of that path until the permanent choice at Mastery 10.
- **Later-game abilities:** one signature ability per path (8) and per final style (16).
- **Reasons to log in:** a Tower Quiz every few hours (`!answer`), a bounty on the strongest climber online (level
  50+ only), leaderboards on the Monument statue, a familiarity bar in the Upgrade tab.
- **The Arrival Yard** now has the Spire's sealed door and a stone naming whoever opens each floor first.
- **Houses** cost more on higher floors (about 8 hours of that floor's hunting; Floor 1 unchanged).
- **Season reset** is now safe: `/season end` then `windows\Season-Reset.bat`. I rehearsed it on a copy of your real
  database, which caught a mistake that would have broken the old reset.
- **Rangers:** a new Ranger's quiver goes straight onto the shield hand, so the bow works from the first minute.

## Good to know
- The leaderboard on the Monument lists our test characters (Spell Mystic and friends) at the top. They live on the
  test account and will be removed before launch.
- The friend client package was rebuilt with the new art; Grok's next install picks it up.
- Not done yet: Bandit Road and Old Quarry rebuilds, Floor 2's own map, NPC and outfit art in the game, the escort
  quest (P9b), fires and lights in town (P3b).

## Playtest checklist (about 45 minutes)
1. **New character (10 min):** make one. Find the Spire's sealed door and read the stone next to it. Do Pell's quest:
   does it show in the Quest Tracker (bottom right)? If Ranger: does your bow fire right after the Registrar?
2. **Hearthgate (5 min):** walk the Hearth Square. Do the townsfolk feel alive or annoying? Say `hi` to one.
3. **Find a quest (5 min):** press J, Quests tab. Can you find a quest giver using only what it says? Look for "!" on
   the minimap.
4. **Monsters (10 min):** at Boar Meadow or Wolf Copse: did a rat steal from you? Did wolves come as a pack?
5. **Toad Pond (5 min):** walk the new east side. Big enough now?
6. **A new quest (10 min):** take Vesper's stones quest and read one stone, or try the sluice levers in Reedmarsh.
7. **Art (any time):** do the new monster sprites look right in the game?

## Open questions (my recommendation is assumed until you answer; QUESTIONS.md)
- **Q46** (style stance at Mastery 5): built as recommended. Does it feel right?
- **Q47** (rebuild the yard and Hearthgate before the alpha): started (the yard's Spire door, the townsfolk). More to
  come unless you say stop.
- **Q51** (the bot panel for new players): keep it, start it folded. Not done yet.
- Still open: Q45 (spear for Rangers), Q48 (Gate Hound respawns: built), shop prices.

## Art and map requests
- No requests for you tonight. The art estimate for the rest of the game is in `ART_REQUESTS.md` (about 10-12
  sessions of creature art for Floors 2-10, done a floor at a time).
