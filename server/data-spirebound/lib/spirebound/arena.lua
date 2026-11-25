-- Equal-footing arena events (DESIGN.md 15). Roadmap 5.7c.
-- Everyone fights with the same health and mana, and every hit or heal between participants is a fixed amount,
-- so level and gear don't matter (the engine can't swap a character's level or gear, so we even out the numbers).
-- Kinds: Last Man Standing (free for all, one life), Team Rush (first team to 20 kills), Capture the Banner
-- (stand on the banner square with no enemy on it: 1 point every 5 seconds, first to 60).
SpireArena = {
	HP = 1500, MANA = 1000,
	HIT = { 90, 130 }, SPELL = { 130, 190 }, HEAL = { 150, 220 },
	MIN_PLAYERS = 4, MAX_PLAYERS = 20, MIN_LEVEL = 20,
	SIGNUP_TIME = 5 * 60, MAX_TIME = 10 * 60,
	RUSH_KILLS = 20, BANNER_POINTS = 60, BANNER_TICK = 5,
	TITLE = "Arena Victor",
	HOURS = { 19, 22 }, -- server hours an event opens sign-ups (kinds rotate by day)
}
SpireArena.KINDS = {
	lms = { id = "lms", name = "Last Man Standing", teams = false },
	rush = { id = "rush", name = "Team Rush", teams = true },
	banner = { id = "banner", name = "Capture the Banner", teams = true },
	-- every push, pull, slow and root works at full strength on players (DESIGN 6.7, Jay 2026-11-17): the weekly
	-- test of "chaotic but fun" PvP before it ever reaches the open world
	wild = { id = "wild", name = "Wild PvP", teams = false, wild = true },
}
-- The week (Spire Pressure, Jay 2026-11-25): Capture the Banner is the twice-weekly objective match (Wednesday and
-- Saturday), Friday is Wild PvP day, the other days alternate Last Man Standing and Team Rush. Index = weekday,
-- 1 = Sunday ... 7 = Saturday.
SpireArena.WEEK = { "rush", "lms", "rush", "banner", "lms", "wild", "banner" }

-- Spire Pressure (DESIGN.md 15, roadmap M4; Jay 2026-11-25: "sure i like the way this sounds"): fights end. Every
-- 30 seconds of a running event everyone deals 15% more damage and loses 10% of their event health. Anyone who stands
-- idle for 60 seconds is moved elsewhere in the arena; idle for 2 minutes is a deserter: out, no rewards, and no
-- events for 7 days. The event's MVP gets a statue in Hearthgate until the next event.
SpireArena.PRESSURE_EVERY = 30
SpireArena.PRESSURE_DAMAGE = 0.15
SpireArena.PRESSURE_HP = 0.10
SpireArena.PRESSURE_MAX = 7 -- at most 7 steps: +105% damage, 30% health
SpireArena.IDLE_MOVE = 60
SpireArena.IDLE_DESERT = 120
SpireArena.DESERTER_BAN = 7 * 86400

-- Pure state machine --------------------------------------------------------
function SpireArena.new(kind, now)
	return { kind = kind, phase = "signup", opened = now, players = {}, order = {}, score = { a = 0, b = 0 }, kills = {} }
end

function SpireArena.join(st, id, name, level)
	if st.phase ~= "signup" then
		return false, "Sign-ups are closed."
	end
	if st.players[id] then
		return false, "You are already signed up."
	end
	if level < SpireArena.MIN_LEVEL then
		return false, "You need level " .. SpireArena.MIN_LEVEL .. " to fight in the Arena."
	end
	if #st.order >= SpireArena.MAX_PLAYERS then
		return false, "The Arena is full."
	end
	st.players[id] = { name = name, alive = true, kills = 0 }
	table.insert(st.order, id)
	return true
end

function SpireArena.leave(st, id)
	if not st.players[id] then
		return
	end
	st.players[id].alive = false
	st.players[id].left = true
end

-- Start: needs enough players. Teams alternate in sign-up order. Returns true or false + reason.
function SpireArena.start(st, now)
	if #st.order < SpireArena.MIN_PLAYERS then
		st.phase = "cancelled"
		return false, "Not enough fighters signed up."
	end
	local k = SpireArena.KINDS[st.kind]
	for i, id in ipairs(st.order) do
		st.players[id].team = k.teams and ((i % 2 == 1) and "a" or "b") or nil
	end
	st.phase = "running"
	st.started = now
	return true
end

-- May attacker hit victim? (both must be in this event, alive, and not team-mates)
function SpireArena.canHit(st, aId, vId)
	local a, v = st and st.players[aId], st and st.players[vId]
	if not st or st.phase ~= "running" or not a or not v or not a.alive or not v.alive then
		return false
	end
	return a.team == nil or a.team ~= v.team
end

