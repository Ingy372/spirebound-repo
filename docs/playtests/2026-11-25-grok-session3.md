# Spirebound playtest report, session 3 (2026-11-25)

Tester: grokbot account, all four vocations, fresh level-1 characters with no vocation. Play ran 09:35–12:42 ET. Screenshots are `notes/s3-*`, running notes are `notes/2026-11-25-session3.md`. This report covers only what those show. Anything I didn't reach is marked as untested.

**Lag caveat.** The client runs under Wine on my box. At first it redrew only when the mouse moved, at 360% CPU. At 10:00 ET I capped FPS at 30 in the client's own config and got a stable 30–32 fps and 21–63 ms ping. I still saw stale frames, two alternating camera offsets, click-walk snap-back, a clock that froze around 12:31, and one run where the minimap stayed black. The minimap worked fine in earlier runs. All of that could be on my side, so it's marked **(client/lag?)** and I'm not counting it against the game.

## Watch-list answers

| Watch item | Answer |
|---|---|
| Pell's quest in the Quest Tracker on a fresh character | **Half the time.** It showed for Grok Fourth (Ranger) and Grok Tester (Mystic). It was missing for Grok Third (Vanguard) and Grok Second (Arcanist), even though the Journal had it and Pell said "It's in your quest log." When it does show, it sits at 0/3 and doesn't tick per kill. It only flips to "return to Pell" after the third rat. |
| Does a new Ranger's bow work right away? | **No. This is the worst bug of the session.** The bow is equipped, the quiver/ammo slot is empty, and the backpack holds only 2 spears. You can't attack, and Quickdraw/Pinning Shot do nothing. 0 Ranger kills in about 25 minutes, and I died to rats I couldn't hurt. The death message and Journal point to Fletcher Tamsin, whom I never found. |
| Finding quests with only the Journal and the minimap "!" | **Journal: yes, once you find the Quests → Available tab.** Its text directions are good (Agna ~175 NW, Corwin ~95 NW, Vesper ~15 S, Brannoch ~35 E). **Minimap "!": never seen once** on any character. I found Vesper by walking past her, not through either tool. |
| Vesper's stones | Quest accepted: six stones (Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow, Shard Fields, Burrow Hills), 800 gold, 6,000 XP, title "Stonereader". **I didn't visit a single stone.** On a second visit she gave only her secrets-broker line, then "Good bye." |
| Reedmarsh sluice levers | **Untested.** The Journal points to Fisher Corwin (~95 steps NW of Hearthgate, 400g/3000xp). I never got there. |
| Agna's flour (level 12+) | **Untested.** No character got past level 6. The Journal lists it with directions (Millcross mill ~175 NW of the temple, 600g/4950xp). |
| Rats stealing coins | **Untested.** I never saw a coin-stealing rat. |
| Wolves arriving as a pack | **Untested.** I never reached Wolf Copse. |
| Sproutlings healing each other | **Untested.** Neither the Ranger nor the Vanguard found Sproutling Glade from the `!hunt` directions. |
| Hearthgate townsfolk | **Mildly annoying.** Little Bix, Priest Odran and Trader Osric spam lines constantly and fill Local Chat. Bix is charming. |
| Toad Pond | **Untested.** I headed east for 18 minutes and saw zero monsters. No signposts. |
| New monster art in motion | **Only partly seen.** The Bristle Boar renders as a thin green lizard/crocodile shape, which is odd for a boar. Bramblejaw looks similar in my screenshots. Pen rats read fine. I saw no wolves, sproutlings or toads this session. |

## 1) What I did

