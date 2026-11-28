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
	FIELD_RESPAWN = 10 * 60, -- field boss (the Gate Hound): every climber needs its credit for the Stair Key (review A4-3)
	FIELD_MIN_SHARE = 0.01, -- a field boss credits from 1% of the fight (a crowd at the Pass all gets the step)
	-- roadmap R9 (REVIEW 3.9, 1.4)
	MIN_SHARE = 0.02, -- you need at least 2% of the fight's total contribution to be credited
	TAKEN_WEIGHT = 0.5, -- damage you soak from the boss counts half
	ROOM_CAP = 20, -- players allowed in a boss room at once
	LETHAL_HIT = 250, -- a marked hit this strong may kill: it gets the longer warning (Q19)
	WARN_LETHAL_MS = 1000,
	LOCKOUT = 20 * 3600, -- private repeat kill: once per character every 20 hours
	PRIVATE_MAX = 5,
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

-- Pure: credited names at kill time: took part within the credit window and did at least MIN_SHARE of everything
-- (damage to the boss, healing of the fighters, half the damage soaked), top 20 by total contribution.
function SpireBoss.credited(state, now, minShare)
	local list, total = {}, 0
	for _, h in pairs(state.hits) do
		total = total + h.total
	end
	for name, h in pairs(state.hits) do
		if now - h.last <= SpireBoss.CREDIT_WINDOW and h.total >= total * (minShare or SpireBoss.MIN_SHARE) then
			table.insert(list, { name = name, amount = h.total })
		end
	end
	return Floors.rankCredit(list)
end

-- Pure: how long a marked hit waits before it lands (Q19: longer for hits that can kill)
function SpireBoss.warningMs(maxDamage)
	return math.abs(maxDamage or 0) >= SpireBoss.LETHAL_HIT and SpireBoss.WARN_LETHAL_MS or SpireBoss.TELEGRAPH_MS
end

-- No calendar on boss doors (Jay, 2026-11-27, Q13: "no set day when the boss doors open. its upon players being
-- ready."): a floor boss's hall opens as soon as its requirements (the Stair Key on Floor 1) are met. The old calendar
-- gate (day 3, then a floor every 6 days) is gone.

-- Pure: may this party start a private repeat kill? members = { { name, lockedAt } }, all = within reach of the leader
function SpireBoss.privateCheck(members, allNear, floorCleared, roomBusy, now)
	if not floorCleared then
		return false, "The private hall opens only after this floor has been cleared."
	end
	if roomBusy then
		return false, "Another party is in the private hall. Try again soon."
	end
	if #members < 1 or #members > SpireBoss.PRIVATE_MAX then
		return false, "Bring a party of 1 to " .. SpireBoss.PRIVATE_MAX .. "."
	end
	if not allNear then
		return false, "Your whole party must stand with you."
	end
	for _, m in ipairs(members) do
		if m.lockedAt and now - m.lockedAt < SpireBoss.LOCKOUT then
			local h = math.ceil((SpireBoss.LOCKOUT - (now - m.lockedAt)) / 3600)
			return false, m.name .. " fought here less than 20 hours ago (" .. h .. " h left)."
		end
	end
	return true
end

-- Titles and rewards for players who were offline at the kill wait for their next login (R9)
local function pending()
	return kv.scoped("spirebound-boss-pending")
end

function SpireBoss.grantTitle(name, title)
	local p = Player(name)
	if p then
		p:kv():scoped("spirebound-titles"):set(title, os.time())
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. title .. ".")
		return true
	end
	local list = pending():get(name) or {}
	table.insert(list, title)
	pending():set(name, list)
	return false
end

function SpireBoss.applyPending(player)
	local list = pending():get(player:getName())
	if not list then
		return 0
	end
	for _, title in ipairs(list) do
		player:kv():scoped("spirebound-titles"):set(title, os.time())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "While you were away, the tower remembered you: title " .. title .. ".")
	end
	pending():remove(player:getName())
	return #list
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

-- Pure: how soon a boss of this kind comes back after a kill, and the share of the fight that earns credit
function SpireBoss.respawnSeconds(kind)
	return kind == "field" and SpireBoss.FIELD_RESPAWN or SpireBoss.REPEAT_RESPAWN
end

function SpireBoss.minShare(kind)
	return kind == "field" and SpireBoss.FIELD_MIN_SHARE or SpireBoss.MIN_SHARE
end

-- A fight record rebuilt from the engine's own damage map (review A4-5: after a script reload the record is gone, and
-- the kill used to give no credit, no unlock and no return). damageMap = creature:getDamageMap(); nameOf(cid) -> the
-- player's name (summons count as their owner) or nil.
function SpireBoss.stateFromDamageMap(damageMap, nameOf, now)
	local state = SpireBoss.newState()
	state.started = now
	for cid, d in pairs(damageMap or {}) do
		local name = nameOf(cid)
		local amount = type(d) == "table" and (d.total or 0) or (tonumber(d) or 0)
		if name and amount > 0 then
			SpireBoss.recordHit(state, name, amount, now)
		end
	end
	return state
end

-- Review A4-6: a boss whose coins should reach every credited fighter, not whoever opens the body, pays each one into
-- the bank (online at once, offline through the database)
function SpireBoss.payCredited(credit, amount, bossName)
	for _, name in ipairs(credit) do
		local p = Player(name)
		if p then
			local bag, bank = SpireGive.gold(p, amount) -- Q76: coins go in the backpack (offline: the bank, below)
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Your share of the %s's hoard: %d gold, %s.", bossName, amount, SpireGive.goldWhere(bag, bank)))
		else
			db.query("UPDATE `players` SET `balance` = `balance` + " .. amount .. " WHERE `name` = " .. db.escapeString(name))
		end
	end
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

-- Telegraphed hit: show a warning on the tiles, damage whoever still stands there after the warning (warningMs).
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
	end, SpireBoss.warningMs(math.max(math.abs(minDmg or 0), math.abs(maxDmg or 0))))
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
