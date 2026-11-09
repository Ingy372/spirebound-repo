# Weekly report — week of 2026-11-08

## What's new
- **The plan is written.** `DESIGN.md` (the game bible from your brief; my gap-fills are marked "Claude's call, Jay can veto") and `ROADMAP.md` (10 phases of small, checkable tasks).
- **Switched to Canary.** The October TFS setup is archived in `legacy/` (nothing deleted). Canary v3.6.1 now boots with our own Spirebound datapack, with zero errors, and 13 automatic in-game checks run on every build.
- **Working already (server side):** four vocations (Vanguard, Ranger, Arcanist, Mystic + promotions), the Registrar NPC (pick vocation + Normal / Hardcore / Death Game, step down later), difficulty bonuses and Death Game rules (PvE death retires the character; player killers can't delete you), medium XP stages, party XP bonus with a 6-player cap, saved world floor records with the floor-unlock announcement, and 24 sword skills with combos.
- **One-click setup for your PC** in the `windows` folder.
- **Phase 1 progress:** 11 of 21 tasks done. Next up: map tools and the Floor 1 placeholder map, Floor 1 monsters, starter NPCs, the Gate Hound and Axe-Lord bosses, and the client UI (floor indicator, sword-skill bar, cursor colors).

## Playtest checklist (about 20 minutes)
This week is a quick install test, not a gameplay test yet. The map is still a borrowed stand-in, so don't judge looks.
1. In the repo folder, open `windows` and double-click **Install-Spirebound.bat**. Allow the Windows prompts. Wait for **Done!** (first run downloads about 1 GB).
2. Double-click **Start-Spirebound.bat**. A black server window should say "Spirebound server online!", then the client opens.
3. Log in: account `jay`, password `spirebound`. Pick **Climber**.
4. Walk around for a minute. Type `arc slash` (it should say you need a sword: proof the sword skills are loaded).
5. Close everything with **Stop-Spirebound.bat**.
6. Write what happened in `PLAYTEST.md`: "install OK" or copy any red error text. Screenshots welcome.

## Open questions (my recommendation is already in use; details in QUESTIONS.md)
- **Q1 GitHub access (please do this one):** I can't upload to GitHub from here. Add `Ingy372/spirebound-repo` to the GitHub repos Claude can access, or press "Push origin" in GitHub Desktop. Until then all work is safe on your PC only.
- **Q2:** delete the stray `phase-0-toolchain` branch from your Dojo-game repo.
- Q3 keep seasons (yes) · Q4 bot rules: only helpers built into our client · Q5 old design changes (FYI) · Q6 Twin Fang: 3 per season · Q7 newer Tibia systems off · Q8 Hardcore +25% XP/+15% loot, Death Game +50%/+30% · Q9 newbie protection to level 50, 70% level-range rule.

## Art and map requests
- **Art batch 1** (`ART_REQUESTS.md`): the 4 vocation outfits, 11 Floor 1 monsters, Gate Hound, Axe-Lord (two forms), 5 town NPCs. Batch 2: small UI pieces (cursors, floor badge, skill frames). Prompts are ready to paste into Grok.
- **Maps** (`MAP_REQUESTS.md`): Floor 1 and Underkeep Wing 1 are the first real maps needed. Script-made placeholders come next week, so nothing waits on you.
