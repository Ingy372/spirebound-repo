-- Spire Siege: sign-ups, equal-footing fight for the throne room, the weekly holder. Rules in lib/spirebound/siege.lua.
-- Players: !siege join | !siege leave | !siege       GM: /siege open, /siege start, /siege stop
SpireSiege.current = nil
local saved = {}

local function store(player)
	return player:kv():scoped("spirebound-arena")
end

local function fillUp(player)
	player:setHealth(player:getMaxHealth())
	player:addMana(player:getMaxMana() - player:getMana())
end

local function gatePos(st, guid)
	return WorldPoints["siege_gate_" .. (st.gates[st.players[guid].guild] or 1)]
end

local function enter(player, st)
	local s = { maxHp = player:getMaxHealth(), maxMana = player:getMaxMana() }
	saved[player:getGuid()] = s
	store(player):set("siegesaved", s)
	player:setMaxHealth(SpireSiege.HP)
	player:setMaxMana(SpireSiege.MANA)
	fillUp(player)
	player:teleportTo(gatePos(st, player:getGuid()))
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Siege begins! Hold the throne room with only your guild inside to score. Everyone has the same health, hits and heals.")
end

local function leaveSiege(player)
	local guid = player:getGuid()
	local s = saved[guid] or store(player):get("siegesaved")
	if s then
		player:setMaxHealth(s.maxHp)
		player:setMaxMana(s.maxMana)
		fillUp(player)
	end
	saved[guid] = nil
	store(player):remove("siegesaved")
	if SpirePvP.zoneAt(player:getPosition()) == "siege" then
		local town = player:getTown()
		player:teleportTo(town and town:getTemplePosition() or WorldPoints["temple_hearthgate"])
		player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	end
end

local function guildName(gid)
	local g = Guild(gid)
	return g and g:getName() or ("guild " .. gid)
end

local function finish(st, winner)
	st.phase = "over"
	if winner and winner ~= 0 then
		kv.scoped("spirebound-siege"):set("holder", { guild = winner, name = guildName(winner), untilTime = os.time() + SpireSiege.HOLD_TIME, since = os.time() })
		local g = Guild(winner)
		local leader = nil
		if g then
			local q = db.storeQuery("SELECT `ownerid` FROM `guilds` WHERE `id` = " .. winner)
			if q then
				leader = Result.getNumber(q, "ownerid")
				Result.free(q)
			end
		end
		if leader then
			kv.scoped("player"):scoped(tostring(leader)):scoped("spirebound-titles"):set(SpireSiege.TITLE, os.time())
		end
		Game.broadcastMessage(string.format("%s holds the Spire keep for the coming week! Its members gain +5%% experience and loot.", guildName(winner)), MESSAGE_EVENT_ADVANCE)
	else
		Game.broadcastMessage("The Siege ends with no clear victor. The keep stays as it was.", MESSAGE_EVENT_ADVANCE)
	end
	for _, guid in ipairs(st.order) do
		local p = Player(st.players[guid].name)
		if p then
			leaveSiege(p)
		end
	end
	logger.info("[Spirebound] siege ended, winner guild {}", winner or 0)
	SpireSiege.current = nil
end
SpireSiege.finish = finish

local function inThrone(pos)
	local nw, se = WorldPoints["siege_throne_nw"], WorldPoints["siege_throne_se"]
	return pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end

local function tick()
	local st = SpireSiege.current
	if not st or st.phase ~= "running" then
		return
	end
	local now = os.time()
	if now - (st.lastTick or st.started) >= SpireSiege.TICK then
		st.lastTick = now
		local holders = {}
		for _, guid in ipairs(st.order) do
			local p = Player(st.players[guid].name)
			if p and inThrone(p:getPosition()) then
				table.insert(holders, guid)
			end
		end
		local g = SpireSiege.tick(st, holders)
		if g and st.score[g] % 24 == 0 then
			local parts = {}
			for gid, s in pairs(st.score) do
				table.insert(parts, guildName(gid) .. " " .. s)
			end
			Game.broadcastMessage("Siege: " .. table.concat(parts, ", "), MESSAGE_STATUS)
		end
	end
	local h = SpireSiege.holder()
	local winner = SpireSiege.result(st, now, h and h.guild)
	if winner then
		finish(st, winner)
		return
	end
	addEvent(tick, 1000)
end

function SpireSiege.begin()
	local st = SpireSiege.current
	if not st or st.phase ~= "signup" then
		return
	end
	for _, guid in ipairs(st.order) do
		if not Player(st.players[guid].name) then
			SpireSiege.leave(st, guid)
		end
	end
	local ok, why = SpireSiege.start(st, os.time())
	if not ok then
		Game.broadcastMessage("The Siege is cancelled: " .. why, MESSAGE_EVENT_ADVANCE)
		SpireSiege.current = nil
		return
	end
	for _, guid in ipairs(st.order) do
		local p = Player(st.players[guid].name)
		if p and st.players[guid].alive then
			enter(p, st)
		elseif p and st.players[guid].dropped then
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your guild needs at least " .. SpireSiege.MIN_MEMBERS .. " fighters for the Siege.")
		end
	end
	Game.broadcastMessage("The Spire Siege has begun!", MESSAGE_EVENT_ADVANCE)
	addEvent(tick, 1000)
