-- Spirebound server config template. Rendered by ops/render_config.sh into server/config.lua (git-ignored).
-- Values written ${LIKE_THIS} come from /etc/spirebound/spirebound.env on the host (never from git).
-- Rule sources: 02_LOCKED_DECISIONS, 05_WORLD_RULES, 16_SCALE_OPS_ANTICHEAT, 22_CORE_DETAILS.

-- Combat (skull timings beyond these engine defaults are patch P3, phase 1)
worldType = "pvp"
hotkeyAimbotEnabled = true
protectionLevel = 20
killsToRedSkull = 3
killsToBlackSkull = 6
pzLocked = 60 * 1000
removeChargesFromRunes = true
removeChargesFromPotions = true
removeWeaponAmmunition = true
removeWeaponCharges = true
timeToDecreaseFrags = 24 * 60 * 60
whiteSkullTime = 15 * 60
stairJumpExhaustion = 2000
experienceByKillingPlayers = false
expFromPlayersLevelRange = 75

-- Connection
ip = "${SPIRE_PUBLIC_IP}"
bindOnlyGlobalAddress = false
loginProtocolPort = 7171
gameProtocolPort = 7172
statusProtocolPort = 7171
maxPlayers = 600
motd = "Welcome to Spirebound. Fan-inspired, unofficial. No pay-to-win."
onePlayerOnlinePerAccount = true
allowClones = false
allowWalkthrough = true
serverName = "Spirebound"
statusTimeout = 5000
replaceKickOnLogin = true
maxPacketsPerSecond = 25

-- Deaths: item loss is handled by patch P5 (phase 1); disable the engine default
deathLosePercent = -1

-- Houses (15): listed prices come from data/houses.csv, rent weekly
housePriceEachSQM = -1
houseRentPeriod = "weekly"
houseOwnedByAccount = false
houseDoorShowPrice = true
onlyInvitedCanMoveHouseItems = true

-- Item usage
timeBetweenActions = 200
timeBetweenExActions = 1000

-- Map
mapName = "spirebound"
mapAuthor = "Spirebound build agent"

-- Market (8% fee is implemented in phase 3)
marketOfferDuration = 30 * 24 * 60 * 60
premiumToCreateMarketOffer = false
checkExpiredMarketOffersEachMinutes = 60
maxMarketOffersAtATimePerPlayer = 100

-- MySQL
mysqlHost = "${SPIRE_DB_HOST}"
mysqlUser = "${SPIRE_DB_USER}"
mysqlPass = "${SPIRE_DB_PASS}"
mysqlDatabase = "${SPIRE_DB_NAME}"
mysqlPort = 3306
mysqlSock = ""

-- Misc. No premium account exists (02, 21): everyone has the full game.
allowChangeOutfit = true
freePremium = true
kickIdlePlayerAfterMinutes = 15
maxMessageBuffer = 4
emoteSpells = false
classicEquipmentSlots = false
classicAttackSpeed = false
showScriptsLogInConsole = false
showOnlineStatusInCharlist = false
yellMinimumLevel = 10
yellAlwaysAllowPremium = false
forceMonsterTypesOnLoad = true
cleanProtectionZones = false
luaItemDesc = false
showPlayerLogInConsole = true

-- VIP and depot (22: one shared depot, 2,000 items)
vipFreeLimit = 100
vipPremiumLimit = 100
depotFreeLimit = 2000
depotPremiumLimit = 2000

-- World light
defaultWorldLight = true

-- Server save (05:00 ET; globalevents/globalevents.xml)
serverSaveNotifyMessage = true
serverSaveNotifyDuration = 5
serverSaveCleanMap = false
serverSaveClose = false
serverSaveShutdown = true

-- Rates: XP comes from data/xp_table.csv and monster rows; no multipliers, no stages.
experienceStages = nil
rateExp = 1
rateSkill = 1
rateLoot = 1
rateMagic = 1
rateSpawn = 1

-- Monsters
deSpawnRange = 2
deSpawnRadius = 50
removeOnDespawn = true
walkToSpawnRadius = 14

-- Spirebound uses "Stamina" as a combat resource on the mana bar (06), not Tibia's hunting stamina.
staminaSystem = false

-- Scripts
warnUnsafeScripts = true
convertUnsafeScripts = true

-- Startup
defaultPriority = "high"
startupDatabaseOptimization = false

-- Status server information
ownerName = "Spirebound"
ownerEmail = ""
url = "${SPIRE_WEBSITE_URL}"
location = "United States"
