-- Upgraded gear needs a level (Jay, 2026-11-27, Q86: "yes"; roadmap QA9). A tier 3 piece needs level 20, tier 4
-- level 25, tier 5 level 30 (SpireGearData.TIER_LEVEL, tools/gen_gear.py). Below that the piece can be carried,
-- traded and stored, but not worn: putting it on is refused, and one that ends up worn anyway (the client's quick
-- equip, or a level lost) goes back into the backpack.

-- Pure: is this inventory position a worn slot (not the backpack slot, not a container)?
function SpireGear.isWornSlot(pos)
	return pos.x == 0xFFFF and pos.y >= CONST_SLOT_FIRST and pos.y <= CONST_SLOT_LAST
		and pos.y ~= CONST_SLOT_BACKPACK -- (a container's position has y >= 0x40)
end

local function tooLowText(need)
	return string.format("You need level %d to wear this at its tier.", need)
end

local function unwear(player, item, need)
	local bp = player:getSlotItem(CONST_SLOT_BACKPACK)
	if bp and item:moveTo(bp) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s needs level %d to wear; it went back into your backpack.", item:getName(), need))
		return true
	end
	return false
end

local move = EventCallback("SpireGearLevelMove")
function move.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if SpireGear.isWornSlot(toPosition) then
		local ok, need = SpireGear.canWield(item, player:getLevel())
		if not ok then
			player:sendCancelMessage(tooLowText(need))
			return false
		end
	end
	return true
end
move:register()

local moved = EventCallback("SpireGearLevelMoved")
function moved.playerOnItemMoved(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if SpireGear.isWornSlot(toPosition) then
		local ok, need = SpireGear.canWield(item, player:getLevel())
		if not ok then
			unwear(player, item, need)
		end
	end
end
moved:register()

-- On login (also after a respawn): nothing worn above the character's level
function SpireGear.checkWorn(player)
	local n = 0
	for slot = CONST_SLOT_FIRST, CONST_SLOT_LAST do
		local item = slot ~= CONST_SLOT_BACKPACK and player:getSlotItem(slot)
		if item then
			local ok, need = SpireGear.canWield(item, player:getLevel())
			if not ok and unwear(player, item, need) then
				n = n + 1
			end
		end
	end
	return n
end

local login = CreatureEvent("SpireGearLevelLogin")
function login.onLogin(player)
	SpireGear.checkWorn(player)
	return true
end
login:register()
