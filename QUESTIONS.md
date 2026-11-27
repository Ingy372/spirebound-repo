# Questions for Jay

How this works: each question has Claude's recommendation. Claude assumes the recommendation and keeps working. To answer, write under "Jay's answer" (a word or two is fine). Answered questions get moved to the bottom.

---

## Open

*Q54-Q61 are the cuts from the 2026-11-25 project review. A word or two each is enough ("yes", "no", "later"). Where the thing is your own decision, nothing in the game changes until you answer.*

### Q102. Ground features, cooking and Town Works: my smaller calls (2026-11-27)
Built (roadmap FD2, FD4, FD5). I assumed each of these; tell me if you want one changed.
- **Cooking is "drop it on the fire".** The game client cannot "use" food on something, so you drag raw food onto a campfire and it cooks right there; drop a second ingredient on the dish to combine. **Recommendation: keep.**
- **The three grounds the design left open:** Bramble Run gets berry bushes (berries for cooking, now and then a thornsnap wakes), Smugglers' Ridge gets hidden stashes under loose stones (gold, and two bandits come running), the Fallen Bastion gets an old ballista you can fire at the ruins. **Recommendation: keep.**
- **Works project 4:** the Old Watchtower has no tower to climb yet, so "repair the collapsed stair" became "clear the keep's fallen north gate" (a second way into the keep). When the tower gets real floors (MR5) it can become the stair again. **Recommendation: keep for now.**
- **The Stair Camp's healer and seller are objects, not people:** a healer's shrine (full health and mana out of a fight) and a supply crate (health potions at the shop price). **Recommendation: keep; real NPCs later if you want them.**
- **The Bandit Lieutenant and the signal fire are group-sized:** a lone level 28 dies to either (they sit in the deep loop and the apex). **Recommendation: keep; they are meant to be done with friends.**
- **NPCs do not buy dishes yet** (the design says "for little"); players can still sell them to each other. Open task FD4b.

### Q101. The story I wrote for the tower, and my calls on Floor 1 depth (2026-11-27)
You said: "i would lean in the direction of a place to conquer with a grand prize waiting at the top of the tower kinda thing. does that sound good, not the best story teller." This is what I built on it. Change anything.
- **The prize:** the **Summit Wish**. One wish, for whoever reaches the top of the Spire. Nobody is trapped; everyone came by choice to win it.
- **Floor 1's mystery:** a company called the **First Climb** went up long ago and never came down. Their names are chiselled off the Monument. The ruins, quarry and watchtower are theirs, the ruin guards are their garrison still at their posts, and the Axe-Lord was their rearguard captain, ordered to let nobody follow. The last page says the Wish is real and costs something, and that they went on to the Highlands anyway.
- **The big quest's rewards:** take one of four chests, once a season: one free weapon tier step, a backpack with its own look, 10,000 gold, or a mantle. Only the first is power, and it stays inside the gear system.
- **Cooking:** no bench and no recipe window. You use food on a fire. Dishes never help in a fight.
- **Town Works:** gold given is destroyed; the top giver of each project gets a title for the season, nothing else.
- **Recommendation:** keep all of it. Assumed until you answer. Full design: `docs/superpowers/specs/2026-11-27-floor1-depth-design.md`.
- Jay's answer:

### Q100. Adventure layer, my smaller calls (2026-11-27)
Built from your answers in Q99. These are mine; say if you want any changed.
- **Riddles:** I rewrote all 13 Floor 1 hints as riddles with no place names, directions or NPC names. A riddle shows only on Vesper's list once that secret is sold, or in your Journal if a message bottle gave it to you. Nobody sees all the riddles by default any more (before, the Journal showed every hint to everyone).
- **The purse:** 1,000 gold for every secret, into the bank, once per account. The three gear secrets also pay Vesper's top price if sold, without saying why.
- **Where secret gear sits:** the Millrace Boots under the mill and the Warden's Signet in the walled-up cell. The Shrinekeeper's Pendant goes to everyone who fights the shrine's two guardians. They can't be traded, dropped, stored or sold. Next season they move with the season remix.
- **Rare weapon pictures:** until Grok's icons arrive, the rare wand and rod borrow stronger base items, scaled back so they never out-damage the quest weapon. Side effect: they need level 13 to wield.
- **On the Monument and board:** a first find of a secret reads "A secret of Floor 1 (no. 3): Name". It never says where or which one. Hidden beasts and elites are named.
- **Recommendation:** keep all of it. Assumed until you answer.
- Jay's answer:

### Q99. Adventure and "someone has something I don't": build it now, before the full-party run? (2026-11-27)
You asked whether Floor 1 keeps a player hooked the whole way and has enough FOMO. My audit: the first 30 minutes and levels 10 to 20 are good; levels 20 to 28 go flat (mostly "kill 30 or 40" in the money grounds, no new secret beast, the weapon already earned); and almost nothing on the floor is scarce or visible. Nine of the 13 secrets pay only coins, a rare weapon drop looks like the ordinary one and nobody is told, trophies can't be seen by other players, and every player of a class ends up with the same two addons. The fixes are roadmap Step 4b (AD1 to AD7).
The roadmap's one rule (your "Yes, rewrite it", 2026-11-25) says nothing new is built until a real party clears Floor 1. Step 4b is mostly new rewards and announcements on things that already exist, but AD4 (rare roaming monsters) and AD5 (treasure maps, two new hidden places) are new content.
- **Recommendation:** yes, lift the rule for Step 4b only. Do AD1, AD2, AD3 and AD6 first (existing systems, no new art), then AD4 and AD5.
- **Second choice inside it (AD3):** a few prizes each season that only the first finders can ever have (as Twin Fang already works: first 3). My recommendation: looks and titles only, never power, so late joiners are not weaker, only less decorated.
- Jay's answer (2026-11-27): "yes lift the rule from the 25th. most things have been fleshes out. i havent run the play test yet but i dont feel like the servers quite ready. it needs a few more passes of detail work, like were doing now." And on secrets: "i feel like 1-3 secrets per floor should give gear, the rest can give special cosmetics or titles. players wont know what gives what so it will be up to them to decide if the secrets worth keeping, or rolling the dice to get an exclusive item. thoughts on this? im open to feedback"
- **Built on your answer; my calls, veto any (design: `docs/superpowers/specs/2026-11-27-adventure-layer-design.md`):**
  - Secret gear is a ring, an amulet or boots, never a weapon or armour, so it never beats the quest weapon path. Floor 1's three: Millrace Boots, Shrinekeeper's Pendant, Warden's Signet.
  - Secret gear can't be traded: wearing it proves you found the place.
  - Vesper never says what a secret pays, so keeping or selling stays a gamble.
  - First-finder prizes each season are looks and titles only.
  - **Your clarification (2026-11-27):** "i do not want the location of the secret announced. the only hints i want for the secrets need to be coded in thick riddles. it should be incredibly difficult to find a secret through the hints alone ... (always) a medium gold reward. 1-3 exclusive items total that can only be obtained through secrets per floor. the rest of the rewards can be titles, cosmetics, pets, or auras." Done that way. Two readings of mine to check: when a secret is sold, Vesper's list now shows its riddle instead of directions (before, a sold secret came with directions); and "medium gold" is 1,000 on Floor 1, once per account.
  - The four rare roaming monsters: Goldback Toad, Frenzied Boar, Pale Stag, the Paymaster.

