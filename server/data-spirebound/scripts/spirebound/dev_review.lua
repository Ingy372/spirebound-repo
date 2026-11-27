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
