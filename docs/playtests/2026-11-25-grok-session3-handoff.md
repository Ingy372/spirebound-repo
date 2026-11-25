# Spirebound session 3 handoff for Claude (2026-11-25)

## Context
Spirebound is Jay Lindemuth's unreleased Open Tibia server. In session 3, a playtest bot played fresh level-1, no-vocation characters on the grokbot account through all four vocations: Ranger (Grok Fourth), Vanguard (Grok Third), Arcanist (Grok Second, never got past the rat pen) and Mystic (Grok Tester). Play ran 09:35–12:42 ET. Everything below comes from `notes/2026-11-25-session3.md` and the `notes/s3-*` screenshots. All paths are relative to `/workspace/spirebound-playtest/`. Each item is checked against session 1 (`2026-11-24-report.md`) and session 2 (`2026-11-24-session2-report.md`). The client ran under Wine on the tester's box at about 30 fps. Items marked **possibly client-side** may be render or input lag on the tester's side, so check them on a normal client before spending time on them. The XP boost is 2250%.

Status key: **New** = first seen this session. **Repeat** = seen in an earlier session. **Regression** = reported fixed or working earlier, broken again.

## P0: blocks progress or kills characters

### SB3-01 New Ranger starts with no ammo and can't attack
- **Class:** Ranger. **Status:** New (first Ranger ever played).
- **Location:** Right after choosing Ranger + Normal at Registrar Maelis, then Hearthgate.
- **Text:** Journal: "Fletcher Tamsin sells quivers and arrows". The death message mentions a quiver and a fletcher. Quickdraw with no target: "You need a target: click a monster first (or pick it in the Battle List), then use quickdraw."
- **Repro:** Fresh character → Pell → Registrar → pick Ranger, Normal → look at equipment and backpack → attack any rat.
- **Expected:** The Ranger can damage a monster within seconds of picking the class.
- **Actual:** Bow equipped, ammo slot empty, backpack holds only 2 spears. Auto-attack does nothing, and Quickdraw/Pinning Shot do nothing on a target. 0 kills in ~25 min, one death to rats. The tester never found Fletcher Tamsin, and Trader Osric only buys loot.
- **Evidence:** `notes/s3-ranger-equipment-noammo.png`, `notes/s3-ranger-backpack-spears.png`, `notes/s3-ranger-quickdraw-sticky-crosshair.webp`
- **Fix direction:** The Ranger should leave the Registrar with a quiver of starter arrows already in the ammo slot, or at least have class skills that don't need ammo. Fletcher Tamsin should be on the path out of the Registrar, or marked in the Journal and on the minimap.

### SB3-02 Logout fight-lock persists for minutes with no enemies
- **Class:** All (seen on Arcanist, Ranger, Vanguard). **Status:** New.
- **Location:** The stone path south of the rat pen (Grok Second), outside Hearthgate (Grok Fourth), the Arrival Yard before any fight (Grok Third). The temple worked fine.
- **Text:** "You may not logout during or immediately after a fight!" and, on Grok Fourth, "You cannot logout during or immediately after a fight." (two different strings).
- **Repro:** Fight rats in the pen (they respawn constantly). Walk out to the stone path with no monsters on screen and the Battle List empty. Press Ctrl+L repeatedly for 5+ minutes.
- **Expected:** Logout is allowed shortly after the last hit given or taken, the usual short fight timer.
- **Actual:** Grok Second: refused ~8× over 6 min (11:40–11:46). The last damage line was at 11:39, and the client had to be killed to escape. Grok Fourth: refused ~13 min, then a boar entered the Battle List and killed the character (one death caused). Grok Third: refused on a character that hadn't fought anything yet, with an empty Battle List. In the temple, Ctrl+L was instant (Grok Third 11:27, Grok Tester ~12:22).
- **Evidence:** `notes/s3-arcanist-logout-refused-norats.webp`, `notes/s3-arcanist-logout-refused-ratpen.webp`, `notes/s3-ranger-logout-refused.webp`, `notes/s3-vanguard-logout-refused-nofight.webp`
- **Fix direction:** The fight flag should expire a fixed short time after the last combat event and should not be refreshed by monsters that aren't engaging the player. Respawning pen rats shouldn't keep a player locked once they've left the pen. Use one consistent refusal string, ideally one that says how many seconds remain.

