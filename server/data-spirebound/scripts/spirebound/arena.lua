-- Arena events: sign-ups, equal-footing fights, scoring and rewards. Rules in lib/spirebound/arena.lua.
-- Players: !arena join | !arena leave | !arena        GM: /arena open lms|rush|banner, /arena start, /arena stop
SpireArena.current = nil
local saved = {} -- guid -> { maxHp, maxMana } while inside

local function arenaKv(player)
	return player:kv():scoped("spirebound-arena")
end

local function temple(player)
	local town = player:getTown()
	return town and town:getTemplePosition() or WorldPoints["temple_hearthgate"]
end

local function fillUp(player)
	player:setHealth(player:getMaxHealth())
	player:addMana(player:getMaxMana() - player:getMana())
end

local function spawnPos(st, guid)
	local p = st.players[guid]
	if p.team == "a" then
		return WorldPoints["arena_a"]
	elseif p.team == "b" then
		return WorldPoints["arena_b"]
	end
	local nw, se = WorldPoints["arena_nw"], WorldPoints["arena_se"]
	for _ = 1, 20 do
		local pos = Position(math.random(nw.x + 1, se.x - 1), math.random(nw.y + 1, se.y - 1), nw.z)
		local tile = Tile(pos)
		if tile and tile:getGround() and not tile:hasProperty(CONST_PROP_BLOCKSOLID) and tile:getCreatureCount() == 0 then
			return pos
		end
	end
	return WorldPoints["arena_center"]
end

local function enter(player, st)
	local guid = player:getGuid()
	local s = { maxHp = player:getMaxHealth(), maxMana = player:getMaxMana() }
	saved[guid] = s
	arenaKv(player):set("saved", s)
	player:setMaxHealth(SpireArena.HP)
	player:setMaxMana(SpireArena.MANA)
	fillUp(player)
	player:teleportTo(spawnPos(st, guid))
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	local team = st.players[guid].team
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s begins!%s Everyone has %d health and the same hits and heals.",
		SpireArena.KINDS[st.kind].name, team and (" You are on the " .. (team == "a" and "West" or "East") .. " team.") or "", SpireArena.HP))
end

local function leaveArena(player)
	local guid = player:getGuid()
	local s = saved[guid] or arenaKv(player):get("saved")
	if s then
		player:setMaxHealth(s.maxHp)
		player:setMaxMana(s.maxMana)
		fillUp(player)
	end
	saved[guid] = nil
	arenaKv(player):remove("saved")
	if SpirePvP.zoneAt(player:getPosition()) == "arena" then
		player:teleportTo(temple(player))
		player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	end
end

