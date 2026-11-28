-- Spirebound fishing (lib/spirebound/fishing.lua). Replaces Canary's sample fishing script.
local waterIds = { 629, 630, 631, 632, 633, 634, 4597, 4598, 4599, 4600, 4601, 4602, 4609, 4610, 4611, 4612, 4613, 4614 }
local pending = {} -- playerId -> { biteUntil = ms, pos = Position } or { waitingUntil = ms }
local lastCast = {} -- playerId -> ms of the last cast
SpireFishing.lastCast = lastCast
SpireCleanup.add(function(pid)
	pending[pid], lastCast[pid] = nil, nil
end)

local function nowMs()
	return systemTime and systemTime() or os.time() * 1000 -- milliseconds
end

local function land(player, pos)
	if not player:removeItem(SpireFishing.WORM, 1) then
		player:sendCancelMessage("It got away. You need worms as bait.")
		return
	end
	local floor = math.max(1, Floors.at(pos))
	local night = SpireSecrets.isNight(SpireSecrets.gameHour()) -- review A7-2: the game's hour, as the secrets use
	local luck = (SpireEvents and SpireEvents.fishingLuck(floor) or 1) * (SpireFeatures and SpireFeatures.fishingLuck and SpireFeatures.fishingLuck(pos) or 1) -- FD2: Toad Pond's night spot
	local f = SpireFishing.roll(floor, night, math.random(), luck)
	local forced = SpireFishing.forceNext and SpireFishing.forceNext[player:getId()] -- test servers only (/pilot fishlegend)
	if forced then
		SpireFishing.forceNext[player:getId()] = nil
		for _, row in ipairs(SpireFishing.tables[floor] or {}) do
			if row.id == forced then
				f = row
			end
		end
	end
	if f.bottle and SpireRumours then -- adventure layer 4.7: the note is read at once; the riddle goes to the Journal
		pos:sendMagicEffect(CONST_ME_WATERSPLASH)
		player:addSkillTries(SKILL_FISHING, 2, true)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You fished up a message in a bottle. " .. SpireRumours.openBottle(player))
		return
	end
	SpireGive.reward(player, f.item, f.count or 1) -- never onto the floor when the backpack is full
	player:addSkillTries(SKILL_FISHING, 2, true)
	pos:sendMagicEffect(CONST_ME_WATERSPLASH)
	if f.junk or f.treasure then
		player:sendTextMessage(MESSAGE_LOOT, "You fished up " .. f.name .. ".")
		return
	end
	local kg = f.kg[1] + math.random() * (f.kg[2] - f.kg[1])
	SpirePath.progress(player, "fish", 1)
	SpireChronicle.add(player, "fish", 1)
	local log = SpireFishing.log(player)
	local entry = log:get(f.id) or { count = 0, best = 0 }
	local firstTime = entry.count == 0
	entry.count = entry.count + 1
	entry.first = entry.first or os.time() -- the Discoveries page shows the date of the first catch
	if kg > entry.best then
		entry.best = math.floor(kg * 100) / 100
	end
	log:set(f.id, entry)
	player:sendTextMessage(MESSAGE_LOOT, string.format("You caught a %s (%.2f kg)!%s", f.name, kg, firstTime and " New in your fishing log." or ""))
	if SpireEvents and SpireEvents.derbyCatch then
		SpireEvents.derbyCatch(player, f.name, kg)
	end
	if f.legendary then
		if SpireFinds then -- adventure layer 4.2/4.3: the line (rate-limited, on the board) and the season first
			SpireFinds.announce("fish", { player }, { name = f.name, kg = kg })
			SpireFinds.first("fish", f.id, { player }, f.name)
		else
			Game.broadcastMessage(string.format("%s has landed %s, the legendary fish of Floor %d (%.1f kg)!", player:getName(), f.name, floor, kg), MESSAGE_EVENT_ADVANCE)
		end
	end
	if firstTime then
		local kinds = 0
		for _, row in ipairs(SpireFishing.tables[floor] or {}) do
			if not row.junk and not row.treasure and (log:get(row.id) or { count = 0 }).count > 0 then
				kinds = kinds + 1
			end
		end
		if SpireDiscoveries then
			SpireDiscoveries.checkMilestones(player, floor)
		end
		local title = SpireFishing.titleFor(kinds)
		if title then
			player:kv():scoped("spirebound-titles"):set(title, os.time())
		end
	end
end

local fishing = Action()
function fishing.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if not target or not target.itemid or not table.contains(waterIds, target.itemid) then
		return false
	end
	local pid = player:getId()
	local p = pending[pid]
	local t = nowMs()
	if p and p.biteUntil then
		pending[pid] = nil
		if t <= p.biteUntil then
			land(player, toPosition)
		else
			player:sendCancelMessage("Too slow. It got away.")
		end
		return true
	end
	if p and p.waitingUntil and t < p.waitingUntil then
		player:sendCancelMessage("Your line is already in the water.")
		return true
	end
	if lastCast[pid] and t - lastCast[pid] < SpireFishing.CAST_GAP * 1000 then
		player:sendCancelMessage("Let the water settle a moment before you cast again.")
		return true
	end
	lastCast[pid] = t
	toPosition:sendMagicEffect(CONST_ME_LOSEENERGY)
	player:addSkillTries(SKILL_FISHING, 1, true)
	if math.random(100) > SpireFishing.biteChance(player:getEffectiveSkillLevel(SKILL_FISHING)) then
		pending[pid] = nil
		return true
	end
	local delay = math.random(2000, 6000)
	pending[pid] = { waitingUntil = t + delay }
	addEvent(function(playerId, pos)
		local pl = Player(playerId)
		if not pl then
			pending[playerId] = nil
			return
		end
		pending[playerId] = { biteUntil = nowMs() + SpireFishing.BITE_WINDOW * 1000, pos = pos }
		pos:sendMagicEffect(CONST_ME_WATERSPLASH)
		pl:sendTextMessage(MESSAGE_STATUS, "Something is biting! Use your rod again, quickly!")
	end, delay, pid, toPosition)
	return true
end

fishing:id(3483)
fishing:allowFarUse(true)
fishing:register()
