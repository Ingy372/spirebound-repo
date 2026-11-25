# Spirebound playtest report, session 2 (2026-11-24)

Tester: grokbot account, two fresh characters. **Grok Second** (Arcanist, Normal), about 46 minutes, 22:28–23:14 ET. **Grok Third** (planned Vanguard), about 30 minutes, 23:15–23:45 ET, hard-blocked at the cheese gate. Screenshots are in `notes/` (`s2-*.webp` for Second, `s2v-*.webp` for Third). Running notes: `notes/2026-11-24-session2.md`.

Grok Fourth (planned Ranger) was never played: my computer reset around 23:36–23:46 ET and dropped Wine and Tailscale. Mystic was covered in session 1 on Grok Tester.

**Lag caveat.** Start load was 1.00 / 2.00 / 6.11 on 8 cores — much better than session 1. From 22:41–22:55 ET the game froze, disconnected (ERROR 10054 at 22:51), and left me unable to move after re-login. That stretch was an update job on your host, not a game bug, and I'm not counting it against the game. After it cleared, typing still scrambled and the client still froze at times. That leftover lag is most likely my side: the client was around 170% CPU under Wine with software rendering, box load around 4 on 8 cores, ping 40 ms. Those items are marked **(lag?)**.

## Fix check (the 7 questions)

| # | Check | Arcanist (Grok Second) | Vanguard (Grok Third) | Verdict |
|---|-------|------------------------|-----------------------|---------|
| 1 | Pell's quest in the Quest Tracker after you accept it | No. Pell said "It's in your quest log," but Quest Log (J) was empty and the Tracker only showed "Add Tracked Quest," both after accept and after turn-in. `s2-2231-questlog-empty.webp` | Yes. Journal → Quests showed "In progress: Floor 1 - First Blood (from Guide Pell): Defeat the rats in the pen along the stone path: 0 of 3." The Tracker added it on its own, then flipped to "Completed." `s2v-2316-quest-log-and-tracker.webp` | Partly — works on some characters, not others |
| 2 | Registrar: class and mode descriptions; clean speech bubbles; Server Log confirmation | Pitches are clear and funny enough to choose. Arcanist: "The hardest hitters and the most fragile: kill things before they reach you. Your first spells: ember strike, and mending spark to heal from level 4." Mode list is clear; I didn't read the death-game details. Bubbles still show braces: `{vanguard}, {ranger}, {arcanist}` and `{yes? or {no??}`. Chat log is clean. Confirmation works: NPC "It is written: Arcanist, Normal." Server Log "You are now a Arcanist, living by the Normal rules." (typo: "a Arcanist"). Saying "no" to a mode sends you back to class choice. `s2-2251-registrar-bubble-braces.webp`, `s2-2254-arcanist-pitch-bubble.webp`, `s2-2257-server-log-proving.webp` | Did not reach the Registrar | Partly — descriptions and confirmation are fixed; braces and the typo are not; "no" to mode is awkward |
| 3 | The Proving: first two class spells on the action bar; skill bar matches the class weapon | Landed in the Proving. Action bar showed Spark Edge / Flame Script / Starfall Rite, plus leftover default runes — not ember strike / mending spark, which is what the Server Log taught: "Your attack spell: ember strike… (it is on your action bar too)." Spark Edge does cast. Skills showed Magic Level 0 (still 0 after many casts), Fist / Club / Sword / Axe. No distance or wand line. Before any class is picked, the hotbar already shows club skills (Bell Ringer / Crushing Arc / Tremor Blow). `s2-2300-proving-rats-hotbar.webp`, `s2-2312-skills-window.webp` | Did not reach the Proving. Pre-vocation hotbar also showed the club skills. | Not fixed — two unexplained spell sets; skills don't match a wand class |
| 4 | Cast the attack spell with nothing targeted | Clear message: "You need a target: click a monster first (or pick it in the Battle List), then use ember strike." Later the same line said "spark edge" instead. `s2-2257-no-target-message.webp` | Untested | Fixed |
| 5 | Bramblejaw (step on the glowing stone): difficulty, red-smoke stomp warning, duration | Untested. Warden Ketta said "step on the glowing stone to face Bramblejaw alone." The glowing stone I stepped on was an exit portal to Hearthgate. The fight stone and the exit stone look the same, or the fight never triggered. | Untested | Untested |
| 6 | `!hunt` directions to the recommended ground; time to first class kill | Worked, including from inside town (a Safe-zone temple). "Sproutling Glade, levels 5-10: leave Hearthgate by the south gate, then about 30 steps west to its north entrance." Those directions got me there. I got kills. First class kill was a Hopper Toad at 23:08 ET; I didn't time it from registration. Name is now "Sproutling Glade" (session 1 called it "Sprouting Glade"). `s2-2301-hunt-reply.webp`, `s2-2308-first-kill-hotbar.webp` | Untested | Fixed — directions work; time to first kill was not timed |
| 7 | First walk out of the Guarded area: does the [Open PvP] explanation make sense? | Untested. I never left a Guarded or Safe zone, so I never saw that message. | Untested | Untested |

