-- Quivers (Jay's playtest, 2026-11-13: "there is no way to equip arrows for the ranger").
-- In this game version a bow or crossbow only fires arrows or bolts from a QUIVER worn in the shield hand; the old
-- arrow slot doesn't take them. Rangers get a quiver with their arrows inside it; Rangers made before this fix get
-- one at their next login. Fletcher Tamsin sells more.
SpireQuiver = { ID = 35562 }

function SpireQuiver.give(player, arrows)
	local q = player:addItem(SpireQuiver.ID, 1)
	if q and arrows and arrows > 0 then
		q:addItem(3447, arrows)
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your arrows go in the quiver: wear the quiver in your shield hand, "
		.. "and your bow fires from it. Fletcher Tamsin in Hearthgate sells more arrows and quivers.")
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
	elseif player:getVocation():getBaseId() == 3 then
		return true
	end
	return true
end
login:register()
