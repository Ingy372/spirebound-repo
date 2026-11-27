-- Rare roaming monsters in the game (roadmap AD4). Rules and numbers: lib/spirebound/roamers.lua, tools/gen_adventure.py.
local D = SpireAdventureData
local R = SpireRoamers

local timer = nil   -- addEvent id of the next appearance
local watch = nil   -- addEvent id of the sighting / expiry check

local function removeAll(cur)
	for _, cid in ipairs(cur.guards or {}) do
		local g = Creature(cid)
		if g then
			g:getPosition():sendMagicEffect(CONST_ME_POFF)
			g:remove()
		end
	end
	local m = Creature(cur.cid)
	if m then
		m:getPosition():sendMagicEffect(CONST_ME_POFF)
		m:remove()
	end
end

local function schedule(seconds)
	if timer then
		stopEvent(timer)
	end
	timer = addEvent(function()
		timer = nil
		R.spawnNext()
	end, (seconds or R.delay(math.random())) * 1000)
end

-- Every 2 seconds while a roamer is out: the first player within sight hears "sighted"; at 15 minutes it leaves.
local function check()
	watch = nil
	local cur = R.current
	if not cur then
		return
	end
	local m = Creature(cur.cid)
	if not m then
		R.current = nil
		return
	end
	if os.time() - cur.at >= D.roamerStays then
		removeAll(cur)
		R.current = nil
		Game.broadcastMessage(R.goneLine(cur.roamer), MESSAGE_EVENT_ADVANCE)
		logger.info("[Spirebound] roamer {} slipped away from {}", cur.roamer.name, cur.ground)
		schedule()
		return
	end
	if not cur.seen then
		local pos = m:getPosition()
		for _, p in ipairs(Game.getSpectators(pos, false, true, D.roamerSight, D.roamerSight, D.roamerSight, D.roamerSight)) do
			if p:getPosition().z == pos.z then
				cur.seen = p:getName()
				R.say("roamer_seen", nil, cur.roamer.name, R.groundTitle(cur.ground))
				break
			end
		end
	end
	watch = addEvent(check, 2000)
end

