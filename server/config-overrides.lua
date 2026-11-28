-- Spirebound settings applied on top of Canary's pinned config.lua.dist
-- by tools/build_server.py. One "key = value" per line; each key must
-- already exist in config.lua.dist (the build fails if not), so upstream
-- changes can't silently drop a setting. A key starting with "+" is a
-- setting Canary reads but doesn't list in config.lua.dist; it is appended.
-- Passwords never go here: @MYSQL_*@ values come from server/local.env
-- (git-ignored) or environment variables.

-- Identity
serverName = "Spirebound"
serverMotd = "Welcome to Spirebound. The tower awaits."
dataPackDirectory = "data-spirebound"
+useAnyDatapackFolder = true
mapName = "spirebound"
toggleDownloadMap = false

-- Database
mysqlHost = "@MYSQL_HOST@"
mysqlUser = "@MYSQL_USER@"
mysqlPass = "@MYSQL_PASS@"
mysqlDatabase = "@MYSQL_DATABASE@"

-- PvP (DESIGN.md 6). Newbie protection below level 50.
worldType = "pvp"
protectionLevel = 1  -- newbie protection (level 50) is done in scripts so boss rooms can be the exception
experienceByKillingPlayers = false
-- Red/black skulls are handled by Spirebound scripts (weighted unjust kills, DESIGN.md 6.4); the engine's own counter is switched off
dayKillsToRedSkull = 999
weekKillsToRedSkull = 999
monthKillsToRedSkull = 999
pushWhenAttacking = false

-- Rates (DESIGN.md 5.5): stages live in server/core-overrides/stages.lua
rateUseStages = true
-- Normal loot (Jay, 2026-11-27, Q84: "why would we keep every drop at a doubled rate...?"); was 2. Roadmap QA20.
rateLoot = 1
-- Autoloot and rare drops first (DESIGN.md 15)
autoLoot = true
-- Looted coins stay in the backpack until the player deposits them (Jay, 2026-11-27, Q76: "they should stay in the bag
-- until the player deposits them in the bank"). Was on since the party playtest of 2026-11-26 (hand-off P2-7).
autoBank = false
-- Free blessings only below level 8 for Hardcore and Death Game (Jay, 2026-11-27, Q80: "yes"; roadmap QA11). The engine's
-- "adventurer's blessing" protected every character up to level 21; now it ends after level 7. Normal characters below
-- level 30 still get every blessing from our own script (scripts/spirebound/difficulty_events.lua, QA3).
adventurersBlessingLevel = 7
sortLootByChance = true

-- Accounts: up to 2 characters online per account (DESIGN.md 12)
maxPlayersOnlinePerAccount = 2
maxPlayersOutsidePZPerAccount = 2
freePremium = true

-- Systems switched off at launch (DESIGN.md 2, QUESTIONS.md Q7)
preySystemEnabled = false
taskHuntingSystemEnabled = false
wheelSystemEnabled = false
forgeInfluencedLimit = 0
forgeFiendishLimit = 0
boostedBossSlot = false

-- Spells unlock by level on their own (DESIGN.md). Canary's default makes every spell
-- need learning first and ignores each spell's own "no learning" setting, so it is off.
toggleLearnSpells = false

-- Houses (DESIGN.md 7.3): listed price, no auction, one per character, weekly rent
toggleCyclopediaHouseAuction = false
housePriceEachSQM = 1000
houseBuyLevel = 20
houseRentPeriod = "weekly"
houseOwnedByAccount = false

-- Livestream ("cast", DESIGN.md 15): on, but no experience bonus for streaming (fairness)
livestreamExperienceMultiplier = 1.0

-- Roadmap R4: the client logs in with a random session token from tools/login_server.py, never the password
authType = "session"
