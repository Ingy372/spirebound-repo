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