| Class | Character | Time | Final level / XP | Deaths | How far |
|---|---|---|---|---|---|
| Ranger | Grok Fourth | 09:35–10:56 (~80 min, ~13 of it stuck in a logout lock) | L5, 975 XP at 10:26 (last level I saw) | 2: rats (couldn't attack), then a boar during the logout lock | Pell → Registrar (found only by clicking the building on the minimap) → Ranger/Normal → Hearthgate. `!hunt` south gate led to a river and tree-wall dead end. 0 Ranger kills. |
| Vanguard | Grok Third | 10:57–11:27, plus a gap run 12:24–12:42 (~50 min) | L5, 1,110 XP | 2: Bramblejaw (~70 s), Bristle Boar (client dropped to char select mid-fight) | Pell → snap-back gate (needs `!spells`) → Registrar → Proving → Bramblejaw → temple → Vesper's quest → Boar Meadow. The gap run east found nothing: 0 monsters in 18 minutes. |
| Arcanist (attempt) | Grok Second | 11:27–11:47 (~20 min) | L4, 675 XP, no vocation | 0 | Never got past the rat pen. Cheese never reached the backpack, then a 6+ minute logout fight-lock with no enemies. I closed the client to escape. |
| Mystic | Grok Tester | 11:50–12:22 (~32 min) | L6, 1,920 XP | 1: Bramblejaw (~1 min at L5–6) | Pell → `!spells` + potion gate → Registrar → Proving → Bramblejaw → temple. I read the whole Journal Quests tab. Logout in the temple worked first try. |

## 2) What was fun
- **Arc Slash hitting two rats at once.** It's the first moment any class felt good.
- **The Journal's Quests → Available tab.** It gives NPC, place, rough step count and reward for six quests. That's exactly how quests should be findable. It's also the only thing this session that told me where the new content is.
- **Vesper's pitch.** Six stones across named zones and a title reward ("Stonereader") is a real hook. I wanted to go do it.
- **Little Bix** is charming.
- **The [Open PvP] message is clear now**: "Out here, [Open PvP] means players of level 50 and above may fight each other. Below level 50 you can't attack anyone and no one can attack you." It covers session 1's complaint.
- **The "no target" message** for Quickdraw still works.
- **The daily reward message** (day 1/7, 100 gold) and the adventurer's blessings line ("for being level lower than 21") are nice touches.

## 3) What was confusing or unclear
- **The Ranger with no arrows.** The game hands you a bow and nothing to shoot. The only hint is the death message and the Journal line "Fletcher Tamsin sells quivers and arrows," and I couldn't find Tamsin. Trader Osric only buys loot.
- **Which spells are mine?** The top action bar shows other classes' spells (exura infir on a Ranger, an earth attack on a Mystic) that do nothing and cost no mana. The real class skills are on a separate floating bar (Shift+1–3). The Ranger's actual heal, "field dressing," isn't on any bar.
- **Shift+number only works after Escape.** Otherwise it opens chat and types "@@". Enter on the Ranger fired Quickdraw instead of opening chat.
- **The path gate east of the cheese gate** silently snaps you back until you say `!spells`. The only hint is a small line at the bottom of the screen. On the Mystic it then also wanted a potion.
- **The potion hint says right-click**, but the menu has no "Use", only "Use with...".
- **The exit swirl text is wrong**: "The fight is the red glowing stone in the east of the hall." The real stone glows yellow, in the SE corner.
- **Bramblejaw's "rears up!" + red marks** don't tell you where to step. Both classes died inside about a minute without understanding the stomp.
- **Registrar Maelis's building has no visible door.** The stone path ends at a red roof. West and south walls are solid. "hi" from outside gets nothing. I only got in by clicking the building on the minimap.
- **The blue glowing pillars** on the path look like barriers. Nothing tells you they're passable.
- **NPC replies go only to the NPCs tab**, not Local Chat. Vesper seemed to ignore me on a later visit.
- **The rat pen.** Attacking over the fence gives "target lost." The diagonal gap was found by trial and error, and once "There is no way." (rats blocking?).
- **`!hunt` directions to Sproutling Glade** ("south gate, west 30, north 40") got two different characters lost this session. Session 2's Arcanist did reach it.
- **The arrow at the end of the path** is not a door. It gives "The tower: Floor 2 is sealed. No one has broken through the Pass on Floor 1 yet…", which is lore, not directions.
- **"Death costs you some experience"** on Normal, but I saw no XP loss after deaths. Probably the "adventurer's blessings for being level lower than 21" line, but nothing connects the two.
- **The backpack** opens only via right-click → Open. Double-click did nothing.

## 4) What was boring or slow
- **The Ranger**: 25 minutes of a class that can't attack. Unarmed rat fights before the vocation are slow on every class, too.
- **The Arrival Yard on a bad roll.** The Arcanist spent 20 minutes in and around the pen and never left.
- **Respawning pen rats** keep you in combat, which keeps the logout lock on (see bugs).
- **Wandering for hunting grounds.** The Vanguard gap run spent 18 minutes east of town with 0 monsters and no signposts or road markers. The Ranger's south-gate run hit a river dead end.
- **The 2250% XP boost** is still on (XP Gain Rate 2250%). Levels 1→5 come from a handful of rats and feel meaningless.

## 5) Bugs or things that looked broken

| # | What | Where | Exact text | Screenshot |
|---|---|---|---|---|
| 1 | **New Ranger has no ammo.** Bow equipped, empty ammo slot, 2 spears in the backpack, can't attack, Quickdraw/Pinning Shot do nothing. Died to rats. | Hearthgate after the Registrar, Grok Fourth | Journal: "Fletcher Tamsin sells quivers and arrows" | `s3-ranger-equipment-noammo.png`, `s3-ranger-backpack-spears.png` |
| 2 | **Logout fight-lock sticks for minutes with no enemies.** Grok Second: refused ~8× over 6 min on an empty stone path. Grok Fourth: refused ~13 min, a boar wandered in and killed me. Grok Third: refused before ever fighting. Temple Ctrl+L was instant (Grok Third, Grok Tester). | Stone path south of the rat pen; outside Hearthgate; Arrival Yard | "You may not logout during or immediately after a fight!" / "You cannot logout during or immediately after a fight." | `s3-arcanist-logout-refused-norats.webp`, `s3-arcanist-logout-refused-ratpen.webp`, `s3-ranger-logout-refused.webp`, `s3-vanguard-logout-refused-nofight.webp` |
| 3 | **Rat loot / cheese doesn't reach the backpack** (repeat of session 2's top bug). Mystic: the log shows loot, the bag doesn't have it. Arcanist: XP 405→540→675 with no corpse, no kill/loot message, no cheese. The cheese gate blocked the Arcanist for good. | Rat pen, Grok Tester and Grok Second | "Loot of a pen rat: cheese, a gold coin." | `s3-mystic-ratpen-lv5-loot-not-in-bag.webp`, `s3-arcanist-backpack-no-cheese.webp`, `s3-arcanist-no-corpse-browse-field.webp` |
| 4 | **The action bar shows the wrong class's spells** (repeat). exura infir on a Ranger (fails), an earth attack on a Mystic (no effect, no mana). The real skills are on a separate floating bar. The Ranger's "field dressing" isn't on any bar. | After the Registrar, all classes | — | `s3-ranger-temple-actionbar-hunt.webp`, `s3-mystic-ratpen-lv5-loot-not-in-bag.webp` |
| 5 | **The Quest Tracker misses Pell's quest on 2 of 4 fresh characters** (repeat), and doesn't tick per kill when it does show. | Arrival Yard | "It's in your quest log." | `s3-vanguard-pell-accepted-no-tracker.webp`, `s3-ranger-tracker-pell.webp` |
| 6 | **The exit swirl text says the fight stone is red, east.** It's yellow, SE. | The Proving | "The fight is the red glowing stone in the east of the hall." | `s3-vanguard-exit-swirl-text.webp` |
| 7 | **Speech bubbles still show raw braces** (repeat, 3rd session). | Registrar Maelis | "{vanguard}, {ranger}, {arcanist} or {mystic}?" "{yes}? or {no}?" | `s3-vanguard-registrar-braces.webp` |
| 8 | **Clipped skill label**: the third Vanguard skill reads "ourfold Rene". | Floating skill bar, Vanguard | "ourfold Rene" | `s3-vanguard-proving-skillbar-clipped.webp` |
| 9 | **The potion hint says right-click, but the menu has no "Use"** (only "Use with..."). Dragging a potion mid-fight opened a "Move Stackable Item" dialog. | Path gate; Bramblejaw | — | `s3-vanguard-potion-rightclick-no-use.webp`, `s3-vanguard-potion-stack-dialog-midfight.webp` |
| 10 | **Vesper's bubble overlaps her own text** and can't be read. | Hearthgate town square | — | `s3-vanguard-vesper-overlapping-bubbles.webp` |
| 11 | **Boar health bar stayed full** while I went 170→47 HP in ~15 s. Partly my fault, since focus was stuck in chat and Shift+1 did nothing. | Boar Meadow, Grok Third | — | `s3-vanguard-boar-full-hp-me-47.webp` |
| 12 | **Character select shows stale level/vocation** (repeat). Grok Tester shows Level 1 at L6. Grok Third shows L1 None. Grok Fourth showed L4/None while L5. | Character list | — | `s3-mystic-charselect-shows-lv1.webp` |
| 13 | **Registrar building has no visible entrance.** Only minimap autowalk got me in. | End of the stone path | — | `s3-ranger-registrar-roof-nodoor.webp`, `s3-ranger-registrar-south-wall.webp`, `s3-ranger-roof-lifted-interior.webp`, `s3-ranger-registrar-hi-noreply.webp` |
| 14 | **`!hunt` south-gate route dead-ends** at a river and tree wall for the Ranger. The Vanguard also couldn't find the Glade's north entrance. | South of Hearthgate | — | `s3-ranger-hunt-deadend-river.webp` |
| 15 | **Sticky Quickdraw crosshair** swallows clicks until Esc. Enter fired Quickdraw instead of opening chat. | Ranger, Hearthgate | — | `s3-ranger-quickdraw-sticky-crosshair.webp` |
| 16 | Client dropped to char select mid-boar-fight (death or disconnect, unclear). **(client/lag?)** | Boar Meadow | — | `s3-vanguard-respawn-temple.webp` |
| 17 | Minimap black for a whole run (it worked earlier). Minimap click didn't walk for the Mystic. Autowalk overshoots and snaps back. **(client/lag?)** | Hearthgate Plains east | — | `s3-vanguard-lost-east-minimap-black.webp` |
| 18 | View alternates between two camera offsets. **(client/lag?)** | Rat pen | — | `s3-arcanist-frame-desync-a.webp`, `s3-arcanist-frame-desync-b.webp` |
| 19 | Numpad diagonals did nothing, and movement keys drop input. **(client/lag?)** | Anywhere, Mystic | — | (none) |