-- Bring a roamer out (id or name; ground and spot picked at random if not given). Returns the monster or nil, why.
function R.spawn(id, gid, pos)
	local r = R.get(id)
	if not r then
		return nil, "no such roamer"
	end
	if R.current and Creature(R.current.cid) then
		return nil, R.current.roamer.name .. " is already out"
	end
	if not pos then
		local grounds = {}
		for _, x in ipairs(r.grounds) do
			if (not gid or x == gid) and #R.spots(x) > 0 then
				table.insert(grounds, x)
			end
		end
		if #grounds == 0 then
			return nil, "no spot for " .. r.name
		end
		gid = grounds[math.random(#grounds)]
		local spots = R.spots(gid)
		local spot = spots[math.random(#spots)]
		pos = Position(spot.x, spot.y, spot.z)
	end
	gid = gid or R.groundAt(pos)
	local m = Game.createMonster(r.name, pos, true, true)
	if not m then
		return nil, "could not place " .. r.name
	end
	local cur = { roamer = r, cid = m:getId(), ground = gid or "?", at = os.time(), guards = {} }
	for _, gd in ipairs(r.guards or {}) do
		for _ = 1, gd.count do
			local g = Game.createMonster(gd.name, pos, true, false)
			if g then
				table.insert(cur.guards, g:getId())
			end
		end
	end
	R.current = cur
	pos:sendMagicEffect(CONST_ME_TELEPORT)
	logger.info("[Spirebound] roamer {} out in {} at {}", r.name, gid or "?", pos:toString())
	if watch then
		stopEvent(watch)
	end
	watch = addEvent(check, 2000)
	return m
end

function R.spawnNext()
	local r = D.roamers[math.random(#D.roamers)]
	local m, why = R.spawn(r.id)
	if not m then
		logger.warn("[Spirebound] roamer: {}", why or "?")
		schedule()
	end
end

-- The kill: loot in the body, credit and keepsakes for everyone on the credit list, the server-wide line
local death = CreatureEvent("SpireRoamerDeath")
function death.onDeath(creature, corpse, killer, mostDamageKiller)
	local r = R.byName(creature:getName())
	if not r then
		return true
	end
	local cur = R.current
	local gid = cur and cur.cid == creature:getId() and cur.ground or nil
	if cur and cur.cid == creature:getId() then
		R.current = nil
		schedule()
	end
	if corpse and corpse:isContainer() then
		local plat, gold = R.coins(r.purse)
		if plat > 0 then corpse:addItem(3035, plat) end
		if gold > 0 then corpse:addItem(3031, gold) end
		corpse:addItem(D.rough, D.roamerShards)
		if math.random() < D.roamerEmber then
			corpse:addItem(D.ember, 1)
		end
	end
	local players, names = {}, {}
	for cid in pairs(creature:getDamageMap()) do
		local p = Player(cid)
		if p then
			table.insert(players, p)
			table.insert(names, p)
		end
	end
	if #players == 0 then
		return true
	end
	R.say("roamer_killed", names, r.name, gid and R.groundTitle(gid) or nil)
	if SpireFinds and SpireFinds.first then
		SpireFinds.first("roamer", r.id, players, r.name)
	end
	for _, p in ipairs(players) do
		if SpireDiscoveries and SpireDiscoveries.mark then
			SpireDiscoveries.mark(p, "roamer", r.id)
		end
		if R.creditKill(p, r) and SpireFinds and SpireFinds.announce then
			SpireFinds.announce("rare_weapon", { p }, r.keepsakeName, nil)
		end
	end
	return true
end
death:register()

-- The Frenzied Boar speeds up as it is hurt: faster at two thirds and again at one third of its health
local frenzy = {}
local hurt = CreatureEvent("SpireRoamerHurt")
function hurt.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local after = creature:getHealth() - math.abs(primaryDamage) - math.abs(secondaryDamage)
	local stage = after <= creature:getMaxHealth() / 3 and 2 or (after <= creature:getMaxHealth() * 2 / 3 and 1 or 0)
	local had = frenzy[creature:getId()] or 0
	if stage > had then
		frenzy[creature:getId()] = stage
		creature:changeSpeed(40 * (stage - had))
		creature:say(stage == 2 and "The Frenzied Boar is in a blind fury!" or "The Frenzied Boar's crest flares red!", TALKTYPE_MONSTER_SAY)
		creature:getPosition():sendMagicEffect(CONST_ME_HITBYFIRE)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hurt:register()

local startup = GlobalEvent("SpireRoamersStartup")
function startup.onStartup()
	if SpireDiscoveries and SpireDiscoveries.register then
		for _, r in ipairs(D.roamers) do
			SpireDiscoveries.register("roamer", r.id, r.name, 1)
		end
	end
	schedule()
	return true
end
startup:register()

-- GM: /roamer list | /roamer <name> [here] | /roamer away
local gm = TalkAction("/roamer")
function gm.onSay(player, words, param)
	param = param:gsub("^%s+", ""):gsub("%s+$", "")
	if param == "" or param == "list" then
		local cur = R.current
		local lines = { cur and string.format("Out now: %s in %s (%d s left).", cur.roamer.name, cur.ground, D.roamerStays - (os.time() - cur.at)) or "No roamer out." }
		for _, r in ipairs(D.roamers) do
			table.insert(lines, string.format("%s (levels %d-%d): %s", r.name, r.lo, r.hi, table.concat(r.grounds, ", ")))
		end
		player:showTextDialog(D.mapItem, table.concat(lines, "\n"))
		return false
	end
	if param == "away" then
		if R.current then
			R.current.at = os.time() - D.roamerStays
		end
		return false
	end
	local here = param:match("%s+here$")
	local name = param:gsub("%s+here$", "")
	local m, why = R.spawn(name, nil, here and player:getPosition() or nil)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, m and ("Roamer out: " .. m:getName() .. " at " .. m:getPosition():toString()) or why)
	return false
end
gm:separator(" ")
gm:groupType("god")
gm:register()
