-- Spire Manor in the game (rules: lib/spirebound/manor.lua; map: maps/manor.py).
--   !manor                 what the manor offers
--   !manor travel <floor>  by the Waystone on the roof: to that open floor's town (owner and guests)
--   !manor home            the owner, from inside any town: back to the Waystone

local function manorHouse()
	for _, h in ipairs(Game.getHouses()) do
		if SpireManor.is(h) then
			return h
		end
	end
end
SpireManor.house = manorHouse

-- The owner's name (the engine's house object only knows the owner's number)
function SpireManor.ownerName(house)
	local guid = house:getOwnerGuid()
	local online = Player(guid)
	if online then
		return online:getName()
	end
	local q = db.storeQuery("SELECT `name` FROM `players` WHERE `id` = " .. guid)
	local name = q and Result.getString(q, "name") or nil
	if q then
		Result.free(q)
	end
	return name
end

local function inFight(player)
	return player:isPzLocked() or player:getCondition(CONDITION_INFIGHT, CONDITIONID_DEFAULT) ~= nil
end

local function templeOf(floor)
	return floor == 1 and WorldPoints.temple_hearthgate or WorldPoints["f" .. floor .. "_temple"]
end

local function journey(player, to)
	player:kv():scoped("spirebound"):set("manorWaystone", os.time())
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	player:teleportTo(Position(to.x, to.y, to.z))
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
end

-- Used by the command and by the tests (a real character, the real map)
function SpireManor.travel(player, floor)
	local stone, pos = WorldPoints.manor_waystone, player:getPosition()
	local near = stone ~= nil and pos.z == stone.z and pos:getDistance(stone) <= SpireManor.WAYSTONE_RADIUS
	local ok, why = SpireManor.waystoneOut({ nearStone = near, floor = floor, floorOpen = floor ~= nil and floor >= 1 and Floors.isOpen(floor) and templeOf(floor) ~= nil,
		inFight = inFight(player), lastUse = player:kv():scoped("spirebound"):get("manorWaystone"), now = os.time() })
	if not ok then
		return false, why
	end
	journey(player, templeOf(floor))
	return true, "The Waystone carries you to " .. (Floors.names[floor] or ("Floor " .. floor)) .. "."
end

function SpireManor.home(player)
	local house = manorHouse()
	local ok, why = SpireManor.recall({ isOwner = house ~= nil and house:getOwnerGuid() == player:getGuid(),
		inTown = SpirePvP.zoneAt(player:getPosition()) == "town", inFight = inFight(player),
		lastUse = player:kv():scoped("spirebound"):get("manorWaystone"), now = os.time() })
	if not ok then
		return false, why
	end
	journey(player, WorldPoints.manor_waystone)
	return true, "The Waystone calls you home."
end

local cmd = TalkAction("!manor")
function cmd.onSay(player, words, param)
	local p = (param or ""):lower()
	local floor = p:match("^%s*travel%s+(%d+)")
	if p:match("^%s*travel") then
		local _ok, text = SpireManor.travel(player, tonumber(floor))
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
	elseif p:match("^%s*home") then
		local _ok, text = SpireManor.home(player)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
	else
		local house = manorHouse()
		local owner = house and house:getOwnerGuid() ~= 0 and SpireManor.ownerName(house) or nil
		player:showTextDialog(2821, table.concat(SpireManor.lines(), "\n") .. "\n\n" .. (owner and ("Keeper this season: " .. owner .. ".") or "It has no Keeper this season."))
	end
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()

-- The Keeper's title: given the first time the owner logs in (it stays, like every title)
local login = CreatureEvent("SpireManorLogin")
function login.onLogin(player)
	local house = manorHouse()
	if house and house:getOwnerGuid() == player:getGuid() then
		local titles = player:kv():scoped("spirebound-titles")
		if not titles:get(SpireManor.TITLE) then
			titles:set(SpireManor.TITLE, os.time())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You hold the deed to Spire Manor: you earned the title " .. SpireManor.TITLE .. ". Say !manor to see what your house can do.")
		end
	end
	return true
end
login:register()

-- The manor's furniture is a fixture: tables, racks, the exercise dummies and the rest stay where the map put them
local fixed = EventCallback("SpireManorFixtures")
function fixed.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if item:getActionId() == SpireManor.FIXTURE_AID then
		player:sendCancelMessage("That belongs to Spire Manor.")
		return false
	end
	return true
end
fixed:register()
