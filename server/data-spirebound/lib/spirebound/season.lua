-- Seasons (DESIGN.md 4). Roadmap 8.1.
-- Ending a season: every character is archived to the Hall of Seasons, account-wide rewards (titles, Death Game
-- honours, explorer and angler counts) are copied to the ACCOUNT, then characters, houses, guilds and world progress
-- are wiped for a fresh launch week. Accounts, account rewards and the Hall of Seasons are kept.

SpireSeason = {}

local function seasonKv()
	return kv.scoped("spirebound-season")
end

function SpireSeason.current()
	return seasonKv():get("number") or 1
end

local function playerKv(guid)
	return kv.scoped("player"):scoped(tostring(guid))
end

local function accountKv(accountId)
	return kv.scoped("account"):scoped(tostring(accountId)):scoped("spirebound-legacy")
end
SpireSeason.accountKv = accountKv

-- Archive one character (works for offline characters). Returns the archived record.
function SpireSeason.archivePlayer(guid, accountId, name, level, vocationId, season)
	local pk = playerKv(guid)
	local titles = {}
	local ok, keys = pcall(function() return pk:scoped("spirebound-titles"):keys() end)
	for _, t in ipairs(ok and keys or {}) do
		table.insert(titles, t)
	end
	local difficulty = pk:scoped("spirebound"):get("difficulty") or 0
	local retired = pk:scoped("spirebound"):get("retired") == true
	local okS, secrets = pcall(function() return pk:scoped("spirebound-secrets"):keys() end)
	local okF, fish = pcall(function() return pk:scoped("spirebound-fishing"):keys() end)
	local record = {
		name = name, level = level, vocation = vocationId, difficulty = difficulty, retired = retired,
		titles = titles, secrets = okS and #secrets or 0, fish = okF and #fish or 0, season = season,
	}
	kv.scoped("hall-of-seasons"):scoped("season-" .. season):set(name, record)
	-- account-wide rewards carry over
	local acc = accountKv(accountId)
	local accTitles = acc:get("titles") or {}
	for _, t in ipairs(titles) do
		accTitles[t] = accTitles[t] or season
	end
	if difficulty == 3 then
		accTitles["Deathbound (Season " .. season .. ")"] = season
	end
	acc:set("titles", accTitles)
	acc:set("explored", (acc:get("explored") or 0) + record.secrets)
	acc:set("seasons", (acc:get("seasons") or 0) + 1)
	return record
end

-- The SQL that wipes a season. Never touches accounts or account-level/hall-of-seasons KV.
function SpireSeason.wipeStatements()
	return {
		"DELETE FROM `players` WHERE `group_id` < 4",
		"UPDATE `houses` SET `owner` = 0, `paid` = 0, `warnings` = 0, `bid` = 0, `bid_end` = 0, `last_bid` = 0, `highest_bidder` = 0",
		"DELETE FROM `house_lists`",
		"DELETE FROM `guild_wars`",
		"DELETE FROM `guilds`",
		"DELETE FROM `market_offers`",
		"DELETE FROM `market_history`",
		"DELETE FROM `kv_store` WHERE `key_name` LIKE 'player.%' OR `key_name` LIKE 'spirebound-floors%' OR `key_name` LIKE 'spirebound-secrets-public%'"
			.. " OR `key_name` LIKE 'spirebound-bounties%' OR `key_name` LIKE 'spirebound-headstart%' OR `key_name` LIKE 'spirebound-twinfang%'"
			.. " OR `key_name` LIKE 'spirebound-fortune%' OR `key_name` LIKE 'spirebound-recruit%' OR `key_name` LIKE 'spirebound-memorial%'"
			.. " OR `key_name` LIKE 'spirebound-openhouse%'",
	}
end

-- Copy account-wide titles onto a character at login (so every season starts with your legacy titles)
function SpireSeason.applyLegacy(player)
	local acc = accountKv(player:getAccountId())
	local titles = acc:get("titles") or {}
	local mine = player:kv():scoped("spirebound-titles")
	for t, _ in pairs(titles) do
		if not mine:get(t) then
			mine:set(t, os.time())
		end
	end
end
