-- !language en|pt|es: pick the language of Spirebound's server messages and the Journal (roadmap 6.3).
local login = CreatureEvent("SpireLanguageLogin")
function login.onLogin(player)
	SpireI18n.load(player)
	SpireClient.send(player, { t = "lang", lang = SpireI18n.langOf(player) })
	return true
end
login:register()

local cmd = TalkAction("!language")
function cmd.onSay(player, words, param)
	local pick = param:lower():gsub("%s", "")
	if SpireI18n.LANGS[pick] then
		SpireI18n.setLang(player, pick)
		SpireClient.send(player, { t = "lang", lang = pick })
		player:sendTextMessage(MESSAGE_STATUS, "Language set to " .. SpireI18n.LANGS[pick] .. ".")
	else
		player:sendTextMessage(MESSAGE_STATUS, "Say !language en, !language pt (Português) or !language es (Español).")
	end
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()
