# Questions for Jay

How this works: each question has Claude's recommendation. Claude assumes the recommendation and keeps working. To answer, write under "Jay's answer" (a word or two is fine). Answered questions get moved to the bottom.

---

## Open

### Q1. GitHub: Claude can't push to the repo from this session (needs you, 2 minutes)
Claude can commit on your PC's copy but GitHub refuses the upload: the repo isn't in this session's allowed GitHub repos, and your PC's copy has no saved GitHub login for Claude to use. Work is safe on your PC, but not backed up to GitHub until this is fixed.
- **Recommendation:** in the Claude app, add `Ingy372/spirebound-repo` to the GitHub repositories Claude can access. Until then, push from your PC whenever you like (GitHub Desktop: open the repo → "Push origin").
- Jay's answer:

### Q2. A stray copy of old Spirebound work is in your Dojo-game repo
Your PC's Spirebound folder was pointed at your **Dojo-game** GitHub repo, so an older session uploaded a branch called `phase-0-toolchain` there. Claude fixed the folder so it now points at `spirebound-repo`. Nothing in Dojo-game was changed besides that extra branch.
- **Recommendation:** delete the `phase-0-toolchain` branch from the Dojo-game repo on GitHub (Branches page → trash icon). Everything in it is also in spirebound-repo.
- Jay's answer:

### Q3. Seasons or 100 permanent floors? (FYI, no action needed)
- **Recommendation: keep seasons** (about 5 months each, 10 floors at launch growing to ~25). Seasonal resets give every season a fresh "launch week", and resets close the level gap that lets top guilds farm new players. 100 permanent floors would need far more content and the world-first race would happen only once. Full reasoning in DESIGN.md §4.
- Jay's answer:

### Q4. Cyntara's bot rules are stricter on paper than you may remember (FYI)
Cyntara's written rules ban macros and outside programs. In practice its own client has helpers built in (walker, looter, experimental vBot support), and the game quietly withholds some rewards from players who used the auto-walker recently.
- **Recommendation:** allow only helpers built into our client: auto-heal, auto-eat, ring/amulet refill, loot helper. Ban cavebots/walkers, auto-targeting, auto skill rotations, auto-fishing, and all outside programs. Details in DESIGN.md §12.
- Jay's answer:

### Q5. Your new brief changes several decisions from the October design pack (FYI)
The new brief wins, and DESIGN.md follows it: Canary instead of TFS, 4 vocations instead of 5 paths, 10 launch floors instead of 5, Tibia gold instead of "col", standard Tibia death penalty on Normal, a donation shop that includes convenience items, dual wielding, fishing, difficulty modes. The old TFS server setup moves to a `legacy/` folder (task 1.2); the reusable tools and many design details (Floor 1 layout, bosses, PvP zones, Underkeep) are kept.
- **Recommendation:** nothing to do. Tell Claude if you want anything from the old pack back.
- Jay's answer:

### Q6. How rare is Twin Fang (dual wielding)?
- **Recommendation:** only the first **3** Vanguards per season who finish the hidden Floor 8 trial. Tell Claude a different number (1 is the most "SAO", but very harsh).
- Jay's answer:

### Q7. Newer Tibia systems in Canary: on or off?
Canary includes Prey, Imbuements, the Forge, the Wheel of Destiny, Charms and the official coin store.
- **Recommendation:** all **off** at launch to keep Spirebound focused and avoid pay-to-win paths. Weapon proficiency stays on (sword skills use it). Any can be switched on later.
- Jay's answer:

### Q8. Difficulty bonuses
- **Recommendation:** Hardcore +25% XP / +15% loot; Death Game +50% XP / +30% loot.
- Jay's answer:

### Q9. PvP protection numbers
- **Recommendation:** newbie protection below level 50; can't start a fight with anyone below 70% of your level (outside Contested zones and boss rooms); "outnumbered" damage reduction when 3+ players attack you. Details in DESIGN.md §6.4.
- Jay's answer:

---

## Answered
(none yet)
