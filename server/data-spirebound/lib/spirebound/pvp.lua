-- PvP and community health (DESIGN.md 6). Roadmap 2.1 - 2.4.
-- Pure rules first (tested in-game), game helpers after.

SpirePvP = {
	NEWBIE_LEVEL = 50, -- below this you can't attack or be attacked (except in boss rooms)
	LEVEL_RANGE = 0.70, -- can't start a fight with someone below 70% of your level (outside Contested/Deadzone/boss rooms)
	BULLY_GAP = 30, -- unjust kill on someone 30+ levels lower counts double
	RED_DAY = 3, RED_WEEK = 5, RED_MONTH = 10,
	BLACK_DAY = 6, BLACK_WEEK = 10,
	RED_DAYS = 7, BLACK_DAYS = 14,
	GUARD_MARK = 30 * 60, -- seconds a Guarded-zone killer is hunted by town guards
	OUTNUMBER_WINDOW = 10, -- seconds
	SANCTUARY_KILLS = 2, SANCTUARY_WINDOW = 6 * 3600, SANCTUARY_TIME = 30 * 60,
}

local DAY, WEEK, MONTH = 86400, 7 * 86400, 30 * 86400

-- Which zone tier is a position in? (WorldZones from the generated world_points.lua; later entries win)
function SpirePvP.zoneAt(pos)
	local tier = "open"
	for _, z in ipairs(WorldZones or {}) do
		if (z.z == -1 or z.z == pos.z) and pos.x >= z.x1 and pos.x <= z.x2 and pos.y >= z.y1 and pos.y <= z.y2 then
			tier = z.tier
		end
	end
	return tier
end

-- a = attacker, v = victim: { level, skull, guid, guildId, attackedMeRecently (bool), sanctuaryVsMyGuild (bool) }
-- returns true, or false + reason
function SpirePvP.canAttack(a, v, zone)
	if zone == "town" then
		return false, "You can't fight in town."
	end
	if zone ~= "bossroom" and (a.level < SpirePvP.NEWBIE_LEVEL or v.level < SpirePvP.NEWBIE_LEVEL) then
		return false, "Players below level " .. SpirePvP.NEWBIE_LEVEL .. " are protected."
	end
	if v.sanctuaryVsMyGuild or a.sanctuaryVsTheirGuild then
		return false, "Sanctuary: your guilds can't fight each other right now."
	end
	local skulled = v.skull == SKULL_WHITE or v.skull == SKULL_YELLOW or v.skull == SKULL_ORANGE or v.skull == SKULL_RED or v.skull == SKULL_BLACK
	if zone ~= "contested" and zone ~= "deadzone" and zone ~= "bossroom" and not skulled and not v.attackedMeRecently then
		if v.level < math.floor(a.level * SpirePvP.LEVEL_RANGE) then
			return false, "That player is far below your level. You can only fight back if they attack you first."
		end
	end
	return true
end

-- How many unjust kills is this kill worth?
function SpirePvP.unjustWeight(killerLevel, victimLevel, zone, victimDeathGame)
	if zone == "contested" or zone == "deadzone" then
		return 0
	end
	local w = zone == "guarded" and 3 or 1
	if killerLevel - victimLevel >= SpirePvP.BULLY_GAP then
		w = w * 2
	end
	if victimDeathGame then
		w = w * 2
	end
	return w
end

-- frags = { { t = time, w = weight }, ... } -> day, week, month totals
function SpirePvP.fragTotals(frags, now)
	local d, wk, m = 0, 0, 0
	for _, f in ipairs(frags) do
		local age = now - f.t
		if age <= DAY then d = d + f.w end
		if age <= WEEK then wk = wk + f.w end
		if age <= MONTH then m = m + f.w end
	end
	return d, wk, m
end

-- Returns the skull these frags earn: SKULL_BLACK, SKULL_RED or nil
function SpirePvP.skullFor(frags, now)
	local d, wk, m = SpirePvP.fragTotals(frags, now)
	if d >= SpirePvP.BLACK_DAY or wk >= SpirePvP.BLACK_WEEK then
		return SKULL_BLACK
	end
	if d >= SpirePvP.RED_DAY or wk >= SpirePvP.RED_WEEK or m >= SpirePvP.RED_MONTH then
		return SKULL_RED
	end
	return nil
end

-- Pure: how long a skull lasts, in SECONDS REMAINING. The engine's player:setSkullTime() takes a duration
-- (it counts down while the player is online), not a calendar time.
function SpirePvP.skullSeconds(skull)
	if skull == SKULL_BLACK then
		return SpirePvP.BLACK_DAYS * 86400
	elseif skull == SKULL_RED then
		return SpirePvP.RED_DAYS * 86400
	end
	return 0
end

function SpirePvP.deathLossMultiplier(skull)
	return (skull == SKULL_RED or skull == SKULL_BLACK) and 2 or 1
end

-- Outnumbered shield: 10% less player damage per attacker beyond 2, max 40%
function SpirePvP.outnumberedReduction(attackers)
	return math.min(40, math.max(0, 10 * (attackers - 2)))
end

-- Sanctuary: kills = list of times this victim was killed by one guild. True if a new Sanctuary starts.
function SpirePvP.sanctuaryDue(kills, now)
	local n = 0
	for _, t in ipairs(kills) do
		if now - t <= SpirePvP.SANCTUARY_WINDOW then
			n = n + 1
		end
	end
	return n >= SpirePvP.SANCTUARY_KILLS
end

function SpirePvP.cursor(skull)
	if skull == SKULL_RED then return "red" end
	if skull == SKULL_BLACK then return "black" end
	if skull == SKULL_WHITE or skull == SKULL_YELLOW or skull == SKULL_ORANGE then return "orange" end
	return "green"
end

-- Game helpers ---------------------------------------------------------
local function scope(player)
	return player:kv():scoped("spirebound-pvp")
end
SpirePvP.scope = scope

function SpirePvP.isMurderer(player)
	local s = player:getSkull()
	return s == SKULL_RED or s == SKULL_BLACK
end