### SB3-03 Rat loot (cheese) doesn't reach the backpack, so the cheese gate blocks
- **Class:** Pre-vocation (Arcanist and Mystic characters this session). **Status:** Repeat. This was session 2's top bug on Grok Third, and it's still inconsistent.
- **Location:** The Arrival Yard rat pen and the cheese gate east of Pell.
- **Text:** "Loot of a pen rat: cheese, a gold coin." (Mystic, 12:08). The Arcanist got no kill or loot line at all.
- **Repro:** Fresh character → Pell's quest → kill pen rats → check the backpack and the corpse (Browse Field) → try the cheese gate.
- **Expected:** Every loot line that names cheese means cheese is in the backpack, and the gate opens.
- **Actual:** Mystic: the Server Log names the cheese, and the backpack doesn't show it (the Mystic did eventually pass the gate after `!spells` + potion). Arcanist: XP rose 405→540→675 from kills, with no corpse (Browse Field empty), no loot message and no cheese. The character was permanently blocked from reaching the Registrar. Grok Third (Vanguard) also logged "Loot of a pen rat: cheese" (`s3-vanguard-penrat-loot-cheese.webp`) and did progress.
- **Evidence:** `notes/s3-mystic-ratpen-lv5-loot-not-in-bag.webp`, `notes/s3-arcanist-backpack-no-cheese.webp`, `notes/s3-arcanist-no-corpse-browse-field.webp`, `notes/s3-vanguard-penrat-loot-cheese.webp`
- **Fix direction:** Loot, corpse and gate should agree. Either auto-loot puts the cheese in the backpack and the gate checks the inventory, or the corpse stays openable. Every kill should produce a corpse or a loot line. Add a fallback so a character with Pell's quest done can never be hard-blocked: Pell could hand out cheese, or the gate could check quest state instead of an item.

### SB3-04 Action bar shows the wrong class's spells; real skills on a separate bar
- **Class:** All. **Status:** Repeat (sessions 1 and 2), not fixed.
- **Location:** After the Registrar, everywhere.
- **Text:** Main bar shows "exura infir" on a Ranger (fails) and an earth attack on a Mystic (no effect, no mana). The floating bar shows Quickdraw/Pinning Shot/Arrow Storm (Ranger), Arc Slash/Riposte Line/"ourfold Rene" (Vanguard), Thorn Edge/Frost Script/Verdant Burst (Mystic), on Shift+1–3.
- **Repro:** Pick any class, look at the main action bar, press its slots.
- **Expected:** One bar with the class's own attack and heal, and nothing from other classes.
- **Actual:** Dead spells from other classes on the main bar. The Ranger's real heal "field dressing" isn't on any bar. Shift+1–3 only works after pressing Escape, otherwise it opens chat and types "@@".
- **Evidence:** `notes/s3-ranger-temple-actionbar-hunt.webp`, `notes/s3-mystic-ratpen-lv5-loot-not-in-bag.webp`, `notes/s3-vanguard-proving-skillbar-clipped.webp`
- **Fix direction:** On class pick, the main bar should be cleared and filled with that class's attack skills plus its heal. Skill hotkeys should work while chat is in its default state.
- **Note:** It's arguably P1 because the floating bar does work, but it ties into SB3-01 and makes classes look broken, so it's listed here.

## P1: major confusion

### SB3-05 Quest Tracker misses Pell's quest on some characters and doesn't tick
- **Class:** Pre-vocation. **Status:** Repeat (session 1: never showed; session 2: 1 of 2 characters).
- **Location:** The Arrival Yard, after accepting Pell's quest.
- **Text:** Pell: "Thank you! It's in your quest log." Tracker, when present: "Guide Pell's Test (0/3 Pen Rats)".
- **Actual:** Showed for Grok Fourth and Grok Tester. Missing from the sidebar for Grok Third and Grok Second, though the Journal Quests tab had it. When present, it stayed 0/3 per kill and only flipped to "return to Pell" after the third kill.
- **Evidence:** `notes/s3-vanguard-pell-accepted-no-tracker.webp`, `notes/s3-ranger-tracker-pell.webp`
- **Fix direction:** Accepting a quest should always add it to the tracker, and the counter should update on each kill.

