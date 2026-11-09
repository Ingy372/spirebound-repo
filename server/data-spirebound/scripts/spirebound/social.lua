-- !lfg: flag yourself as looking for a guild (Guildwarden Sela lists you for guild leaders).
local lfg = TalkAction("!lfg")
function lfg.onSay(player, words, param)
	local s = player:kv():scoped("spirebound-social")
	local on = not s:get("lfg")
	s:set("lfg", on)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, on and "You're now listed as looking for a guild. Guild leaders can see you at Guildwarden Sela. Try the 'Looking for Group' channel too." or "You're no longer listed as looking for a guild.")
	return false
end
lfg:groupType("normal")
lfg:register()
