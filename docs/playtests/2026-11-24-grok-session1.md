# Spirebound playtest report, session 1 (2026-11-24)

Tester: Grok Tester (account grokbot), a brand-new player. About 63 minutes of play, 19:28–20:31 ET.
Screenshots are in `notes/`. Full running notes: `notes/2026-11-24-session.md`.

**Big caveat first.** My computer was badly overloaded for most of the session: load average 13–14 on 8 cores, mostly from an unrelated process. The client, running under Wine, redrew slowly and dropped held arrow keys. I've marked every item that the lag could explain as **(lag?)**, and I'm not counting slowness itself against the game. A rerun on a normal PC is needed for those items. Everything not marked happened regardless of speed.

## 1) What I did
- Logged in and walked the Arrival Yard stone path. Did Guide Pell's quest: kill Pen Rats, report back, get 100 gold.
- Got stopped by the first energy gate (it needs cheese). Went back to the pen, looted cheese and passed the gates along the path.
- At Registrar Maelis I looked at the vanguard pitch, said no, then picked **Mystic**. Shift-click Look confirms "You are a mystic." Maelis then asked for a game mode (normal, hardcore or death game). I answered "normal" but never got a confirmation.
- Opened the Journal ("How do I" page). Left town, used `!hunt`, and tried to reach the Sprouting Glade (lv 5–10). I couldn't find the way in, ended up in a meadow west of town and took some hits from a Sprouting, a Hopper Toad and a Bristle Boar. My dewfall heal worked, but I never landed a confirmed Mystic kill.
- Ended at level 5 with 1,110 XP. No deaths, no Floor 1 quest. (Most of the XP came from the rat pen with the 2250% boost.)

## 2) What was fun
- Guide Pell's opening is good. "Walk the stone path east and each stop teaches one thing" sets clear expectations, and the blue keywords (heal, skills, spells, gold, death, where to hunt) work.
- The "stop N" tutorial path with Server Log hints is a good idea. "Press J for your Journal: its 'How do I' page answers most questions" is exactly the right tip.
- `!hunt` is a great feature. It gives the area, level range, direction, the next zone at level 7, and a live "quiet (0 players)" status. I'd keep it and make it more prominent.
- Committing to a game mode ("you may always step down later, but never up") has good flavor.
- Hitting level 5 in about 12 minutes feels rewarding, although see section 4.

## 3) What was confusing or unclear
- **The login field says "email"** but wants the account name.
- **Rat pen entrance:** it's hard to see the gap in the fence. I tried attacking rats over the wall first.
- **Cheese gate:** nothing tells you before the gate that you'll need cheese, so you walk back to the pen. Say it in Pell's quest text or on a sign at the pen.
- **Looting:** it's not obvious that you right-click the corpse, choose Open, then drag the item into your backpack. The "Dead rat" container window just appears.
- **The gate corridor all looks the same.** Only Shift-click Look on a signpost ("Stop 2") told me I was making progress. Show "Stop 2 of N" on screen or in the Server Log.
- **The vocation pitches are too thin.** One line each plus yes/no: "Vanguards hold the front line with sword, axe or club and a shield." There's nothing about playstyle, difficulty, solo vs. group, or what the first spells are. For a first-timer this is the biggest decision in the game, so it deserves more.
- **The game-mode prompt** offers "death game" with no explanation of what it means or what you lose. And my answer "normal" never got a confirmation, so I still don't know which mode I'm in.
- **Mystic gets the wrong hotbar and tutorial text.** After picking Mystic, the hotbar still shows Bell Ringer, Crushing Arc and Tremor Blow (club or vanguard skills), and the stop is titled "Sword skills and spells". The real spells, frost strike and dewfall, are only found by typing `!spells`, and nothing points you to binding them.
- **`!hunt` directions don't match the map.** "Sprouting Glade: south, about 80 steps" runs straight into a solid tree wall outside the gate. East is walled too. West is a long corridor, and I never found the Glade entrance. Either open a path south or make the directions say how to get there.
- **`!hunt` is refused inside the Guarded town zone**, which is exactly where a new player will try it first. Let it work in town.
- **Casting with no target fails silently.** "frost strike" with nothing selected does nothing and logs nothing. Add a "You need a target" message.
- **Ctrl+O doesn't open Options**, and the gear icon is hard to find.
- **The zone label says [Open PvP] on Floor 1.** If PvP is really open on the newbie floor, that's a big deal for new players and should be explained. If it's not, the label is wrong.

