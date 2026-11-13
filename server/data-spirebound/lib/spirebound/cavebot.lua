-- Built-in cavebot penalty (DESIGN.md 12, Jay 2026-11-08). Roadmap 2.12.
-- The Spirebound client reports when its cavebot is switched on or off. While on, and for LINGER seconds after:
-- XP x0.45, loot x0.5, no secrets/rare rewards, no boss rooms. Auto-targeting alone costs nothing. No visible marker.
SpireCavebot = {
	XP = 0.45,
	LOOT = 0.50,
	LINGER = 10 * 60, -- QUESTIONS.md Q11 (Claude's recommendation until Jay answers)
	state = {}, -- playerGuid -> { on = bool, offAt = time }
}

-- Pure
function SpireCavebot.penaltyActive(st, now)
	if not st then
		return false
	end
	if st.on then
		return true
	end
	return st.offAt ~= nil and now - st.offAt < SpireCavebot.LINGER
end

function SpireCavebot.setState(guid, on, now)
	local st = SpireCavebot.state[guid] or {}
	if st.on and not on then
		st.offAt = now
	end
	st.on = on
	SpireCavebot.state[guid] = st
	return st
end

function SpireCavebot.active(player)
	return SpireCavebot.penaltyActive(SpireCavebot.state[player:getGuid()], os.time())
end

function SpireCavebot.blocksRewards(player)
	return SpireCavebot.active(player) or SpireCavebot.standingBot(SpireCavebot.track[player:getGuid()], os.time())
end

-- Roadmap R15 (Q16 assumed): the server does not only trust the client's report.
--   * Hunting while standing still: 5+ kills in 10 minutes without moving more than a tile counts as botting
--     (auto-target + auto-heal on one spot), with the same penalty, until you walk again.
--   * Following a botter: a party member within 7 tiles of a botting member earns the same 45% experience.
--   * Hunting tasks: while botting, only every second kill counts.
--   * Suspicion log: very long unbroken hunts are written to the log for staff (no automatic ban).
SpireCavebot.STILL_TIME = 10 * 60
SpireCavebot.STILL_KILLS = 5
SpireCavebot.LONG_HUNT = 6 * 3600
SpireCavebot.track = {} -- guid -> { pos = {x, y, z}, since = time, kills = { times }, huntStart = time, lastKill = time }

-- Pure: is this "hunting while standing still"? rec as in track
function SpireCavebot.standingBot(rec, now)
	if not rec or not rec.since or now - rec.since < SpireCavebot.STILL_TIME then
		return false
	end
	local n = 0
	for _, t in ipairs(rec.kills or {}) do
		if now - t <= SpireCavebot.STILL_TIME then
			n = n + 1
		end
	end
	return n >= SpireCavebot.STILL_KILLS
end

-- Pure: note a position; moving more than one tile resets the "still" clock
function SpireCavebot.notePos(rec, pos, now)
	if not rec.pos or math.max(math.abs(rec.pos.x - pos.x), math.abs(rec.pos.y - pos.y)) > 1 or rec.pos.z ~= pos.z then
		rec.pos = { x = pos.x, y = pos.y, z = pos.z }
		rec.since = now
	end
end

function SpireCavebot.noteKill(rec, now)
	rec.kills = rec.kills or {}
	table.insert(rec.kills, now)
	while #rec.kills > 0 and now - rec.kills[1] > SpireCavebot.STILL_TIME do
		table.remove(rec.kills, 1)
	end
	if not rec.lastKill or now - rec.lastKill > 15 * 60 then
		rec.huntStart = now -- a break of 15 minutes starts a new hunt
	end
	rec.lastKill = now
end

function SpireCavebot.botting(player)
	return SpireCavebot.active(player) or SpireCavebot.standingBot(SpireCavebot.track[player:getGuid()], os.time())
end

-- following a botting party member
function SpireCavebot.followingBot(player)
	local party = player:getParty()
	if not party then
		return false
	end
	local members = party:getMembers()
	table.insert(members, party:getLeader())
	for _, m in ipairs(members) do
		if m ~= player and m:getPosition():getDistance(player:getPosition()) <= 7 and SpireCavebot.botting(m) then
			return true
		end
	end
	return false
end

function SpireCavebot.xpFactor(player)
	return (SpireCavebot.botting(player) or SpireCavebot.followingBot(player)) and SpireCavebot.XP or 1
end
