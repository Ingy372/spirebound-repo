"""Floors 2-10 content spec (DESIGN.md 3.1). One place for names, biomes and monster rosters.
Read by maps/layout_floor.py (map), tools/gen_monsters.py (monsters), tools/gen_floor_content.py (NPCs, quests,
secrets, fish, bosses). Names for floors 2-5 come from the October design pack; floors 6-10 are new.
Every name here is original (tools/check_names.py runs on it)."""

FLOORS = {
    2: dict(name="Highrest Highlands", town="Highrest", biome=("grass", "dried", "dirt"), band=(35, 60),
            camp=["Horned Grazer", "Ridge Cat", "Dust Strider", "Hill Cutthroat", "Blight Wasp"],
            elite="Herd Bull", labyrinth="Stonehide Bull", apex="Mesa Wyrmling",
            field_boss="Horn Brute", floor_boss="Crowned Aurochs",
            field_pattern="stomp", boss_pattern="charge",
            fish=["Highland Trout", "Stone Loach", "Ridge Char", "Wind Minnow", "Silverjaw", "Dusk Grayling", "Old Hornback"]),
    3: dict(name="Rootwell Fogwood", town="Rootwell", biome=("jungle", "jungle", "dirtfloor"), band=(60, 90),
            camp=["Spore Bat", "Moss Crawler", "Fog Lurker", "Bark Mantis", "Lantern Wisp"],
            elite="Moss Elder", labyrinth="Rootbound Husk", apex="Grove Hydraling",
            field_boss="Mossback Warden", floor_boss="Sleeping Trunk",
            field_pattern="root", boss_pattern="sleep",
            fish=["Fog Perch", "Root Eel", "Mossfin", "Lantern Carp", "Bog Pike", "Glowscale", "The Drowned Log"]),
    4: dict(name="Lakehold", town="Lakehold", biome=("sand", "sand", "cobble"), band=(90, 120),
            camp=["Lake Eel", "Drowned Footman", "Reed Witch", "Tide Crab", "Castle Hound"],
            elite="Drowned Sergeant", labyrinth="Helm Knight", apex="Siege Beast",
            field_boss="Lake Knight", floor_boss="Knight of the Closed Helm",
            field_pattern="lance", boss_pattern="silence",
            fish=["Lake Bream", "Castle Carp", "Reed Pike", "Tide Shrimp", "Moat Eel", "Bellfish", "Queen of the Lake"]),
    5: dict(name="Ringhold", town="Ringhold", biome=("gravel", "gravel", "stonefloor"), band=(120, 160),
            camp=["Deserter", "Drill Construct", "Arena Hound", "Pit Brawler", "Ring Archer"],
            elite="Deserter Lieutenant", labyrinth="Sand Golem", apex="Undying Champion",
            field_boss="Arena Warden", floor_boss="Empty Colossus",
            field_pattern="stances", boss_pattern="split",
            fish=["Cistern Minnow", "Sandgill", "Arena Carp", "Brass Perch", "Pit Loach", "Champion's Koi", "The Gilded One"]),
    6: dict(name="Emberreach", town="Cinderhold", biome=("rocksoil", "rocksoil", "earth"), band=(160, 200),
            camp=["Ash Hound", "Slag Golem", "Ember Imp", "Forge Thrall", "Cinder Drake"],
            elite="Forge Overseer", labyrinth="Magma Sentinel", apex="Pyre Wyrm",
            field_boss="Bellows Giant", floor_boss="Cinder Matriarch",
            field_pattern="stomp", boss_pattern="charge",
            fish=["Ash Minnow", "Ember Carp", "Sulfur Eel", "Coal Perch", "Slagfin", "Firegill", "The Smelter"]),
    7: dict(name="Glasswater Marsh", town="Reedhaven", biome=("swamp", "mud", "wood"), band=(200, 250),
            camp=["Glass Toad", "Reed Stalker", "Bog Hag", "Crystal Leech", "Marsh Troll"],
            elite="Bog Elder", labyrinth="Sunken Watcher", apex="Shard Hydra",
            field_boss="Mire Colossus", floor_boss="The Many-Mouthed",
            field_pattern="root", boss_pattern="sleep",
            fish=["Glass Minnow", "Marsh Pike", "Reed Eel", "Crystal Carp", "Bog Catfish", "Prismfin", "The Glass King"]),
    8: dict(name="Frostspire", town="Rimewatch", biome=("snow", "snow", "gravel"), band=(250, 300),
            camp=["Frost Wolf", "Ice Golem", "Snow Raider", "Rime Wisp", "Glacier Bear"],
            elite="Raider Chieftain", labyrinth="Frozen Sentinel", apex="Hoarfrost Wyrm",
            field_boss="Avalanche Brute", floor_boss="Rimebound Jarl",
            field_pattern="lance", boss_pattern="silence",
            fish=["Ice Cod", "Frost Char", "Snow Salmon", "Glacier Pike", "Rime Eel", "Aurora Trout", "Old Iceback"]),
    9: dict(name="The Hollow Bazaar", town="Last Market", biome=("cobble", "cobble", "blackmarble"), band=(300, 350),
            camp=["Ledger Ghost", "Bazaar Thief", "Coin Mimic", "Catacomb Rat", "Gilded Husk"],
            elite="Debt Collector", labyrinth="Vault Guardian", apex="Treasure Devourer",
            field_boss="The Auctioneer", floor_boss="The Ledger King",
            field_pattern="stances", boss_pattern="split",
            fish=["Gutter Minnow", "Coin Carp", "Canal Eel", "Ledger Perch", "Velvet Pike", "Goldfin", "The Banker"]),
    10: dict(name="The Cobalt Labyrinth", town="Bluegate", biome=("stonefloor", "stonefloor", "blackmarble"), band=(350, 400),
             camp=["Cobalt Knight", "Azure Wraith", "Sapphire Golem", "Blue Shade", "Labyrinth Stalker"],
             elite="Cobalt Champion", labyrinth="Cobalt Warden", apex="Lapis Wyrm",
             field_boss="Sapphire Gatekeeper", floor_boss="Azhrakkar, the Cerulean Ruin",
             field_pattern="stomp", boss_pattern="ruin",
             fish=["Cobalt Minnow", "Azure Perch", "Sapphire Eel", "Blue Carp", "Lapis Pike", "Starfin", "The Cerulean Leviathan"]),
}

FLOOR_TITLES = {2: "Hornbreaker", 3: "Rootbreaker", 4: "Lakebreaker", 5: "Ringbreaker", 6: "Emberbreaker",
                7: "Marshbreaker", 8: "Frostbreaker", 9: "Ledgerbreaker", 10: "Ruinbreaker"}


def origin(n):
    """Top-left corner of floor n (n >= 2). Floor 1 is at 1000,1000 (maps/layout_floor1.py)."""
    return 2000 + (n - 2) * 400, 1000


SIZE = 300
