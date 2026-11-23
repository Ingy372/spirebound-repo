# Update, 2026-11-23: gear progression

(The 2026-11-13 report is in git history. Since then: five calmer hunting grounds, spawn habits, 45 new spells, PvP spell rules and the client spellbook. They are logged in PROGRESS.md.)

## What's new
- **Your weapon, your path.** At level 10, Captain Dorrow (Hearthgate's north gate) gives you a weapon from the barracks, and you pick the kind: sword, axe or mace; bow or crossbow; wand; rod.
- **Tiers.** Every monster on Floor 1's grounds can drop **Hearth Shards**. Three shards at Weaponsmith Garrick raise your weapon or armour one tier, up to 5. Rough shards drop everywhere, cut shards on the harder grounds, and flawless shards from elites and the Old Watchtower. Upgrades never fail. Shards sell well on the market, so you can save them or sell them.
- **Familiarity.** The more you fight with a weapon, the better you know it (0 to 10, up to +15% damage). A new, stronger weapon starts at 0. On Floor 2 a new weapon passes your maxed Floor 1 weapon after about 2 hours, so sticking with old faithful works for a while.
- **Style (permanent).** Fighting also fills your class Mastery. At Mastery 10 (around level 37) you get your first style ability and choose a path: Marksman or Trapper, Bulwark or Reaver, Emberwright or Stormbinder, Lifebinder or Wildcaller. Later you choose a final style. The only way to undo a choice is a **Mastery Respec Scroll from the shop**, as you asked.
- **The Floor 1 checklist.** Your weapon from Dorrow → *Tempered in the Field* (Dorrow, Wolf Copse) → *Iron for the Stair* 1 and 2 (Hunter Brannoch, your armour) → the Gate Hound (3 cut shards) → the Axe-Lord (your weapon **awakens**: new name, its full power, for everyone who helped).
- **The Upgrade tab.** Press J. The first tab always starts with one sentence: your next step and where to go. `!upgrade` opens it, and you get the same line at every login.
- **Four hidden mini-bosses.** Each one gives a permanent trophy the first time you help kill it. The Upgrade tab never mentions them. Their spots are secrets you can sell to Vesper.
- **Shop starter gear.** A starter set for levels 1-15 that can't be upgraded. Dorrow's weapon at tier 2 already beats it. (The shop stays closed until launch.)
- **"Venomous slime" fixed.** It was the poisonous slime the Alchemist wants, dropped by Hopper Toads. Every material's look text now names the monster and the ground, and crafters tell you where to find anything you're missing.

## Before you play (one step)
Restart the server so it runs the new code: double-click `windows\Stop-Spirebound.bat`, then `windows\Start-Spirebound.bat`.

## Playtest checklist (about 45 minutes)
Use your level 12 Ranger.
1. **Dorrow (5 min):** go to Hearthgate's north gate, say `hi`, then `weapon`, then `bow` or `crossbow`. Do you get the weapon? Look at it: does it show tier and familiarity?
2. **The Upgrade tab (5 min):** press J. Is the top line clear about what to do next and where? Is anything on the tab confusing?
3. **Hunt (20 min):** hunt anywhere around your level. Do you see "familiarity" go up? Do you find a rough Hearth Shard? (About 1 kill in 180 drops one, so you may not find one in 20 minutes. Tell me if that feels too rare.)
4. **Tempered in the Field (10 min):** ask Dorrow for a `quest`, hunt the wolves in Wolf Copse, then `report`. Does the weapon go up a tier?
5. **Weaponsmith (5 min):** if you have 3 rough shards, say `hi`, `upgrade`, `yes` to Weaponsmith Garrick. If you don't have them yet, say `upgrade` anyway: does he tell you clearly what you need and where to get it?

## Open questions (my recommendation is assumed until you answer; see QUESTIONS.md)
- Shop prices for the starter set (300 coins) and the respec scroll (500 coins) are placeholders until you set prices (roadmap 7.3).
- Rangers can't pick a spear as their barracks weapon, because thrown spears are used up. Do you want a spear that isn't thrown? My recommendation: no, keep bow and crossbow.

## Art and map requests
- New in `ART_REQUESTS.md` Batch 6: three mini-boss sprites (I make these with the Blender pipeline and send them for your OK), plus Grok icons for the three Hearth Shards and the Mastery Respec Scroll.
- No new map requests: the mini-bosses use existing secret spots.
