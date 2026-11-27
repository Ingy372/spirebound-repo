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
--   /rv shrine                             review item 10: step on the Sealed Shrine secret, then again as if another
--                                          character of the same account found it; logs the gold each time
--   /rv dailyfresh | dailyalt              item 10: forget the account's (fresh) or only this character's (alt) daily
--   /rv boxprep [fresh]                    item 10: stand by the Underkeep strongbox ("fresh": forget the account's day)
--   /rv fishprep | fishstate               review A7-1: a rod in the left hand and worms on the river bank at
--                                          1122,1213 (water at 1125,1213); fishstate logs the fishing tries so far
--   /rv levelnine                          review A9: a real level-up from 8 to 9; logs whether the "slower" hint came
--   /rv journal                            review A5-1: the Journal's Quests tab as the client receives it
--   /rv shopon | newseason | shopstate     review S-1: open the shop with 1,000 coins (fresh ledger); then forget this
--                                          season's hand-over and the items (as a wipe does) and log out; then count the
--                                          candelabra in the Store Inbox
--   /rv perkhit                            tester: a 100 hit on a monster at 20% health, without and then with the
--                                          Executioner perk; logs both (MonsterType:isBoss crashed every hit)
--   /rv pvpdmg <other player>              tester: the other player hits you; logs the PvP damage the credit rules saw
--   /rv privprep [key]                     tester: by the private hall's door with Floor 2 open, with or without the key
--   /rv where                              log your position
--   /rv goto <npc>                         stand beside that NPC (and get 1,000 gold)
--   /rv crystalfloor <mode> x y z          TC1: stand at x,y,z with the Amber Waycrystal on the tile west of you (so a
--                                          test can right-click it); mode "fight": a wolf bites you first
--   /rv chestprep <ground> [alt]           tester: stand by that ground's chest; "alt": forget this character's own record
--                                          (as a second character of the same account), keep the account's
--   /rv wellvein                           tester: the Well Vein secret for this character, then as a second one
--   /rv taskdone                           tester: a finished Field Rat task, a full backpack, then report it
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
	logger.info("[LOADTEST] rv {} {} level={} exp={} bless={} mode={} hp={} gold={}", what, player:getName(), player:getLevel(),
		player:getExperience(), blessings(player), Difficulty.get(player), player:getHealth(), player:getBankBalance() + player:getMoney())
end

local function accountDaily(player)
	return kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-daily")
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
		if case == "bossother" then                        -- the private boss hall (a boss room: PvP for all, no skull)
			local h = WorldPoints.boss_private_floor1
			spot = Position(h.x, h.y + 4, h.z)
		end
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
		if case == "firstvictim" or case == "firstother" or case == "bossother" then
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
	elseif cmd == "shrine" then
		local pos = WorldPoints.secret_s7
		kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-secretgold"):remove("sealed_shrine")
		local secrets = player:kv():scoped("spirebound-secrets")
		local function stepOn()
			secrets:remove("s7")                                   -- this character has not found it (yet)
			player:teleportTo(Position(pos.x, pos.y + 2, pos.z), true)
			local before = player:getBankBalance() + player:getMoney()
			player:teleportTo(pos)                                 -- a real step onto the secret tile
			return player:getBankBalance() + player:getMoney() - before
		end
		local first = stepOn()
		local second = stepOn()
		for _, c in ipairs(Game.getSpectators(pos, false, false, 4, 4, 4, 4)) do
			if c:isMonster() then
				c:remove()                                         -- the guardians it woke
			end
		end
		logger.info("[LOADTEST] rv shrine {} first={} second={}", player:getName(), first, second)
	elseif cmd == "dailyfresh" or cmd == "dailyalt" then
		player:kv():scoped("spirebound"):remove("daily_last")
		player:kv():scoped("spirebound"):remove("daily_streak")
		if cmd == "dailyfresh" then
			accountDaily(player):remove("daily_last")
			accountDaily(player):remove("daily_streak")
		end
		state(player, cmd)
		local pid = player:getId()
		addEvent(function()                      -- a real logout, so the next login runs the login events again
			local p = Player(pid)
			if p then
				p:remove()
			end
		end, 500)
	elseif cmd == "boxprep" then
		if rest == "fresh" then
			accountDaily(player):remove("underkeep_box1")
		end
		player:kv():scoped("spirebound-underkeep"):remove("box1")
		local c = WorldPoints.underkeep_chest
		player:teleportTo(Position(c.x - 1, c.y, c.z), true)
		local tile, ids = Tile(c), {}
		for i, it in ipairs(tile and tile:getItems() or {}) do
			table.insert(ids, it:getId() .. "@" .. tostring(tile:getThingIndex(it)))
		end
		logger.info("[LOADTEST] rv boxtile {} at={},{},{} items={}", player:getName(), player:getPosition().x, player:getPosition().y,
			player:getPosition().z, table.concat(ids, ","))
		state(player, "boxprep")
	elseif cmd == "fishprep" then
		player:addItem(SpireFishing.WORM, 50)
		player:teleportTo(Position(1122, 1213, 7), true)
		local spot = Position(1121, 1213, 7)                     -- the rod lies beside you (a rod can't be held in a hand)
		for _, it in ipairs(Tile(spot) and Tile(spot):getItems() or {}) do
			it:remove()
		end
		local rod = Game.createItem(3483, 1, spot)
		local t = Tile(Position(1125, 1213, 7))
		logger.info("[LOADTEST] rv fishprep {} water={} rod={} stack={}", player:getName(), t and t:getGround() and t:getGround():getId() or 0,
			rod and rod:getId() or 0, rod and Tile(spot):getThingIndex(rod) or -1)
		logger.info("[LOADTEST] rv fishstate {} tries={}", player:getName(), player:getSkillTries(SKILL_FISHING))
	elseif cmd == "fishstate" then
		logger.info("[LOADTEST] rv fishstate {} tries={}", player:getName(), player:getSkillTries(SKILL_FISHING))
	elseif cmd == "levelnine" then
		if player:getLevel() > 8 then -- back down to level 8 (a level-8 test character may not use chat commands)
			player:removeExperience(player:getExperience() - Game.getExperienceForLevel(8), false)
		end
		local got = {}
		local real = Player.sendTextMessage
		Player.sendTextMessage = function(self, t, text, ...)
			if self:getId() == player:getId() then
				table.insert(got, tostring(text))
			end
			return real(self, t, text, ...)
		end
		local ok, err = pcall(function()
			player:addExperience(Game.getExperienceForLevel(9) - player:getExperience() + 1, false)
		end)
		Player.sendTextMessage = real
		local hint = false
		for _, t in ipairs(got) do
			hint = hint or t:find("experience comes slower", 1, true) ~= nil
		end
		logger.info("[LOADTEST] rv level9 {} level={} hint={} ok={}", player:getName(), player:getLevel(), hint and 1 or 0, ok and 1 or tostring(err))
	elseif cmd == "journal" then
		local _, lines = SpireJournal.quests(player)
		local group = 0
		for _, l in ipairs(lines) do
			if l:find("Gate Hound", 1, true) and l:find("Stonehorn Ram", 1, true) then
				group = group + 1
			end
		end
		logger.info("[LOADTEST] rv journal {} lines={} stairkey_group_line={}", player:getName(), #lines, group)
	elseif cmd == "shopon" then
		SpireShop.ENABLED = true                                  -- test servers only (closed until launch)
		local s = kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-shop")
		s:remove("bought")
		s:remove("deliveredSeason")
		SpireShop.setCoins(player, 1000)
		logger.info("[LOADTEST] rv shopon {} coins={}", player:getName(), SpireShop.coinsOf(player))
	elseif cmd == "newseason" then
		local s = kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-shop")
		s:set("deliveredSeason", SpireSeason.current() - 1)      -- as if it was bought last season
		local had = player:getItemCount(2911)
		player:removeItem(2911, had)                              -- the wipe took the character and its items
		logger.info("[LOADTEST] rv newseason {} had={} bought={}", player:getName(), had, tostring((s:get("bought") or {}).candelabrum))
		local pid = player:getId()
		addEvent(function()
			local p = Player(pid)
			if p then
				p:remove()
			end
		end, 500)
	elseif cmd == "shopstate" then
		local inbox = player:getStoreInbox()
		logger.info("[LOADTEST] rv shopstate {} inbox={} carried={}", player:getName(), inbox and inbox:getItemCountById(2911) or -1,
			player:getItemCount(2911))
	elseif cmd == "perkhit" then
		local function hit()
			local m = Game.createMonster("Stonehorn Ram", player:getPosition(), true, true)   -- 900 health: 20% still takes a full hit
			m:addHealth(-math.floor(m:getMaxHealth() * 0.8))
			local before = m:getHealth()
			logger.info("[LOADTEST] rv perkmon {} hp={} max={}", player:getName(), m:getHealth(), m:getMaxHealth())
			doTargetCombatHealth(player, m, COMBAT_PHYSICALDAMAGE, -100, -100, CONST_ME_NONE, ORIGIN_MELEE)
			local d = before - m:getHealth()
			m:remove()
			return d
		end
		player:kv():scoped("spirebound-perks"):remove("floor1")
		SpirePerks.apply(player)
		local plain = hit()
		SpirePerks.choose(player, 1, "executioner")
		local perk = hit()
		local fx = SpirePerks.effects(player)
		logger.info("[LOADTEST] rv perkhit {} plain={} executioner={} effects={} pure={}", player:getName(), plain, perk, #fx,
			SpirePerks.dealt(fx, 100, 0.2, false, function() return 1 end))
	elseif cmd == "pvpdmg" then
		local o = Player(rest)
		if not o then
			logger.info("[LOADTEST] rv pvpdmg {} seen=-1", player:getName())
			return true
		end
		local spot = Position(1250, 1055, 7)
		player:teleportTo(spot, true)
		o:teleportTo(Position(spot.x + 1, spot.y, spot.z), true)
		local hp = player:getHealth()
		doTargetCombatHealth(o, player, COMBAT_ENERGYDAMAGE, -100, -100, CONST_ME_NONE)
		logger.info("[LOADTEST] rv pvpdmg {} lost={} seen={}", player:getName(), hp - player:getHealth(),
			SpirePvP.damageFrom(player:getGuid(), o:getGuid(), os.time(), 60))
	elseif cmd == "privprep" then
		if not Floors.get(1).bossDeadAt then
			Floors.recordClear(1, { "Loadbot" }, nil, 0)        -- Floor 2 open on this test copy
		end
		local k = player:kv():scoped("spirebound")
		if rest == "key" then
			k:set("stair_key_pilot", 1)
		else
			k:remove("stair_key_pilot")
		end
		player:kv():scoped("spirebound-bosslock"):remove("1")
		SpireBoss.privateBusy[1] = nil
		local d = WorldPoints.lab3_up
		player:teleportTo(Position(d.x + 1, d.y, d.z), true)
		logger.info("[LOADTEST] rv privprep {} key={} floor2={}", player:getName(), SpireStairKey.has(player) and 1 or 0, Floors.isOpen(2) and 1 or 0)
	elseif cmd == "floorsreset" then                       -- undo privprep's Floor 1 clear (the test database is shared)
		for n = 1, 10 do
			Floors.reset(n)
		end
		logger.info("[LOADTEST] rv floorsreset {} floor2={}", player:getName(), Floors.isOpen(2) and 1 or 0)
	elseif cmd == "where" then
		local p = player:getPosition()
		logger.info("[LOADTEST] rv where {} x={} y={} z={}", player:getName(), p.x, p.y, p.z)
	elseif cmd == "goto" then
		local n = Npc(rest)
		if n then
			local p = n:getPosition()
			player:teleportTo(Position(p.x, p.y + 1, p.z), true)
		end
		player:setBankBalance(player:getBankBalance() + 1000)
		state(player, "goto")
	elseif cmd == "crystalfloor" then
		local iid = 3251
		local def = SpireCrystalData.byItem[iid]
		local mode, x, y, z = rest:match("^(%a+)%s+(%d+)%s+(%d+)%s+(%d+)$")
		player:teleportTo(Position(tonumber(x), tonumber(y), tonumber(z)), true)
		local me = player:getPosition()
		local spot = Position(me.x - 1, me.y, me.z)
		for _, it in ipairs(Tile(spot) and Tile(spot):getItems() or {}) do
			it:remove()
		end
		local had = player:getItemCount(iid)
		if had > 0 then
			player:removeItem(iid, 1)
		end
		local placed = Game.createItem(iid, 1, spot)
		logger.info("[LOADTEST] rv crystalstack {} index={} top={}", player:getName(), Tile(spot):getThingIndex(placed),
			Tile(spot):getTopVisibleThing(player) and Tile(spot):getTopVisibleThing(player):getId() or 0)
		if mode == "fight" then
			local m = Game.createMonster("Meadow Wolf", Position(me.x, me.y + 1, me.z), true, true)
			if m then
				doTargetCombatHealth(m, player, COMBAT_PHYSICALDAMAGE, -5, -5, CONST_ME_NONE)
				m:remove()
			end
		end
		local choices = SpireCrystals.choices(1, player:getLevel(), "town")
		local town = SpireCrystals.townPos(def)
		local g = choices[2] and choices[2].pos or { 0, 0, 0 }
		logger.info("[LOADTEST] rv crystalfloor {} had={} spot={},{},{} town={},{},{} ground={},{},{} gid={}", player:getName(), had,
			spot.x, spot.y, spot.z, town.x, town.y, town.z, g[1], g[2], g[3], choices[2] and choices[2].id or "none")
	elseif cmd == "crystalcount" then
		local me = player:getPosition()
		local t = Tile(Position(me.x - 1, me.y, me.z))
		logger.info("[LOADTEST] rv crystalcount {} carried={} x={} y={} z={}", player:getName(), player:getItemCount(3251), me.x, me.y, me.z)
	elseif cmd == "chestprep" then
		local gid, alt = rest:match("^(%S+)%s*(%a*)$")
		player:kv():scoped("spirebound-chests"):remove(gid)
		if alt ~= "alt" then
			kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-chests-first"):remove(gid)
		end
		local c = WorldPoints["chest_" .. gid]
		player:teleportTo(Position(c.x, c.y + 1, c.z), true)
		state(player, "chestprep")
	elseif cmd == "wellvein" then
		local pos = WorldPoints.secret_s10
		kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-secretgold"):remove("s10")
		local secrets = player:kv():scoped("spirebound-secrets")
		local function stepOn()
			secrets:remove("s10")
			player:teleportTo(Position(pos.x, pos.y + 2, pos.z), true)
			local before = player:getBankBalance() + player:getMoney()
			player:teleportTo(pos)
			return player:getBankBalance() + player:getMoney() - before
		end
		local first = stepOn()
		local second = stepOn()
		logger.info("[LOADTEST] rv wellvein {} first={} second={}", player:getName(), first, second)
	elseif cmd == "taskdone" then
		local rhen = Npc("Taskmaster Rhen")
		if rhen then
			local rp = rhen:getPosition()
			player:teleportTo(Position(rp.x, rp.y + 1, rp.z), true)
		end
		local s = SpireTasks.scope(player)
		local t = SpireTasks.get("t1_fieldrat")
		s:set("active", t.id)
		s:set("kills", t.count)
		local bp = player:getSlotItem(CONST_SLOT_BACKPACK)
		local filled = 0
		while bp and bp:getEmptySlots(false) > 0 and filled < 40 do
			bp:addItem(3003, 1) -- ropes: one per slot, until the backpack is full
			filled = filled + 1
		end
		local before = player:getBankBalance() + player:getMoney()
		local ok, text = SpireTasks.report(player)
		logger.info("[LOADTEST] rv taskdone {} ok={} reward={} gained={} free_slots={}", player:getName(), ok and 1 or 0, t.gold,
			player:getBankBalance() + player:getMoney() - before, bp and bp:getEmptySlots(false) or -1)
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
