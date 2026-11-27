-- Finds, auras, titles and the Discoveries page in the game (adventure layer 4.1-4.3, 4.6).
-- Rules: lib/spirebound/finds.lua, discoveries.lua, auras.lua.
--   !finds               the Floor 1 Discoveries page (same as the Journal tab)
--   !finds anonymous     hide (or show again) your name in server-wide find lines
--   !aura <name|off>     choose which of your auras shows, or none
--   !title <name|off>    choose the title others see when they look at you

-- ---------------------------------------------------------------- the Discoveries rows of Floor 1
-- Categories that keep their own record are read from it (nothing is marked twice)
SpireDiscoveries.sources.secret = function(player, id)
	return player:kv():scoped("spirebound-secrets"):get(id)
end
SpireDiscoveries.sources.beast = function(player, id)
	return player:kv():scoped("spirebound"):get("trophy_" .. id)
end
SpireDiscoveries.sources.fish = function(player, id)
	local e = SpireFishing.log(player):get(id)
	return e and (e.count or 0) > 0 and (e.first or true) or nil
end
SpireDiscoveries.sources.stone = function(player, id)
	return SpireQuests.collected(player, "builders")[id]
end
SpireDiscoveries.sources.chest = function(player, id)
	local rec = player:kv():scoped("spirebound-chests"):get(id)
	if rec and (rec.first or rec.last) then
		return (rec.first and rec.first > 0) and rec.first or rec.last or true
	end
end


function SpireFinds.registerFloorRows()
	for _, s in ipairs(SpireSecrets.list) do
		SpireDiscoveries.register("secret", s.id, s.name, s.floor)
	end
	for _, t in ipairs(SpireTrophies.LIST) do
		SpireDiscoveries.register("beast", t.id, t.boss, t.floor or 1)
	end
	local elites = {}
	for name in pairs(SpireFinds.ELITE_NAMES) do
		table.insert(elites, name)
	end
	table.sort(elites)
	for _, name in ipairs(elites) do
		SpireDiscoveries.register("elite", name, name, SpireFinds.ELITE_NAMES[name])
	end
	local chests = {}
	for name in pairs(WorldPoints) do
		if name:sub(1, 6) == "chest_" then
			table.insert(chests, name:sub(7))
		end
	end
	table.sort(chests)
	for _, gid in ipairs(chests) do
		for _, g in ipairs(SpireWilds.grounds) do
			if g.id == gid then
				SpireDiscoveries.register("chest", gid, g.title:gsub("^The ", "") .. " chest", 1)
			end
		end
	end
	for floor, list in pairs(SpireFishing.tables) do
		for _, f in ipairs(list) do
			if not f.junk and not f.treasure then
				SpireDiscoveries.register("fish", f.id, f.name, floor)
			end
		end
	end
	local titles = {}
	for _, g in ipairs(SpireWilds.grounds) do
		titles[g.id] = g.title
	end
	for _, st in ipairs(SpireQuestObjects and SpireQuestObjects.STONES or {}) do
		SpireDiscoveries.register("stone", st.id, "Builders' stone, " .. (titles[st.id] or st.id):gsub("^The ", ""), 1)
	end
end

local startup = GlobalEvent("SpireDiscoveriesStartup")
function startup.onStartup()
	SpireFinds.registerFloorRows() -- at start-up, so rows other scripts add at load time (s14, s15...) are in too
	return true
end
startup:register()

-- ---------------------------------------------------------------- titles and the look line
-- The title others see: the one chosen with !title, else the most recently earned
function SpireFinds.titles(player)
	local store = player:kv():scoped("spirebound-titles")
	local ok, keys = pcall(function() return store:keys() end)
	local out = {}
	for _, k in ipairs(ok and keys or {}) do
		table.insert(out, { name = k, at = store:get(k) or 0 })
	end
	table.sort(out, function(a, b) return a.at > b.at end)
	return out
end

function SpireFinds.shownTitle(player)
	local chosen = player:kv():scoped("spirebound"):get("title_on")
	if chosen == "off" then
		return nil
	end
	local list = SpireFinds.titles(player)
	for _, t in ipairs(list) do
		if t.name == chosen then
			return t.name
		end
	end
	return list[1] and list[1].name or nil
end

-- Pure: the extra lines when you look at a player. info = { title, trophies = {names}, secrets = n, firsts = n }
function SpireFinds.lookText(name, info)
	local parts = {}
	if info.title then
		table.insert(parts, "Title: " .. info.title .. ".")
	end
	if info.trophies and #info.trophies > 0 then
		table.insert(parts, "Trophies: " .. table.concat(info.trophies, ", ") .. ".")
	end
	if (info.secrets or 0) > 0 then
		table.insert(parts, "Secrets found: " .. info.secrets .. ".")
	end
	if (info.firsts or 0) > 0 then
		table.insert(parts, "First finder (" .. info.firsts .. ").")
	end
	if #parts == 0 then
		return nil
	end
	return name .. "'s record: " .. table.concat(parts, " ") -- (not "Name: ...", which reads like something they said)
end

function SpireFinds.lookInfo(target)
	local trophies = {}
	local have = SpireTrophies.have(target)
	for _, t in ipairs(SpireTrophies.LIST) do
		if have[t.id] then
			table.insert(trophies, t.name)
		end
	end
	return {
		title = SpireFinds.shownTitle(target),
		trophies = trophies,
		secrets = #SpireSecrets.foundList(target),
		firsts = target:kv():scoped("spirebound-firsts"):get("all") or 0,
	}
