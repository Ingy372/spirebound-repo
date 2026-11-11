-- Journal window requests from the client (roadmap 6.1). Builders: lib/spirebound/journal.lua
local opcode = CreatureEvent("SpireJournalOpcode")
function opcode.onExtendedOpcode(player, op, buffer)
	if op ~= SpireClient.OPCODE then
		return true
	end
	local tab = SpireJournal.tabFromRequest(buffer)
	if tab then
		local reply = SpireJournal.build(player, tab)
		if reply then
			SpireClient.send(player, reply)
		end
	end
	return true
end
opcode:register()

local login = CreatureEvent("SpireJournalLogin")
function login.onLogin(player)
	player:registerEvent("SpireJournalOpcode")
	return true
end
login:register()

-- Typing !journal tells players where the window is (the client opens it with the J key)
local cmd = TalkAction("!journal")
function cmd.onSay(player, words, param)
	player:sendTextMessage(MESSAGE_STATUS, "Press J to open your Journal: secrets, fishing log, quests, hunting task, top climbers and the Memorial.")
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()
