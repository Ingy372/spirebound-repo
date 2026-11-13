-- Wires the difficulty rules (lib/spirebound/difficulty.lua) into the game.

-- In-memory: last time an outside player damaged a Death Game character, by guid.
local lastOutsideHit = {}

-- XP bonus
local xp = EventCallback("SpireDifficultyXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	local mode = Difficulty.get(player)
	local withBonus = Difficulty.applyXp(mode, exp)
	if withBonus > exp then -- remember what the harder mode's bonus gave (stepping down takes it back, Q14)
		local s = player:kv():scoped("spirebound")
		s:set("bonusXp", (s:get("bonusXp") or 0) + (withBonus - exp))
	end
	return math.floor(withBonus * SpireCavebot.xpFactor(player) * SpireSiege.factor(player))
end
xp:register()

-- Heavier death XP loss for Hardcore (and for Death Game deaths saved by PvP)
local lose = EventCallback("SpireDifficultyLoseXp")
function lose.playerOnLoseExperience(player, exp)
	local lost = Difficulty.finalDeathLoss(Difficulty.get(player), exp, player:getLevel(), player:getExperience())
	return math.floor(lost * SpirePvP.deathLossMultiplier(player:getSkull()))
end
lose:register()

-- Catch-up: skills train twice as fast below level 50 (DESIGN.md 15)
local skills = EventCallback("SpireCatchUpSkills")
function skills.playerOnGainSkillTries(player, skill, tries)
	if player:getLevel() < 50 then
		tries = tries * 2
	end
	-- Hardcore skill debt from a death is paid off first
	local debts = player:kv():scoped("spirebound-skilldebt")
	local debt = debts:get(tostring(skill))
	if debt and debt > 0 then
		local left
		tries, left = Difficulty.payDebt(debt, tries)
		debts:set(tostring(skill), left)
		if left == 0 then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your Hardcore death penalty for this skill is paid off.")
		end
	end
	return tries
end
skills:register()

-- Loot bonus: an extra, scaled loot roll for Hardcore / Death Game corpse owners
local loot = EventCallback("SpireDifficultyLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local player = Player(corpse:getCorpseOwner())
	if not player or not player:canReceiveLoot() then
		return
	end
	local bonus = (Difficulty.lootBonus[Difficulty.get(player)] or 0) + (SpireSiege.factor(player) - 1) -- Siege holders: +5%
	local mType = monster:getType()
	if bonus <= 0 or not mType then
		return
	end
	corpse:addLoot(mType:generateLootRoll({ factor = bonus, gut = false }, {}, player))
end
loot:register()

-- Track outside-player damage on Death Game characters
local hits = CreatureEvent("SpireDeathGameHits")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local victim = creature:getPlayer()
	local hitter = attacker and attacker:getPlayer()
	if not hitter and attacker and attacker:getMaster() then
		hitter = attacker:getMaster():getPlayer() -- summons count as their owner
	end
	local amount = math.max(0, primaryDamage) + math.max(0, secondaryDamage)
	if victim and amount > 0 and attacker and attacker:isMonster() and not attacker:getMaster() then
		SpireDeathGame.noteMonsterHit(attacker:getId(), victim:getGuid(), os.time()) -- for the "dragged in" rule
	end
	if victim and hitter and hitter ~= victim and amount > 0 and Difficulty.get(victim) == Difficulty.DEATHGAME then
		local outside = Difficulty.countsAsOutsidePlayer(Difficulty.playerInfo(victim), Difficulty.playerInfo(hitter))
		SpireDeathGame.noteHit(victim:getGuid(), { guid = hitter:getGuid(), outside = outside }, amount, os.time())
		if outside then
			lastOutsideHit[victim:getGuid()] = os.time()
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hits:register()

-- Death Game: PvE death retires the character; PvP-saved deaths do not
local death = CreatureEvent("SpireDeathGameDeath")
function death.onDeath(player, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	if Difficulty.get(player) ~= Difficulty.DEATHGAME then
		return true
	end
	local guid = player:getGuid()
	local victimInfo = Difficulty.playerInfo(player)
	-- who struck the killing blow (summons count as their owner)
	local k = nil
	local kp = killer and (killer:getPlayer() or (killer:getMaster() and killer:getMaster():getPlayer()))
	if kp and kp ~= player then
		k = { guid = kp:getGuid(), outside = Difficulty.countsAsOutsidePlayer(victimInfo, Difficulty.playerInfo(kp)) }
	elseif killer and killer:isMonster() then
		k = { monsterId = killer:getId() }
	end
	local verdict, why = SpireDeathGame.judge(guid, player:getMaxHealth(), k, os.time(), function(otherGuid)
		local other = Player(otherGuid)
		return other ~= nil and Difficulty.countsAsOutsidePlayer(victimInfo, Difficulty.playerInfo(other))
	end)
	if verdict == "saved" then
		logger.info("[Spirebound] Death Game character {} saved, not retired ({})", player:getName(), why)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "This was not the tower's doing (" .. why .. "). It spares your life this time.")
	else
		local cause = killer and killer:getName() or "the tower"
		Difficulty.retire(player, cause)
		SpireDeathGame.free(guid)
		player:save()
		Game.broadcastMessage(string.format("%s, a Death Game climber of level %d, has fallen to %s. Their name is carved on the Memorial.", player:getName(), player:getLevel(), cause), MESSAGE_EVENT_ADVANCE)
		logger.info("[Spirebound] Death Game character {} retired (killed by {})", player:getName(), cause)
	end
	lastOutsideHit[guid] = nil
	SpireDeathGame.forget(guid)
	return true
end
death:register()

-- The Deathbound title (account-wide): a Death Game character that reaches level 50 alive
local bound = CreatureEvent("SpireDeathbound")
function bound.onAdvance(player, skill, oldLevel, newLevel)
	if skill == SKILL_LEVEL and SpireDeathGame.earnsDeathbound(Difficulty.get(player), newLevel, Difficulty.isRetired(player)) then
		local acc = SpireSeason.accountKv(player:getAccountId())
		local titles = acc:get("titles") or {}
		local t = "Deathbound (Season " .. SpireSeason.current() .. ")"
		if not titles[t] then
			titles[t] = SpireSeason.current()
			acc:set("titles", titles)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Level 50 on the Death Game: you have earned the title Deathbound.")
		end
	end
	return true
end
bound:register()

-- GM: /restore <name> brings back a character retired by an unfair death (server crash or server lag)
local restore = TalkAction("/restore")
function restore.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	local ok, why = SpireDeathGame.restore(param or "")
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, ok and (param .. " is restored and may log in again.") or ("Not restored: " .. why))
	logger.info("[Spirebound] GM {} used /restore {}: {}", player:getName(), param, ok and "restored" or why)
	return false
end
restore:separator(" ")
restore:groupType("gamemaster")
restore:register()

-- Login: block retired characters, register per-player events
local login = CreatureEvent("SpireDifficultyLogin")
function login.onLogin(player)
	if Difficulty.isRetired(player) then
		player:sendCancelMessage("This character fell in the Death Game and rests on the Memorial.")
		return false
	end
	player:registerEvent("SpireDeathGameHits")
	player:registerEvent("SpireDeathGameDeath")
	player:registerEvent("SpireDeathbound")
	player:registerEvent("SpireHardcorePrepareDeath")
	player:registerEvent("SpireHardcoreItemDrop")
	SpireHardcore.settleDeath(player)
	return true
end
login:register()

-- Hardcore: skill debt and extra item drops (roadmap 2.14b) --------------
SpireHardcore = {}
local SKILLS = { SKILL_FIST, SKILL_CLUB, SKILL_SWORD, SKILL_AXE, SKILL_DISTANCE, SKILL_SHIELD, SKILL_FISHING }

local function snapshot(player)
	local snap = { magic = { player:getBaseMagicLevel(), player:getManaSpent() } }
	for _, s in ipairs(SKILLS) do
		snap[tostring(s)] = { player:getSkillLevel(s), player:getSkillTries(s) }
	end
	return snap
end

-- Called at login: compare with the snapshot taken just before death and add the Hardcore extra as debt
function SpireHardcore.settleDeath(player)
	local store = player:kv():scoped("spirebound")
	local snap = store:get("deathsnap")
	if not snap then
		return
	end
	store:remove("deathsnap")
	local voc = player:getVocation()
	local debts = player:kv():scoped("spirebound-skilldebt")
	local total = 0
	for _, s in ipairs(SKILLS) do
		local b = snap[tostring(s)]
		if b then
			local lost = Difficulty.lostTries(function(l) return voc:getRequiredSkillTries(s, l) end, b[1], b[2], player:getSkillLevel(s), player:getSkillTries(s))
			local add = Difficulty.skillDebt(Difficulty.HARDCORE, lost)
			if add > 0 then
				debts:set(tostring(s), (debts:get(tostring(s)) or 0) + add)
				total = total + add
			end
		end
	end
	local m = snap.magic
	if m then
		local lost = Difficulty.lostTries(function(l) return voc:getRequiredManaSpent(l) end, m[1], m[2], player:getBaseMagicLevel(), player:getManaSpent())
		local add = Difficulty.skillDebt(Difficulty.HARDCORE, lost)
		if add > 0 then
			debts:set(tostring(SKILL_MAGLEVEL), (debts:get(tostring(SKILL_MAGLEVEL)) or 0) + add)
			total = total + add
		end
	end
	if total > 0 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Hardcore: your death costs extra training. Your next skill and magic progress goes to paying it off first.")
	end
end

local prep = CreatureEvent("SpireHardcorePrepareDeath")
function prep.onPrepareDeath(player, killer, realDamage)
	if Difficulty.get(player) == Difficulty.HARDCORE then
		player:kv():scoped("spirebound"):set("deathsnap", snapshot(player))
	end
	return true
end
prep:register()

local AMULET_OF_LOSS = 3057
local DROP_SLOTS = { CONST_SLOT_HEAD, CONST_SLOT_NECKLACE, CONST_SLOT_ARMOR, CONST_SLOT_RIGHT, CONST_SLOT_LEFT, CONST_SLOT_LEGS, CONST_SLOT_FEET, CONST_SLOT_RING, CONST_SLOT_AMMO }

local drop = CreatureEvent("SpireHardcoreItemDrop")
function drop.onDeath(player, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	if not corpse or Difficulty.get(player) ~= Difficulty.HARDCORE then
		return true
	end
	local neck = player:getSlotItem(CONST_SLOT_NECKLACE)
	if neck and neck:getId() == AMULET_OF_LOSS then
		neck:remove() -- no amulet protects a Hardcore character (DESIGN.md 5.5)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your amulet of loss shatters. It cannot protect a Hardcore climber.")
	end
	local skull = player:getSkull()
	local tile = Tile(player:getPosition())
	local chance = Difficulty.extraItemDropChance(Difficulty.HARDCORE, skull == SKULL_RED or skull == SKULL_BLACK, tile and tile:hasFlag(TILESTATE_PVPZONE))
	if chance <= 0 then
		return true
	end
	for _, slot in ipairs(DROP_SLOTS) do
		local item = player:getSlotItem(slot)
		if item and math.random(1, 1000) <= chance * 10 then
			item:moveTo(corpse)
		end
	end
	return true
end
drop:register()