## 1) What I did
- **Grok Second.** Walked the Arrival Yard, did Pell's First Blood quest (Pen Rats, cheese, report: 100 gold and 300 XP), and reached the Registrar after a host-side freeze and disconnect around 22:41–22:55 ET. Looked at the Mystic pitch, picked **Arcanist**, took Normal mode, and landed in the Proving. Two Pen Rats were already biting me there. I confirmed the no-target cast message, then stepped on a glowing stone and was dumped in Hearthgate — no Bramblejaw. `!hunt` sent me to Sproutling Glade. I got Hopper Toad and Sproutling kills, died once to Hopper Toads (paralyze, low HP), respawned at the temple, and confirmed mending spark heals. Ended at level 5 with 1,806 XP.
- **Grok Third.** Fresh login, Pell's quest appeared in the Journal and Tracker this time. Found the rat pen through a fence gap, killed three rats (level 1 to 4), reported to Pell, and was stopped at the cheese gate. The log later said cheese was looted, but the backpack was empty and no corpse was left to open. Stuck there more than 10 minutes, then gave up on this character.
- **Grok Fourth** was not played.

## 2) What was fun
- The class pitches are in a much better place than session 1. They tell you playstyle, fragility, and the first spells, and they're funny. I could actually choose.
- The Registrar hall looks great. Warden Ketta in the Proving is a good idea: she explains the rats, Bramblejaw, healing, and a skip.
- Pell's flow is still strong, and he now warns you about the cheese before the gate: "open a body to take the cheese it carries: the gate after the pen won't open without one."
- The no-target message is clear and useful.
- `!hunt` earned its keep this time. The directions were true, it worked in town, and I got real class kills in the Glade — something I never managed in session 1.
- Small NPC flavor lands: "Coins are safer here than in your pockets." "Wounds? Come, sit."
- mending spark works.

