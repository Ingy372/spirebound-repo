-- Hunting task kill counting and rare-drop announcements.
local kill = CreatureEvent("SpireTaskKill")
function kill.onKill(player, target)
	if not target or not target:isMonster() or target:getMaster() then
		return true
	end
	local s = SpireTasks.scope(player)
	local active = s:get("active")
	if not active then
		return true
	end
	local t = SpireTasks.get(active)
	if t and t.monster == target:getName() and SpireCavebot.botting(player) then
		local half = (s:get("botHalf") or 0) + 1 -- R15: while botting, only every second kill counts
		s:set("botHalf", half % 2)
		if half % 2 == 1 then
			return true
		end
	end
	if t and t.monster == target:getName() then
		local n = (s:get("kills") or 0) + 1
		s:set("kills", n)
		if n == t.count then
			SpirePath.progress(player, "task", 1)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Task complete: " .. t.count .. " " .. t.monster .. "s. Report to Taskmaster Ren in Hearthgate.")
		elseif n < t.count and n % 10 == 0 then
			player:sendTextMessage(MESSAGE_STATUS, string.format("Task: %d of %d %ss.", n, t.count, t.monster))
		end
	end
	return true
end
kill:register()

local login = CreatureEvent("SpireTaskLogin")
function login.onLogin(player)
	player:registerEvent("SpireTaskKill")
	return true
end
login:register()

-- Rare drops (2% chance or less) are announced to the looter and their party
local rare = EventCallback("SpireRareDrops")
function rare.monsterPostDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	local mType = monster:getType()
	if not owner or not mType then
		return
	end
	local rareIds = {}
	for _, l in ipairs(mType:getLoot() or {}) do
		if l.chance and l.chance <= 2000 and l.itemId then
			rareIds[l.itemId] = true
		end
	end
	for i = 0, corpse:getSize() - 1 do
		local item = corpse:getItem(i)
		if item and rareIds[item:getId()] then
			local text = string.format("Rare drop! %s found %s on %s.", owner:getName(), item:getName(), monster:getName())
			local party = owner:getParty()
			if party then
				for _, m in ipairs(party:getMembers()) do m:sendTextMessage(MESSAGE_LOOT, text) end
				party:getLeader():sendTextMessage(MESSAGE_LOOT, text)
			else
				owner:sendTextMessage(MESSAGE_LOOT, text)
			end
		end
	end
end
rare:register()
