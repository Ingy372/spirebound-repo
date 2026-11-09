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
protectionLevel = 50
experienceByKillingPlayers = false
dayKillsToRedSkull = 3
weekKillsToRedSkull = 5
monthKillsToRedSkull = 10
pushWhenAttacking = false

-- Rates (DESIGN.md 5.5): stages live in server/core-overrides/stages.lua
rateUseStages = true
rateLoot = 2

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

-- Houses
houseRentPeriod = "weekly"
houseOwnedByAccount = false