## 3) What was confusing or unclear
- **Two spell sets, no explanation.** The game teaches ember strike and mending spark. The action bar shows Spark Edge, Flame Script and Starfall Rite. Spark Edge does damage. I don't know whether these are the same spells under different names, or a second kit I wasn't told about.
- **The skill panel doesn't match an Arcanist.** Fist, Club, Sword, Axe. No wand or distance line. Magic Level stayed at 0 after a lot of casts, so I have no idea if I'm getting better at my class.
- **The Bramblejaw stone and the exit stone are indistinguishable.** Ketta tells you to step on the glowing stone to fight. I did, and I was in Hearthgate. I missed the intended first class fight entirely.
- **The cheese gate argues with itself.** It says "Open a rat's body (right-click it) and take the cheese it carried before you go on." Auto-loot then announces the cheese and removes the body. On Grok Second I got through. On Grok Third the log said "Loot of a pen rat: cheese, 3 gold coins," the backpack was empty, and the gate still refused me.
- **The rat pen entrance is still hard to find.** The gap is easy to miss. I got in through a dirt stub south of the pen. The east side of the pen is a blocked gate: "Beat a rat in the pen first…"
- **The colonnade of identical pillars** feels like you aren't moving.
- **Saying "no" to a game mode** throws you all the way back to class choice, so you have to re-pick the class you already committed to.
- **Clicking a monster on the map walks to it instead of attacking.** The Battle List is reliable; clicking a Battle List entry can also toggle the target off.
- **Clicking the wand icon** enters "use with" mode. The game then says "You can only use it on creatures."
- **Esc turns chat off**, so a typed spell becomes movement. Classic OTClient trap, and it still bites.
- **A level 3 tip points you to Toad Pond** (east gate, 40 steps east) before you've even picked a vocation.
- **The character list is stale.** After Grok Second was already level 4 in-game, a disconnect showed Level 1, vocation None. After the Arcanist run it still showed Level 1 / None for a level 5 Arcanist. Grok Tester (session 1) did show Level 5 Mystic, so this isn't consistent either.

## 4) What was boring or slow
- **Three rats took a fresh character from level 1 to 4** (135 XP a rat, 2250% XP boost still on). Levels feel meaningless. A level 3 hunting tip fires before you've left the tutorial.
- **The cheese-gate stall.** Even before the hard block, Grok Third lost several minutes walking back to the pen after the corpses had decayed.
- **The identical-pillar colonnade** is still a slog, same complaint as session 1.
- I got into class combat faster than session 1, which is good — but only because I accidentally skipped Bramblejaw. If that fight is the intended "first fight as your class," I never got it.

## 5) Bugs or things that looked broken

| # | What | Where | Screenshot |
|---|------|-------|-----------|
| 1 | **Top bug.** Cheese gate hard-blocks the character. Log: "Loot of a pen rat: cheese, 3 gold coins." No corpse left to open. Backpack empty. Gate still: "Open a rat's body (right-click it) and take the cheese it carried before you go on." Auto-loot and the gate text contradict each other. Grok Second (and Grok Tester in session 1) passed the same gate, so this is inconsistent. | Cheese gate east of Pell, Grok Third, 23:33–23:45 ET | `s2v-2326-cheese-gate-msg.webp` (gate); `s2v-2321-rats-levelup4.webp` (earlier "Loot of a pen rat: cheese, 2 gold coins") |
| 2 | Quest Tracker / Quest Log inconsistent. Empty for Grok Second after accept and after turn-in. Worked and auto-tracked for Grok Third. | Arrival Yard, both characters | `s2-2231-questlog-empty.webp`, `s2v-2316-quest-log-and-tracker.webp` |
| 3 | Speech bubbles still render keyword braces (`{vanguard}`, `{yes? or {no??}`). Chat log is clean. | Registrar Maelis | `s2-2251-registrar-bubble-braces.webp`, `s2-2254-arcanist-pitch-bubble.webp` |
| 4 | Action bar does not show the taught class spells. Bar: Spark Edge / Flame Script / Starfall Rite. Taught: ember strike / mending spark. Server Log claims ember strike "is on your action bar too." Pre-vocation bar shows club skills (Bell Ringer / Crushing Arc / Tremor Blow). | The Proving, and the hotbar before any class is picked | `s2-2300-proving-rats-hotbar.webp`, `s2-2312-skills-window.webp` |
| 5 | Skills window has no wand or distance line. Magic Level stayed 0 after many casts. | Hearthgate, Grok Second at level 5 | `s2-2312-skills-window.webp` |
| 6 | Confirmation typo: "You are now a Arcanist, living by the Normal rules." | Server Log, on entering the Proving | `s2-2257-server-log-proving.webp` |
| 7 | Stepping on the glowing stone in the Proving exits to Hearthgate instead of starting Bramblejaw. The two stones are not visually distinct. | The Proving | `s2-2300-proving-rats-hotbar.webp` |
| 8 | Character list shows Level 1 / vocation None for a character who is already leveled (and, later, already an Arcanist). | Character select after the 22:42 ET disconnect, and again after logout | `s2-2242-disconnected-charselect.webp` |
| 9 | "There is not enough room" appears when you bump a wall or the gate. Misleading — it isn't a backpack problem. | Cheese gate, colonnade | (none) |
| 10 | Two Pen Rats attack on arrival in the Proving, unannounced (165→138 HP over about 90 seconds). | The Proving, Grok Second | `s2-2257-no-target-message.webp`, `s2-2300-proving-rats-hotbar.webp` |
| 11 | Clicking the wand icon enters use-with mode ("You can only use it on creatures") instead of casting. | Sproutling Glade | `s2-2308-first-kill-hotbar.webp` |
| 12 | Typing came out scrambled ("emelmbre rs tsrtrisk") and the client froze or dropped movement at times **(lag? — likely my Wine client)** | Registrar / Proving; also the 22:41–22:43 ET freeze, which was your host | `s2-2242-disconnected-charselect.webp`, `s2-2243-stuck-no-move.webp` |

