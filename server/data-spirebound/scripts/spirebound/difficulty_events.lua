-- Wires the difficulty rules (lib/spirebound/difficulty.lua) into the game.

-- In-memory: last time an outside player damaged a Death Game character, by guid.
local lastOutsideHit = {}

-- XP bonus
local xp = EventCallback("SpireDifficultyXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	return math.floor(Difficulty.applyXp(Difficulty.get(player), exp) * SpireCavebot.xpFactor(player))
end
xp:register()

-- Heavier death XP loss for Hardcore (and for Death Game deaths saved by PvP)
local lose = EventCallback("SpireDifficultyLoseXp")
function lose.playerOnLoseExperience(player, exp)
	local lost = Difficulty.applyDeathLoss(Difficulty.get(player), exp)
	return math.floor(lost * SpirePvP.deathLossMultiplier(player:getSkull()))
end
lose:register()

-- Loot bonus: an extra, scaled loot roll for Hardcore / Death Game corpse owners
local loot = EventCallback("SpireDifficultyLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local player = Player(corpse:getCorpseOwner())
	if not player or not player:canReceiveLoot() then
		return
	end
	local bonus = Difficulty.lootBonus[Difficulty.get(player)] or 0
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
	return true
end
login:register()