## 4) What was boring or slow
- **Walking the tutorial path.** Several identical gates in a row with nothing to do between them.
- **Walking out of town to hunt**, then the long west corridor. That's a lot of walking before your first fight as your new vocation. (Partly lag?)
- **Pacing.** I was about an hour in and still hadn't killed anything with my chosen vocation. Most players would quit before then. Put a vocation-appropriate fight right outside the Registrar.
- **The 2250% XP boost** makes the rat pen level you so fast that the levels feel meaningless. Probably a test setting, but worth mentioning.

## 5) Bugs or things that looked broken
| # | What | Where | Screenshot |
|---|------|-------|-----------|
| 1 | Hotbar shows club skills (Bell Ringer, Crushing Arc, Tremor Blow) for a Mystic. Before you have any vocation, pressing them gives "Your vocation can't use this spell." | After the Registrar, anywhere | `0751-registrar-garbled-chat.webp`, `0830-meadow-hotbar-mismatch-damage-log.webp` |
| 2 | NPC overhead bubble renders the keyword markup raw: `{yes? or {no??}` | Registrar Maelis, temple | `0745-registrar-mystic-pitch.webp`, `0745-registrar-vanguard-pitch.webp` |
| 3 | No reply or confirmation after answering "normal" to the game-mode prompt | Registrar Maelis | `0754-normal-typed-no-reply.webp`, `0755-still-no-gamemode-reply.webp` |
| 4 | `!hunt` says the Sprouting Glade is south about 80 steps, but south of the gate is a solid tree wall | Just outside the Hearthgate town gate | `0809-outside-gate-tree-wall-south.webp` |
| 5 | Monsters hit me while invisible or flickering, and the Battle List stayed empty during attacks **(lag?)** | Meadow west of town | `0830-meadow-hotbar-mismatch-damage-log.webp` |
| 6 | Right-click attacks on Pen Rats sometimes did nothing: no HP loss, no XP **(lag?)** | Rat pen | `0740-rats-nibbling-no-autoattack.webp` |
| 7 | My first "report" to Pell got no reply and had to be typed again **(lag?)** | Guide Pell | (none) |
| 8 | Some of my chat lines came out scrambled ("nroa", "naorc") **(probably my side: Wine input under load)** | Registrar | `0751-registrar-garbled-chat.webp` |
| 9 | The Quest Tracker and Journal never showed Pell's quest, before or after finishing it | Anywhere | (none) |
| 10 | The login title text renders in a rune or glyph font that I couldn't read | Login screen | `0728-language-picker.webp` |

## 6) How it compares with other Open Tibia servers
This part is from general OT knowledge. I haven't played other OT servers myself.
- **Ahead of typical OTs:** most custom OTs drop you in Rookgaard-style with no guidance, or with a wall of text. A walked tutorial path, an NPC keyword guide, Server Log hints, a Journal "How do I" page and `!hunt` is more onboarding than most servers bother with. `!hunt`, with its level range, direction and live population, is the standout.
- **Behind well-polished OTs:** the client is close to stock OTClient Redemption. vBot, the Store button, dozens of icons and a raw default layout look unfinished to someone opening the game for the first time. Polished servers usually ship a trimmed, branded client with the bot panel off.
- **Vocations:** four renamed classes (vanguard, ranger, arcanist, mystic) is a familiar setup. But the hotbar and tutorial still assume a melee class, which reads like the Mystic path wasn't tested end to end.
- **Game modes:** hardcore or "death game" ladders exist on some OTs and are a real hook. They need to be explained to work, though.

## 7) Five changes that would most make me keep playing
1. **Get the first real fight in fast.** Right after the Registrar, put an easy vocation-specific mob or mini-quest in reach, with the correct spells already on the hotbar. An hour in, I still hadn't fought as a Mystic.
2. **Fix the hotbar and tutorial per vocation.** Auto-bind frost strike and dewfall (and each class's equivalents), and rename "Sword skills" to match the class.
3. **Make `!hunt` directions true and usable from town.** Open a path south to the Sprouting Glade, or give real directions or a minimap marker, and let `!hunt` work inside the Guarded zone.
4. **Explain the big choices.** Give each vocation a 3–4 line pitch (playstyle, difficulty, first spells). Explain normal vs. hardcore vs. death game, and confirm the mode once it's picked.
5. **Clean up the client and the feedback.** Hide vBot and the Store for new players, fix the `{yes?` bubble markup, make the Quest Tracker show active quests, and add "you need a target" and "Stop 2 of N" messages.

Rerun needed: items 5–8 and the overall movement and combat feel should be retested once my computer isn't overloaded.
