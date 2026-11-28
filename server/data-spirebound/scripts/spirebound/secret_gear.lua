-- Secret gear in the game (adventure layer 4.1). Rules: lib/spirebound/gear.lua (secret gear section).
-- Bonuses follow what is worn. Since Jay's answer of 2026-11-27 (Q100: "secret gear can be traded.") the pieces
-- trade, drop, store and sell like any other gear; only a secret makes a new one.

local function refresh(player)
	local pid = player:getId()
	addEvent(function()
		local p = Player(pid)
		if p then
			SpireGear.applySecret(p)
		end
	end, 50)
end

local moved = EventCallback("SpireSecretGearMoved")
function moved.playerOnItemMoved(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if fromPosition.x == 0xFFFF or toPosition.x == 0xFFFF then
		refresh(player)
	end
end
moved:register()

-- Pieces found before Q100 still say "Bound to its finder"; give them the current text.
local function retext(item)
	local g = SpireGear.secretOf(item)
	if g then
		item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, SpireGear.secretText(g))
	end
end

local login = CreatureEvent("SpireSecretGearLogin")
function login.onLogin(player)
	for slot = CONST_SLOT_FIRST, CONST_SLOT_LAST do
		local item = player:getSlotItem(slot)
		if item then
			retext(item)
			if item:isContainer() then
				for _, inner in ipairs(item:getItems(true) or {}) do
					retext(inner)
				end
			end
		end
	end
	refresh(player)
	return true
end
login:register()
