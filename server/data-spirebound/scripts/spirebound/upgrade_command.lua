-- !upgrade opens the Journal's Upgrade tab (gear progression spec 4.7); !style shows the style tree and makes choices.
-- Both are also one click away in the Journal's Commands tab (rule R19).

local up = TalkAction("!upgrade")
function up.onSay(player, words, param)
	local reply = SpireJournal.build(player, "upgrade")
	reply.open = true
	SpireClient.send(player, reply)
	player:sendTextMessage(MESSAGE_STATUS, SpireUpgrade.nextLine(SpireUpgrade.viewFor(player)))
	return false
end
up:separator(" ")
up:groupType("normal")
up:register()

local confirming = {} -- player id -> style key waiting for "!style confirm"
SpireCleanup.add(function(pid) confirming[pid] = nil end)

local function describeTree(player)
	local voc = player:getVocation():getBaseId()
	local tree = SpireGearData.style[voc]
	if not tree then
		return { "Choose your path with Registrar Maelis first: your style tree comes with it." }
	end
	local v = SpireStyle.get(player)
	local L = { string.format("Your style: %s %d/10.", SpireStyle.stageName(v), v.level) }
	for _, p in ipairs(tree.paths) do
		local mark = (v.path == p.key) and " (yours)" or ""
		table.insert(L, string.format("%s%s: %s. Then %s or %s.", p.name, mark, p.role, p.finals[1].name, p.finals[2].name))
	end
	if v.choiceReady then
		local names = {}
		for _, o in ipairs(v.options) do
			table.insert(names, o.name:lower())
		end
		table.insert(L, "Your choice is ready. Say !style " .. table.concat(names, " or !style ") .. ". It is permanent.")
	else
		table.insert(L, "Your next choice comes when this stage reaches level 10.")
	end
	return L
end

local style = TalkAction("!style")
function style.onSay(player, words, param)
	local pid = player:getId()
	param = (param or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
	if param == "" then
		for _, l in ipairs(describeTree(player)) do
			player:sendTextMessage(MESSAGE_STATUS, l)
		end
		return false
	end
	if param == "confirm" then
		local key = confirming[pid]
		confirming[pid] = nil
		if not key then
			player:sendTextMessage(MESSAGE_STATUS, "Nothing to confirm. Say !style and a style name first.")
			return false
		end
		local ok, msg = SpireStyle.choose(player, key)
		player:sendTextMessage(ok and MESSAGE_EVENT_ADVANCE or MESSAGE_STATUS, msg)
		if ok then
			player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
		end
		return false
	end
	local voc = player:getVocation():getBaseId()
	local v = SpireStyle.get(player)
	for _, o in ipairs(v.options or {}) do
		if o.name:lower() == param or o.key == param:gsub(" ", "_") then
			local ok, msg = SpireStyle.canChoose(voc, v.points, v.path, v.final, o.key)
			if not ok then
				player:sendTextMessage(MESSAGE_STATUS, msg)
				return false
			end
			confirming[pid] = o.key
			player:sendTextMessage(MESSAGE_STATUS, string.format("Choose %s for good? There is no going back. Say !style confirm.", o.name))
			return false
		end
	end
	local key = param:gsub(" ", "_")
	local _, msg = SpireStyle.canChoose(voc, v.points, v.path, v.final, key)
	player:sendTextMessage(MESSAGE_STATUS, msg)
	return false
end
style:separator(" ")
style:groupType("normal")
style:register()

-- At login: the one next step, once
local login = CreatureEvent("SpireUpgradeLogin")
function login.onLogin(player)
	addEvent(function(pid)
		local p = Player(pid)
		if p and p:getVocation():getBaseId() > 0 then
			p:sendTextMessage(MESSAGE_STATUS, SpireUpgrade.nextLine(SpireUpgrade.viewFor(p)) .. " (Journal: Upgrade tab, or !upgrade)")
		end
	end, 3000, player:getId())
	return true
end
login:register()