end

function SpireSiege.open()
	if SpireSiege.current then
		return false
	end
	SpireSiege.current = SpireSiege.new(os.time())
	Game.broadcastMessage(string.format("Spire Siege sign-ups are open for %d minutes! Guild members say !siege join. Same health, hits and heals for everyone.", SpireSiege.SIGNUP_TIME / 60), MESSAGE_EVENT_ADVANCE)
	SpireSiege.current.timer = addEvent(SpireSiege.begin, SpireSiege.SIGNUP_TIME * 1000)
	return true
end

local hits = CreatureEvent("SpireSiegeHits")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local st = SpireSiege.current
	local v = creature:getPlayer()
	if not st or st.phase ~= "running" or not v or not st.players[v:getGuid()] then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local a = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
	if primaryType == COMBAT_HEALING then
		local ap = a and st.players[a:getGuid()]
		if a and a ~= v and not (ap and ap.guild == st.players[v:getGuid()].guild) then
			return 0, primaryType, 0, secondaryType
		end
		return SpireArena.amount("heal", math.random()), primaryType, 0, secondaryType
	end
	if not a or not SpireSiege.canHit(st, a:getGuid(), v:getGuid()) then
		return 0, primaryType, 0, secondaryType
	end
	local dmg = SpireArena.amount(origin == ORIGIN_SPELL and "spell" or "hit", math.random())
	if dmg >= v:getHealth() then
		fillUp(v)
		v:teleportTo(gatePos(st, v:getGuid()))
		v:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
		a:sendTextMessage(MESSAGE_STATUS, "You drove " .. v:getName() .. " back to their gate.")
		return 0, primaryType, 0, secondaryType
	end
	return dmg, primaryType, 0, secondaryType
end
hits:register()

local logout = CreatureEvent("SpireSiegeLogout")
function logout.onLogout(player)
	local st = SpireSiege.current
	if st and st.players[player:getGuid()] then
		SpireSiege.leave(st, player:getGuid())
		if st.phase == "running" then
			leaveSiege(player)
		end
	end
	return true
end
logout:register()

local login = CreatureEvent("SpireSiegeLogin")
function login.onLogin(player)
	player:registerEvent("SpireSiegeHits")
	player:registerEvent("SpireSiegeLogout")
	if store(player):get("siegesaved") then
		leaveSiege(player)
	end
	return true
end
login:register()

-- Weekly: sign-ups open 15 minutes before 20:00 on Sundays (server time)
local schedule = GlobalEvent("SpireSiegeSchedule")
function schedule.onThink(interval)
	local t = os.date("*t")
	local openMinute = 60 - SpireSiege.SIGNUP_TIME / 60
	if t.wday == SpireSiege.DAY and t.hour == SpireSiege.HOUR - 1 and t.min == openMinute and not SpireSiege.current then
		SpireSiege.open()
	end
	return true
end
schedule:interval(60 * 1000)
schedule:register()

local cmd = TalkAction("!siege")
function cmd.onSay(player, words, param)
	local st = SpireSiege.current
	local p = param:lower()
	if p == "join" then
		if not st then
			player:sendCancelMessage("Siege sign-ups open Sundays at 19:45 server time.")
			return false
		end
		local g = player:getGuild()
		local ok, why = SpireSiege.join(st, player:getGuid(), player:getName(), player:getLevel(), g and g:getId() or 0)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, ok and "You are signed up for the Siege. Stay online!" or why)
	elseif p == "leave" then
		if st and st.phase == "signup" then
			SpireSiege.leave(st, player:getGuid())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You left the Siege list.")
		end
	else
		local h = SpireSiege.holder()
		local text = "The Spire Siege runs Sundays at 20:00 server time (sign-ups from 19:45)."
		if h and os.time() < h.untilTime then
			text = text .. " The keep is held by " .. h.name .. " (+5% experience and loot for its members)."
		end
		if st then
			text = text .. " Right now: " .. st.phase .. ", " .. #st.order .. " signed up."
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
	end
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()

local gm = TalkAction("/siege")
function gm.onSay(player, words, param)
	if param == "open" then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, SpireSiege.open() and "Siege sign-ups opened." or "A Siege is already on.")
	elseif param == "start" and SpireSiege.current then
		stopEvent(SpireSiege.current.timer)
		SpireSiege.begin()
	elseif param == "stop" and SpireSiege.current then
		stopEvent(SpireSiege.current.timer)
		if SpireSiege.current.phase == "running" then
			finish(SpireSiege.current, 0)
		else
			SpireSiege.current = nil
		end
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "/siege open, /siege start, /siege stop")
	end
	return false
end
gm:separator(" ")
gm:groupType("gamemaster")
gm:register()