end

local look = EventCallback("SpireLookAtPlayer")
function look.playerOnLook(player, thing, position, distance)
	if not thing or not thing.isPlayer or not thing:isPlayer() then
		return
	end
	local text = SpireFinds.lookText(thing:getName(), SpireFinds.lookInfo(thing))
	if text then
		local pid = player:getId()
		addEvent(function() -- after the engine's own "You see ..." line
			local p = Player(pid)
			if p then
				p:sendTextMessage(MESSAGE_LOOK, text)
			end
		end, 50)
	end
end
look:register()

-- ---------------------------------------------------------------- commands
local finds = TalkAction("!finds")
function finds.onSay(player, words, param)
	local p = (param or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
	if p == "anonymous" or p == "anon" then
		local on = not SpireFinds.isAnonymous(player)
		SpireFinds.setAnonymous(player, on)
		player:sendTextMessage(MESSAGE_STATUS, on and "Your name is now hidden in find announcements (\"Someone found ...\"). Say !finds anonymous again to show it."
			or "Your name shows in find announcements again.")
		return false
	end
	local lines = SpireDiscoveries.lines(player, 1)
	table.insert(lines, "")
	table.insert(lines, "(Say !finds anonymous to hide your name when you find something rare.)")
	player:showTextDialog(2823, table.concat(lines, "\n"):sub(1, 4000))
	return false
end
finds:separator(" ")
finds:groupType("normal")
finds:register()

local aura = TalkAction("!aura")
function aura.onSay(player, words, param)
	local p = (param or ""):gsub("^%s+", ""):gsub("%s+$", "")
	local owned = SpireAuras.owned(player)
	if p:lower() == "off" then
		SpireAuras.setActive(player, nil)
		player:sendTextMessage(MESSAGE_STATUS, "Your aura is off. Say !aura and a name to show one again.")
		return false
	end
	if p == "" then
		if #owned == 0 then
			player:sendTextMessage(MESSAGE_STATUS, "You have no aura yet. Auras come from the tower's secrets and from being first.")
			return false
		end
		local names = {}
		for _, a in ipairs(owned) do
			table.insert(names, a.name)
		end
		local on = SpireAuras.active(player)
		player:sendTextMessage(MESSAGE_STATUS, string.format("Your auras: %s. Showing: %s. Say !aura <name> or !aura off.", table.concat(names, ", "), on and on.name or "none"))
		return false
	end
	local a = SpireAuras.match(p)
	if not a or not SpireAuras.has(player, a.id) then
		player:sendTextMessage(MESSAGE_STATUS, "You don't have that aura.")
		return false
	end
	SpireAuras.setActive(player, a.id)
	player:getPosition():sendMagicEffect(a.effects[1])
	player:sendTextMessage(MESSAGE_STATUS, "Now showing: " .. a.name .. ".")
	return false
end
aura:separator(" ")
aura:groupType("normal")
aura:register()

local title = TalkAction("!title")
function title.onSay(player, words, param)
	local p = (param or ""):gsub("^%s+", ""):gsub("%s+$", "")
	local list = SpireFinds.titles(player)
	if p:lower() == "off" then
		player:kv():scoped("spirebound"):set("title_on", "off")
		player:sendTextMessage(MESSAGE_STATUS, "Others no longer see a title on you. Say !title and a name to show one.")
		return false
	end
	if p == "" then
		if #list == 0 then
			player:sendTextMessage(MESSAGE_STATUS, "You have no titles yet.")
			return false
		end
		local names = {}
		for _, t in ipairs(list) do
			table.insert(names, t.name)
		end
		player:sendTextMessage(MESSAGE_STATUS, string.format("Your titles: %s. Shown: %s. Say !title <name> or !title off.", table.concat(names, ", "), SpireFinds.shownTitle(player) or "none"))
		return false
	end
	for _, t in ipairs(list) do
		if t.name:lower() == p:lower() then
			player:kv():scoped("spirebound"):set("title_on", t.name)
			player:sendTextMessage(MESSAGE_STATUS, "Others now see your title: " .. t.name .. ".")
			return false
		end
	end
	player:sendTextMessage(MESSAGE_STATUS, "You don't have that title.")
	return false
end
title:separator(" ")
title:groupType("normal")
title:register()

-- ---------------------------------------------------------------- auras on show
local tick = 0
local show = GlobalEvent("SpireAuras")
function show.onThink(interval)
	tick = tick + 1
	for _, p in ipairs(Game.getPlayers()) do
		local a = SpireAuras.active(p)
		if a and (tick % a.every) == (p:getId() % a.every) and not p:isInGhostMode() then
			local fx = a.effects[(math.floor(tick / a.every) % #a.effects) + 1]
			p:getPosition():sendMagicEffect(fx)
		end
	end
	return true
end
show:interval(1000)
show:register()

-- Milestones that came from records kept elsewhere (fish, stones) are checked at login too
local login = CreatureEvent("SpireDiscoveriesLogin")
function login.onLogin(player)
	local pid = player:getId()
	addEvent(function()
		local p = Player(pid)
		if p then
			SpireDiscoveries.checkMilestones(p, 1)
		end
	end, 2000)
	return true
end
login:register()
