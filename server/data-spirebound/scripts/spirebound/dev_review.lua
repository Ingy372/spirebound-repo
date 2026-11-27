-- Real-character checks for the Floor 1 review fixes (tools/loadtest.py review). Like dev_loadbot.lua: only when the
-- server was started with SPIRE_LOADTEST=1 (tools/loadtest.py does that on its own test copy; the live server never
-- sets it), and only for the loadbotN@localhost test accounts. Each command does one thing to a real, logged-in
-- character through the game's own code and logs the result as a "[LOADTEST] rv ..." line the tool reads.
--   /rv mode <normal|hardcore|deathgame>   choose a difficulty (as the Registrar does), then the login blessing rule
--   /rv state                              log level, experience, blessings, difficulty
--   /rv die                                a real monster appears next to you and kills you (a real death)
--   /rv weapon <gear id> <tier> <0/1>      that Spirebound weapon in your hand, full familiarity, awakened or not
--   /rv hit [monster]                      one real hit of exactly 100 on a real monster; logs what it lost
--   /rv xp <monster>                       kill one; logs the experience that arrived
--   /rv bot on|off                         the cavebot switch
--   /rv loot <monster> <n>                 kill n; logs the coins that reached you (bank and bag)
--   /rv dg <case> <other player>           review A8-2: a Death Game death next to another real player; logs the verdict
--                                          (cases: dragfought, dragged, firstvictim, firstother)
--   /rv axelord                            review A4-6: kill the real Axe-Lord; logs what reached your bank
--   /rv bossreload                         review A4-5: fight the real Gate Hound, lose its fight record (as a script
--                                          reload does), kill it; logs whether you were still credited
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

-- all test characters log in from 127.0.0.1, which would make every one of them a "friend" (same IP) for the Death Game
-- rules; on test servers the loadbot characters count as coming from different places
local realInfo = Difficulty.playerInfo
function Difficulty.playerInfo(p)
	local info = realInfo(p)
	if isBot(p) then
		info.ip = 0
	end
	return info
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

local function state(player, what)
	logger.info("[LOADTEST] rv {} {} level={} exp={} bless={} mode={} hp={}", what, player:getName(), player:getLevel(),
		player:getExperience(), blessings(player), Difficulty.get(player), player:getHealth())
end

local MODES = { normal = Difficulty.NORMAL, hardcore = Difficulty.HARDCORE, deathgame = Difficulty.DEATHGAME }

