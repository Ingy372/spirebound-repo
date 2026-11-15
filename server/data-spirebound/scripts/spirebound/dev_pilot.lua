-- The test autopilot (tools/autopilot.py, client module game_autopilot): lets Claude's test characters jump to the
-- start of a test route and heal between runs, so a run tests the place, not the walk there.
-- Only works on the local test account whose e-mail is autopilot@localhost (server/sql/dev_accounts.sql). The sign-up
-- page refuses any e-mail without a real domain, so no player can ever have that account; for everyone else the words
-- are ordinary chat.
--   /pilot jump x, y, z    go there
--   /pilot heal            full health and mana
local pilot = TalkAction("/pilot")

function pilot.onSay(player, words, param)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	if email ~= "autopilot@localhost" then
		return false -- not a dev account: the words go out as ordinary chat, as if the command did not exist
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	if cmd == "jump" then
		local x, y, z = rest:match("(%d+)%D+(%d+)%D+(%d+)")
		local to = x and Position(tonumber(x), tonumber(y), tonumber(z))
		if not to or not Tile(to) then
			player:sendCancelMessage("pilot: no such place")
			return true
		end
		player:teleportTo(to)
		player:sendTextMessage(MESSAGE_STATUS, "pilot: jumped")
	elseif cmd == "heal" then
		player:addHealth(player:getMaxHealth())
		player:addMana(player:getMaxMana())
		player:sendTextMessage(MESSAGE_STATUS, "pilot: healed")
	else
		player:sendCancelMessage("pilot: jump x, y, z | heal")
	end
	return true -- handled: the client showed "/pilot ..." as normal chat when this returned false
end

pilot:separator(" ")
pilot:groupType("normal")
pilot:register()
