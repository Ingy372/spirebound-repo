-- Wires the difficulty rules (lib/spirebound/difficulty.lua) into the game.

-- In-memory: last time an outside player damaged a Death Game character, by guid.
local lastOutsideHit = {}

-- XP bonus
local xp = EventCallback("SpireDifficultyXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	return math.floor(Difficulty.applyXp(Difficulty.get(player), exp) * SpireCavebot.xpFactor(player) * SpireSiege.factor(player))
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
	if victim and hitter and (primaryDamage > 0 or secondaryDamage > 0) then
		if Difficulty.countsAsOutsidePlayer(Difficulty.playerInfo(victim), Difficulty.playerInfo(hitter)) then
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
	if Difficulty.isPvPSavedDeath(lastOutsideHit[guid], os.time()) then
		logger.info("[Spirebound] Death Game character {} died with recent PvP damage: saved (not retired)", player:getName())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Another player struck you moments before your death. The tower spares your life this time.")
	else
		local cause = killer and killer:getName() or "the tower"
		Difficulty.retire(player, cause)
		Game.broadcastMessage(string.format("%s, a Death Game climber of level %d, has fallen to %s. Their name is carved on the Memorial.", player:getName(), player:getLevel(), cause), MESSAGE_EVENT_ADVANCE)
		logger.info("[Spirebound] Death Game character {} retired (killed by {})", player:getName(), cause)
	end
	lastOutsideHit[guid] = nil
	return true
end
death:register()

-- Login: block retired characters, register per-player events
local login = CreatureEvent("SpireDifficultyLogin")
function login.onLogin(player)
	if Difficulty.isRetired(player) then
		player:sendCancelMessage("This character fell in the Death Game and rests on the Memorial.")
		return false
	end
	player:registerEvent("SpireDeathGameHits")
	player:registerEvent("SpireDeathGameDeath")
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
