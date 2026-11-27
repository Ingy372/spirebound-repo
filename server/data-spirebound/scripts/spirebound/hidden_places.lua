-- The Smugglers' Vault and the Sealed Cut in the game (roadmap AD5). Rules: lib/spirebound/floor1_adventure.lua;
-- map: maps/hidden_places.py. The way in is a "door you click" (memory: no push-back teleports): the Vault's barred
-- grate takes a Vault Key, the Sealed Cut's rubble mouth takes the three mason's-mark rubbings; either takes you and
-- your party members within 3 steps inside. Inside, the secret's trigger wakes the beast (SpireTrophies.onSecret).
local H = SpireHidden
local AID_GRATE, AID_MOUTH, AID_MARK = 47160, 47161, 47162
local MARK = 2263 -- a carved stone pillar: the masons' marked stones (placed at start-up, no map edit)

SpireHidden.marks = SpireHidden.marks or {} -- ground id -> position of its marked stone

local function partyNear(player)
	local out, here = { player }, player:getPosition()
	local party = player:getParty()
	if party then
		local members = party:getMembers() or {}
		table.insert(members, party:getLeader())
		for _, p in ipairs(members) do
			if p and p:getId() ~= player:getId() then
				local q = p:getPosition()
				if q.z == here.z and math.max(math.abs(q.x - here.x), math.abs(q.y - here.y)) <= H.PARTY_REACH then
					table.insert(out, p)
				end
			end
		end
	end
	return out
end

local function takeIn(player, dest, text)
	local to = Position(dest.x, dest.y, dest.z)
	for _, p in ipairs(partyNear(player)) do
		p:getPosition():sendMagicEffect(CONST_ME_POFF)
		p:teleportTo(to)
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
	end
	to:sendMagicEffect(CONST_ME_TELEPORT)
end

-- the beast is resting: keep the key / the rubbings and say for how long (rounded up to quarter hours)
local function resting(player, trophyId, what)
	local st = SpireTrophies.state and SpireTrophies.state(trophyId)
	if type(st) == "number" then
		local q = math.ceil(st / 900) * 15
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s Whatever lives down there is resting. Come back in about %d minutes.", what, q))
		return true
	end
	return false
end

-- The Vault's barred grate (use it, or use the Vault Key on it: the cellar's bandits leave their bodies on the grate,
-- and a body on top would take the click; client test 2026-11-27)
local function openGrate(player)
	if player:getItemCount(H.KEY) < 1 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "An iron grate, barred from below. The bar has a keyhole stamped with a coin.")
		return true
	end
	if resting(player, "ironpurse", "Far below, a lamp is out and nothing stirs.") then
		return true
	end
	player:removeItem(H.KEY, 1)
	takeIn(player, WorldPoints.vault_entry, "The Vault Key turns, the bar lifts, and the key snaps in the lock. You climb down a rope ladder.")
	return true
end

local grate = Action()
function grate.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	return openGrate(player)
end
grate:aid(AID_GRATE)
grate:register()

local key = Action()
function key.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local g = WorldPoints.vault_grate
	if g and toPosition and toPosition.x == g.x and toPosition.y == g.y and toPosition.z == g.z then
		return openGrate(player)
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "A heavy key stamped with a coin. It fits no lock here.")
	return true
end
key:id(H.KEY)
key:register()

-- The Sealed Cut's rubble mouth
local mouth = Action()
function mouth.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local missing = H.missingRubbings(function(id) return player:getItemCount(id) end)
	if #missing > 0 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format(
			"Rubble chokes an old cut in the rock. Three mason's marks are scratched round it, and you carry rubbings of %d of them.",
			3 - #missing))
		return true
	end
	if resting(player, "the_unfinished", "You hold the rubbings to the marks, but the stone stays cold.") then
		return true
	end
	for _, gid in ipairs(H.RUBBING_GROUNDS) do
		player:removeItem(H.RUBBINGS[gid], 1)
	end
	takeIn(player, WorldPoints.sealed_cut_entry, "You press the three rubbings to their marks. The rubble shifts aside, and you slip into the cut before it settles again.")
	return true