### SB3-06 Proving exit-swirl text gives the wrong stone color and position
- **Class:** All. **Status:** New text. Session 2 bug "fight stone and exit stone look the same" is partly fixed: the fight is now reachable.
- **Location:** The Proving.
- **Text:** "This swirl skips Bramblejaw and goes straight to Hearthgate. The fight is the red glowing stone in the east of the hall. Step on the swirl again to leave anyway."
- **Actual:** The fight stone glows yellow, in the SE corner.
- **Evidence:** `notes/s3-vanguard-exit-swirl-text.webp`
- **Fix direction:** The text should match the stone's real color and position.

### SB3-07 Bramblejaw stomp warning unreadable; L5–6 dies in about a minute
- **Class:** Vanguard, Mystic. **Status:** New (first time the fight was reached).
- **Text:** "Bramblejaw rears up!" plus red marks.
- **Actual:** Vanguard at L5 with 170 HP died in ~70 s with the boss at 60–70%. Mystic at L5–6 died in ~1 min. Neither could tell where to step. The potion worked via "Use with" mid-fight. Dragging a potion opened a "Move Stackable Item" dialog.
- **Evidence:** `notes/s3-vanguard-bramblejaw-intro.webp`, `notes/s3-vanguard-bramblejaw-rears-up.webp`, `notes/s3-vanguard-potion-stack-dialog-midfight.webp`
- **Fix direction:** The warning should say what to do ("step out of the red"), and the safe tiles should be obvious. The first class fight should be beatable by a fresh L5 of each class. Warden Ketta could state the mechanic before the fight.

