-- Quivers (Jay's playtest, 2026-11-13: "there is no way to equip arrows for the ranger").
-- In this game version a bow or crossbow only fires arrows or bolts from a QUIVER worn in the shield hand; the old
-- arrow slot doesn't take them. Rangers get a quiver with their arrows inside it; Rangers made before this fix get
-- one at their next login. Fletcher Tamsin sells more.
SpireQuiver = { ID = 35562 }

function SpireQuiver.give(player, arrows)
	-- HB (2026-11-25): worn straight away when the shield hand is free, so a new Ranger's bow fires at once
	-- SpireGive ignores carrying weight: a low-level Ranger once lost the quiver to the floor (Grok session 3)
	local q = SpireGive.item(player, SpireQuiver.ID, 1, CONST_SLOT_RIGHT)
	local worn = player:getSlotItem(CONST_SLOT_RIGHT)
	local free = q ~= nil and worn ~= nil and worn:getId() == SpireQuiver.ID
	if q and arrows and arrows > 0 then
		SpireGive.into(q, 3447, arrows)
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, (free and "Your quiver is on your shield hand: " or "Your arrows go in the quiver: wear the quiver in your shield hand, and ")
		.. "your bow fires from it. Fletcher Tamsin in Hearthgate sells more arrows and quivers.")
	return q
end

local login = CreatureEvent("SpireQuiverLogin")
function login.onLogin(player)
	local s = player:kv():scoped("spirebound")
	if player:getVocation():getBaseId() == 3 and not s:get("quiverGiven") then
		s:set("quiverGiven", true)
		if player:getItemCount(SpireQuiver.ID) == 0 then
			SpireQuiver.give(player, 0)
		end
	elseif player:getVocation():getBaseId() == 3 and not s:get("quiverRepairS3") then
		-- Grok session 3: Rangers whose starter quiver fell on the Registrar's floor get one now, with arrows
		s:set("quiverRepairS3", true)
		if player:getItemCount(SpireQuiver.ID) == 0 and player:getItemCount(3447) == 0 then
			SpireGive.withRoom(player, function() SpireQuiver.give(player, 100) end)
		end
	end
	return true
end
login:register()