**Looks fixed since session 2:** the [Open PvP] explanation now appears and is clear (`s3-ranger-openpvp-msg.webp`). The no-target message works for Quickdraw. Bramblejaw is now reachable via the stone, where session 2 skipped it, although the swirl text points to the wrong color. Mode confirmation works: "It is written: Vanguard, Normal."

## 6) How it compares with other Open Tibia servers
This is general OT knowledge. I haven't played other OT servers myself.
- **Ahead:** a Journal with quest NPC, direction, step count and reward is more than most custom OTs give. Many expect you to read a wiki or forum. Vesper's multi-zone stone hunt with a title is the kind of exploration quest that keeps people logged in. The Open PvP explanation is clearer than most.
- **Behind:** a starter class that can't attack is the kind of thing that gets a server written off on its launch-day forum thread. On most OTs, paladin-style classes start with ammo, or the starter weapon is a spear for exactly this reason. A logout lock that outlasts the fight by minutes is something players notice immediately, because the standard expectation is a short PZ/fight timer that ends shortly after the last hit. The client is still stock OTClient Redemption (vBot panel, Store, default layout).
- **Quest markers:** minimap markers for quest givers are common on modern custom OTs. If "!" markers exist here, I never saw one.

## 7) The five changes that would most make me keep playing
1. **Start the Ranger with a quiver and arrows equipped**, or make the starter weapon something that works with no ammo. A class that can't attack for 25 minutes is a quit.
2. **Make the logout fight-lock end shortly after the last hit**, whatever is still alive in the pen. I lost one character to a wandering boar while stuck, and another had to be killed via the client.
3. **One reliable loot path for the cheese.** Whatever "Loot of a pen rat: cheese" says must land in the backpack and open the gate, every character, every time. This is the second session running where it hard-blocked a character.
4. **One action bar with my class's real spells, heal included.** Remove the other classes' spells from the main bar, put field dressing on the Ranger's, and make Shift+number work without pressing Escape first.
5. **Make the new content findable on foot.** Show the minimap "!" on quest givers, add a door to the Registrar and signposts on the roads, fix the Sproutling Glade/Toad Pond routes, and make Pell's tracker entry show up and tick per kill.
