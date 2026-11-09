-- Guildwarden Sela (Hearthgate): found guilds and arrange consent-based wars (DESIGN.md 6.4 item 6, 7.2).
local npcName = "Guildwarden Sela"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the guildwarden"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 138, lookHead = 79, lookBody = 86, lookLegs = 95, lookFeet = 114, lookAddons = 1 }
npcConfig.flags = { floorchange = false }

local FOUND_COST, FOUND_LEVEL = 20000, 30

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local function isLeader(player)
	local g = player:getGuild()
	return g and player:getGuildLevel() == 3, g
end

local function say(npc, player, text)
	npcHandler:say(text, npc, player)
end

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local lower = msg:lower()
	local now = os.time()

	-- recruiting board (DESIGN.md 6.5: finding a clan was the hardest part)
	if lower == "recruit on" or lower == "recruit off" then
		local leader, guild = isLeader(player)
		if not leader then
			return say(npc, player, "Only a guild leader can post on the recruiting board.")
		end
		kv.scoped("spirebound-recruit"):set(tostring(guild:getId()), lower == "recruit on" and guild:getName() or false)
		return say(npc, player, lower == "recruit on" and "Your guild is on the recruiting board." or "Your guild is off the board.")
	end
	if lower == "guilds" or lower == "recruiting" then
		local names = {}
		local q = db.storeQuery("SELECT `name`, `id` FROM `guilds`")
		if q then
			repeat
				if kv.scoped("spirebound-recruit"):get(tostring(Result.getNumber(q, "id"))) then
					table.insert(names, Result.getString(q, "name"))
				end
			until not Result.next(q)
			Result.free(q)
		end
		return say(npc, player, #names == 0 and "No guild is recruiting right now. Say !lfg to let leaders know you're looking." or ("Recruiting: " .. table.concat(names, ", ") .. "."))
	end
	if lower == "lfg" or lower == "looking" then
		local names = {}
		for _, p in ipairs(Game.getPlayers()) do
			if p:kv():scoped("spirebound-social"):get("lfg") and not p:getGuild() then
				table.insert(names, p:getName() .. " (" .. p:getLevel() .. ")")
			end
		end
		return say(npc, player, #names == 0 and "Nobody is looking for a guild right now." or ("Looking for a guild: " .. table.concat(names, ", ") .. "."))
	end

	-- found <name>
	local newName = msg:match("^[Ff]ound%s+(.+)$")
	if newName then
		newName = newName:gsub("^%s+", ""):gsub("%s+$", "")
		if player:getGuild() then
			return say(npc, player, "You already belong to a guild.")
		elseif player:getLevel() < FOUND_LEVEL then
			return say(npc, player, "Come back at level " .. FOUND_LEVEL .. ".")
		elseif #newName < 3 or #newName > 29 or not newName:match("^[%a][%a ]+$") then
			return say(npc, player, "A guild name must be 3 to 29 letters and spaces.")
		elseif SpireWar.guildByName(newName) then
			return say(npc, player, "That name is taken.")
		elseif not player:removeMoneyBank(FOUND_COST) then
			return say(npc, player, "Founding a guild costs " .. FOUND_COST .. " gold.")
		end
		db.query(string.format("INSERT INTO `guilds` (`name`, `ownerid`, `creationdata`) VALUES (%s, %d, %d)", db.escapeString(newName), player:getGuid(), now))
		local gid = SpireWar.guildByName(newName)
		local q = gid and db.storeQuery(string.format("SELECT `id` FROM `guild_ranks` WHERE `guild_id` = %d AND `level` = 3", gid))
		if q then
			local rank = Result.getNumber(q, "id")
			Result.free(q)
			db.query(string.format("INSERT INTO `guild_membership` (`player_id`, `guild_id`, `rank_id`) VALUES (%d, %d, %d)", player:getGuid(), gid, rank))
		end
		Game.broadcastMessage(string.format("A new guild is founded: %s, led by %s.", newName, player:getName()), MESSAGE_EVENT_ADVANCE)
		return say(npc, player, "It is written. Log out and back in to wear your guild's name.")
	end

	-- war <days> <kill limit or 0> <guild name>
	local days, limit, enemy = lower:match("^war%s+(%d+)%s+(%d+)%s+(.+)$")
	if days then
		local leader, guild = isLeader(player)
		if not leader then
			return say(npc, player, "Only a guild leader can declare war.")
		end
		days, limit = tonumber(days), tonumber(limit)
		local ok, why = SpireWar.validTerms(days, limit)
		if not ok then
			return say(npc, player, why)
		end
		local eid, ename = SpireWar.guildByName(enemy)
		if not eid or eid == guild:getId() then
			return say(npc, player, "I know no such guild.")
		elseif SpireWar.active(guild:getId(), eid) then
			return say(npc, player, "There is already a war or an offer between your guilds.")
		elseif not SpireWar.cooldownOver(SpireWar.lastEnded(guild:getId(), eid), now) then
			return say(npc, player, "Your guilds fought less than 7 days ago. Let the dead rest.")
		elseif not player:removeMoneyBank(SpireWar.FEE) then
			return say(npc, player, "A war offer costs " .. SpireWar.FEE .. " gold.")
		end
		db.query(string.format("INSERT INTO `guild_wars` (`guild1`, `guild2`, `name1`, `name2`, `status`, `started`, `ended`, `frags_limit`, `duration_days`) VALUES (%d, %d, %s, %s, 0, %d, 0, %d, %d)",
			guild:getId(), eid, db.escapeString(guild:getName()), db.escapeString(ename), now, limit, days))
		return say(npc, player, string.format("Your offer is sent: %d days%s. %s's leader must come to me and say {accept} %s.", days, limit > 0 and (", first to " .. limit .. " kills wins") or "", ename, guild:getName()))
	end

	-- accept <guild> / reject <guild>
	local verb, other = lower:match("^(%a+)%s+(.+)$")
	if verb == "accept" or verb == "reject" then
		local leader, guild = isLeader(player)
		if not leader then
			return say(npc, player, "Only a guild leader can answer a war offer.")
		end
		local oid, oname = SpireWar.guildByName(other)
		local q = oid and db.storeQuery(string.format("SELECT `id`, `duration_days` FROM `guild_wars` WHERE `status` = 0 AND `guild1` = %d AND `guild2` = %d", oid, guild:getId()))
		if not q then
			return say(npc, player, "There is no war offer from that guild.")
		end
		local wid, wdays = Result.getNumber(q, "id"), Result.getNumber(q, "duration_days")
		Result.free(q)
		if verb == "reject" then
			db.query(string.format("UPDATE `guild_wars` SET `status` = 2, `ended` = %d WHERE `id` = %d", now, wid))
			return say(npc, player, "Refused. No war today.")
		end
		if not player:removeMoneyBank(SpireWar.FEE) then
			return say(npc, player, "Accepting costs " .. SpireWar.FEE .. " gold, the same as the offer.")
		end
		db.query(string.format("UPDATE `guild_wars` SET `status` = 1, `started` = %d, `ended` = %d WHERE `id` = %d", now, now + wdays * 86400, wid))
		Game.broadcastMessage(string.format("WAR! %s and %s are at war for %d days.", oname, guild:getName(), wdays), MESSAGE_EVENT_ADVANCE)
		return say(npc, player, "So be it. Members see the war after logging in again. War kills never mark anyone a murderer.")
	end
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Greetings, |PLAYERNAME|. I keep the guild rolls. Say {found} <name> to start a guild (level " .. FOUND_LEVEL .. ", " .. FOUND_COST .. " gold). Leaders can offer a {war}: say war <days> <kill limit, 0 for none> <guild>. Wars only happen if both leaders agree. See who is {recruiting}, or who's {looking} for a guild. Leaders: {recruit on} / {recruit off}.")
npcHandler:setMessage(MESSAGE_FAREWELL, "May your banner fly high.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
