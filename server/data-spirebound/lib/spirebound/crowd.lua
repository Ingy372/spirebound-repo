-- The crowd system (FLOOR1_WILDS_PLAN.md Part 7; Jay, Q31: "yes"). Each walled hunting ground counts the players inside
-- it every 30 seconds. When it is over-full, extra monster groups switch on at its crowd spots; when the crowd leaves
-- they switch off again (living crowd monsters stay until killed, they just don't come back).
--   Quiet  : fewer than 5 players  -> nothing extra
--   Busy   : 5 to 7                -> the odd-numbered crowd spots
--   Packed : 8 or more             -> every crowd spot
--   Rush   : 12 or more, Guarded (starter) grounds only -> every spot, and crowd monsters return 3x as fast
-- A ground steps up at once and steps down only after 5 minutes below the line. After a restart every ground is Quiet.
-- Rules here are pure (tested); the 30-second tick is scripts/spirebound/crowd.lua. Ground data: wilds_data.lua.

SpireCrowd = SpireCrowd or {
	TICK = 30,
	STEP_DOWN = 300,
	NEAR = 7, -- never spawn a group while a player is this close to the spot
	grounds = {}, -- id -> { state, below = time first seen below the line, count }
	spots = {}, -- "id:n" -> { alive = { creature ids }, ready = time it may refill }
}

local RANK = { quiet = 1, busy = 2, packed = 3, rush = 4 }

-- Pure: the state a ground's player count asks for
function SpireCrowd.stateFor(count, guarded)
	if count >= 12 and guarded then
		return "rush"
	elseif count >= 8 then
		return "packed"
	elseif count >= 5 then
		return "busy"
	end
	return "quiet"
end

-- Pure: next state of a ground record { state, below } at time `now`
function SpireCrowd.step(rec, count, guarded, now)
	local want = SpireCrowd.stateFor(count, guarded)
	local cur = rec.state or "quiet"
	if RANK[want] > RANK[cur] then
		rec.state, rec.below = want, nil
	elseif RANK[want] < RANK[cur] then
		rec.below = rec.below or now
		if now - rec.below >= SpireCrowd.STEP_DOWN then
			rec.state, rec.below = want, nil
		end
	else
		rec.below = nil
	end
	rec.count = count
	return rec.state or "quiet"
end

-- Pure: is crowd spot number n switched on in this state?
function SpireCrowd.spotOn(state, n)
	if state == "packed" or state == "rush" then
		return true
	end
	return state == "busy" and n % 2 == 1
end

-- Pure: how long a crowd group takes to come back (real seconds)
function SpireCrowd.respawn(state, base)
	return state == "rush" and math.floor(base / 3) or base
end

function SpireCrowd.ground(id)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == id then
			return g
		end
	end
end

function SpireCrowd.inside(g, pos)
	return pos.z == g.z and pos.x >= g.x1 and pos.x <= g.x2 and pos.y >= g.y1 and pos.y <= g.y2
end

-- Players that count: anyone inside the ground at ground level except staff (cavebot users count too)
function SpireCrowd.countPlayers(g)
	local n = 0
	for _, p in ipairs(Game.getPlayers()) do
		if not p:getGroup():getAccess() and SpireCrowd.inside(g, p:getPosition()) then
			n = n + 1
		end
	end
	return n
end

function SpireCrowd.playerNear(pos)
	local r = SpireCrowd.NEAR
	for _, p in ipairs(Game.getSpectators(pos, false, true, r, r, r, r)) do
		if not p:getGroup():getAccess() then
			return true
		end
	end
	return false
end

local function aliveCount(rec)
	local n = 0
	for _, cid in ipairs(rec.alive or {}) do
		local c = Creature(cid)
		if c and not c:isRemoved() and c:getHealth() > 0 then
			n = n + 1
		end
	end
	return n
end

-- One ground, one tick: update its state and refill its switched-on crowd spots.
-- A test can pass the player count and a "player near this spot?" function; otherwise real players are used.
function SpireCrowd.update(g, now, count, near)
	local rec = SpireCrowd.grounds[g.id] or { state = "quiet" }
	SpireCrowd.grounds[g.id] = rec
	local state = SpireCrowd.step(rec, count or SpireCrowd.countPlayers(g), g.guarded, now)
	local rapid = SpireCrowd.rapidRespawn()
	if rapid and state ~= "rush" then
		state = "packed" -- R20: the Rapid Respawn weekend fills every ground
	end
	local isNear = near or SpireCrowd.playerNear
	local spawned = 0
	for _, s in ipairs(g.spots) do
		local key = g.id .. ":" .. s.n
		local sr = SpireCrowd.spots[key] or { alive = {}, ready = 0 }
		SpireCrowd.spots[key] = sr
		local alive = aliveCount(sr)
		if alive == 0 and #sr.alive > 0 then -- the whole group is dead: start its wait
			sr.alive = {}
			sr.ready = now + math.floor(SpireCrowd.respawn(state, g.respawn) / (rapid and 2 or 1))
		end
		local pos = Position(s.x, s.y, s.z)
		if alive == 0 and SpireCrowd.spotOn(state, s.n) and now >= sr.ready and not isNear(pos) then
			for _, m in ipairs(s.group) do
				for _ = 1, m[2] do
					local mon = Game.createMonster(m[1], pos, true, false)
					if mon then
						table.insert(sr.alive, mon:getId())
					end
				end
			end
			spawned = spawned + 1
		end
	end
	return state, spawned
end

-- the weekend bonus (lib/spirebound/events.lua); a test can force it with SpireCrowd.forceRapid
function SpireCrowd.rapidRespawn()
	if SpireCrowd.forceRapid ~= nil then
		return SpireCrowd.forceRapid
	end
	local w = SpireEvents and SpireEvents.currentWeekend and SpireEvents.currentWeekend()
	return w ~= nil and w.id == "respawn"
end

function SpireCrowd.tick(now)
	for _, g in ipairs(SpireWilds.grounds) do
		SpireCrowd.update(g, now)
	end
end

-- The !hunt line for a ground: "Boar Meadow: busy (6 players, extra monsters are out)"
function SpireCrowd.statusLine(id)
	local g = SpireCrowd.ground(id)
	if not g then
		return nil
	end
	local rec = SpireCrowd.grounds[id] or { state = "quiet", count = 0 }
	local n = rec.count or 0
	local who = n == 1 and "1 player" or (n .. " players")
	local extra = ({
		quiet = "no extra monsters",
		busy = "extra monsters are out",
		packed = "every extra group is out",
		rush = "every extra group is out, coming back fast",
	})[rec.state or "quiet"]
	return string.format("%s: %s (%s, %s)", g.title, rec.state or "quiet", who, extra)
end

-- Party caves (Q32: "yes"): the cavebot is refused below
function SpireCrowd.caveAt(pos)
	for _, c in ipairs(SpireWilds.caves) do
		if pos.z == c.z and pos.x >= c.x1 and pos.x <= c.x2 and pos.y >= c.y1 and pos.y <= c.y2 then
			return c
		end
	end
end
