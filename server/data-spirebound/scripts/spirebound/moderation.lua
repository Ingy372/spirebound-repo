-- Moderation in game (roadmap R14). Rules and lists: lib/spirebound/moderation.lua.

-- !report <name>, <what happened>
local report = TalkAction("!report")
function report.onSay(player, words, param)
	local about, what = SpireMod.parseReport(param)
	if not about then
		player:sendCancelMessage("Say: !report <name>, <what happened>   (for example: !report Bad Guy, kept blocking the cave)")
		return false
	end
	local n = SpireMod.addReport(player:getName(), about, what)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Thank you. A gamemaster will read your report.")
	for _, p in ipairs(Game.getPlayers()) do
		if p:getGroup():getAccess() then
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Report #%d from %s about %s: %s", n, player:getName(), about, what))
		end
	end
	logger.info("[Spirebound] report from {} about {}: {}", player:getName(), about, what)
	return false
end
report:separator(" ")
report:groupType("normal")
report:register()

-- !rules
local rules = TalkAction("!rules")
function rules.onSay(player, words, param)
	player:showTextDialog(2821, SpireMod.rulesText())
	return false
end
rules:groupType("normal")
rules:register()

-- GM: /mute <name>, <minutes>   /unmute <name>   /reports   /gmlog
local MUTE_SUB = 4900
local mute = TalkAction("/mute")
function mute.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	local name, minutes = (param or ""):match("^%s*([^,]+),%s*(%d+)")
	local target = name and Player(name)
	if not target then
		player:sendCancelMessage("Say: /mute <name>, <minutes>  (the player must be online)")
		return false
	end
	minutes = math.min(tonumber(minutes), 7 * 24 * 60)
	for _, kind in ipairs({ CONDITION_MUTED, CONDITION_CHANNELMUTEDTICKS }) do
		local c = Condition(kind)
		c:setParameter(CONDITION_PARAM_SUBID, MUTE_SUB)
		c:setParameter(CONDITION_PARAM_TICKS, minutes * 60 * 1000)
		target:addCondition(c)
	end
	target:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("A gamemaster has muted you for %d minutes. Say !rules to read the rules.", minutes))
	SpireMod.log(player:getName(), "muted", target:getName(), minutes .. " minutes")
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, target:getName() .. " is muted for " .. minutes .. " minutes.")
	return false
end
mute:separator(" ")
mute:groupType("gamemaster")
mute:register()

local unmute = TalkAction("/unmute")
function unmute.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	local target = Player(param or "")
	if target then
		target:removeCondition(CONDITION_MUTED, CONDITIONID_DEFAULT, MUTE_SUB)
		target:removeCondition(CONDITION_CHANNELMUTEDTICKS, CONDITIONID_DEFAULT, MUTE_SUB)
		SpireMod.log(player:getName(), "unmuted", target:getName())
	end
	return false
end
unmute:separator(" ")
unmute:groupType("gamemaster")
unmute:register()

local reports = TalkAction("/reports")
function reports.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	if param == "clear" then
		kv.scoped("spirebound-reports"):set("open", {})
		SpireMod.log(player:getName(), "cleared reports")
		return false
	end
	local lines = { "Open reports (/reports clear when done):" }
	for i, r in ipairs(SpireMod.reports()) do
		table.insert(lines, string.format("#%d %s, %s about %s: %s", i, os.date("%d %b %H:%M", r.t), r.from, r.about, r.text))
	end
	player:showTextDialog(2821, table.concat(lines, "\n"))
	return false
end
reports:separator(" ")
reports:groupType("gamemaster")
reports:register()

local gmlog = TalkAction("/gmlog")
function gmlog.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	local lines = { "Last GM actions:" }
	for _, e in ipairs(SpireMod.recentLog(30)) do
		table.insert(lines, string.format("%s %s %s %s %s", os.date("%d %b %H:%M", e.t), e.gm, e.action, e.target, e.detail))
	end
	player:showTextDialog(2821, table.concat(lines, "\n"))
	return false
end
gmlog:groupType("gamemaster")
gmlog:register()

-- the rules on a character's first login
local login = CreatureEvent("SpireRulesLogin")
function login.onLogin(player)
	local s = player:kv():scoped("spirebound")
	if not s:get("rulesShown") then
		s:set("rulesShown", true)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Welcome! Say !rules to read the rules, and !report <name>, <what happened> if someone breaks them.")
	end
	return true
end
login:register()