## 6) How it compares with other Open Tibia servers
This part is from general OT knowledge. I haven't played other OT servers myself.
- **Ahead of typical OTs:** the onboarding path is still stronger than the usual "drop them in Rookgaard" approach. This session added better class pitches, a working mode confirmation, a useful no-target message, and `!hunt` directions that actually lead to the right entrance and work from town. That's real progress from session 1.
- **Behind well-polished OTs:** a tutorial gate that can hard-lock a brand-new character is worse than a plain, slightly confusing Rookgaard quest. If auto-loot takes the cheese and the gate still wants a corpse click, some fraction of new players will quit right there. The client still looks like stock OTClient Redemption (vBot, Store, default layout). The action bar and skill panel still don't match the class you just picked, which is the same kind of unfinished vocation path I flagged for Mystic in session 1.
- **XP rate:** 135 XP per rat and level 1 to 4 in three kills, with a 2250% boost showing in the skills window, is far above what a new player expects on a serious OT. Fine as a test setting; it makes early levels feel fake if it ships.

## 7) Five changes that would most make me keep playing
1. **Fix the cheese gate so it can't hard-lock anyone.** If cheese is auto-looted, put it in the backpack and open the gate. If you want the player to open the body, don't auto-loot the body away. The gate text and the loot system have to tell the same story.
2. **One spell set, on the bar, under the names you teach.** Bind ember strike and mending spark (or rename the bar to those), and drop the leftover club skills and default runes. Make the skill panel show wand or magic, and make Magic Level actually move.
3. **Make the Bramblejaw stone obviously different from the exit portal.** I skipped the intended first class fight by stepping on the wrong glow. A label, a different color, or a confirmation would do it.
4. **Make quest tracking reliable.** When Pell says "It's in your quest log," it should be there — every character, every time — and already on the Tracker.
5. **Clean up the small cuts that make the game feel unfinished:** braces in speech bubbles, "a Arcanist," "There is not enough room" on walls, a character list that doesn't save level or vocation, and Esc silently turning chat off so spells become movement.

## Not tested yet
- Bramblejaw: difficulty, the red-smoke stomp warning, and how long the fight takes.
- The [Open PvP] explanation the first time you leave the Guarded area.
- Vanguard past the cheese gate: Registrar, Proving, spells, hunt, first class fight.
- Ranger on Grok Fourth (computer reset; needs the Tailscale device re-approved before I can log in again).
- Death-game and hardcore mode details.
- A timed "first kill as your class" from the moment you register.
- Whether Magic Level ever increases on a longer session.
- A retest of the cheese-gate loot path on a fresh character after a fix.

Rerun needed: Grok Fourth as Ranger, and a Vanguard (or a re-roll of Grok Third) once the cheese gate is passable, so checks 3–7 can be finished on those classes. Retest leftover freezes and scrambled typing on a normal PC, or after a client render path that isn't software Wine.
