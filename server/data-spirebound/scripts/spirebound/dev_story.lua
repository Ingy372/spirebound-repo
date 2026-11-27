-- Test-only commands for The First Climb (FD1) and the Oathroom (FD3), for the autopilot's Pilot characters.
--   /story reset              forget every chapter, record, choice and Oathroom chest: a fresh start on the story
--   /story where              print where the story objects stand (into the server log and the chat)
--   /story oathend            end the Oathroom run now (everyone inside is put out)
--   /story oathhold n         (tests) the Captain's hall needs only n seconds of waves this run
--   /story oathsafe           (tests) the rune floor's safe path is the middle stone on every row, this run
if os.getenv("SPIRE_DEV") ~= "1" and os.getenv("SPIRE_TESTS") ~= "1" and os.getenv("SPIRE_LOADTEST") ~= "1" then
	logger.info("[Spirebound] {} not loaded: this is not a dev or test server", "the /story test commands")
	return
end

local story = TalkAction("/story")
function story.onSay(player, words, param)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	if not email or not email:match("^autopilot%d*@localhost$") then
		return false
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	local say = function(t) player:sendTextMessage(MESSAGE_STATUS, "story: " .. t) end
	if cmd == "reset" then
		for _, c in ipairs(SpireFirstClimb.CHAPTERS) do
			player:setStorageValue(c.storage, -1)
			player:setStorageValue(c.killStorage, -1)
		end
		player:setStorageValue(SpireOathroom.QUEST.storage, -1)
		player:setStorageValue(SpireOathroom.QUEST.killStorage, -1)
		local fc = player:kv():scoped("spirebound-fc")
		for _, k in ipairs(fc:keys() or {}) do
			fc:remove(k)
		end
		local oath = player:kv():scoped("spirebound-oath")
		for _, k in ipairs(oath:keys() or {}) do
			oath:remove(k)
		end
		local col = player:kv():scoped("spirebound-collect")
		col:remove("fc_tally")
		col:remove("fc_pages")
		say("the First Climb starts over")
	elseif cmd == "where" then
		for k, pos in pairs(SpireFirstClimb.placed or {}) do
			say(string.format("%s at %d, %d, %d", k, pos.x, pos.y, pos.z))
		end
	elseif cmd == "oathend" then
		SpireOathroom.endRun("A test ended the run.")
		say("oath run ended")
	elseif cmd == "oathsafe" then -- (tests) the rune floor's safe stone is the middle one (lane 3) on every row, this run
		if SpireOathroom.run then
			for i = 1, SpireOathroom.RUNE_ROWS do
				SpireOathroom.run.path[i] = 3
			end
		end
		say("rune path: lane 3")
	elseif cmd == "oathhold" then
		SpireOathroom.HOLD = tonumber(rest) or SpireOathroom.HOLD
		say("hold " .. SpireOathroom.HOLD)
	else
		say("reset | where | oathend | oathhold n")
	end
	return true
end
story:separator(" ")
story:groupType("normal")
story:register()