### SB3-08 The second path gate silently snaps you back until `!spells`
- **Class:** All. **Status:** New.
- **Location:** The path gate east of the cheese gate.
- **Text:** Bottom-screen hint: "Say !spells to see the sword skills and spells your path will teach you." The Mystic also needed a potion step.
- **Actual:** Walking in snaps you back with no message in the log. The hint is easy to miss. It also says "sword skills" to every class (repeat of session 1's "Sword skills" wording).
- **Evidence:** `notes/s3-vanguard-gate-stuck-before-spells.webp`, `notes/s3-vanguard-gate-open-after-spells.webp`
- **Fix direction:** The gate should print the requirement in the Server Log when refused, and the wording should be class-neutral.

### SB3-09 Potion hint says right-click, but there's no "Use"
- **Class:** All. **Status:** New.
- **Text:** The right-click menu has only "Use with...".
- **Evidence:** `notes/s3-vanguard-potion-rightclick-no-use.webp`
- **Fix direction:** The hint should match the real action ("Use with..." on yourself), or potions should get a plain Use.

### SB3-10 Registrar building has no visible entrance
- **Class:** All. **Status:** New (earlier sessions reached Maelis without noting this).
- **Location:** End of the stone path. The red roof, west and south walls are solid. North/east unchecked.
- **Text:** The arrow at path end: "The tower: Floor 2 is sealed. No one has broken through the Pass on Floor 1 yet: the first party to defeat its guardian opens the way to the floor boss." Maelis answers "hi" only when adjacent.
- **Actual:** The only way in found was clicking the building on the minimap (~2 min autowalk).
- **Evidence:** `notes/s3-ranger-registrar-roof-nodoor.webp`, `notes/s3-ranger-registrar-south-wall.webp`, `notes/s3-ranger-roof-lifted-interior.webp`, `notes/s3-ranger-registrar-hi-noreply.webp`, `notes/s3-ranger-tower-sealed-msg.webp`
- **Fix direction:** There should be a visible door on the path side, and the path-end arrow should point to it.

### SB3-11 `!hunt` route to Sproutling Glade doesn't get players there
- **Class:** Ranger, Vanguard. **Status:** Regression (session 2's Arcanist reached it with the same directions).
- **Text:** "Sproutling and Hopper Toad (Sproutling Glade, levels 5-10): leave Hearthgate by the south gate, then about 30 steps west to its north entrance."
- **Actual:** The Ranger hit a river and tree-wall dead end. The Vanguard's dirt road west ended in forest.
- **Evidence:** `notes/s3-ranger-hunt-deadend-river.webp`, `notes/s3-ranger-temple-actionbar-hunt.webp`
- **Fix direction:** Recheck that the route is walkable as described, and add a signpost at the turn.

### SB3-12 Minimap "!" quest markers never seen
- **Class:** All. **Status:** New (watch item).
- **Actual:** No "!" appeared on any character's minimap all session. Vesper was found by walking past her. The minimap was black for one run **(possibly client-side)**, but worked in other runs and still showed no "!".
- **Fix direction:** Quest givers with available quests should show a "!" on the minimap from level 1, or the Journal should say how to enable them.

### SB3-13 Vesper's quest dialogue inconsistent; bubble overlap
- **Class:** Vanguard. **Status:** New.
- **Text:** First visit (11:17): "Six carved stones stand in the wilds around Hearthgate…Reward: 800 gold, 6,000 experience, the title "Stonereader"." Later visit (12:24): "Everything has a price. Especially what nobody else knows." then "Good bye." Her bubble overlaps her own text.
- **Evidence:** `notes/s3-vanguard-vesper-quest-text.webp`, `notes/s3-vanguard-vesper-overlapping-bubbles.webp`, `notes/s3-vanguard-boar-mauling.webp` (quest text visible in chat)
- **Fix direction:** With the quest active, Vesper should report stone progress on "hi" or "quest". Long lines should be split so bubbles don't overlap. NPC replies should also appear in Local Chat, or the NPCs tab should be the obvious default.

### SB3-14 Bristle Boar health bar stays full while it shreds a L5
- **Class:** Vanguard. **Status:** New. **Possibly partly client-side or user error:** chat focus ate Shift+1.
- **Actual:** 170→47 HP in ~15 s, boar bar full. Then the client dropped to character select (death or disconnect, unclear).
- **Evidence:** `notes/s3-vanguard-boar-full-hp-me-47.webp`, `notes/s3-vanguard-boar-mauling.webp`, `notes/s3-vanguard-respawn-temple.webp`
- **Fix direction:** Confirm that auto-attack damage registers on boars. A Boar Meadow monster should be survivable at the level `!hunt` suggests.

## P2: polish

| ID | Title | Class | Status | Text / detail | Evidence | Should |
|---|---|---|---|---|---|---|
| SB3-15 | Raw braces in speech bubbles | All | Repeat (3rd session) | "{vanguard}, {ranger}, {arcanist} or {mystic}?" "{yes}? or {no}?" | `notes/s3-vanguard-registrar-braces.webp` | Bubbles strip keyword markup, as the chat log already does |
| SB3-16 | Clipped skill label | Vanguard | New | "ourfold Rene" | `notes/s3-vanguard-proving-skillbar-clipped.webp` | Full name fits or is truncated cleanly |
| SB3-17 | Character list stale level/vocation | All | Repeat | Grok Tester "Level 1" at L6; Grok Third "L1 None" | `notes/s3-mystic-charselect-shows-lv1.webp` | The list shows the current level and vocation after logout |
| SB3-18 | Sticky Quickdraw crosshair; Enter fires Quickdraw | Ranger | New | Crosshair swallows clicks until Esc | `notes/s3-ranger-quickdraw-sticky-crosshair.webp` | Enter opens chat; the crosshair clears after one use or a miss |
| SB3-19 | Glowing blue pillars look like barriers | All | New | No hint they're passable | `notes/s3-ranger-pillar-lane.webp`, `notes/s3-ranger-path-barrier.webp` | Make passable pillars look passable, or explain them |
| SB3-20 | Rat pen entrance / over-fence targeting | Pre-vocation | Repeat | "Target lost."; "There is no way." | `notes/s3-ranger-ratpen-lv2.webp`, `notes/s3-arcanist-ratpen-lv4.webp` | Obvious gap, signposted |
| SB3-21 | Death XP loss not shown / unexplained | All | New | Mode text: "a death costs you some experience". Login: "You have adventurer's blessings for being level lower than 21!" | `notes/s3-vanguard-respawn-temple.webp`, `notes/s3-vanguard-dorrow-hint.webp` | The death message says the blessing protected your XP |
| SB3-22 | Temple townsfolk spam Local Chat | — | New | Little Bix, Priest Odran, Trader Osric constantly | (none) | Lower the frequency, or put ambient lines in their own channel |
| SB3-23 | Backpack opens only via right-click → Open | All | New | Double-click did nothing | (none) | Double-click opens containers **(possibly client-side)** |
| SB3-24 | Player sprite blends into tree canopy | All | New | — | `notes/s3-ranger-sprite-in-trees.webp` | Player stays readable over foliage |
| SB3-25 | Boar art reads as a thin green lizard | — | New (art) | Bramblejaw looks similar | `notes/s3-vanguard-boar-mauling.webp`, `notes/s3-vanguard-bramblejaw-rears-up.webp` | Flag for the art pipeline (not a code fix) |
| SB3-26 | Two different logout-refusal strings | All | New | "You may not…" vs "You cannot…" | see SB3-02 | One string |

### Possibly client-side (retest on a normal client before acting)
- Minimap black for a whole run. Worked in earlier runs. `notes/s3-vanguard-lost-east-minimap-black.webp`
- Minimap click didn't walk (Mystic). Autowalk overshoots then snaps back. Click-walk keeps walking several seconds.
- Camera alternates between two offsets. `notes/s3-arcanist-frame-desync-a.webp`, `notes/s3-arcanist-frame-desync-b.webp`
- Clock frozen around 12:31. Walking ~3 tiles per 10 s at one point (box load 3.8).
- Numpad diagonals did nothing, and movement keys drop input.
- Client dropped to character select mid-boar-fight.

### Looks fixed since earlier sessions
- [Open PvP] explanation shows on leaving the Guarded zone and is clear (session 2: untested). `notes/s3-ranger-openpvp-msg.webp`
- The no-target message works for Quickdraw.
- Bramblejaw is reachable (session 2 skipped it via the exit swirl).
- Mode confirmation: "It is written: Vanguard, Normal. One last step before Hearthgate: the Proving, below us. Climb well."
- Journal Quests → Available gives usable text directions for six quests.

## Design / UX recommendations
1. **First minute after class pick:** every class should be able to deal damage and heal from its main bar. Ammo, if it exists, should be pre-equipped.
2. **Make every gate explain itself in the Server Log when it refuses you** (cheese, `!spells`, potion), not just in a bottom-screen overlay.
3. **One source of truth for tutorial progress:** quest state should drive the tracker, the gates and Pell's dialogue, not item presence alone.
4. **Make content findable on foot:** "!" markers, signposts at road forks, a door on the Registrar, and `!hunt` routes walked and verified.
5. **First boss as a teacher:** Bramblejaw's mechanic should be explained before the fight and telegraphed in plain words. Tune it so a fresh L5 of each class can win with potions.
6. **Calm the temple:** ambient NPC chatter shouldn't drown Local Chat in the place players respawn.
7. **The XP boost (2250%)** makes levels 1–5 meaningless. Fine for testing, but worth confirming it's off for launch.

## Still untested, please verify
- Reedmarsh sluice levers (Fisher Corwin, ~95 NW). Not reached.
- Agna's flour (level 12+, Millcross ~175 NW). No character got past L6.
- Visiting any of Vesper's six stones.
- Rats stealing coins. None seen.
- Wolves arriving as a pack. Wolf Copse not reached.
- Sproutlings healing each other. Glade not reached this session.
- Toad Pond. Not found heading east, 0 monsters in 18 min.
- New monster art in motion for wolves, sproutlings and toads. Not seen.
- Arcanist past the cheese gate (Registrar, Proving, spells, first class kill) on Grok Second.
- A Ranger kill of any kind once ammo is fixed.
- Whether Fletcher Tamsin exists and where.
- Whether Normal-mode death XP loss works above level 21.
- The "!" minimap markers on a non-Wine client.