### Q98. Hearthgate v4.1: where should Waycrystals land? (2026-11-27)
You first said the Hearth's top floor would be the Waycrystal landing, together with the Monument; then you asked to flip the floors so the lockers and bank are upstairs. I moved the Monument down with the rest, so crystals now land on the Hearthstone on the ground floor (the same spot as respawning).
- **Recommendation:** keep it on the ground floor, next to the Monument, so everyone arriving walks into the busy hall and climbs the stairs to the lockers.
- Assumed until you answer: ground floor, on the Hearthstone.
- Jay's answer:

### Q95. Waycrystals: the name and the rules I chose (2026-11-26, from your idea in Q94)
You asked for teleport crystals, one colour per floor. What I am building, my call until you say otherwise:
- **Name:** "Waycrystal" (for example "Amber Waycrystal (Floor 1)"). "Teleport Crystal" is the exact item name in Sword Art Online, and our rule is no SAO names players can see.
- **Use:** right-click it: a small menu offers that floor's town, or any of its hunting grounds your level has reached (you arrive at the ground's gate). It is used up when the teleport happens.
- **Not an escape:** you stand still for 3 seconds (moving or being hit cancels it); refused while in a fight, in boss rooms, arenas, the tutorial and party caves, and for floors that are not open yet. This matters most for Death Game characters.
- **Where to buy:** each floor's Runewright, never the donation shop. It replaces the Runewright's old 300-gold temple scroll.
- **Price:** about 4 minutes of that floor's hunting income each (there and back costs about 8 minutes); Floor 1's is 150 gold.
- **Recommendation:** keep all of the above.
- Assumed until you answer: as above.
- Jay's answer:

*Q82-Q94 come from the Floor 1 review and the map review (2026-11-26). Nothing is built for them until you answer.*

### Q97. Hearthgate's new layout: build it as planned? (2026-11-26)
You asked for a full redesign of the town unless I'd score it a solid A. I score it a B: tidy, but shops are 29 to 50 steps from where you appear (the Guild Hall 80), the middle is a building rather than a place to gather, and there are no districts. The plan (`docs/design/hearthgate_v4_plan.md`, picture `docs/HEARTHGATE_V4_PLAN.png`): the same size and gates, an eight-sided wall, a great round plaza in the middle where you appear on the Hearthstone in the open air (the Town of Beginnings nod), the Hearth as the great hall on its north side, every shop facing the plaza, the halls together in the north-east, Spire Manor in walled grounds in the south-east, and three neighbourhoods with different kinds of home. About a day of work.
- **Recommendation:** build it, after the Underkeep rebuild has finished with the map.
- Assumed until you answer: build it as planned.
- Jay's answer: (2026-11-26) build it; hand the building to an Opus session.
- **Built 2026-11-27.** Shops are now 19 to 25 steps from the Hearthstone (were 29 to 50) and the Crown Quarter 31 to 44 (was up to 80). Walked in the client on the live server. See FLOOR1.md, "Hearthgate v4".

### Q95. Spire Manor: are these the right things to sell with it? (2026-11-26)
You asked for the manor to "feel premium" and have "features that players would want to pay for, but not be totally game breaking". It is rebuilt (four furnished floors) and comes with: a private depot and mailbox, a steward who is your bank, a housekeeper who sells supplies and buys loot at the town's own prices, three training dummies, 10 mannequins, a free Fortune Hall license, longer Open House, a permanent title, and the Waystone on the roof (travel to any open floor's town; the owner can be called home from inside any town; every 30 minutes, never in a fight). Nothing gives experience, damage, defence or loot. Full list: DESIGN.md 7.6, or `!manor` in game.
- **Recommendation:** keep all of it. The Waystone is the one to think about: it saves the owner (and guests) walking and, later, teleport crystals. I think that is exactly the kind of comfort worth paying for, and it can't be used to escape a fight. If you'd rather it not replace crystals at all, I'd make it owner-only or once an hour.
- Assumed until you answer: as built.
- Jay's answer:

### Q96. One manor, one buyer: sell it once a season, or let more people pay? (2026-11-26)
There is one Spire Manor and one owner, so it can be sold once per season (the last owner gets first refusal next season). That keeps it special, but it is one sale. Options: (a) keep it as the single trophy house; (b) auction it for Spire Coins at each season start; (c) add two or three smaller "estate" houses with a few of the manor's comforts (depot, steward) at a lower price.
- **Recommendation:** (a) for the friends test, then (b) at public launch: an auction makes the one house worth far more than a fixed price, and losing bidders keep their coins for cosmetics.
- Assumed until you answer: (a).
- Jay's answer:

### Q82. Can players attack each other in the boss rooms below level 50? (2026-11-26, Floor 1 review A4-2)
Today anyone can attack anyone in the Gate Hound's arena and the Axe-Lord's hall, whatever their level. A level-60 could wait in the hall and kill a level-30 party mid-fight.
- **Recommendation:** in boss rooms, players can only attack each other from level 50.
- Assumed until you answer: no change.
- Jay's answer:

### Q83. Floor 1's length now that the engine's own bonuses are counted (2026-11-26, Floor 1 review A3-1)
The engine quietly adds 1.5x experience below level 50 and another 1.5x for fresh stamina, on top of our stages. Measured, a kill gives 22.5x at levels 1-8, 9x at 9-20 and 6.75x at 21-50. So Floor 1 is shorter than the 11-15 hours you chose in Q30.
- **Recommendation:** keep the 11-15 hours: lower our stages so the totals match (I re-measure first; roadmap RV2).
- Assumed until you answer: no change.
- Jay's answer (2026-11-27): "Yes, 11-15 hours". Done the same night: the engine's hidden 1.5x below level 50 is taken back out on every kill; Tibia's rested bonus (1.5x for the first 3 hours of a day) stays. By the model a rested player reaches level 35 in about 6 hours of pure hunting and a tired one in about 9.4; real play is about 40% slower, so most players land in 11-15 hours. RV2 measures it in the game.

### Q84. Loot is doubled by the engine: keep the richer game or trim drops? (2026-11-26, Floor 1 review E-1)
The server doubles every drop chance (loot rate 2). Measured, a Road Bandit gives 42 coins a kill against the 33 our economy plan expects, and some items drop twice as often as the tables say.
- **Recommendation:** keep loot rate 2 and lower the few drops that matter (gems, cheese) in the tables, so the plan and the game agree.
- Assumed until you answer: no change.
- Jay's answer:

### Q85. Do Tibia's item names count as "CipSoft names"? (2026-11-26, Floor 1 review)
Many items keep their Tibia names ("magic plate armor", "wand of vortex"). Our name rule covers monsters, NPCs and places.
- **Recommendation:** rename the items players see most (weapons, armour, wands and rods sold or dropped on Floor 1) before the friends test; leave the rest for later.
- Assumed until you answer: no change.
- Jay's answer:

### Q86. Should upgraded gear need a level to wear? (2026-11-26, Floor 1 review B4-9)
A tier-5 weapon can be traded to a level-8 character and wielded at once.
- **Recommendation:** a level requirement by tier (tier 3: level 20, tier 5: level 30).
- Assumed until you answer: no change.
- Jay's answer:

### Q87. Mastery respecs only from the donation shop? (2026-11-26, Floor 1 review)
- **Recommendation:** also a steep in-game route (gold that grows with each respec), so the shop sells convenience, not the only way.
- Assumed until you answer: no change.
- Jay's answer:

### Q88. Spear Rangers have no barracks weapon (2026-11-26, Floor 1 review B4-3)
Rangers who use spears get nothing from the barracks the bow users get.
- **Recommendation:** add a Trailwarden Spear on the same tiers as the barracks bow.
- Assumed until you answer: no change.
- Jay's answer:

### Q89. The Underkeep: make it a real dungeon? (2026-11-26, Floor 1 review A2-1 and map review M2)
The Underkeep under the city is six big bare halls; Wing 1 holds about 18 monsters in one 70 by 50 room. It reads as a warehouse, not a secret dungeon.
- **Recommendation:** rebuild Wing 1 first as a real dungeon: corridors, guard rooms, cells, a collapsed and a flooded part, a loop and a dead end with a reward, about 50 monsters of three kinds, one mini-boss and the promised secret. The other wings follow with their floors. It is several days of work, so it waits for your yes (roadmap MR2).
- Jay's answer (2026-11-26): "yes. being honest i dont know how many people im going to get to help me play test. i may end up just being my self or maybe myself and one other person." Being built (MR2). For all planning: Floor 1 must be testable alone or as a pair.

### Q90. Solo players and the Stair Key (2026-11-26, Floor 1 review A3-2 and A5-1; FYI)
The review worried that the Stair Key step (30 Road Bandits) needs a group. Checked on the built map: the Bandit Road's surface already holds Road Bandits in ones and twos only (11 on the surface, the Captain alone at the camp); the packs of 3-4 are in the Smugglers' Cellar below, which is the party part.
- **Recommendation:** keep it as it is: a solo player can finish the step on the surface.
- Assumed until you answer: keep.
- Jay's answer:

### Q91. A guild can fill the 20-player boss hall (2026-11-26, Floor 1 review A4-4)
- **Recommendation:** at most 10 of the 20 credited places per guild, so a big guild cannot lock others out of the first kill.
- Assumed until you answer: no change.
- Jay's answer:

### Q92. The private boss hall without the Stair Key (2026-11-26, Floor 1 review A4-7)
After the first clear, any party can say !private at the top of the labyrinth and fight the Axe-Lord alone, Stair Key or not.
- **Recommendation:** keep it as a catch-up for late climbers, but each member needs the Stair Key.
- Assumed until you answer: no change.
- Jay's answer:

### Q93. How hand-made should Floor 1 look before friends see it? (2026-11-26, map review M3, M4, M7, M8, M10-M15)
The map is tidy and correct, but it looks generated: every hunting ground is a box, most roads are straight with square corners, all ~80 homes are the same empty square, and the public halls (Hunters' Hall, Registrar, the inns, Spire Manor) are big rooms with little in them.
- **Recommendation:** two jobs before the friends test, each in the generator so Floors 2-10 inherit them: (1) wandering outlines and winding roads for every ground (roadmap MR3); (2) five or six house plans with beds and furniture, and furnished public halls (roadmap MR4). The smaller polish (MR5) is left for the Cowork finishing pass you planned.
- Jay's answer (2026-11-26): "im not worried about the game feeling hand made, im worried about it being fun and functional. currently the housing options are boring and all the same. unique housing options with 1 grand mansion house that a player can buy for real money is what i was going for. i wanted the town to have somewhat of a resemblance to sword art onlines town of beginnings. but at the same time dont want anything having restrictions on it to hold to that hope." So: the pure looks (box-shaped grounds, straight roads, the labyrinth and watchtower looks: MR3, MR5) wait in "Later"; housing and Spire Manor went to the review session at Jay's request; a nod to that kind of town only where it costs nothing (the central plaza), with original names and layout as always.

### Q94. The empty land on Floor 1 (2026-11-26, map review M11)
About a third of the 400 by 400 floor is open lawn with nothing to find (south-east, south-west, far west, north-west).
- **Recommendation:** use it for the launch-size grounds of Step 4 (levels 17-30, helps launch-day crowding), and meanwhile scatter a few small landmarks (a shrine, a camp, a wreck) so wandering is rewarded.
- Jay's answer (2026-11-26): "i would lean towards fill in the empty land with small game monsters to help it feel less empty. i had an idea to incorporate 'teleport crystals' to help players save time, to create a unique system, and to provide another area to burn player income. the teleport crystal can be set to instantly teleport you to town, or it can open a menu and teleport you to a training zone on that floor specifically. teleport crystals should come in 10 different colors for each floor and labeled accordingly." So: small harmless creatures over the empty lawns (roadmap MR6), and the crystals (roadmap TC1, DESIGN.md 3.7; the choices left to me are Q95).

### Q81. Three hidden bugs fixed tonight change how strong and how fast everyone is (2026-11-26, Floor 1 review; FYI and one choice)
The review tested with a real character and found three things that had never worked, although 281 automatic tests passed: (1) the damage bonus of weapon tiers, familiarity, the awakening, Mastery and trophies was never applied; (2) no experience bonus or cut was ever applied (Hardcore +25%, Death Game +50%, the cavebot's 45%, Beacons, weekend events, the boosted creature), nor the double skill training below level 50; (3) the cavebot's loot cut crashed on every kill, so botting gave full loot. All three are fixed and checked on real test characters. What you will notice: a character with an upgraded weapon now hits up to 61% harder (a tier-3 weapon about 30%), Hardcore and Death Game level faster, botting really is slower, and melee and magic skills below level 50 train twice as fast as they did yesterday.
- **Recommendation:** keep all of it (it is what DESIGN.md always said), and I re-measure the Axe-Lord and the hunting pace with the bonuses working (roadmap RV1, RV2) before anything is retuned. If the doubled skill training below 50 feels too fast once you play it, say so and I'll halve it.
- Assumed until you answer: keep.
- Jay's answer:

### Q80. Should a Hardcore death risk your items before level 22? (2026-11-26, Floor 1 review)
A Hardcore death already costs experience at any level (tested: a level-15 Hardcore character lost 7.5%, a Normal one nothing). But the game hands every character its blessings back at each login up to level 21 (the engine's "starter blessing"), so a young Hardcore character never drops an item, while it earns 25% more experience and 15% more loot from the first minute.
- **Recommendation:** Hardcore and Death Game characters keep the free blessings only below level 8 (the first minutes). From level 8 a Hardcore death costs the full 15% and can drop gear, unless the player buys blessings from the priest. I built and tested this tonight and then took it out again, because it is your rule to change: it is a 20-minute job to put back.
- Assumed until you answer: no change (today's behaviour stays).
- Jay's answer:

### Q79. The Vanguard's barracks weapons now hit harder than any Floor 1 shop sword (2026-11-26, Floor 1 review)
The review found that the Hearthguard Sword, Axe and Mace were weaker than swords Garrick sells in the same room (a 160-gold longsword beat the reward sword until tier 3, and the 8,000-gold spike sword beat it for ever), and that the Axe was 25% behind the Mace for the same price. Fixed: all three now have attack 20 and defence 15 of their own, +1 attack per tier (25 at tier 5); the rare Briarguard Sabre starts the same; the donation shop's Climber's Sword is 18; Garrick no longer sells the spike sword on Floor 1 (his best is the longsword, 17). (My call; you can veto.)
- **Recommendation:** keep it. A Vanguard's reward weapon should be the best thing they can hold on the floor.
- Assumed until you answer: yes.
- Jay's answer:

### Q78. How many players should it take to beat the Axe-Lord? (2026-11-26, party playtest)
A level-30 party of three in upgraded Floor 1 gear killed the Gate Hound in a minute without a death, then wiped twice on the Axe-Lord: the best try did 19% of his health in 45 seconds. As he is now (12,000 health, hits up to 260 plus a 300 line attack), beating him needs about 8-10 level-30 players, or 5 well-geared level-34s. The room holds 20.
- **Recommendation:** make him a party boss for 4-6 players around level 30-35 (lower his health and his biggest hits, keep his phases), so the first floor clear at launch is something a guild party can do on the first evening, and say "bring 4 or more" in the Journal. Keep him a raid only if you want Floor 1's first clear to need a whole guild.
- Assumed until you answer: a party boss for 4-6 (tuning waits for your answer; task PT5).
- Jay's answer (2026-11-27, asked again because you may test alone or as a pair): "Keep him a raid". So the Axe-Lord stays a fight for a large group (about 8-10 level-30s). RV1 re-measures him with the weapon bonuses working and keeps him at raid size; a solo or pair playtest stops at the Gate Hound or brings Pilot test characters.

### Q77. Normal climbers below level 50 keep their items when they die (2026-11-26, party playtest)
The game has always told young Normal climbers "your death cost you nothing", but from level 22 (when Tibia's free starter blessing ends) a death without blessings dropped the whole backpack and some gear, and the engine still took experience. Both are fixed to match the promise: below level 50 on Normal you keep your experience and your items (the game hands out the blessings for free at each login). Hardcore and Death Game keep their risk. (My call; you can veto.)
- **Recommendation:** keep it. Floor 1 deaths then cost only the walk back; if you want a sting before 50 (your "challenge" goal), say so and I'll make the message and the Registrar say clearly what a death costs instead.
- Assumed until you answer: yes, keep items and experience below 50 on Normal.
- Jay's answer:

### Q76. Looted coins go straight to the bank (2026-11-26, party playtest)
In the party playtest a level-15 tank's backpack was half full of coin stacks and the next purchase failed. I switched on the engine's "coins to the bank" option: gold from monsters goes into your bank account, quest gold too, and shops already take the price from the bank. (My call; you can veto.)
- **Recommendation:** keep it. Less clutter, and nobody loses coins on the floor.
- Assumed until you answer: yes (it is on after the next restart).
- Jay's answer:

### Q75. Should the solo grounds stay this safe for a party, and dying cost nothing below level 50? (2026-11-26, party playtest)
Three test characters went from level 3 to 21 as a party without one death; the first deaths came at the Bandit Road (a group ground), which matches the design. On Normal, dying below level 50 costs no experience ("young climber"), so on Floor 1 a death only costs the walk back.
- **Recommendation:** keep both for now. The solo grounds are meant for one player; a party there is supposed to be comfortable. Your "challenge" lives in the group grounds, caves and bosses. Revisit after your solo playthrough.
- Assumed until you answer: no change.
- Jay's answer:

### Q74. A "share the gold" option for parties? (2026-11-26, party playtest)
Loot goes to whoever gets the kill credit, so the tank ended with 1,250 gold and the healer with 56 (not enough for mana potions). The bank's "transfer 200 to Fern" works, and the Journal now teaches it.
- **Recommendation:** later (after Step 3, per the "nothing new" rule), add a party switch that splits looted gold evenly between nearby members, straight into their banks.
- Assumed until you answer: only the Journal tip for now.
- Jay's answer:

### Q73. Let Bristle Boars come in twos? (2026-11-26, 10.4)
Boar Meadow (levels 9-15) is the one ground that still can't feed a crowd: the measurement gave four hunters only 57-89 kills an hour each (200 is the aim). Boars are "loners" (my call when the spawn habits were set): always alone, never doubled, so the meadow can only grow by adding more single boars, and the danger and rest-spot rules allowed just two more.
- **Recommendation:** make boars a "pair" (ones and twos). The meadow would roughly double without changing its layout, and the Vanguard ground keeps hard hitters that walk up to you. The elite (Old Bristleback) stays alone.
- Other option: keep them loners and add a second small boar ground for levels 9-15.
- Assumed until you answer: no change (boars stay loners).
- Jay's answer:

### Q72. A launch-week crowd boost for the harder hunting grounds? (2026-11-26, N2)
The measurement (docs/N2_capacity.md) says Floor 1 feeds about 30 hunters at once at a good pace, about 9 of them in the
level 9-30 grounds; the launch target is 150. The lead session will make the grounds bigger (10.4). Separately: you
decided the crowd system lets harder grounds grow only to 1.5 times "so good spots stay worth competing for" (Q31). In
the test it added 20-60% when a ground filled up.
- **Recommendation:** keep your rule, and let the bigger map (10.4) do the work. Optionally, for the first week of a
  season only, let the harder grounds grow to 2-3 times, when everyone is on Floor 1 at once.
- Assumed until you answer: no change (your rule stays).
- Jay's answer:

### Q71. Outfit addons: who gives them and what they ask (2026-11-26, 6.5c)
You approved all sixteen addon drawings. Now each one is a quest reward (my calls, you can veto any of them):
- **Who:** Vanguards ask Captain Dorrow, Rangers Hunter Brannoch, Arcanists Vesper, Mystics Fisher Corwin. Say "outfit" to them. A class only gets its own two quests; the second needs the first. At level 14 the game tells each player who to ask.
- **Addon 1** (from level 14 to 17): beat one of Floor 1's six elites, the rare lone leaders (Vanguard: Moonhowl; Ranger: Blackthorn; Arcanist: the Prism Shardling; Mystic: the Mossback Snapper).
- **Addon 2** (from level 19 to 24): a harder job (Vanguard: the Granite Warden; Ranger: 40 bandit crossbowmen; Arcanist: 30 hedge hexers; Mystic: 40 field shardlings).
- Each pays some experience too, and unlocks the addon on both the man's and the woman's outfit.
- **Recommendation:** keep it like this. Elites are rare, so addon 1 is a small hunt of its own, and an addon shows you did it.
- Assumed until you answer: yes.
- **Changed 2026-11-27 (adventure layer, roadmap AD5, my call):** three of the addon 2 jobs were plain kill counts, so they are now a hunt for a named target that comes out after you drop 15 of its kind in its ground (the Journal says so): Ranger: outshoot **Deadeye Sorrel** on Smugglers' Ridge (was 40 crossbowmen); Arcanist: take the book from **the Page-Thief** on the Bandit Road (was 30 hexers); Mystic: calm **Glasswing**, the oldest shardling, in the Shard Fields (was 40 shardlings). If it gets away (10 minutes), 5 more kills call it back. Vanguard's Granite Warden is unchanged. Veto any of them and I put the kill count back.
### Q70. Put the website on a public https:// address now, or wait? (2026-11-26, 7.1b)
The scripts are ready (`windows\Open-Public-Website.bat`, steps in `windows\README.md`): free, through Tailscale Funnel, an address ending in `.ts.net` with a real certificate, no domain to buy. Only the website (sign-up and account pages) goes public; the game itself still needs Tailscale. Anyone on the internet could then make accounts on your PC.
- **Recommendation:** wait until the friends test (9.3) is close; switch it on that day, and off again after. A proper domain name comes with picking a host (10.1).
- Assumed until you answer: wait; nothing is public.
- Jay's answer:

### Q69. Hearthgate's buildings: reshape them, or leave that to the final polish? (2026-11-26, N3)
I dressed Hearthgate (market parasols, goods and a cart by the stalls, flower pots round the Hearth, a well, a covered wagon, braziers at the gates, two campfires, and a notice board in the square with live news: the floor race, the beacon, the weekend bonus, the biggest bounties). What's left of N3 is "varied building shapes": today every house is the same square box. The houses are saved in the database (the game restores their doors on boot), so reshaping them can break owned houses.
- **Recommendation:** leave the houses' shapes to the Cowork polish near the end, as planned; I reshape only the shops and public buildings (an L-shaped inn, a tower over the gate) if you say the town still looks generated after you walk it.
- Assumed until you answer: leave it to the polish.
- Jay's answer:

### Q68. More tutorial gates in the Arrival Yard (cursors, the Journal, skills)? (2026-11-26, P7)
The roadmap asks for three more gates in the yard (learn the cursors, open the Journal, use a skill). Every tester so far has got stuck somewhere in the first 30 minutes, and each new gate is one more place to get stuck.
- **Recommendation:** don't add them until you've played the first hour yourself (R0). If you find yourself not knowing the Journal or the skill keys, I add those two as signs plus one gate.
- Assumed until you answer: no new gates for now.
- Jay's answer:

### Q67. Floors 2-4 are real places now; each has its own twist (2026-11-26, R13b / S6)
Floors 2, 3 and 4 each have eight walled hunting grounds, built like Floor 1's: one training ground beside town, one ground for each class, two mixed, one party ground and party caves, with the apex as the big-group ground. The easiest grounds are next to town, the hardest far north. Each floor has one behaviour the floors below don't (my call):
  - Floor 2: the herd animals (grazers, striders) run when badly hurt and come back once they've recovered.
  - Floor 3: the plant creatures (moss crawlers, husks) regrow if you leave them.
  - Floor 4: Reed Witches mend the monsters around them; kill the witch first.
Also: the walk test in the client found that Floor 2's ordinary monsters were far too strong once a whole loop woke at once (a level 60 test Vanguard died in the level 35-41 ground). Ordinary monsters on Floors 2-10 now hit at 60% of the old numbers; bosses are unchanged.
- **Recommendation:** keep the twists. When you reach Floor 2 in a playtest, tell me whether Grazing Downs feels right for a fresh level 35.
- Jay's answer:

### Q67. Approve the Gate Hound's own corpse? (2026-11-26, art)
You asked for it: Tibia's dead hellhound has three heads but is red, yellow and green, and our hound is slate-blue. Drawn the way Tibia does animal corpses: slumped with its three heads flopped on the ground, gashes and a blood pool, then rotting with the ribs showing, then its three-skulled skeleton. Sheet: `ART_FOR_JAY/gate_hound_corpse.png`.
- **Recommendation:** approve. Until then it keeps the Tibia hellhound corpse.
- Jay's answer (2026-11-26): "Approve it". Installed as N7b.

### Q66. Approve our own corpses for the golem, the Underkeeper and the Vault Wraith? (2026-11-26, art)
Every monster now leaves a body that matches it, using Tibia's own corpses wherever one fits (as you said). Only three of our monsters have nothing in Tibia that works, so I drew theirs the way Tibia draws corpses, from what I learned looking at Tibia's own: the Ruin Sentinel / Granite Warden breaks into its own stone chunks (like a Tibia stone golem), the Underkeeper collapses into a heap of bones, chain and lantern, and the Vault Wraith leaves its robe crumpled beside its strongbox. Each has three steps (fresh, older, last remains). Sheet: `ART_FOR_JAY/corpses_sheet.png` (plain grey).
- **Recommendation:** approve all three. Until you do, they keep the closest Tibia corpse (stone golem, skeleton, wraith).
- Jay's answer (2026-11-26): "Approve all three". Installing them is roadmap N7.

### Q65. I raised the party experience bonus from +30% to +50% per extra member (2026-11-26, S1b)
The new economy model, checked against a real five-character party run, showed that hunting in a party cave paid each member only about 1.25 times what the same player earns hunting that ground alone. DESIGN.md says team hunting must beat solo, and the target for group grounds is 1.5 times. So I changed the bonus (it is marked as my call): a party of four, one of each class, now gets 70% of every kill's experience each (it was 55%). In the party caves that works out to about 1.5 to 1.9 times what a solo hunter earns there (it was about 1.15 to 1.5). Gold is not affected; loot is still split as before.
- **Recommendation:** keep +50%. If parties feel too strong in your playtest, +40% still beats solo (about 1.3 to 1.7 times).
- Your answer: (keep / go back to +30% / other number)

### Q64. The guild official's new look has a beard; the NPC is "Guildwarden Sela" (2026-11-25, art)
You approved the redrawn Guild Warden (navy robe, banner staff, short beard). In the game that job belongs to Guildwarden Sela, who wore a woman's outfit until now.
- **Recommendation (assumed):** Sela wears the approved look now, so no borrowed Tibia look is left on her. If you'd rather keep Sela as a woman, say so and I'll make a beardless version (one short art job); or rename the NPC to fit the art.
- Jay's answer (2026-11-25): "I honestly don't care on the guildmaster". Sela keeps the approved look.

### Q63. Class outfits: only your own class, and for women too? (2026-11-25, art)
Your four approved class outfits are going into the game (task 6.5). My calls:
- each class can wear only its own outfit (Vanguards the Vanguard outfit...), given when you pick the class and put on once; you can still change back to the other outfits. A glance then tells the classes apart in PvP;
- women's characters wear the same outfit until a women's version is made (four more models, next in the art queue if you want them);
- the outfit colours you pick do nothing on these four yet (that needs a colour layer, a later art job).
- **Recommendation:** yes to all three. Also: should every floor's priest and banker share the Hearthgate priest and banker looks, or wait for their own art? I recommend **wait** (each town feels different).
- Jay's answer:

### Q63. Rename the Bristle Boar? (2026-11-25)
You called the red-crested boar the "fire boar" and said "it might be named frenzied boar or just regular boar". It is our Bristle Boar today (Boar Meadow), and it now walks across the website banner.
- **Recommendation:** keep "Bristle Boar" for the common one, and save "Frenzied Boar" for a rarer, angrier red variant later (a money monster vets hunt for), so the name means something.
- Other option: rename the common one to Frenzied Boar now.
- Assumed until you answer: keep Bristle Boar.
- Jay's answer:

### Q62. New rules on the website and sign-up page (2026-11-25)
You asked for the rules and a "not allowed" list on the website. The full rulebook is now on the Rules page, on the sign-up page (players must tick "I agree" before an account is made) and in `docs/RULES.md`, all written from one file. Most of it was already decided; these lines are new, my call:
- no sharing anyone's personal details, no sexual harassment, no advertising other servers or things for sale;
- no pretending to be staff or one of the tower's NPCs; no names of real, well-known people;
- no getting into other people's accounts and no attacking the server;
- no killing your own characters or a friend's to farm bounties, rewards or leaderboard places.
The sign-up page now refuses rude names, names from other games, staff titles (GM, Admin...) and the names of our own NPCs and monsters. Names it can't judge (a famous person, a clever insult) stay a gamemaster's job.
- **Recommendation:** keep them all.
- Assumed until you answer: yes.
- Jay's answer:

### Q54. Launch with 3 finished floors instead of 10? (2026-11-25)
The design says 10 floors at launch. But floors unlock about 6 days apart (the calendar gate), so Floor 4 isn't needed until about week 3 and Floor 10 until about week 8. Ten floors of our own maps and art before launch is most of a year's work; three is a few months.
- **Recommendation:** launch with Floors 1-3 finished to the standard Floor 1 is getting, and add a floor every week or two during the season. Say "new floors every week" instead of "10 floors".
- Other option: keep 10 at launch and accept a much later launch date.
- Assumed until you answer: the design stays at 10, but I work on Floors 1-3 first either way.
- Jay's answer:

### Q55. Drop Hardcore mode? (2026-11-25)
Three difficulty modes split a small population three ways, and Hardcore is the one nobody will talk about: Normal is the game, Death Game is the headline.
- **Recommendation:** two modes, Normal and Death Game. A Death Game character who steps down becomes Normal.
- Other option: keep all three.
- Assumed until you answer: all three stay.
- Jay's answer:

### Q56. Twin Fang and the Fortune Hall (2026-11-25; also Q17 and Q18)
- **Twin Fang** goes to the first 3 characters each season. That is a power prize for the fastest guild, which pulls against your "no bullying" pillar. **Recommendation:** make it a style anyone can earn through the trial (hard, but open), or make it look-only.
- **Fortune Hall** (gambling with gold) is a legal risk once gold can be bought indirectly through shop items sold on the market. **Recommendation:** leave it out of season 1 and decide after talking to a professional (roadmap 7.5).
- Assumed until you answer: both stay as designed; neither gets more work.
- Jay's answer:

### Q57. Shrink crafting to arrows and potions? (2026-11-25)
You said on 23 Nov you're "not a fan of crafting", and the gear path has replaced it for weapons and armour. What's left is four crafters (Fletcher, Alchemist, Runewright, Tailor) and a material from every monster.
- **Recommendation:** keep the Fletcher and Alchemist (special arrows and cheaper potions give monster materials a use, so hunters trade), drop the Tailor's and Runewright's recipes, and cut the house workshop bench and garden (roadmap 3.5b).
- Other options: cut crafting completely (materials just sell to a trader); or keep all of it.
- Assumed until you answer: shrink it as recommended (not built yet; nothing is removed before the friends test).
- Jay's answer:

### Q58. Too many small reward loops (2026-11-25)
A player now has nine things handing out small rewards: hunting tasks, the Season Path, the Spire Chronicle, the daily login streak, the hourly lucky climber, the Tower Quiz, Floor Beacons, the boosted creature of the day and world events. Each has its own command. It reads as clutter, and the review of other servers shows that piles of systems don't hold players (Halera: 50+ systems, about 5 online).
- **Recommendation:** keep the ones you chose (Beacons, Chronicle) plus hunting tasks and world events. Fold the daily streak into the Season Path, and drop the lucky climber, the quiz and the boosted creature, or keep them as rare weekend extras. Show everything on one Journal page (roadmap N5).
- Assumed until you answer: fold as recommended, after the friends test.
- Jay's answer:

### Q59. Switch off big-group events until there are players for them (2026-11-25)
Spire Siege, the arena events and Spire Pressure need dozens of players online. With a handful of testers an event that starts and gets nobody looks worse than no event.
- **Recommendation:** each event starts only when enough people are online (Claude's numbers: arena 8, siege 20). Below that it doesn't announce at all. Nothing is deleted.
- Assumed until you answer: yes.
- Jay's answer:

### Q60. The case against the cavebot on Floor 1 (2026-11-25; you asked for the reasons behind Grok's R5)
The calm hunting grounds you asked for each feed one or two players. With a built-in cavebot and three windows per computer, a few players can hold every spawn on Floor 1 around the clock, and at a season launch everyone needs those spawns the same evening. New players would find every ground taken by characters nobody is playing. That is the strongest version of Grok's argument, and it only bites where grounds are small and everyone is the same level: Floor 1 at launch.
- **Recommendation:** keep the cavebot as you designed it, but it does not work on Floor 1 for the first two weeks of a season, and never in the four starter grounds. Decide again once roadmap N2 has measured how many players Floor 1 really feeds.
- Other options: as designed everywhere; or off on Floor 1 for good.
- Assumed until you answer: as designed (your decision); nothing changes.
- Jay's answer:

### Q61. The new roadmap order (2026-11-25)
ROADMAP.md is now one list: first-hour fixes, finish the last third of Floor 1, then a real party clears Floor 1 (you, with Grok's characters or friends), then make Floor 1 big enough for a launch evening, Floor 2's own map, Hearthgate polish, an art count, website accounts, friends test. **Nothing new gets built until the party run passes.** If you bring a new idea before then, I'll write it under "Later" and tell you so, unless you say it jumps the queue.
- Assumed until you answer: yes.
- Jay's answer:

### Q53. How many game windows can one person run at once? (2026-11-25)
You said multi-clienting is welcome (extra characters, trainers, playing two at once). Today's rule is 2 game windows per computer. With the built-in cavebot, a much higher limit lets one person run a small bot army that floods the market with gold and items.
- **Recommendation:** raise it to **3 per computer**: enough for a main, a helper and a trainer, still not a bot farm. The website count shows real people separately, so nobody is fooled by the numbers.
- Other options: keep 2; or no limit.
- Assumed until you answer: 3.
- Jay's answer:

### Q52. The Arrival Yard levels you too fast (2026-11-25)
Grok: three rats in the pen took a fresh character from level 1 to 4 (Pen Rats give 135 experience at the early 10x rate, plus Pell's 300), so "levels feel meaningless" and a level 3 tip fired in the yard (the tip is fixed).
- **Recommendation:** lower the yard's rewards so a new character leaves the yard at level 2-3 and reaches level 4 (first heal) in the first hunting ground. Floor 1's overall length stays the same.
- Other option: keep it; fast early levels feel good.
- Built 2026-11-25 as recommended: a new character now leaves the yard at level 2 and the Proving at level 3 (checked in the client). Say if you want the old fast start back.
- Jay's answer:

### Q51. The bot panel on a new player's screen (2026-11-24)
Grok (and the playtest task) asked to hide the vBot panel for new players; it looks unfinished. But the design builds bot helpers into our client on purpose (DESIGN.md 11: cavebot at 45% experience), so I left it.
- **Recommendation:** keep it, but start it collapsed for new characters, and later replace it with our own simpler cavebot window. Not urgent.
- Other option: hide it completely until our own cavebot window exists.
- Built 2026-11-25 (the recommendation): the bot panel starts folded once per install; players can unfold it.

### Q48. The Gate Hound now comes back after it dies (2026-11-24)
It used to appear only until the first party killed it, then never again. But the Floor 1 checklist (the gear system you approved) asks every climber to defeat it, and it pays 3 cut Hearth Shards to everyone who helped, so after launch day nobody else could finish that step.
- **Recommendation (built):** it returns 30 minutes after each kill, like the Axe-Lord. The first kill still opens the labyrinth for everyone, once, with the server-wide announcement.
- Other option: keep it one-time and move the "3 cut shards" step to something repeatable.
- Assumed until you answer: it comes back.
- Jay's answer:

### Q47. Floor 1's first impression: rebuild the Arrival Yard and Hearthgate before the alpha? (2026-11-23)
From the overnight Floor 1 review (`FLOOR1_REVIEW.md` sections 2 and 7): the Arrival Yard is a plain rectangle with four wall-gates, and Hearthgate is a strict grid of same-sized buildings. These are the first screenshots any tester or streamer sees.
- **Recommendation:** yes. Rebuild the yard as an arrival at the foot of the tower (sealed Floor 2 gate in view, a plaque of first clears) and give Hearthgate a market square, varied buildings, walking townsfolk and ambient effects, before inviting alpha testers (roadmap P3 and P7).
- Assumed until you answer: yes, do it before the alpha.
- Jay's answer:

### Q46. When should a player make their first style choice? (2026-11-23)
Today the first permanent style choice (Marksman or Trapper, and so on) comes at Mastery 10, around level 37, which is just after Floor 1 ends. An alpha tester who plays only Floor 1 never makes it, and that choice is the most exciting part of the new system.
- **Recommendation:** add a small, free-to-swap "stance" at Mastery 5 (around the Gate Hound) that previews the two paths, so Floor 1 players feel the choice coming. Keep the permanent choice at Mastery 10.
- Other option: move the permanent choice earlier, to about level 30, so it lands on the Axe-Lord.
- Assumed until you answer: the free stance at Mastery 5.
- Jay's answer:

### Q45. A spear for Rangers' barracks weapon? (2026-11-23)
Captain Dorrow's level 10 weapon comes in bow or crossbow for Rangers, not spear: in this engine thrown spears are used up or drop on the target, so a tiered spear would be lost on the first throw. **My recommendation: keep bow and crossbow.** If you want spears, I can make a non-thrown spear later.
Jay's answer:

### Q44. Answered 2026-11-17: spells in PvP
Jay chose the proven Tibia core for controlling players plus his counter system as terrain (vine walls that fire
burns, a barrier rune, party haste, wall-breaking arrows), with full-chaos "Wild PvP" as a weekly arena event first.
Written into `DESIGN.md` 6.7 and built the same day. Also assumed (Claude's recommendations, Jay picked "yes, build
it"): Undying Oath works against players, Lifeseed only against monsters, the barrier rune is the Arcanist's only.

### Q43. The new spells: Elemental Clash, and spells that move monsters (2026-11-17)
Every class now has 28 to 31 of its own spells (was 17 to 19), with new kinds: chains, knock-backs and pulls, roots,
burning ground, meteors that are marked on the ground a second before they land, and a 15-second "form" at level 230.
Two things to judge while playing:
1. **Elemental Clash**: hitting a monster with two different elements in a row (say fire, then lightning) does 25% more
   and the monster shouts the clash's name ("Flashfire!"). Recommendation: keep; it makes mixed groups stronger.
2. **Pushing and pulling monsters** (Shield Bash, Iron Reach, Repulse, Gravity Well, Recoil Shot...). Bosses can't be
   moved. Recommendation: keep; if it makes hunting too easy, the first fix is longer cooldowns.
- Assumed until you answer: keep both.
- Jay's answer:

### Q42. Reed Snapper: a snapping turtle, not a turtle-crab? (2026-11-15)
You said the Reed Snapper "looks like a mix between a crab and a turtle". The original request asked for a "turtle-crab", which is why it had crab pincers. I rebuilt it as one animal: a spiked snapping turtle with a reed-covered shell and a hooked beak, no pincers. It keeps a low, wide, sideways scuttle as its only crab trait.
- **Recommendation:** keep it as a snapping turtle. If you want a crab instead, I would make it a full crab with a mossy shell rather than mixing the two again.
- Assumed until you answer: snapping turtle.

*Q13–Q25 come from the full review (`REVIEW.md` section B). Section numbers point into that file.*

### Q42. Which Floor 1 ground is for which class, and party size 8 (2026-11-16)
From the new spawn rules (`DESIGN.md` 9.4). My picks: the Ratwarren, Toad Pond and Sproutling Glade are the all-class training grounds; Boar Meadow suits the Vanguard, Reedmarsh the Ranger, Waspgrass Fields the Arcanist, Thornsnap Hollow the Mystic; Burrow Hills, Wolf Copse and Shard Fields are mixed; the party caves, the bandit Vault and the lower Quarry are for groups of 3 to 4; the Old Watchtower's inner room and cave is the one ground for 4 to 8. I also raised the party size from 6 to 8 so those 8 can share experience. Recommendation: go with these; tell me any you want swapped.

### Q41. The starter grounds keep most of their monsters on the level below (2026-11-14)
To meet the calm rules (at most 3 monsters able to reach you near the gate, 4 further in), the open-air part of Toad Pond, Sproutling Glade and Waspgrass Fields now holds about 12 monsters each, spread out with quiet stretches between. The other ~36 of each ground are in the cave (or on the hill) below, where they come in pairs and threes. The Ratwarren already works this way. Recommendation: keep it. The surface is the gentle, safe part for new players, and you choose to go down when you want more. If the surface feels too empty when you try it, I can add a few more singles there.

### Q33. Do the walled hunting grounds look the way you want? (2026-11-13)
Every ground is now a walled place with ring trails (see the playtest list in WEEKLY_REPORT.md). Up close they read like a wood or a rocky field; from far away they look a little like a hedge maze, because the loops are regular.
- Recommendation: keep the skeleton (it is what makes botting and sharing work) and let the end-of-project Cowork polish break up the outlines by hand.
- Jay's answer:

### Q34. Taskmaster names, and how the coins change (2026-11-13)
Floors 2-10 needed taskmaster names: Doral, Ilsa, Varn, Kesh, Brenna, Otho, Sigra, Marlo, Quillan (Floor 2 to 10). Using a coin stack changes every full 100 up and leaves the rest; using a crystal coin breaks it into 100 platinum. A small platinum stack no longer breaks into gold (shops give change anyway).
- Recommendation: keep both as built. Rename any taskmaster you like; it is a one-line change.
- Jay's answer:

### Q35. How many hunting tasks at once? (2026-11-13)
The new task window lists every monster on the floor (25 on Floor 1, 8 on the others), but you can hold one task at a time, and each task comes back 20 hours after you finish it.
- Recommendation: keep one at a time for now; if it feels slow in playtests, allow three.
- Jay's answer:

### Q36. Spell overhaul: balance to check in playtests (2026-11-13)
All four vocations have a new spell list (docs/design/spells.md). Things to judge while playing:
1. Vanguard has no area spell until level 33 (Whirlwind, weak on purpose, like Tibia's knight). Recommendation: keep; if levelling feels too slow, move Whirlwind to 25 before raising its damage.
2. The Ranger's Scatter Shot is the strongest early area spell (the Ranger is meant to be the easiest class to level alone). Recommendation: keep.
3. Making runes now uses up a blank rune (10 gold), as the economy model always assumed. Recommendation: keep.
4. The runes themselves still carry the engine's item names (for example "great fireball rune"). Recommendation: rename them to Spirebound names in a later task.
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
- *Built 2026-11-13 (R21) as recommended: 22%.*
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
- *Updated 2026-11-25 (N4, full count in `ART_COUNT.md`): Floors 1-3 show about 900 borrowed looks (65 monster kinds, 47 NPCs, the outfits, 142 items, 79 wall pieces, 42 grounds, 186 map objects, about 100 effects); about 265 hours to make them all. New recommendation: mix. Keep making everything that moves (monsters, NPCs, outfits, mounts) with the Blender pipeline and effects with our effect maker (about 100 hours). For the still world (ground, walls, map objects: about 300 looks, about 100 hours) start from the OpenTibia Sprite Pack, the one open-licence Tibia-style pack (free with credit to the artists, Creative Commons Attribution 4.0). It is small and old, so first check which of our 300 map looks it covers, then make the gaps in a matching style. Items: Grok or Claude still renders, either works.*
- Jay's answer:

### Q22. Friends test: Floors 1–2 only? [9.2 of review]
- **Recommendation:** yes. Seal Floors 3–10, switch off arena, siege, shop and Season Path for the test. Wipe after.
- *Built 2026-11-13 (R13) as recommended. You can switch it in game: `/scope test` or `/scope launch`.*
- *Changed 2026-11-23 (Claude, from the Floor 1 review): the Season Path is now ON for the test. Its daily and weekly goals are the "what do I do today" loop testers should try.*
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

### Q50. A first fight as your new class within minutes (2026-11-24)
Grok spent an hour without one kill as a Mystic: after the Registrar there is no next step, just "go hunt".
- **Recommendation (assumed, roadmap G2):** the Registrar's last line starts a tiny "First hunt" quest: kill 5 monsters at the Ratwarren (next to the west gate) with your new spells, report to Captain Dorrow for a small reward. The temple sign points the way.
- Other option: a practice dummy or a small pen right outside the temple, before any walking.
- **Jay's answer (2026-11-24):** "a small one person boss fight. you decide how should all go." Also yes to continuing the tutorial after picking a class (G2).

### Q49. The first levels come very fast (2026-11-24)
Grok reached level 5 in the rat pen in about 12 minutes and felt the levels meant little. The experience rate (25x below level 51) is your setting from the design, so I have not touched it.
- **Recommendation:** keep it for now and judge it in your next playtest; if it feels too fast, lower only the Arrival Yard's rats.
- **Jay's answer (2026-11-24):** "i honestly am not sure on the xp rate." Kept as it is; Claude's recommendation stands: judge it in the next playtest (Jay's or Grok's rerun) and lower only the Arrival Yard if it still feels too fast.

### Spawn rules: habits, ground types, the floor recipe (2026-11-16)
Jay: "yep i like the idea so far." Group size: "that is good but we should also create an occasional hunting ground that can support 4-8 players." One high-level player soloing a group ground: "yes". Written into `DESIGN.md` 9.4 and `FLOOR1_HUNTING_PLAN.md` Part 10. This also settles Q41: how many monsters stand on a starter ground's surface now follows from each monster's habit.

### Q40. Should Field Rats be able to hurt a brand-new vanguard? (2026-11-14)
The test autopilot played the Ratwarren with a fresh level 2 vanguard (sword and the starting wooden shield). Four rats stood next to it for half a minute and it never lost a single hit point: the shield blocked every bite. Rangers, arcanists and mystics have no shield and will take some damage. Recommendation: keep it. It's the very first ground, and in the original game rats barely scratch a knight too. The danger starts at Toad Pond. If you'd like rats to bite a little, I'd raise their bite slightly rather than add more rats.
- Jay's answer (2026-11-14): "q40 is a game logic question. you would know better on that one than me." Decided: keep it. Rats stay harmless to a shielded vanguard; the other classes still take bites, and real danger starts at Toad Pond and Burrow Hills.

### Q37. Cavebot on the new solo cave and hill levels? (2026-11-14, from FLOOR1_HUNTING_PLAN.md)
You said yes to "no cavebot in caves" (Q32) when every cave was a party cave. The new plan gives most grounds extra levels meant for solo hunting (tunnels, hilltops), with the party cave as the deepest level.
- **Recommendation:** allow the cavebot (with its usual penalty) on every solo level; keep refusing it in the party caves only.
- Jay's answer (2026-11-14): "ill go with your recommendations on the question."

### Q38. Which hunting areas felt fine? (2026-11-14)
You wrote "certain areas are fine but the whole spawn shouldn't be a massive swarm."
- **Recommendation (assumed):** the party caves and the Old Watchtower's inner room stay packed; each route may end in one marked dead-end "nest" of 4 or 5; everything else calms down. Tell me if a particular ground already felt right and I will keep its feel.
- Jay's answer (2026-11-14): "ill go with your recommendations on the question."

### Q39. Try two pilot grounds before the rest are rebuilt? (2026-11-14)
The Ratwarren (a yard above, a warren below) and Burrow Hills (hills, a plateau, tunnels, a party cave) get rebuilt first.
- **Recommendation:** yes, play those two and write notes in PLAYTEST.md. The builder carries on with the other ten meanwhile and applies your notes as they arrive.
- Jay's answer (2026-11-14): "ill go with your recommendations on the question."

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
