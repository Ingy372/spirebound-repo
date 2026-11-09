-- Field and floor boss framework (DESIGN.md 3.2, 9.2). Roadmap 1.18 / 1.19.
-- Pure helpers are separate from game wiring so in-game tests can check them.

SpireBoss = {
	CREDIT_WINDOW = 90, -- seconds: you need to have hit the boss this recently to be credited
	RESET_NO_DAMAGE = 60, -- seconds without player damage -> boss resets
	RESET_EMPTY = 30, -- seconds with no players in the room -> boss resets
	TELEGRAPH_MS = 600, -- warning before a marked-tile hit lands
	ENRAGE_STEP = 30, -- seconds between enrage damage steps
	ENRAGE_BONUS = 0.5, -- +50% boss damage per step
	REPEAT_RESPAWN = 30 * 60, -- floor boss respawn after a kill (repeat kills give no first-clear rewards)
	defs = {}, -- boss name -> definition (registered in scripts/spirebound/bosses_floor1.lua)
	fights = {}, -- monster id -> live fight state
}

function SpireBoss.register(name, def)
	SpireBoss.defs[name] = def
end

-- Pure: fight state is { hits = { [playerName] = { total = n, last = t } }, ... }
function SpireBoss.recordHit(state, playerName, amount, now)
	local h = state.hits[playerName] or { total = 0, last = 0 }
	h.total = h.total + amount
	h.last = now
	state.hits[playerName] = h
	state.lastPlayerDamage = now
end

-- Pure: credited names at kill time (hit within the credit window), top 20 by total contribution.
function SpireBoss.credited(state, now)
	local list = {}
	for name, h in pairs(state.hits) do
		if now - h.last <= SpireBoss.CREDIT_WINDOW then
			table.insert(list, { name = name, amount = h.total })
		end
	end
	return Floors.rankCredit(list)
end

-- Pure: should the boss reset?
function SpireBoss.shouldReset(state, now, playersInRoom)
	if not state.started then
		return false
	end
	if playersInRoom == 0 then
		state.emptySince = state.emptySince or now
		if now - state.emptySince >= SpireBoss.RESET_EMPTY then
			return true
		end
	else
		state.emptySince = nil
	end
	return now - (state.lastPlayerDamage or now) >= SpireBoss.RESET_NO_DAMAGE
end

-- Pure: enrage damage multiplier given the fight's start time and headcount.
function SpireBoss.enrageMultiplier(state, now)
	if not state.started then
		return 1
	end
	local enrageAt = state.started + Floors.enrageSeconds(state.headcount or 1)
	if now < enrageAt then
		return 1
	end
	local steps = math.floor((now - enrageAt) / SpireBoss.ENRAGE_STEP) + 1
	return 1 + SpireBoss.ENRAGE_BONUS * steps
end

function SpireBoss.newState()
	return { hits = {}, started = nil, headcount = 0, phase = 1, lastPlayerDamage = nil, emptySince = nil, flags = {} }
end

-- Game helpers ---------------------------------------------------------

function SpireBoss.playersInArea(nw, se)
	local list = {}
	local cx, cy = math.floor((nw.x + se.x) / 2), math.floor((nw.y + se.y) / 2)
	local rx, ry = math.ceil((se.x - nw.x) / 2) + 1, math.ceil((se.y - nw.y) / 2) + 1
	for _, c in ipairs(Game.getSpectators(Position(cx, cy, nw.z), false, true, rx, rx, ry, ry)) do
		local p = c:getPosition()
		if p.x >= nw.x and p.x <= se.x and p.y >= nw.y and p.y <= se.y and p.z == nw.z then
			table.insert(list, c)
		end
	end
	return list
end

-- Telegraphed hit: show a warning on the tiles, damage whoever still stands there TELEGRAPH_MS later.
function SpireBoss.markTiles(bossId, tiles, minDmg, maxDmg)
	for _, pos in ipairs(tiles) do
		pos:sendMagicEffect(CONST_ME_REDSMOKE)
	end
	addEvent(function()
		local boss = Creature(bossId)
		if not boss then
			return
		end
		for _, pos in ipairs(tiles) do
			pos:sendMagicEffect(CONST_ME_HITAREA)
			local tile = Tile(pos)
			if tile then
				for _, c in ipairs(tile:getCreatures() or {}) do
					if c:isPlayer() then
						doTargetCombatHealth(boss, c, COMBAT_PHYSICALDAMAGE, minDmg, maxDmg, CONST_ME_DRAWBLOOD)
					end
				end
			end
		end
	end, SpireBoss.TELEGRAPH_MS)
end

function SpireBoss.spawn(name)
	local def = SpireBoss.defs[name]
	if not def or not WorldPoints[def.spawnPoint] then
		logger.error("[Spirebound] boss {} has no spawn point", name)
		return nil
	end
	local m = Game.createMonster(name, WorldPoints[def.spawnPoint], false, true)
	if m then
		SpireBoss.fights[m:getId()] = SpireBoss.newState()
	end
	return m
end