end
mouth:aid(AID_MOUTH)
mouth:register()

-- The three marked stones: a rubbing each (one of each kind in your bag at a time)
local mark = Action()
function mark.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local gid = item:getCustomAttribute("mark")
	local rid = gid and H.RUBBINGS[gid]
	if not rid then
		return false
	end
	if player:getItemCount(rid) > 0 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You already carry a rubbing of this mark.")
		return true
	end
	SpireGive.reward(player, rid, 1)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You press a sheet against the mason's mark and rub it with charcoal. " ..
		ItemType(rid):getName() .. " added to your backpack.")
	item:getPosition():sendMagicEffect(CONST_ME_POFF)
	return true
end
mark:aid(AID_MARK)
mark:register()

-- start-up: action ids on the two ways in, and the three marked stones beside each ground's middle
function SpireHidden.place()
	local placed = 0
	local g = WorldPoints.vault_grate and Tile(WorldPoints.vault_grate)
	if g and g:getGround() then
		g:getGround():setActionId(AID_GRATE)
		placed = placed + 1
	end
	local mt = WorldPoints.sealed_cut_mouth and Tile(WorldPoints.sealed_cut_mouth)
	local rubble = mt and mt:getTopTopItem()
	if rubble then
		rubble:setActionId(AID_MOUTH)
		rubble:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "Three mason's marks are scratched into the rocks round it.")
		placed = placed + 1
	end
	for _, gid in ipairs(H.RUBBING_GROUNDS) do
		if not H.marks[gid] then
			local spot
			for _, name in ipairs({ "centre_", "loop_%s_b", "loop_%s_c", "camp_" }) do
				local key = name:find("%%s") and name:format(gid) or (name .. gid)
				local c = WorldPoints[key]
				local s = c and SpireQuestObjects.findSpot(c, 10, 1, false)
				if s and SpireRoamers.groundAt(s) == gid then
					spot = s
					break
				end
			end
			if spot then
				local it = Game.createItem(MARK, 1, spot)
				if it then
					it:setActionId(AID_MARK)
					it:setCustomAttribute("mark", gid)
					it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A worn stone with a mason's mark cut deep into it. A rubbing would copy it.")
					H.marks[gid] = spot
					placed = placed + 1
					logger.info("[Spirebound] hidden places: marked stone of {} at {}", gid, spot:toString())
				end
			else
				logger.warn("[Spirebound] hidden places: no room for the marked stone in {}", gid)
			end
		end
	end
	return placed
end

local startup = GlobalEvent("SpireHiddenStartup")
function startup.onStartup()
	logger.info("[Spirebound] hidden places: {} of 5 objects ready", SpireHidden.place())
	return true
end
startup:register()

-- Ironpurse's Tally: +2% gold from your kills
local gold = EventCallback("SpireTrophyGold")
function gold.monsterOnDropLoot(monster, corpse)
	local player = Player(corpse:getCorpseOwner())
	if not player or not corpse:isContainer() then
		return
	end
	local bonus = H.goldBonus(SpireTrophies.have(player))
	if bonus <= 0 then
		return
	end
	local coins = 0
	for i = 0, corpse:getSize() - 1 do
		local it = corpse:getItem(i)
		if it and it:getId() == 3031 then coins = coins + it:getCount() end
		if it and it:getId() == 3035 then coins = coins + 100 * it:getCount() end
	end
	local extra = math.floor(coins * bonus + math.random())
	if extra > 0 then
		corpse:addItem(3031, math.min(100, extra))
	end
end
gold:register()

-- Unfinished Hand: +1 armour (one less damage from every physical hit)
local armour = CreatureEvent("SpireTrophyArmour")
function armour.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	if primaryType == COMBAT_PHYSICALDAMAGE and creature:isPlayer() then
		local a = H.armourBonus(SpireTrophies.have(creature))
		if a > 0 then
			primaryDamage = H.armoured(primaryDamage, a)
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
armour:register()

local login = CreatureEvent("SpireTrophyArmourLogin")
function login.onLogin(player)
	player:registerEvent("SpireTrophyArmour")
	return true
end
login:register()
