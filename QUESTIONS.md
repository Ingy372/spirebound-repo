# Questions for Jay

How this works: each question has Claude's recommendation. Claude assumes the recommendation and keeps working. To answer, write under "Jay's answer" (a word or two is fine). Answered questions get moved to the bottom.

---

## Open

*Q13–Q25 come from the full review (`REVIEW.md` section B). Section numbers point into that file.*

### Q33. Do the walled hunting grounds look the way you want? (2026-11-13)
Every ground is now a walled place with ring trails (see the playtest list in WEEKLY_REPORT.md). Up close they read like a wood or a rocky field; from far away they look a little like a hedge maze, because the loops are regular.
- Recommendation: keep the skeleton (it is what makes botting and sharing work) and let the end-of-project Cowork polish break up the outlines by hand.
- Jay's answer:

### Q13. Calendar gate on floor bosses? [1.4]
Nothing stops a big guild finishing all 10 floors in the first week or two, and then the season's story is over.
- **Recommendation:** yes. Each floor boss room unseals on a date (Floor 2 no earlier than day 3, then one floor every 5–7 days). Every unlock becomes an event. Also drop the "25 floors per season" promise; say "10 floors, more if the season goes well".
- *Built 2026-11-13 (R9) as recommended, with 6 days between floors. It only runs after you start a season with `/calendar start`, so test boss runs on your PC are never blocked.*
- Jay's answer:

### Q14. Death Game: what does stepping down cost, and what happens on a lag/crash death? [2.7, 3.4]
Today a Death Game character earns +50% XP and can step down to Normal any time, keeping every level, so it's the *safest* way to level.
- **Recommendation:** stepping down removes the extra XP the bonus gave (you keep what a Normal character would have earned). Deaths caused by a server crash or server lag are restored by a GM; your own internet dropping is not ("the tower is cruel"), and that rule is written on the website.
- Jay's answer:

### Q15. Pay-to-win line: can shop items be traded for gold? [6.3]
If shop items can be sold to players for gold, then money → gold → gear is two steps away, so "never pay-to-win" isn't quite true.
- **Recommendation:** (b) shop items stay tradeable (lets non-payers earn cosmetics), but each floor's best gear is bound to the character that earned it. Shop items can never be bet (already true).
- Jay's answer:

### Q16. Bot rules in detail [3.8]
- **Recommendation:** auto sword-skill rotation is **not** allowed (remove the attack helper from the client; combos should be skill). Auto-target + auto-heal while standing still counts as botting after 10 minutes without manual movement. A character following a botting one gets the same 45% XP.
- Jay's answer:

### Q17. Fortune Hall: keep, cap or drop? [6.5]
Gold has a real-money price once shop items can be sold for gold, which makes a gold casino risky with payment companies.
- **Recommendation:** keep it, but with a low cap (10,000 gold per bet), hosts set their own limit, and the 5% truly destroyed. Revisit with a professional before the shop takes money.
- Jay's answer:

### Q18. Twin Fang: real power or style? [2.5]
As built, it's +50% damage on every melee hit for three players: the strongest build in the game.
- **Recommendation:** style with a small edge: off-hand hit at 20–25%, one-handed swords only, trial solo. Keep it rare and flashy.
- Jay's answer:

### Q19. Boss warning time [3.9]
Big hits land 0.6 s after the warning; players far from the server have about a third of a second.
- **Recommendation:** 1.0 s for hits that can kill, 0.6 s for the rest. Decide after one boss fight.
- *Built 2026-11-13 (R9) as recommended: marked hits of 250 or more get 1.0 s.*
- Jay's answer:

### Q20. Houses: many more, or rentable rooms? [3.7]
There are 63 houses on the whole server, and most house features need one.
- **Recommendation:** both: about 3× more houses on the real maps, plus cheap rentable rooms in each town's inn that give access to the portal, workshop and Fortune Hall table.
- Jay's answer:

### Q21. Art: make everything with Grok, or start from an open sprite pack? [8.1]
A public launch needs every tile, wall, tree, item and effect replaced, not just the ~150 pieces in ART_REQUESTS.md: thousands of sprites.
- **Recommendation:** start from an open-licence Tibia-style sprite pack for tiles and items; make monsters, bosses, outfits and the UI yourself with Grok. I'll first prove the pipeline with one sprite (R22) so we know the real cost.
- Jay's answer:

### Q22. Friends test: Floors 1–2 only? [9.2 of review]
- **Recommendation:** yes. Seal Floors 3–10, switch off arena, siege, shop and Season Path for the test. Wipe after.
- *Built 2026-11-13 (R13) as recommended. You can switch it in game: `/scope test` or `/scope launch`.*
- Jay's answer:

### Q23. Who moderates at launch, in which languages? [§4]
- **Recommendation:** you plus 2 trusted friends as GMs (ideally one Portuguese and one Spanish speaker), with the report command and GM log from R14.
- Jay's answer:

### Q24. Azhrakkar's look [8.4]
He's too close to the boss that inspired him (giant blue horned fiend with a huge sword).
- **Recommendation:** change colour (deep red/black), no goat head, a different weapon (a chained halberd). Keep the size and the sweep attack.
- Jay's answer:

### Q25. Money: business, policies and tax before the shop opens? [6.5]
- **Recommendation:** launch the first season **without a shop**. Open it only once you've registered what you need to, have refund/privacy policies, and have checked tax with a professional.
- Jay's answer:

### Q26. Spire Manor: price, and can the owner sell it on? (2026-11-11)
You said it should be "pay to obtain only". I built it as a shop-only house: !buyhouse refuses it, and the shop hands it over. It is cosmetic only, with no stat bonuses, and there is one per server. It is free of rent, and it is released when its owner leaves it or the season ends.
- **Recommendation:** a placeholder price of 5,000 Spire Coins, set properly with the other shop prices (7.3). The owner **can't** sell or trade it to another player (that keeps "pay to obtain only" true). Add a second manor on a later floor if there is demand.
- Jay's answer:

### Q27. Upgrade/forge system (from the second research pass)
Almost every popular server has a way to upgrade gear (item +1 to +10, fusion, Canary's Forge). In Q7 I recommended keeping Canary's Forge off at launch.
- **Recommendation:** keep it off for Floors 1-2, and switch the Forge on from Floor 3 as a loot and gold sink that players trade for. No forge materials in the shop, ever.
- Jay's answer:

### Q28. "A banker that can store gold between all accounts": did I read that right? (2026-11-12)
I built an **account vault**: gold that every character on the same account can reach at any banker ("vault deposit 500", "vault withdraw 500"). Each character still has its own bank balance, and gold can still be sent to another player's character with "transfer", as in Tibia.
- **Recommendation:** keep it like this. Sharing gold between different people's accounts is already covered by "transfer" and the market. If you meant something else, describe it in a sentence.
- Jay's answer:

### Q29. Is the junk buyer too generous? (2026-11-12)
Trader Osric buys nearly every monster drop at close to the standard Tibia NPC prices. Materials sell to him for 8–25 gold each, still well under what they're worth to crafters, so trading between players stays worthwhile.
- **Recommendation:** keep these prices for the friends test, then adjust from what testers earn per hour (ECONOMY.md shows the model).
- Jay's answer:

### Q1. GitHub: Claude can't push to the repo from this session (needs you, 2 minutes)
Claude can commit on your PC's copy but GitHub refuses the upload: the repo isn't in this session's allowed GitHub repos, and your PC's copy has no saved GitHub login for Claude to use. Work is safe on your PC, but not backed up to GitHub until this is fixed.
- **Recommendation:** in the Claude app, add `Ingy372/spirebound-repo` to the GitHub repositories Claude can access. Until then, push from your PC whenever you like (GitHub Desktop: open the repo → "Push origin").
- Jay's answer:

### Q2. A stray copy of old Spirebound work is in your Dojo-game repo
Your PC's Spirebound folder was pointed at your **Dojo-game** GitHub repo, so an older session uploaded a branch called `phase-0-toolchain` there. Claude fixed the folder so it now points at `spirebound-repo`. Nothing in Dojo-game was changed besides that extra branch.
- **Recommendation:** delete the `phase-0-toolchain` branch from the Dojo-game repo on GitHub (Branches page → trash icon). Everything in it is also in spirebound-repo.
- Jay's answer:

### Q11. Should the cavebot XP cut linger 10 minutes after switching it off?
Without it, someone can bot the boring parts, switch it off just before a boss or rare monster for full XP, then switch it back on.
- **Recommendation:** keep the 10 minutes. If you'd rather have full XP the moment it's off, write "no linger".
- Jay's answer:

### Q12. Features from the top-server research (DESIGN.md §15)
Top servers all have: autoloot, scheduled events, weekend bonuses, guild castle wars, offline training, livestream, tasks/boss timers, and an Android client. I added all of these to the plan, plus a free "Season Path" (play goals → cosmetics) and catch-up rules for new players (no death XP loss on Normal below level 50).
- **Recommendation:** keep the whole list. Two things to look at: (a) **hunting tasks** come back (you turned off Canary's version; ours is simpler, from NPCs, paying gold and cosmetic points); (b) **no character bazaar** (selling characters for shop coins), because it feeds real-money trading.
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

### Q30. Slow the early levels so Floor 1 lasts? (2026-11-12, from FLOOR1_WILDS_PLAN.md)
With experience at 25 times normal, a new character passes level 35 (the end of Floor 1) after about 1 hour 15 minutes. Twelve hunting grounds go by in minutes each.
- **Recommendation:** levels 1 to 8 at 10 times, 9 to 20 at 4 times, 21 to 50 at 3 times. Floor 1 then takes about 11 to 15 hours by hand, about a day and a half on the cavebot. Later stages get the same check when Floor 2 is planned.
- Jay's answer (2026-11-12): "yes slow it down to what you recommend. it should last about 11-15 hours. this will give a great sense of FOMO on launch day and on season resets."

### Q31. Crowd system: more monsters when a hunting ground is over-full? (2026-11-12)
Each ground counts the players inside it. Past 5 players, extra monster groups switch on at set spots; past 8, all of them; they switch off five minutes after the crowd leaves. Starter grounds can reach four times their normal size (for launch day); harder grounds only one and a half times, so good spots stay worth competing for.
- **Recommendation:** build it as described in FLOOR1_WILDS_PLAN.md Part 7.
- Jay's answer (2026-11-12): "yes"

### Q32. No cavebot inside the new caves? (2026-11-12)
Six hunting grounds get a cave underneath with bigger groups, meant for a party of two to four at the keyboard. The loops above are for solo players and bots.
- **Recommendation:** refuse the cavebot in caves, the same way boss rooms do.
- Jay's answer (2026-11-12): "yes go with what you recommend."

### Q10. Cavebot numbers
- Jay's answer (2026-11-08): **XP 45% while botting** ("you want the players to have a reason to bot occasionally"); **no icon or indicator**; blocked from secrets/chests/boss rooms: yes; auto-targeting alone free: yes; third-party bots banned: yes. Loot stays 50% (my call). Linger: see Q11.

### Spells and ammo (Jay, 2026-11-08)
- Spells unlock automatically at their level, no gold. Players can't conjure ammo; ammo and healing supplies are the gold burn. DESIGN.md §5.3b updated (3 Ranger conjure spells replaced).

### Q3. Seasons or 100 permanent floors? (FYI, no action needed)
- **Recommendation: keep seasons** (about 5 months each, 10 floors at launch growing to ~25). Seasonal resets give every season a fresh "launch week", and resets close the level gap that lets top guilds farm new players. 100 permanent floors would need far more content and the world-first race would happen only once. Full reasoning in DESIGN.md §4.
- Jay's answer (2026-11-08): **"Seasons are a go then."**

### Q4. Cyntara's bot rules are stricter on paper than you may remember (FYI)
Cyntara's written rules ban macros and outside programs. In practice its own client has helpers built in (walker, looter, experimental vBot support), and the game quietly withholds some rewards from players who used the auto-walker recently.
- **Recommendation:** allow only helpers built into our client: auto-heal, auto-eat, ring/amulet refill, loot helper. Ban cavebots/walkers, auto-targeting, auto skill rotations, auto-fishing, and all outside programs. Details in DESIGN.md §12.
- Jay's answer (2026-11-08): **cavebot and auto-targeting will be built into the client; with the cavebot on, XP is cut a lot so manual play is much better; botters risk being PKed.** DESIGN.md §12 rewritten to match (see Q10 for my numbers).
