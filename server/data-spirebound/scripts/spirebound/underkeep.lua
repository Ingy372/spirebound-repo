-- The Underkeep, Wing 1 (DESIGN.md 3.4). Entry is the secret "The Underkeep" (s1, scripts/spirebound/secrets.lua).
-- Daily strongbox: once per character per day, gold + a chance at a gem.
local DAILY = 20 * 3600

local box = Action()
function box.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local s = player:kv():scoped("spirebound-underkeep")
	local last = s:get("box1") or 0
	if os.time() - last < DAILY then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The strongbox is empty. It refills every day.")
		return true
	end
	s:set("box1", os.time())
	player:addMoney(math.random(800, 1500))
	if math.random(100) <= 25 then
		player:addItem(math.random(2) == 1 and 3029 or 3032, 1)
	end
	item:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You open the old strongbox. Come back tomorrow for more.")
	return true
end
box:position(WorldPoints.underkeep_chest)
box:register()

-- Wings 2-6 open one by one as the tower climbs (DESIGN.md 3.4). Until then, the portal into the wing is a boulder.
local TELEPORT, BOULDER = 1949, 1772

local function setWing(wid, open)
	local src, dest, req = WorldPoints["uk_door" .. wid], WorldPoints["uk_door" .. wid .. "_dest"], WorldPoints["uk_wing" .. wid .. "_req"]
	if not src or not dest or not req then
		return
	end
	local tile = Tile(src)
	if not tile then
		return
	end
	local tp, rock = tile:getItemById(TELEPORT), tile:getItemById(BOULDER)
	if open and rock then
		rock:remove()
		local t = Game.createItem(TELEPORT, 1, src)
		if t and t.setDestination then
			t:setDestination(dest)
		end
		Game.broadcastMessage("A deeper wing of the Underkeep has opened: Wing " .. wid .. ".", MESSAGE_EVENT_ADVANCE)
	elseif not open and tp then
		tp:remove()
		Game.createItem(BOULDER, 1, src)
	end
end

function SpireUnderkeep_refresh()
	for wid = 2, 6 do
		local req = WorldPoints["uk_wing" .. wid .. "_req"]
		if req then
			setWing(wid, Floors.isOpen(req.x))
		end
	end
end

local startup = GlobalEvent("SpireUnderkeepStartup")
function startup.onStartup()
	SpireUnderkeep_refresh()
	return true
end
startup:register()

local check = GlobalEvent("SpireUnderkeepCheck")
function check.onThink(interval)
	SpireUnderkeep_refresh()
	return true
end
check:interval(60000)
check:register()
