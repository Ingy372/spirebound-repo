# Spell test in the real client, 2026-11-17 (tasks J13b and J14)

Every spell of every vocation cast by a level 300 tester through the autopilot (`python tools/spell_routes.py`, then `python tools/autopilot.py spells_<vocation>`), with six sturdy Bristle Boars around it. Each line is what the server saw 2.5 s after the cast (`/pilot trace`): monsters hit and total damage, monsters gone, monsters that moved (knock-backs, pulls and ordinary walking), and the caster's health change (boars hit back between casts, so heals can show as a loss).

Results: 142 spells, all cast. Refused only where the place forbids it: Skystep needs a gap in the floor (none at the test spot); Blink, Firewake, Hawk's Path and Disengage were blocked by trees or boars in the way and were then cast on the open road (`spells_dashes`): Blink moved 3 tiles, Firewake 4 with a burning trail; Charge was refused while already next to its target and works from a few tiles away (`spells_dashes_vanguard`). Worldfire's line is missing from the second run because the tester logged out before the trace was written; in the first run it hit 6 monsters for 5789.

Bug found and fixed by this test: ally spells (Mend Other, Field Dressing, Rejuvenate, Lifeward, Bloomburst, Linked Mend, Lifeseed) refused to cast on yourself without typing a name.

```
 Spell Arcanist | Ember Strike | CAST: hit 1 monsters for 205, 0 gone, 2 moved, your health -47 
 Spell Arcanist | Kindle | CAST: hit 1 monsters for 15, 0 gone, 0 moved, your health -41 
 Spell Arcanist | Mending Spark | CAST: hit 1 monsters for 25, 0 gone, 1 moved, your health -8 
 Spell Arcanist | Wayfinder | CAST: hit 1 monsters for 14, 0 gone, 4 moved, your health -48 
 Spell Arcanist | Cleanse | CAST: hit 1 monsters for 12, 0 gone, 2 moved, your health -29 
 Spell Arcanist | Skystep | REFUSED: hit 1 monsters for 15, 0 gone, 4 moved, your health -63 
 Spell Arcanist | Volt Strike | CAST: hit 1 monsters for 203, 0 gone, 2 moved, your health -48 
 Spell Arcanist | Hearth Ration | CAST: hit 1 monsters for 10, 0 gone, 1 moved, your health -25 
 Spell Arcanist | Mana Ward | CAST: hit 1 monsters for 31, 0 gone, 4 moved, your health +0 
 Spell Arcanist | Quickstep | CAST: hit 1 monsters for 13, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Forked Arc | CAST: hit 4 monsters for 470, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Fireburst Wave | CAST: hit 1 monsters for 273, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Ember Barrage | CAST: hit 1 monsters for 506, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Arc Beam | CAST: hit 2 monsters for 254, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Gale Step | CAST: hit 1 monsters for 27, 0 gone, 0 moved, your health +0 
 Spell Arcanist | Conjure Fire Rune | CAST: hit 1 monsters for 20, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Blink | REFUSED: hit 1 monsters for 14, 0 gone, 1 moved, your health +0 
 Spell Arcanist | Emberfield | CAST: hit 3 monsters for 922, 0 gone, 0 moved, your health +0 
 Spell Arcanist | Searing Brand | CAST: hit 3 monsters for 874, 0 gone, 0 moved, your health +0 
 Spell Arcanist | Repulse | CAST: hit 7 monsters for 1328, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Gravity Well | CAST: hit 2 monsters for 59, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Conjure Strike Rune | CAST: hit 2 monsters for 37, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Summon Ember Sprite | CAST: hit 1 monsters for 34, 0 gone, 0 moved, your health +0 
 Spell Arcanist | Stormcall | CAST: hit 7 monsters for 2304, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Arcane Empower | CAST: hit 1 monsters for 13, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Skybrand | CAST: hit 5 monsters for 2316, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Inferno Core | CAST: hit 9 monsters for 3637, 0 gone, 3 moved, your health +0 
 Spell Arcanist | Firewake | REFUSED: hit 1 monsters for 26, 0 gone, 2 moved, your health +0 
 Spell Arcanist | Cinder Lance | CAST: hit 1 monsters for 562, 0 gone, 4 moved, your health +0 
 Spell Arcanist | Meteor Rain | CAST: hit 7 monsters for 3400, 0 gone, 4 moved, your health +0 
 Spell Arcanist | Arc Cataclysm | CAST: hit 2 monsters for 423, 0 gone, 4 moved, your health +0 
 Spell Arcanist | Storm Lash | CAST: hit 7 monsters for 2769, 0 gone, 13 moved, your health +0 
 Spell Arcanist | Stormheart | CAST: hit 5 monsters for 1201, 0 gone, 11 moved, your health +0 
 Spell Arcanist | Mirror Image | CAST: hit 5 monsters for 1028, 0 gone, 7 moved, your health +0 
 Spell Mystic | Frost Strike | CAST: hit 1 monsters for 228, 0 gone, 1 moved, your health -20 
 Spell Mystic | Kindle | CAST: hit 1 monsters for 11, 0 gone, 0 moved, your health -49 
 Spell Mystic | Dewfall | CAST: hit 1 monsters for 23, 0 gone, 2 moved, your health -27 
 Spell Mystic | Cleanse | CAST: hit 1 monsters for 15, 0 gone, 2 moved, your health -21 
 Spell Mystic | Wayfinder | CAST: hit 1 monsters for 10, 0 gone, 3 moved, your health -47 
 Spell Mystic | Hearth Ration | CAST: hit 1 monsters for 18, 0 gone, 3 moved, your health -66 
 Spell Mystic | Sapdrain | CAST: hit 1 monsters for 165, 0 gone, 2 moved, your health -17 
 Spell Mystic | Skystep | REFUSED: hit 1 monsters for 15, 0 gone, 0 moved, your health -20 
 Spell Mystic | Thorn Strike | CAST: hit 1 monsters for 237, 0 gone, 3 moved, your health -16 
 Spell Mystic | Quickstep | CAST: hit 1 monsters for 18, 0 gone, 2 moved, your health -36 
 Spell Mystic | Mend Other | CAST: hit 1 monsters for 11, 0 gone, 1 moved, your health -22 
 Spell Mystic | Hailshards | CAST: hit 1 monsters for 403, 0 gone, 3 moved, your health -48 
 Spell Mystic | Frost Wave | CAST: hit 2 monsters for 197, 0 gone, 0 moved, your health -47 
 Spell Mystic | Conjure Healing Rune | CAST: hit 1 monsters for 9, 0 gone, 3 moved, your health -46 
 Spell Mystic | Bramble Patch | CAST: hit 2 monsters for 684, 0 gone, 3 moved, your health -23 
 Spell Mystic | Purify | CAST: hit 3 monsters for 592, 0 gone, 2 moved, your health -37 
 Spell Mystic | Bloomburst | CAST: hit 6 monsters for 711, 0 gone, 3 moved, your health -26 
 Spell Mystic | Barkskin | CAST: hit 1 monsters for 17, 0 gone, 3 moved, your health -27 
 Spell Mystic | Mass Mend | CAST: hit 1 monsters for 12, 0 gone, 2 moved, your health -14 
 Spell Mystic | Rimebind | CAST: hit 1 monsters for 207, 0 gone, 0 moved, your health -39 
 Spell Mystic | Rejuvenate | CAST: hit 1 monsters for 9, 0 gone, 2 moved, your health +20 
 Spell Mystic | Tidecrash | CAST: hit 2 monsters for 350, 0 gone, 0 moved, your health -9 
 Spell Mystic | Conjure Binding Rune | CAST: hit 1 monsters for 33, 0 gone, 2 moved, your health +12 
 Spell Mystic | Summon Wolf Companion | CAST: hit 1 monsters for 21, 0 gone, 1 moved, your health -9 
 Spell Mystic | Thornfield | CAST: hit 6 monsters for 1814, 0 gone, 0 moved, your health -11 
 Spell Mystic | Linked Mend | CAST: hit 1 monsters for 14, 0 gone, 16 moved, your health -39 
 Spell Mystic | Lifeward | CAST: hit 1 monsters for 11, 0 gone, 10 moved, your health -40 
 Spell Mystic | Lifeseed | CAST: hit 1 monsters for 28, 0 gone, 6 moved, your health -34 
 Spell Mystic | Glacier Core | CAST: hit 8 monsters for 2709, 0 gone, 9 moved, your health -32 
 Spell Mystic | Icefall | CAST: hit 8 monsters for 2492, 0 gone, 6 moved, your health -95 
 Spell Mystic | Verdant Renewal | CAST: hit 1 monsters for 28, 0 gone, 6 moved, your health -11 
 Spell Mystic | Wellspring | CAST: hit 1 monsters for 13, 0 gone, 10 moved, your health -15 
 Spell Mystic | Mana Bloom | CAST: hit 1 monsters for 16, 0 gone, 19 moved, your health +12 
 Spell Mystic | Overgrowth | CAST: hit 8 monsters for 2904, 0 gone, 18 moved, your health -9 
 Spell Mystic | Wildheart | CAST: hit 1 monsters for 17, 0 gone, 8 moved, your health +0 
 Spell Mystic | Winter's Breath | CAST: hit 8 monsters for 4838, 0 gone, 15 moved, your health +3 
 Spell Mystic | Worldroot | CAST: hit 1 monsters for 10, 0 gone, 9 moved, your health -7 
 Spell Ranger | Piercing Shot | CAST: hit 1 monsters for 193, 0 gone, 1 moved, your health -41 
 Spell Ranger | Wayfinder | CAST: hit 1 monsters for 118, 0 gone, 2 moved, your health -23 
 Spell Ranger | Kindle | CAST: hit 1 monsters for 225, 0 gone, 1 moved, your health -40 
 Spell Ranger | Field Dressing | CAST: hit 0 monsters for 0, 0 gone, 3 moved, your health +13 
 Spell Ranger | Quickstep | CAST: hit 1 monsters for 139, 0 gone, 0 moved, your health -19 
 Spell Ranger | Cleanse | CAST: hit 1 monsters for 114, 0 gone, 2 moved, your health -29 
 Spell Ranger | Double Nock | CAST: hit 1 monsters for 515, 0 gone, 2 moved, your health -10 
 Spell Ranger | Skystep | REFUSED: hit 0 monsters for 0, 0 gone, 2 moved, your health -20 
 Spell Ranger | Keen Sight | CAST: hit 1 monsters for 444, 0 gone, 1 moved, your health -24 
 Spell Ranger | Hearth Ration | CAST: hit 1 monsters for 198, 0 gone, 4 moved, your health -26 
 Spell Ranger | Scatter Shot | CAST: hit 1 monsters for 325, 0 gone, 1 moved, your health -32 
 Spell Ranger | Recoil Shot | CAST: hit 1 monsters for 312, 0 gone, 3 moved, your health -25 
 Spell Ranger | Snare | CAST: hit 1 monsters for 205, 0 gone, 4 moved, your health -43 
 Spell Ranger | Ambush Shot | CAST: hit 1 monsters for 428, 0 gone, 1 moved, your health -2 
 Spell Ranger | Disengage | REFUSED: hit 1 monsters for 62, 0 gone, 1 moved, your health -8 
 Spell Ranger | Tracker's Mark | CAST: hit 1 monsters for 396, 0 gone, 1 moved, your health -43 
 Spell Ranger | Caltrops | CAST: hit 1 monsters for 169, 0 gone, 4 moved, your health -12 
 Spell Ranger | Swift Foot | CAST: hit 1 monsters for 120, 0 gone, 2 moved, your health -17 
 Spell Ranger | Ricochet | CAST: hit 4 monsters for 760, 0 gone, 1 moved, your health -10 
 Spell Ranger | Radiant Shot | CAST: hit 1 monsters for 420, 0 gone, 1 moved, your health -32 
 Spell Ranger | Mercy Shot | CAST: hit 1 monsters for 234, 0 gone, 2 moved, your health -12 
 Spell Ranger | Sunburst Volley | CAST: hit 4 monsters for 879, 0 gone, 0 moved, your health -8 
 Spell Ranger | Camouflage | CAST: hit 1 monsters for 65, 0 gone, 3 moved, your health +0 
 Spell Ranger | Eagle Eye | CAST: hit 1 monsters for 15, 0 gone, 7 moved, your health +0 
 Spell Ranger | Rapid Volley | CAST: hit 1 monsters for 683, 0 gone, 6 moved, your health +0 
 Spell Ranger | Sanctified Ground | CAST: hit 1 monsters for 3, 0 gone, 14 moved, your health +0 
 Spell Ranger | Falling Star | CAST: hit 5 monsters for 1535, 0 gone, 10 moved, your health +0 
 Spell Ranger | Dawnpiercer | CAST: hit 2 monsters for 356, 0 gone, 9 moved, your health -28 
 Spell Ranger | Scatterwind | CAST: hit 6 monsters for 821, 1 gone, 17 moved, your health -13 
 Spell Ranger | Hunter's Focus | CAST: hit 1 monsters for 8, 0 gone, 5 moved, your health -16 
 Spell Ranger | Hawk's Path | REFUSED: hit 1 monsters for 48, 0 gone, 9 moved, your health -14 
 Spell Ranger | Pinning Volley | CAST: hit 3 monsters for 497, 0 gone, 5 moved, your health -15 
 Spell Ranger | Lightrain | CAST: hit 8 monsters for 2769, 0 gone, 5 moved, your health -27 
 Spell Ranger | Dawnstrider | CAST: hit 3 monsters for 434, 1 gone, 6 moved, your health -64 
 Spell Ranger | Volley of Dawn | CAST: hit 8 monsters for 4681, 1 gone, 12 moved, your health -41 
 Spell Ranger | Constellation | CAST: hit 8 monsters for 4540, 0 gone, 2 moved, your health -22 
 Spell Vanguard | Heavy Strike | CAST: hit 1 monsters for 348, 0 gone, 2 moved, your health -5 
 Spell Vanguard | Wayfinder | CAST: hit 1 monsters for 149, 0 gone, 0 moved, your health -3 
 Spell Vanguard | Second Wind | CAST: hit 1 monsters for 252, 0 gone, 2 moved, your health -8 
 Spell Vanguard | Kindle | CAST: hit 1 monsters for 104, 0 gone, 0 moved, your health -27 
 Spell Vanguard | Cleanse | CAST: hit 1 monsters for 62, 0 gone, 1 moved, your health -12 
 Spell Vanguard | Shield Bash | CAST: hit 1 monsters for 292, 0 gone, 1 moved, your health -19 
 Spell Vanguard | Hearth Ration | CAST: hit 1 monsters for 100, 0 gone, 1 moved, your health -20 
 Spell Vanguard | Skystep | REFUSED: hit 1 monsters for 152, 0 gone, 0 moved, your health -1 
 Spell Vanguard | Quickstep | CAST: hit 1 monsters for 251, 0 gone, 1 moved, your health -15 
 Spell Vanguard | Rending Blow | CAST: hit 1 monsters for 298, 0 gone, 4 moved, your health -10 
 Spell Vanguard | Rally Cry | CAST: hit 1 monsters for 109, 0 gone, 1 moved, your health -21 
 Spell Vanguard | Iron Reach | CAST: hit 1 monsters for 154, 0 gone, 1 moved, your health -33 
 Spell Vanguard | Charge | REFUSED: hit 1 monsters for 180, 0 gone, 0 moved, your health +0 
 Spell Vanguard | Bloodoath Strike | CAST: hit 1 monsters for 345, 0 gone, 2 moved, your health -6 
 Spell Vanguard | Iron Hide | CAST: hit 1 monsters for 326, 0 gone, 2 moved, your health -9 
 Spell Vanguard | Whirlwind | CAST: hit 6 monsters for 963, 0 gone, 4 moved, your health -16 
 Spell Vanguard | Counterguard | CAST: hit 3 monsters for 126, 0 gone, 1 moved, your health -17 
 Spell Vanguard | Intimidate | CAST: hit 3 monsters for 145, 0 gone, 3 moved, your health -13 
 Spell Vanguard | Sunder | CAST: hit 1 monsters for 289, 0 gone, 2 moved, your health -27 
 Spell Vanguard | Battle Hymn | CAST: hit 1 monsters for 131, 0 gone, 5 moved, your health -7 
 Spell Vanguard | Standard of Defiance | CAST: hit 1 monsters for 183, 0 gone, 0 moved, your health -28 
 Spell Vanguard | Guardian Stance | CAST: hit 1 monsters for 72, 0 gone, 1 moved, your health -14 
 Spell Vanguard | Recovery | CAST: hit 1 monsters for 198, 0 gone, 1 moved, your health -27 
 Spell Vanguard | Vault Strike | CAST: hit 1 monsters for 399, 0 gone, 2 moved, your health -3 
 Spell Vanguard | Skyrend | CAST: hit 1 monsters for 613, 0 gone, 2 moved, your health -19 
 Spell Vanguard | Iron Will | CAST: hit 1 monsters for 166, 0 gone, 9 moved, your health -31 
 Spell Vanguard | Last Bastion | CAST: hit 1 monsters for 142, 0 gone, 11 moved, your health -12 
 Spell Vanguard | Final Verdict | CAST: hit 1 monsters for 505, 0 gone, 12 moved, your health -10 
 Spell Vanguard | Bulwark Aura | CAST: hit 1 monsters for 226, 0 gone, 13 moved, your health -28 
 Spell Vanguard | Faultline | CAST: hit 2 monsters for 304, 0 gone, 12 moved, your health -26 
 Spell Vanguard | Undying Oath | CAST: hit 1 monsters for 80, 0 gone, 10 moved, your health -20 
 Spell Vanguard | Aegis Ascendant | CAST: hit 1 monsters for 87, 0 gone, 9 moved, your health -29 
 Spell Vanguard | Unbroken Line | CAST: hit 1 monsters for 210, 0 gone, 11 moved, your health -22 
 Spell Vanguard | Mountainbreaker | CAST: hit 1 monsters for 823, 0 gone, 11 moved, your health -12 
 
 141 casts traced, 9 refused
 Spell Arcanist | Blink | CAST: hit 0 monsters for 0, 0 gone, 0 moved, your health +0 moved you 3 tiles 
 Spell Vanguard | Charge | CAST: hit 1 monsters for 279, 0 gone, 0 moved, your health +0 moved you 1 tiles 
 Spell Arcanist | Blink | CAST: hit 0 monsters for 0, 0 gone, 2 moved, your health +0 moved you 3 tiles 
 Spell Arcanist | Firewake | CAST: hit 0 monsters for 0, 1 gone, 1 moved, your health +0 moved you 4 tiles 
```