local rv = TalkAction("/rv")
function rv.onSay(player, words, param)
	if not isBot(player) then
		return false
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	if cmd == "mode" and MODES[rest] then
		player:kv():scoped("spirebound"):remove("difficulty")
		Difficulty.set(player, MODES[rest]) -- what the Registrar calls
		SpireDifficulty.youngBlessings(player) -- the login rule, for the new mode
		state(player, "mode")
	elseif cmd == "state" then
		state(player, "state")
	elseif cmd == "die" then
		state(player, "before_death")
		local m = Game.createMonster(rest ~= "" and rest or "Meadow Wolf", player:getPosition(), true, true)
		if m then
			local hit = player:getMaxHealth() * 3
			doTargetCombatHealth(m, player, COMBAT_PHYSICALDAMAGE, -hit, -hit, CONST_ME_NONE)
		end
		logger.info("[LOADTEST] rv die {} monster={}", player:getName(), m and "yes" or "no")
	elseif cmd == "weapon" then -- "/rv weapon <gear id> <tier> <awakened 0/1>": in the hand, at full familiarity
		local id, tier, awake = rest:match("^(%S+)%s+(%d+)%s+(%d)")
		local item = id and SpireGear.equip(player, id)
		if item then
			local T = SpireGearData.FAMILIARITY_POINTS[SpireGear.def(id).floor]
			SpireGear.setState(item, { tier = tonumber(tier), famPoints = T[#T], awakened = awake == "1" })
		end
		local held = SpireGear.mainWeapon(player)
		logger.info("[LOADTEST] rv weapon {} held={} power={}", player:getName(), held and (held:getName():gsub(" ", "_")) or "none",
			math.floor(SpireGear.power(held and SpireGear.state(held)) * 100 + 0.5))
	elseif cmd == "hit" then -- one real hit of exactly 100 on a real monster: what does the monster lose?
		local m = Game.createMonster(rest ~= "" and rest or "Ruin Sentinel", player:getPosition(), true, true)
		if m then
			local before = m:getHealth()
			doTargetCombatHealth(player, m, COMBAT_PHYSICALDAMAGE, -100, -100, CONST_ME_NONE, ORIGIN_MELEE)
			logger.info("[LOADTEST] rv hit {} dealt={}", player:getName(), before - m:getHealth())
			m:remove()
		end
	elseif cmd == "xp" then -- kill one real monster: how much experience arrives?
		local before = player:getExperience()
		local m = Game.createMonster(rest, player:getPosition(), true, true)
		if m then
			doTargetCombatHealth(player, m, COMBAT_PHYSICALDAMAGE, -m:getMaxHealth() * 3, -m:getMaxHealth() * 3, CONST_ME_NONE)
		end
		addEvent(function(pid)
			local p = Player(pid)
			if p then
				logger.info("[LOADTEST] rv xp {} gained={} mode={} botting={}", p:getName(), p:getExperience() - before, Difficulty.get(p), SpireCavebot.botting(p) and 1 or 0)
			end
		end, 500, player:getId())
	elseif cmd == "skill" then -- 1000 raw sword-training tries through the engine: how many arrive?
		local before = player:getSkillTries(SKILL_SWORD)
		local lvl = player:getSkillLevel(SKILL_SWORD)
		player:addSkillTries(SKILL_SWORD, 1000)
		local got = player:getSkillTries(SKILL_SWORD) - before
		local voc = player:getVocation()
		for l = lvl + 1, player:getSkillLevel(SKILL_SWORD) do
			got = got + voc:getRequiredSkillTries(SKILL_SWORD, l)
		end
		logger.info("[LOADTEST] rv skill {} level={} tries={}", player:getName(), player:getLevel(), got)
	elseif cmd == "bot" then -- the cavebot switch, as the client reports it
		SpireCavebot.setState(player:getGuid(), rest == "on", os.time())
		logger.info("[LOADTEST] rv bot {} botting={}", player:getName(), SpireCavebot.botting(player) and 1 or 0)
	elseif cmd == "dg" then -- "/rv dg <case> <other player>": a real Death Game death beside a real other player
		local case, otherName = rest:match("^(%a+)%s+(.+)$")
		local o = otherName and Player(otherName)
		if not o then
			logger.info("[LOADTEST] rv dg {} case={} verdict=no_partner", player:getName(), tostring(case))
			return true
		end
		player:kv():scoped("spirebound"):remove("difficulty")
		Difficulty.set(player, Difficulty.DEATHGAME)
		local spot = Position(1250, 1055, 7)              -- open meadow east of the labyrinth corridor (open PvP)
		player:teleportTo(spot, true)
		o:teleportTo(Position(spot.x + 1, spot.y, spot.z), true)
		local m = Game.createMonster("Meadow Wolf", Position(spot.x, spot.y + 1, spot.z), true, true)
		local guid, name, maxhp = player:getGuid(), player:getName(), player:getMaxHealth()
		local otherHp = o:getHealth()
		local myHp = player:getHealth()
		if case == "dragged" or case == "dragfought" then
			doTargetCombatHealth(m, o, COMBAT_ENERGYDAMAGE, -40, -40, CONST_ME_NONE)      -- the wolf bit the other player
		end
		if case == "dragfought" then
			doTargetCombatHealth(player, m, COMBAT_ENERGYDAMAGE, -5, -5, CONST_ME_NONE)    -- and the victim fought it too
		end
		if case == "firstvictim" then
			doTargetCombatHealth(player, o, COMBAT_ENERGYDAMAGE, -5, -5, CONST_ME_NONE)    -- the victim struck first
		end
		if case == "firstvictim" or case == "firstother" then
			local big = math.floor(maxhp * 0.4)   -- PvP damage arrives halved: about 20% lands
			doTargetCombatHealth(o, player, COMBAT_ENERGYDAMAGE, -big, -big, CONST_ME_NONE)
		end
		local pvpLoss = myHp - player:getHealth()
		for _, h in ipairs(SpireDeathGame.hits[guid] or {}) do
			logger.info("[LOADTEST] rv dghit {} amount={} outside={} aggressor={} maxhp={}", name, h.amount, tostring(h.outside), tostring(h.aggressor), maxhp)
		end
		local otherLoss = otherHp - o:getHealth()
		doTargetCombatHealth(m, player, COMBAT_PHYSICALDAMAGE, -maxhp * 3, -maxhp * 3, CONST_ME_NONE)   -- the wolf kills
		addEvent(function()
			local retired = kv.scoped("player"):scoped(tostring(guid)):scoped("spirebound"):get("retired") == true
			logger.info("[LOADTEST] rv dg {} case={} verdict={} pvp_loss={} other_loss={} zone={}", name, case,
				retired and "retire" or "saved", pvpLoss, otherLoss, SpirePvP.zoneAt(spot))
		end, 1000)
	elseif cmd == "axelord" then
		local spot = WorldPoints.axe_lord_spawn
		local boss
		for _, c in ipairs(Game.getSpectators(spot, false, false, 14, 14, 14, 14)) do
			if c:getName() == "Axe-Lord of the Stair" then
				boss = c
			end
		end
		boss = boss or SpireBoss.spawn("Axe-Lord of the Stair")
		local bank = player:getBankBalance()
		player:teleportTo(Position(spot.x, spot.y + 2, spot.z), true)
		local hp = boss:getMaxHealth() * 3
		doTargetCombatHealth(player, boss, COMBAT_PHYSICALDAMAGE, -hp, -hp, CONST_ME_NONE, ORIGIN_MELEE)
		local pid = player:getId()
		addEvent(function()
			local p = Player(pid)
			if p then
				logger.info("[LOADTEST] rv axelord {} bank_gain={}", p:getName(), p:getBankBalance() - bank)
			end
		end, 1000)
	elseif cmd == "bossreload" then
		local spot = WorldPoints.gate_hound_spawn
		local boss
		for _, c in ipairs(Game.getSpectators(spot, false, false, 8, 8, 8, 8)) do
			if c:getName() == "Gate Hound" then
				boss = c
			end
		end
		boss = boss or SpireBoss.spawn("Gate Hound")
		local kvs = player:kv():scoped("spirebound")
		kvs:remove("boss_credit_Gate Hound")
		player:teleportTo(Position(spot.x, spot.y + 2, spot.z), true)
		doTargetCombatHealth(player, boss, COMBAT_PHYSICALDAMAGE, -300, -300, CONST_ME_NONE, ORIGIN_MELEE)   -- a real fight
		local hadRecord = SpireBoss.fights[boss:getId()] ~= nil
		SpireBoss.fights[boss:getId()] = nil                     -- what a script reload does to the fight record
		local hp = boss:getMaxHealth() * 3
		doTargetCombatHealth(player, boss, COMBAT_PHYSICALDAMAGE, -hp, -hp, CONST_ME_NONE, ORIGIN_MELEE)
		local pid = player:getId()
		addEvent(function()
			local p = Player(pid)
			if p then
				logger.info("[LOADTEST] rv bossreload {} had_record={} credited={}", p:getName(), hadRecord and 1 or 0,
					p:kv():scoped("spirebound"):get("boss_credit_Gate Hound") ~= nil and 1 or 0)
			end
		end, 1000)
	elseif cmd == "loot" then -- "/rv loot <monster> <n>": kill n real monsters; how many coins reached the bank and the bag?
		local name, n = rest:match("^(.-)%s+(%d+)$")
		n = tonumber(n) or 1
		local pid, start = player:getId(), player:getBankBalance() + player:getMoney()
		for i = 1, n do
			addEvent(function()
				local p = Player(pid)
				local m = p and Game.createMonster(name, p:getPosition(), true, true)
				if m then
					doTargetCombatHealth(p, m, COMBAT_PHYSICALDAMAGE, -m:getMaxHealth() * 3, -m:getMaxHealth() * 3, CONST_ME_NONE)
				end
			end, i * 150)
		end
		addEvent(function()
			local p = Player(pid)
			if p then
				logger.info("[LOADTEST] rv loot {} kills={} coins={} botting={}", p:getName(), n, p:getBankBalance() + p:getMoney() - start, SpireCavebot.botting(p) and 1 or 0)
			end
		end, n * 150 + 2500)
	end
	return true
end
rv:separator(" ")
rv:groupType("normal")
rv:register()