local function finish(st, winners)
	st.phase = "over"
	local names = {}
	for _, guid in ipairs(winners or {}) do
		table.insert(names, st.players[guid].name)
		local p = Player(st.players[guid].name)
		if p then
			p:kv():scoped("spirebound-titles"):set(SpireArena.TITLE, os.time())
		end
	end
	local kind = SpireArena.KINDS[st.kind].name
	if #names == 0 then
		Game.broadcastMessage(kind .. " is over: a draw.", MESSAGE_EVENT_ADVANCE)
	else
		Game.broadcastMessage(string.format("%s is over! Winner%s: %s.", kind, #names > 1 and "s" or "", table.concat(names, ", ")), MESSAGE_EVENT_ADVANCE)
	end
	for _, guid in ipairs(st.order) do
		local p = Player(st.players[guid].name)
		if p then
			leaveArena(p)
		end
	end
	logger.info("[Spirebound] arena {} ended, winners: {}", st.kind, table.concat(names, ", "))
	SpireArena.current = nil
end
SpireArena.finish = finish

local function tick()
	local st = SpireArena.current
	if not st or st.phase ~= "running" then
		return
	end
	local now = os.time()
	if st.kind == "banner" and now - (st.lastBanner or st.started) >= SpireArena.BANNER_TICK then
		st.lastBanner = now
		local c = WorldPoints["arena_center"]
		local holders = {}
		for _, guid in ipairs(st.order) do
			local p = Player(st.players[guid].name)
			if p then
				local pos = p:getPosition()
				if pos.z == c.z and pos.x >= c.x - 2 and pos.x <= c.x + 1 and pos.y >= c.y - 2 and pos.y <= c.y + 1 then
					table.insert(holders, guid)
				end
			end
		end
		local scored = SpireArena.bannerTick(st, holders)
		if scored then
			c:sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
			if st.score[scored] % 10 == 0 then
				Game.broadcastMessage(string.format("Capture the Banner: West %d - East %d", st.score.a, st.score.b), MESSAGE_STATUS)
			end
		end
	end
	local winners = SpireArena.result(st, now)
	if winners then
		finish(st, winners)
		return
	end
	addEvent(tick, 1000)
end

function SpireArena.begin()
	local st = SpireArena.current
	if not st or st.phase ~= "signup" then
		return
	end
	-- drop sign-ups who logged out
	for _, guid in ipairs(st.order) do
		if not Player(st.players[guid].name) then
			SpireArena.leave(st, guid)
		end
	end
	local active = {}
	for _, guid in ipairs(st.order) do
		if not st.players[guid].left then
			table.insert(active, guid)
		end
	end
	local players = {}
	for _, guid in ipairs(active) do
		players[guid] = st.players[guid]
	end
	st.order, st.players = active, players
	local ok, why = SpireArena.start(st, os.time())
	if not ok then
		Game.broadcastMessage(SpireArena.KINDS[st.kind].name .. " is cancelled: " .. why, MESSAGE_EVENT_ADVANCE)
		SpireArena.current = nil
		return
	end
	for _, guid in ipairs(st.order) do
		local p = Player(st.players[guid].name)
		if p then
			enter(p, st)
		end
	end
	Game.broadcastMessage(string.format("%s has begun with %d fighters!", SpireArena.KINDS[st.kind].name, #st.order), MESSAGE_EVENT_ADVANCE)
	addEvent(tick, 1000)
end

function SpireArena.open(kind)
	if SpireScope.off("arena") then -- R13: off for the friends test
		return false
	end
	if SpireArena.current then
		return false
	end
	local st = SpireArena.new(kind, os.time())
	SpireArena.current = st
	Game.broadcastMessage(string.format("Arena: %s sign-ups are open for %d minutes! Say !arena join (level %d+). Same health, hits and heals for everyone.",
		SpireArena.KINDS[kind].name, SpireArena.SIGNUP_TIME / 60, SpireArena.MIN_LEVEL), MESSAGE_EVENT_ADVANCE)
	st.timer = addEvent(SpireArena.begin, SpireArena.SIGNUP_TIME * 1000)
	return true
end

-- A participant went down
local function down(victim, attacker)
	local st = SpireArena.current
	local kGuid = attacker and attacker:getGuid() or nil
	local what = SpireArena.down(st, victim:getGuid(), kGuid)
	if attacker then
		attacker:sendTextMessage(MESSAGE_STATUS, "You brought down " .. victim:getName() .. ".")
	end
	if what == "out" then
		victim:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You are out. Well fought!")
		leaveArena(victim)
	else
		fillUp(victim)
		victim:teleportTo(spawnPos(st, victim:getGuid()))
		victim:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
		if st.kind == "rush" then
			Game.broadcastMessage(string.format("Team Rush: West %d - East %d", st.score.a, st.score.b), MESSAGE_STATUS)
		end
	end
end

-- Equal footing: every hit and heal between participants is a fixed amount; nobody dies in the Arena
local hits = CreatureEvent("SpireArenaHits")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local st = SpireArena.current
	local v = creature:getPlayer()
	if not st or st.phase ~= "running" or not v or not st.players[v:getGuid()] then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local a = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
	if primaryType == COMBAT_HEALING then
		if a and a ~= v and not (st.players[a:getGuid()] and st.players[a:getGuid()].team ~= nil and st.players[a:getGuid()].team == st.players[v:getGuid()].team) then
			return 0, primaryType, 0, secondaryType -- only you and your team-mates can heal you
		end
		return SpireArena.amount("heal", math.random()), primaryType, 0, secondaryType
	end
	if not a or not SpireArena.canHit(st, a:getGuid(), v:getGuid()) then
		return 0, primaryType, 0, secondaryType
	end
	local dmg = SpireArena.amount(origin == ORIGIN_SPELL and "spell" or "hit", math.random())
	if dmg >= v:getHealth() then
		down(v, a)
		return 0, primaryType, 0, secondaryType
	end
	return dmg, primaryType, 0, secondaryType
end
hits:register()

local logout = CreatureEvent("SpireArenaLogout")
function logout.onLogout(player)
	local st = SpireArena.current
	if st and st.players[player:getGuid()] then
		SpireArena.leave(st, player:getGuid())
		if st.phase == "running" then
			leaveArena(player)
		end
	end
	return true
end
logout:register()

local login = CreatureEvent("SpireArenaLogin")
function login.onLogin(player)
	player:registerEvent("SpireArenaHits")
	player:registerEvent("SpireArenaLogout")
	if arenaKv(player):get("saved") then
		leaveArena(player) -- the server stopped mid-event: put things back
	end
	return true
end
login:register()

-- Daily schedule: sign-ups open at each of SpireArena.HOURS, kind rotating by day
local schedule = GlobalEvent("SpireArenaSchedule")
function schedule.onThink(interval)
	local hour, minute = tonumber(os.date("%H")), tonumber(os.date("%M"))
	if minute == 0 and not SpireArena.current then
		for _, h in ipairs(SpireArena.HOURS) do
			if h == hour then
				SpireArena.open(SpireArena.kindForDay(math.floor(os.time() / 86400)))
			end
		end
	end
	return true
end
schedule:interval(60 * 1000)
schedule:register()

local cmd = TalkAction("!arena")
function cmd.onSay(player, words, param)
	local st = SpireArena.current
	local p = param:lower()
	if p == "join" then
		if not st then
			player:sendCancelMessage("No Arena event is open. Sign-ups open daily at " .. table.concat(SpireArena.HOURS, ":00 and ") .. ":00 server time.")
			return false
		end
		if Difficulty.get(player) == Difficulty.DEATHGAME then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Nobody dies in the Arena, Death Game climber. You are safe here.")
		end
		local ok, why = SpireArena.join(st, player:getGuid(), player:getName(), player:getLevel())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, ok and ("You are signed up for " .. SpireArena.KINDS[st.kind].name .. ". Stay online!") or why)
	elseif p == "leave" then
		if st and st.phase == "signup" and st.players[player:getGuid()] then
			SpireArena.leave(st, player:getGuid())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You left the sign-up list.")
		end
	else
		if not st then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Arena opens sign-ups daily at " .. table.concat(SpireArena.HOURS, ":00 and ") .. ":00 server time. Today: " .. SpireArena.KINDS[SpireArena.kindForDay(math.floor(os.time() / 86400))].name .. ".")
		else
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s: %s, %d signed up.", SpireArena.KINDS[st.kind].name, st.phase, #st.order))
		end
	end
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()

local gm = TalkAction("/arena")
function gm.onSay(player, words, param)
	local action, kind = param:match("(%a+)%s*(%a*)")
	if action == "open" and SpireArena.KINDS[kind] then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, SpireArena.open(kind) and "Arena sign-ups opened." or "An Arena event is already on.")
	elseif action == "start" and SpireArena.current then
		stopEvent(SpireArena.current.timer)
		SpireArena.begin()
	elseif action == "stop" and SpireArena.current then
		stopEvent(SpireArena.current.timer)
		if SpireArena.current.phase == "running" then
			finish(SpireArena.current, {})
		else
			SpireArena.current = nil
		end
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "/arena open lms|rush|banner, /arena start, /arena stop")
	end
	return false
end
gm:separator(" ")
gm:groupType("gamemaster")
gm:register()
