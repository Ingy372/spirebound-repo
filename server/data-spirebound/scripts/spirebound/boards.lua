-- !memorial  -> the Death Game Memorial: every Death Game climber who fell this season
-- !top [normal|hardcore|deathgame] -> the top 20 climbers by experience
local memorial = TalkAction("!memorial")
function memorial.onSay(player, words, param)
	local lines = SpireBoards.memorialLines(SpireBoards.memorial())
	local text = "The Memorial\nDeath Game climbers who fell this season.\n\n"
	if #lines == 0 then
		text = text .. "No names yet. May it stay that way."
	else
		text = text .. table.concat(lines, "\n", 1, math.min(#lines, 100))
	end
	player:showTextDialog(2821, text)
	return false
end
memorial:separator(" ")
memorial:groupType("normal")
memorial:register()

local MODES = { normal = 1, hardcore = 2, deathgame = 3, ["death"] = 3 }
local top = TalkAction("!top")
function top.onSay(player, words, param)
	local key = param:lower():gsub("%s", "")
	local mode = MODES[key]
	local title = mode and ("Top climbers: " .. Difficulty.names[mode]) or "Top climbers"
	local lines = SpireBoards.rankLines(SpireBoards.rows(), mode)
	local text = title .. "\n(\"!top normal\", \"!top hardcore\", \"!top deathgame\")\n\n" .. (#lines > 0 and table.concat(lines, "\n") or "Nobody yet.")
	player:showTextDialog(2821, text)
	return false
end
top:separator(" ")
top:groupType("normal")
top:register()
