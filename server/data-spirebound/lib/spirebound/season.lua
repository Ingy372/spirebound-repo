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

-- When this season's launch began (the owner's /launch start), or nil. Since Jay's answer of 2026-11-27 (Q13: "no set
-- day when the boss doors open. its upon players being ready.") it no longer gates boss doors; it only tells the launch
-- week apart: the crowd boost (QA15) and the cavebot's first-week ban on Floor 1 (QA16).
SpireSeason.LAUNCH_WEEK = 7 * 86400
function SpireSeason.startedAt()
	return seasonKv():get("startedAt")
end

-- Pure: is `now` inside the first 7 days after `start`?
function SpireSeason.launchWeekAt(start, now)
	return start ~= nil and now >= start and now < start + SpireSeason.LAUNCH_WEEK
end

-- tests may force it with SpireSeason.forceLaunchWeek = true / false
function SpireSeason.inLaunchWeek(now)
	if SpireSeason.forceLaunchWeek ~= nil then
		return SpireSeason.forceLaunchWeek
	end
	return SpireSeason.launchWeekAt(SpireSeason.startedAt(), now or os.time())
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
		chronicle = SpireChronicle ~= nil and SpireChronicle.get(accountId, season).finishedAt ~= nil, -- M3: finished this season's Chronicle
	}
	kv.scoped("hall-of-seasons"):scoped("season-" .. season):set(name, record)
	-- account-wide rewards carry over
	local acc = accountKv(accountId)
	local accTitles = acc:get("titles") or {}
	for _, t in ipairs(titles) do
		accTitles[t] = accTitles[t] or season
	end
	if SpireDeathGame.earnsDeathbound(difficulty, level, retired) then
		accTitles["Deathbound (Season " .. season .. ")"] = season
	end
	acc:set("titles", accTitles)
	acc:set("explored", (acc:get("explored") or 0) + record.secrets)
	-- the fishing log carries over (DESIGN.md 4): every kind this character caught joins the account's log
	local log = acc:get("fishlog") or {}
	for _, kind in ipairs(okF and fish or {}) do
		log[kind] = log[kind] or season
	end
	acc:set("fishlog", log)
	acc:set("seasons", (acc:get("seasons") or 0) + 1)
	return record
end

-- The SQL that wipes a season (8.3): data-spirebound/season_wipe.sql, run OFFLINE by tools/season_wipe.sh after
-- /season end has archived everyone and shut the server down. Read here only so the in-game test can check it.
function SpireSeason.wipeStatements()
	local f = io.open(DATA_DIRECTORY .. "/season_wipe.sql", "r")
	if not f then
		return {}
	end
	local text = f:read("*a")
	f:close()
	local out = {}
	for stmt in (text:gsub("%-%-[^\n]*", "")):gmatch("[^;]+") do
		stmt = stmt:gsub("^%s+", ""):gsub("%s+$", "")
		if stmt ~= "" then
			table.insert(out, stmt)
		end
	end
	return out
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
