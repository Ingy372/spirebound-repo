# What the top Open Tibia servers have in common (second pass, 2026-11-11)

Jay asked (2026-11-11): *"research the top 5-10 tibia ots and examine what systems they have in common (minigames,
transportation systems, pvp, gear, houses, premium systems, any patterns at all)"*. The first pass is
`RESEARCH_TOP_SERVERS_2026-11.md` (RubinOT, Aurera Global, Cyleria, Baiak-Ilusion, Gunzodus) and DESIGN.md section 15.
This pass adds who is biggest right now and the areas the first pass skipped.

## Who is biggest right now
Live lists disagree, so treat the numbers as a rough guide.

| Server | Style | Players (source, date) |
|---|---|---|
| RubinOT (17 worlds) | 15.x real map, low rates, store | about 10,400 across all worlds ([TibiaServers](https://tibiaservers.com/), 1 Nov 2026) |
| Best-Baiak | 8.60 high rate, events every hour, VIP | about 1,700 to 3,900 depending on the list ([OTServList](https://otserv-list.com/), [otservlist.com](https://otserverslist.com/)) |
| Streamy z Nadinem | Polish, real map, streamer-run | about 2,600 ([Nostalgic.gg](https://nostalgic.gg/en/blog/top-10-tibia-servers-2026-en)) |
| Miracle 7.4 | classic 7.4, 1x | about 1,700 ([Nostalgic.gg](https://nostalgic.gg/en/blog/most-popular-tibia-private-servers-2026-en)) |
| Ezodus | 10.00 hardcore PvP, castle war event | 600+ on its new world ([OTLand thread](https://otland.net/threads/france-10-00-15-22-start-20th-february-2026-18-00-castle-war-event-tc-rl-trade-allowed-unhallowed-crypt-weapon-proficiency-bloodfire-g.268643/)) |
| Halera | 10.98 custom client: boss gates, battle pass, item fusion | small but well known ([OTLand](https://otland.net/threads/otservers-crafting-the-ultimate-open-tibia-experience.292559/)) |
| Gunzodus, Cyleria, Aurera | covered in the first pass | |

## Patterns, area by area
Each item notes which servers have it, and whether Spirebound has it yet (✅ have, 🟡 partly, ❌ missing).

### Minigames and events
- **Hourly or scheduled automatic events.** Baiak-style servers run one every hour: last man standing, zombie, snowball fight, capture the flag, battlefield, quiz in the help channel. Real-map servers run fewer and bigger ones. 🟡 We have world events every 3 hours plus the arena and siege, but no small "everyone joins for ten minutes" games.
- **Castle or territory war** at least weekly (Ezodus, Baiak, RubinOT, Gunzodus). ✅ Spire Siege.
- **Casino and dice.** A dice NPC or house tables, with the house keeping a cut. ✅ Fortune Hall.
- **Fishing, mining, lottery.** Fishing is everywhere; mining and a daily lottery are common on custom servers. 🟡 Fishing only.
- **Treasure hunts and riddles.** Hidden quests, rewards for finding things. ✅ Secrets.

### Getting around
- **Boats, carpets and carriages** between towns for a small gold fee: universal on real-map servers, and it doubles as a gold sink. 🟡 New today: carriages between Hearthgate and Millcross.
- **A teleport hub** in the main temple with a teleporter to each hunting area or city (Baiak style, sometimes VIP-only for far areas). ❌ Our answer is the floor teleports. A paid "return to the last floor's town" scroll is a common convenience.
- **Mounts.** Speed plus showing off, and almost always the most popular store item. 🟡 Mounts exist in Canary; ours are placeholders (ART_REQUESTS).
- **Temple scroll or home rune.** Many servers sell a "teleport to temple" item, out of combat only. ❌

### PvP
- **Frag and skull systems with clear rules** on every server. ✅
- **War systems:** guild-war declarations with kill limits and a fee. ✅
- **A safe PvP arena** for duels with no death loss. ✅
- **Fixed-gear event PvP** so level gaps don't matter. ✅ Equal-footing arena events.
- **Bounties** on red-skulled players. ✅

### Gear
- **Upgrade or forge systems** on almost every custom server (item +1 to +10, fusion, tiers, "Exaltation Forge" on 15.x). ❌ This is the biggest item gap. Canary ships the Forge (tiers and fusion), so we can switch it on.
- **Imbuements, or socket gems** (real-map 15.x servers). ❌ Canary has imbuements. Worth switching on later, because they are a steady sink for monster loot that players trade.
- **Set bonuses and rarity tiers** (common, rare, epic, legendary drops). 🟡 Rare-drop highlight is planned.
- **Weapon proficiency** (Ezodus 2026, a 15.x feature). ❌ Later.

### Houses
- **House auctions** by bidding (real-map) or a direct buy with a gold price (custom). ✅ Direct buy with a head start.
- **Premium or VIP-only houses:** a small set of the best houses can only be owned by VIP or premium accounts. ❌
- **Store-only "donation houses" or guild halls** on several Baiak-style servers: a big decorated house that comes from the store. ❌ This is Jay's Spire Manor.
- **Display features:** mannequins, item pedestals, trophy walls, house teleports, exercise dummies. 🟡 We have exercise dummies and house portals; display pedestals are missing.

### Premium and VIP
Almost every server sells some form of premium time. Its contents fall into two camps.
- **Pay-to-win camp** (Baiak-style): extra XP, extra loot and VIP-only hunting areas. This is the most common reason players give for quitting.
- **Fair camp** (real-map style): convenience only. Typical perks are more depot space, faster stamina regeneration, the right to own a house, VIP travel discounts, a daily reward chest, and access to the store's cosmetics.
- **Spirebound (DESIGN 11):** cosmetics and convenience only, with no XP or loot boosts. ✅ Same as the fair camp.

### Other patterns
- **Daily login reward or daily task.** ✅ Season Path.
- **Tasks, bestiary, bosstiary.** ✅
- **Boosted creature of the day** (extra XP and loot from one monster). ❌ Cheap to add, and it moves players around the map.
- **Autoloot** (free on most servers now). 🟡 Planned.
- **Loot and exp analyzers.** ✅ Client.

## What this means for Spirebound
Ranked by value for effort. **(Claude's call, Jay can veto)**
1. **Economy loop (doing now, step 5):** NPC buy-back prices low enough that player trade pays more; supplies as a steady sink; useful materials from monsters that players need.
2. **Spire Manor (doing now, step 3):** the store-only showcase house, with display pedestals, a trophy hall, a rooftop terrace, a private portal and a private training room. Cosmetic only, no stat bonuses.
3. **Boosted creature of the day:** small and moves players around. Added to the roadmap.
4. **Forge / upgrade system:** switch on Canary's forge for Floor 3 and up. Added to the roadmap.
5. **Ten-minute mini events** (snowball, quiz, last man standing at fixed gear) between the bigger events. Added to the roadmap.
6. **Temple scroll** (out of combat, cooldown), sold by the Runewright as a small gold sink. Added to the roadmap.
