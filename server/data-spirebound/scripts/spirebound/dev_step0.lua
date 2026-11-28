-- Real-character checks for roadmap Step 0 (Jay's answers of 2026-11-27), run by `python3 tools/loadtest.py review
-- --only QA` on a test copy. Like dev_review.lua: only when the server was started with SPIRE_LOADTEST=1, and only for
-- the loadbotN@localhost test accounts. Each command sets up or reads one thing; the action itself (a trade, a death,
-- a move into the weapon hand, an attack, NPC talk) comes from the bot's own game packets. Results are "[LOADTEST] rv"
-- lines that tools/loadtest.py reads.
--   /s0 state                  level, experience, bag gold, bank gold, blessings, mode
--   /s0 secrets                wear the three secret pieces (and a backpack)
--   /s0 offer                  a backpack and a leather helmet on the head (to offer in a trade)
--   /s0 hold                   which secret pieces this character has
--   /s0 id <name>              log a player's creature id
--   /s0 level <n>              set the level (experience to match)
--   /s0 ground <gear id> <tier> a Spirebound weapon at that tier on the tile east of you
--   /s0 hand                   what is in the weapon hand
--   /s0 bossroom <hound|axe>   stand in the Gate Hound's arena or the Axe-Lord's hall (boss removed, PvP checks only)
--   /s0 hp                     log health
--   /s0 bonus <n>              the Death Game bonus experience earned so far (as if hunted)
--   /s0 goto <npc>             stand beside that NPC
--   /s0 style <path>           a chosen Mastery path (for the respec)
--   /s0 gold <n>               n gold into the bank
--   /s0 launch on|off          this season's launch started now / no launch
--   /s0 crowd <ground> <n>     the crowd tick for that ground as if n players were inside; logs the monsters out
--   /s0 bot on|off             the cavebot switch, as the client reports it
--   /s0 xp <monster>           kill one real monster here; logs the experience that arrived
--   /s0 jump x y z             stand there
--   /s0 windows on|off         count the test accounts like real players for the 3-windows rule
--   /s0 guildfight             the Axe-Lord's first kill with 12 of one guild and 12 others in the credit
--   /s0 bosshall               a started season (day 1): stand in the Axe-Lord's hall with the Stair Key
--   /s0 where                  position
if os.getenv("SPIRE_LOADTEST") ~= "1" then
	return
end

local function isBot(player)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	return email and email:match("^loadbot%d*@localhost$") ~= nil
end

local function out(what, player, fields)
	local parts = {}
	for k, v in pairs(fields or {}) do
		table.insert(parts, k .. "=" .. tostring(v):gsub(" ", "_"))
	end
	table.sort(parts)
	logger.info("[LOADTEST] rv {} {} {}", what, player:getName(), table.concat(parts, " "))
end

local function blessings(player)
	local n = 0
	for b = 1, 8 do
		if player:hasBlessing(b) then
			n = n + 1
		end
	end
	return n
end

local function wear(player, slot, id)
	local old = player:getSlotItem(slot)
	if old then
		old:remove()
	end
	local item = Game.createItem(id, 1)
	return item and player:addItemEx(item, false, slot, FLAG_NOLIMIT) == RETURNVALUE_NOERROR and item or nil
end

local function backpack(player)
	if not player:getSlotItem(CONST_SLOT_BACKPACK) then
		wear(player, CONST_SLOT_BACKPACK, 2854)
	end
end

local function secretsHeld(player)
	local held = {}
	for _, item in ipairs(SpireGear.carried(player)) do
		local g = SpireGear.secretOf(item)
		if g then
			table.insert(held, g.id)
		end
	end
	table.sort(held)
	return #held > 0 and table.concat(held, ",") or "none"
end

local sparring = {} -- player id -> { id = monster id, max = its health }

local s0 = TalkAction("/s0")
function s0.onSay(player, words, param)
	if not isBot(player) then
		return false
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	if cmd == "state" then
		out("s0state", player, { level = player:getLevel(), exp = player:getExperience(), bag = player:getMoney(),
			bank = player:getBankBalance(), bless = blessings(player), mode = Difficulty.get(player) })
	elseif cmd == "secrets" then
		backpack(player)
		for _, g in ipairs(SpireGearData.secretGear) do
			local slot = SpireGear.SECRET_SLOTS[g.slot]
			local old = player:getSlotItem(slot)
			if old then
				old:remove()
			end
			player:addItemEx(SpireGear.makeSecret(g), false, slot, FLAG_NOLIMIT)
		end
		out("s0secrets", player, { held = secretsHeld(player) })
	elseif cmd == "offer" then
		backpack(player)
		wear(player, CONST_SLOT_HEAD, 3355)
		out("s0offer", player, { head = player:getSlotItem(CONST_SLOT_HEAD) and 1 or 0 })
	elseif cmd == "hold" then
		out("s0hold", player, { held = secretsHeld(player) })
	elseif cmd == "id" then
		local p = Player(rest)
		out("s0id", player, { me = player:getId(), myguid = player:getGuid(), other = p and p:getId() or 0 })
	elseif cmd == "level" then
		local n = tonumber(rest) or 1
		local exp = math.floor(((n - 1) ^ 3 * 50 - 150 * (n - 1) ^ 2 + 400 * (n - 1)) / 3)
		player:addExperience(math.max(0, exp - player:getExperience()), false)
		if player:getExperience() > exp then
			player:removeExperience(player:getExperience() - exp, false)
		end
		out("s0level", player, { level = player:getLevel(), exp = player:getExperience() })
	elseif cmd == "ground" then
		local id, tier = rest:match("^(%S+)%s+(%d+)")
		local pos = player:getPosition()
		local spot = Position(pos.x + 1, pos.y, pos.z)
		local item = SpireGear.create(id)
		if item then
			SpireGear.setState(item, { tier = tonumber(tier) })
			Tile(spot):addItemEx(item)
		end
		out("s0ground", player, { x = spot.x, y = spot.y, z = spot.z, item = item and item:getId() or 0 })
	elseif cmd == "hand" then
		local h = player:getSlotItem(CONST_SLOT_LEFT)
		local s = h and SpireGear.state(h)
		out("s0hand", player, { item = h and h:getId() or 0, gear = s and s.id or "none", tier = s and s.tier or -1,
			level = player:getLevel(), carried = (function()
				for _, it in ipairs(SpireGear.carried(player)) do
					if SpireGear.state(it) then return 1 end
				end
				return 0
			end)() })
	elseif cmd == "bossroom" then
		local which, shift = rest:match("^(%a+)%s*(%d*)")
		local name = which == "hound" and "Gate Hound" or "Axe-Lord of the Stair"
		local def = SpireBoss.defs[name]
		local nw, se = def.roomNW and WorldPoints[def.roomNW], def.roomSE and WorldPoints[def.roomSE]
		local c = nw and Position(math.floor((nw.x + se.x) / 2), math.floor((nw.y + se.y) / 2), nw.z) or WorldPoints[def.room.nw]
		for _, m in ipairs(Game.getSpectators(c, false, false, 12, 12, 12, 12)) do
			if m:isMonster() then
				m:remove()
			end
		end
		c = Position(c.x + (tonumber(shift) or 0), c.y, c.z) -- "1": the tile beside, so two characters stand side by side
		player:teleportTo(c, true)
		local tile = Tile(player:getPosition())
		out("s0bossroom", player, { zone = SpirePvP.zoneAt(player:getPosition()), x = player:getPosition().x, y = player:getPosition().y,
			z = c.z, level = player:getLevel(), pz = tile and tile:hasFlag(TILESTATE_PROTECTIONZONE) and 1 or 0,
			nopvp = tile and tile:hasFlag(TILESTATE_NOPVPZONE) and 1 or 0 })
	elseif cmd == "arm" then
		backpack(player)
		wear(player, CONST_SLOT_LEFT, 3264) -- a sword
		out("s0arm", player, { hand = player:getSlotItem(CONST_SLOT_LEFT) and 1 or 0 })
	elseif cmd == "strike" then -- one 100 physical hit through the engine's combat (its PvP checks included)
		local o = Player(rest)
		local before = o and o:getHealth() or 0
		if o then
			doTargetCombatHealth(player, o, COMBAT_PHYSICALDAMAGE, -100, -100, CONST_ME_NONE, ORIGIN_MELEE)
		end
		out("s0strike", player, { lost = o and (before - o:getHealth()) or -1 })
	elseif cmd == "canhit" then
		local o = Player(rest)
		local r = o and SpirePvP.attackResult(player, o)
		out("s0canhit", player, { result = r or -1, ok = r == RETURNVALUE_NOERROR and 1 or 0, skull = player:getSkull(),
			fight = player:getCondition(CONDITION_INFIGHT) and 1 or 0 })
	elseif cmd == "target" then
		local t = player:getTarget()
		out("s0target", player, { target = t and t:getId() or 0, name = t and t:getName() or "none" })
	elseif cmd == "hp" then
		out("s0hp", player, { hp = player:getHealth(), max = player:getMaxHealth() })
	elseif cmd == "bonus" then
		player:kv():scoped("spirebound"):set("bonusXp", tonumber(rest) or 0)
		out("s0bonus", player, { bonus = tonumber(rest) or 0 })
	elseif cmd == "goto" then
		local npc = Npc(rest)
		if npc then
			local p = npc:getPosition()
			player:teleportTo(Position(p.x, p.y + 1, p.z), true)
		end
		out("s0goto", player, { found = npc and 1 or 0 })
	elseif cmd == "style" then
		player:kv():scoped("spirebound"):set("style_path", rest)
		player:kv():scoped("spirebound"):remove("style_respec_at")
		out("s0style", player, { path = rest })
	elseif cmd == "gold" then
		player:setBankBalance(player:getBankBalance() + (tonumber(rest) or 0))
		out("s0gold", player, { bank = player:getBankBalance() })
	elseif cmd == "launch" then
		if rest == "on" then
			kv.scoped("spirebound-season"):set("startedAt", os.time())
		else
			kv.scoped("spirebound-season"):remove("startedAt")
		end
		out("s0launch", player, { week = SpireSeason.inLaunchWeek() and 1 or 0 })
	elseif cmd == "crowd" then
		local gid, n = rest:match("^(%S+)%s+(%d+)")
		local g = SpireCrowd.ground(gid)
		local state, spawned = SpireCrowd.update(g, os.time(), tonumber(n), function() return false end)
		local alive = 0
		for _, s in ipairs(g.spots) do
			local sr = SpireCrowd.spots[g.id .. ":" .. s.n]
			for _, cid in ipairs(sr and sr.alive or {}) do
				if Creature(cid) then
					alive = alive + 1
				end
			end
		end
		out("s0crowd", player, { state = state, spots = #g.spots, groups = spawned, monsters = alive,
			week = SpireSeason.inLaunchWeek() and 1 or 0 })
	elseif cmd == "bot" then
		SpireCavebot.setState(player:getGuid(), rest == "on", os.time())
		out("s0bot", player, { on = rest == "on" and 1 or 0 })
	elseif cmd == "xp" then
		local before = player:getExperience()
		local m = Game.createMonster(rest, player:getPosition(), true, true)
		if m then
			doTargetCombatHealth(player, m, COMBAT_PHYSICALDAMAGE, -m:getMaxHealth() * 3, -m:getMaxHealth() * 3, CONST_ME_NONE)
		end
		addEvent(function(pid)
			local p = Player(pid)
			if p then
				out("s0xp", p, { gained = p:getExperience() - before, ban = SpireCavebot.banReason(p) or "none",
					botting = SpireCavebot.botting(p) and 1 or 0 })
			end
		end, 500, player:getId())
	elseif cmd == "jump" then
		local x, y, z = rest:match("(%d+)%D+(%d+)%D+(%d+)")
		player:teleportTo(Position(tonumber(x), tonumber(y), tonumber(z)), true)
		out("s0jump", player, { x = x, y = y, z = z })
	elseif cmd == "windows" then
		SpireWindows.testers = {}
		if rest == "on" then
			setmetatable(SpireWindows.testers, { __index = function() return false end })
		end
		out("s0windows", player, { counting = rest == "on" and 1 or 0 })
	elseif cmd == "guildfight" then
		-- 12 offline characters of one guild and 12 others (written into the test database), each with a share of the
		-- fight; this bot deals the killing blow to the real Axe-Lord
		db.query("DELETE FROM `guild_membership` WHERE `guild_id` IN (SELECT `id` FROM `guilds` WHERE `name` = 'Step Zero Testers')")
		db.query("DELETE FROM `guilds` WHERE `name` = 'Step Zero Testers'")
		local names = {}
		for i = 1, 24 do
			local n = string.format("Credit Test %02d", i)
			table.insert(names, n)
			db.query("INSERT IGNORE INTO `players` (`name`, `account_id`, `level`, `vocation`, `conditions`) VALUES (" .. db.escapeString(n) .. ", " .. player:getAccountId() .. ", 60, 4, '')")
		end
		db.query("INSERT INTO `guilds` (`name`, `ownerid`, `creationdata`, `motd`) VALUES ('Step Zero Testers', (SELECT `id` FROM `players` WHERE `name` = 'Credit Test 01'), " .. os.time() .. ", '')")
		local rankQ = db.storeQuery("SELECT `r`.`id` AS `rid`, `g`.`id` AS `gid` FROM `guild_ranks` `r` JOIN `guilds` `g` ON `g`.`id` = `r`.`guild_id` WHERE `g`.`name` = 'Step Zero Testers' LIMIT 1")
		local rid, gid = 0, 0
		if rankQ then
			rid, gid = Result.getNumber(rankQ, "rid"), Result.getNumber(rankQ, "gid")
			Result.free(rankQ)
		else
			local gq = db.storeQuery("SELECT `id` FROM `guilds` WHERE `name` = 'Step Zero Testers'")
			gid = gq and Result.getNumber(gq, "id") or 0
			if gq then
				Result.free(gq)
			end
			db.query("INSERT INTO `guild_ranks` (`guild_id`, `name`, `level`) VALUES (" .. gid .. ", 'Member', 1)")
			local rq = db.storeQuery("SELECT `id` FROM `guild_ranks` WHERE `guild_id` = " .. gid .. " LIMIT 1")
			rid = rq and Result.getNumber(rq, "id") or 0
			if rq then
				Result.free(rq)
			end
		end
		for i = 1, 12 do
			db.query("INSERT IGNORE INTO `guild_membership` (`player_id`, `guild_id`, `rank_id`, `nick`) VALUES ((SELECT `id` FROM `players` WHERE `name` = " .. db.escapeString(names[i]) .. "), " .. gid .. ", " .. rid .. ", '')")
		end
		local boss
		for cid, st in pairs(SpireBoss.fights) do
			local c = Creature(cid)
			if c and c:getName() == "Axe-Lord of the Stair" then
				boss = c
			end
		end
		boss = boss or SpireBoss.spawn("Axe-Lord of the Stair")
		if not boss then
			for _, c in ipairs(Game.getSpectators(WorldPoints.boss_room_floor1, false, false, 15, 15, 15, 15)) do
				if c:getName() == "Axe-Lord of the Stair" then
					boss = c
				end
			end
		end
		local st = boss and SpireBoss.fights[boss:getId()]
		if st then
			local now = os.time()
			for i, n in ipairs(names) do
				SpireBoss.recordHit(st, n, 2000 - i, now) -- the guild's twelve did the most
			end
			player:teleportTo(Position(boss:getPosition().x, boss:getPosition().y + 2, boss:getPosition().z), true)
			boss:addHealth(-(boss:getHealth() - 20)) -- (unattributed) so this bot's own blow is a small share
			doTargetCombatHealth(player, boss, COMBAT_PHYSICALDAMAGE, -500, -500, CONST_ME_NONE)
		end
		out("s0guildfight", player, { boss = boss and 1 or 0, record = st and 1 or 0, guild = gid })
	elseif cmd == "credit" then
		local last = SpireBoss.lastCredit or { names = {} }
		local inGuild = 0
		for _, n in ipairs(last.names) do
			if SpireBoss.guildOf(n) then
				inGuild = inGuild + 1
			end
		end
		out("s0credit", player, { total = #last.names, guild = inGuild, capped = last.capped and 1 or 0, boss = last.boss or "none" })
	elseif cmd == "bosshall" then
		kv.scoped("spirebound-season"):set("startedAt", os.time()) -- a season started today: day 1
		player:kv():scoped("spirebound"):set("stair_key_pilot", 1)
		local c = WorldPoints.boss_room_floor1
		player:teleportTo(Position(c.x, c.y + 6, c.z), true)
		out("s0bosshall", player, { x = c.x, y = c.y + 6, z = c.z })
	elseif cmd == "loot" then
		-- kill n real monsters one by one; count the coins that reach the backpack and the bank, plus any left in the
		-- body (a full backpack), then clear the body away so the next kill starts clean
		local name, n = rest:match("^(.-)%s+(%d+)$")
		n = tonumber(n) or 1
		local pid = player:getId()
		local bag0, bank0, left = player:getMoney(), player:getBankBalance(), 0
		local COIN = { [3031] = 1, [3035] = 100, [3043] = 10000 }
		for i = 1, n do
			addEvent(function()
				local p = Player(pid)
				if not p then
					return
				end
				local pos = p:getPosition()
				local m = Game.createMonster(name, pos, true, true)
				if m then
					local at = m:getPosition()
					doTargetCombatHealth(p, m, COMBAT_PHYSICALDAMAGE, -m:getMaxHealth() * 3, -m:getMaxHealth() * 3, CONST_ME_NONE)
					addEvent(function()
						local t = Tile(at)
						for _, it in ipairs(t and t:getItems() or {}) do
							if it:isContainer() then
								for _, c in ipairs(it:getItems(true) or {}) do
									left = left + (COIN[c:getId()] or 0) * c:getCount()
								end
								it:remove()
							end
						end
						local pp = Player(pid)
						local bp = pp and pp:getSlotItem(CONST_SLOT_BACKPACK)
						if bp then -- keep only the coins: other loot would fill the backpack
							for _, c in ipairs(bp:getItems(false) or {}) do
								if not COIN[c:getId()] then
									c:remove()
								end
							end
						end
					end, 100)
				end
			end, i * 150)
		end
		addEvent(function()
			local p = Player(pid)
			if p then
				out("s0loot", p, { kills = n, bag = p:getMoney() - bag0, bank = p:getBankBalance() - bank0, left = left })
			end
		end, n * 150 + 2500)
	elseif cmd == "events" then
		-- with only this character online: a world event (as the 3-hour scheduler picks one), this week's weekend bonus
		-- rule, and an arena event's start (which must wait for 4 fighters)
		local kind, floor = SpireEvents.pick(math.random(), Floors.highestOpen())
		SpireEvents.start(kind, floor)
		local arenaOk = SpireArena.start({ order = { player:getGuid() }, players = { [player:getGuid()] = {} }, kind = next(SpireArena.KINDS) }, os.time())
		out("s0events", player, { online = #Game.getPlayers(), event = SpireEvents.active and SpireEvents.active.kind.id or "none",
			arena = arenaOk and 1 or 0, weekend = SpireEvents.weekendBonus(7, 1) and 1 or 0 })
	elseif cmd == "bag" then
		out("s0bag", player, { bp = player:getSlotItem(CONST_SLOT_BACKPACK) and 1 or 0, bless = blessings(player), level = player:getLevel() })
	elseif cmd == "fam" then -- the first Spirebound weapon this character has: familiarity, bond, where it is
		local found, where
		local h = player:getSlotItem(CONST_SLOT_LEFT)
		if h and SpireGear.state(h) then
			found, where = h, "hand"
		else
			for _, it in ipairs(SpireGear.carried(player)) do
				if SpireGear.state(it) and SpireGear.defOf(it).kind == "weapon" then
					found, where = it, "carried"
					break
				end
			end
		end
		local st = found and SpireGear.state(found)
		out("s0fam", player, { where = where or "none", fam = st and st.fam or -1, bond = st and (SpireGear.bondName(st.bond) or "none") or "none",
			mine = st and st.bond == player:getGuid() and 1 or 0 })
	elseif cmd == "key" then
		player:kv():scoped("spirebound"):set("stair_key_pilot", 1)
		out("s0key", player, { key = SpireStairKey.has(player) and 1 or 0 })
	elseif cmd == "spar" and rest ~= "end" then
		-- out of town, a monster two tiles away, and this character attacking it with whatever is in hand
		local spot = Position(1250, 1060, 7)
		player:teleportTo(spot, true)
		local m = Game.createMonster(rest, Position(spot.x + 2, spot.y, spot.z), true, true)
		if m then
			sparring[player:getId()] = { id = m:getId(), max = m:getMaxHealth() }
			player:setTarget(m)
		end
		out("s0spar", player, { monster = m and 1 or 0 })
	elseif cmd == "spar" then
		local s = sparring[player:getId()]
		local m = s and Creature(s.id)
		local dealt = s and (m and (s.max - m:getHealth()) or s.max) or 0
		if m then
			m:remove()
		end
		out("s0sparend", player, { dealt = dealt })
	elseif cmd == "where" then
		local p = player:getPosition()
		out("s0where", player, { x = p.x, y = p.y, z = p.z, zone = SpirePvP.zoneAt(p) })
	end
	return true
end
s0:separator(" ")
s0:groupType("normal")
s0:register()