-- Pure: the fixed amount for a hit or heal. origin "spell" or "hit"; r in [0,1)
function SpireArena.amount(kind, r)
	local range = kind == "heal" and SpireArena.HEAL or (kind == "spell" and SpireArena.SPELL or SpireArena.HIT)
	return math.floor(range[1] + r * (range[2] - range[1]))
end

-- A participant was brought down. Returns what to do with the victim: "out" (LMS) or "respawn" (teams).
function SpireArena.down(st, vId, kId)
	local v = st.players[vId]
	if not v then
		return nil
	end
	local k = kId and st.players[kId]
	if k and kId ~= vId then
		k.kills = k.kills + 1
	end
	if not SpireArena.KINDS[st.kind].teams then -- every free-for-all (Last Man Standing, Wild PvP)
		v.alive = false
		return "out"
	end
	if st.kind == "rush" and k and k.team and k.team ~= v.team then
		st.score[k.team] = st.score[k.team] + 1
	end
	return "respawn"
end

-- Banner tick: holders = list of ids standing on the banner square. One team alone scores a point.
function SpireArena.bannerTick(st, holders)
	local teams = {}
	for _, id in ipairs(holders) do
		local p = st.players[id]
		if p and p.alive and p.team then
			teams[p.team] = true
		end
	end
	if teams.a and not teams.b then
		st.score.a = st.score.a + 1
		return "a"
	elseif teams.b and not teams.a then
		st.score.b = st.score.b + 1
		return "b"
	end
	return nil
end

-- Is it over? Returns winner ids (list) or nil while still running. A draw returns an empty list.
function SpireArena.result(st, now)
	if st.phase ~= "running" then
		return nil
	end
	local timeUp = now - st.started >= SpireArena.MAX_TIME
	if not SpireArena.KINDS[st.kind].teams then -- every free-for-all (Last Man Standing, Wild PvP)
		local alive = {}
		for _, id in ipairs(st.order) do
			if st.players[id].alive then
				table.insert(alive, id)
			end
		end
		if #alive <= 1 then
			return alive
		end
		if not timeUp then
			return nil
		end
		-- time up: most kills among survivors wins
		table.sort(alive, function(x, y) return st.players[x].kills > st.players[y].kills end)
		if st.players[alive[1]].kills == st.players[alive[2]].kills then
			return {}
		end
		return { alive[1] }
	end
	local target = st.kind == "rush" and SpireArena.RUSH_KILLS or SpireArena.BANNER_POINTS
	-- a team that has nobody left (everyone logged out) loses
	local present = { a = 0, b = 0 }
	for _, id in ipairs(st.order) do
		local p = st.players[id]
		if p.alive and p.team then
			present[p.team] = present[p.team] + 1
		end
	end
	local winner
	if present.a == 0 or present.b == 0 then
		winner = present.a > 0 and "a" or (present.b > 0 and "b" or "draw")
	elseif st.score.a >= target or st.score.b >= target or timeUp then
		winner = st.score.a > st.score.b and "a" or (st.score.b > st.score.a and "b" or "draw")
	end
	if not winner then
		return nil
	end
	local out = {}
	if winner ~= "draw" then
		for _, id in ipairs(st.order) do
			local p = st.players[id]
			if p.team == winner and not p.left and not p.deserter then
				table.insert(out, id)
			end
		end
	end
	return out
end

-- Pure: which kind runs on this day number (days since 1970-01-01, which was a Thursday)
function SpireArena.kindForDay(day)
	return SpireArena.WEEK[(day + 4) % 7 + 1]
end

-- Pure: the pressure step a running event has reached
function SpireArena.pressureStep(started, now)
	if not started then
		return 0
	end
	return math.min(SpireArena.PRESSURE_MAX, math.floor((now - started) / SpireArena.PRESSURE_EVERY))
end

-- Pure: damage multiplier and event health at a pressure step
function SpireArena.pressureDamage(step)
	return 1 + SpireArena.PRESSURE_DAMAGE * step
end

function SpireArena.pressureHp(step)
	return math.floor(SpireArena.HP * (1 - SpireArena.PRESSURE_HP * step) + 0.5)
end

-- Pure: what happens to a fighter idle since lastActive? nil, "move" (once per idle spell) or "desert"
function SpireArena.idleAction(lastActive, moved, now)
	local idle = now - lastActive
	if idle >= SpireArena.IDLE_DESERT then
		return "desert"
	end
	if idle >= SpireArena.IDLE_MOVE and not moved then
		return "move"
	end
	return nil
end

-- Pure: the event's MVP: most kills; ties go to whoever signed up first. Nobody with no kills is MVP.
function SpireArena.mvp(st)
	local best, bestKills = nil, 0
	for _, id in ipairs(st.order) do
		local p = st.players[id]
		if not p.deserter and p.kills > bestKills then
			best, bestKills = id, p.kills
		end
	end
	return best
end

-- Pure: may this character join, given a deserter ban until banUntil?
function SpireArena.banned(banUntil, now)
	return banUntil ~= nil and banUntil > now
end
