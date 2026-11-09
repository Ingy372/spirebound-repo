-- Spirebound difficulty modes (DESIGN.md 5.4 and 6.6).
-- Pure rules live here so in-game tests can check them without a logged-in player.

Difficulty = {
	NONE = 0, -- not chosen yet (still in the Arrival Yard)
	NORMAL = 1,
	HARDCORE = 2,
	DEATHGAME = 3,
}

Difficulty.names = { [1] = "Normal", [2] = "Hardcore", [3] = "Death Game" }
Difficulty.xpBonus = { [0] = 0, [1] = 0, [2] = 0.25, [3] = 0.50 }
Difficulty.lootBonus = { [0] = 0, [1] = 0, [2] = 0.15, [3] = 0.30 }
Difficulty.deathXpLossMultiplier = { [0] = 1, [1] = 1, [2] = 1.5, [3] = 1.5 }
Difficulty.PVP_SAVE_WINDOW = 60 -- seconds: outside-player damage this recent makes a Death Game death a PvP death

-- You may pick any mode once, then only ever move down (3 -> 2 -> 1).
function Difficulty.canChange(current, new)
	if not Difficulty.names[new] then
		return false
	end
	if current == Difficulty.NONE then
		return true
	end
	return new < current
end

function Difficulty.applyXp(mode, exp)
	return math.floor(exp * (1 + (Difficulty.xpBonus[mode] or 0)) + 0.5)
end

function Difficulty.applyDeathLoss(mode, lostExp)
	return math.floor(lostExp * (Difficulty.deathXpLossMultiplier[mode] or 1) + 0.5)
end

-- Tibia's unblessed death loss for a level (used for the Hardcore blessing cap)
function Difficulty.baseDeathLoss(level, totalExp)
	if level < 24 then
		return math.floor(totalExp * 0.1)
	end
	return math.floor(((level + 50) / 100) * 50 * (level * level - 5 * level + 8))
end

-- Final death loss. Hardcore: x1.5, and blessings can only remove half of the unblessed loss.
-- Catch-up (DESIGN.md 15): Normal characters below level 50 lose nothing.
function Difficulty.finalDeathLoss(mode, engineLoss, level, totalExp)
	if mode <= Difficulty.NORMAL and level < 50 then
		return 0
	end
	local lost = Difficulty.applyDeathLoss(mode, engineLoss)
	if mode == Difficulty.HARDCORE then
		lost = math.max(lost, math.floor(Difficulty.baseDeathLoss(level, totalExp) * 0.5))
	end
	return lost
end

-- Does damage from `attacker` count toward saving `victim` from Death Game deletion?
-- Both are plain tables: { guid, ip, guildId, partyId }. Friends can't "tag" you to make you immortal.
function Difficulty.countsAsOutsidePlayer(victim, attacker)
	if not attacker or not attacker.guid or attacker.guid == victim.guid then
		return false
	end
	if victim.ip and victim.ip ~= 0 and attacker.ip == victim.ip then
		return false
	end
	if victim.guildId and victim.guildId ~= 0 and attacker.guildId == victim.guildId then
		return false
	end
	if victim.partyId and attacker.partyId == victim.partyId then
		return false
	end
	return true
end

-- lastOutsideHit: os.time() of the last damage from an outside player (or nil).
function Difficulty.isPvPSavedDeath(lastOutsideHit, now)
	return lastOutsideHit ~= nil and (now - lastOutsideHit) <= Difficulty.PVP_SAVE_WINDOW
end

-- Player helpers ----------------------------------------------------------

local function scope(player)
	return player:kv():scoped("spirebound")
end

function Difficulty.get(player)
	return scope(player):get("difficulty") or Difficulty.NONE
end

function Difficulty.set(player, mode)
	local current = Difficulty.get(player)
	if not Difficulty.canChange(current, mode) then
		return false
	end
	scope(player):set("difficulty", mode)
	if current == Difficulty.DEATHGAME then
		scope(player):set("steppedDownAtLevel", player:getLevel())
	end
	return true
end

function Difficulty.isRetired(player)
	return scope(player):get("retired") == true
end

function Difficulty.retire(player, cause)
	scope(player):set("retired", true)
	kv.scoped("spirebound-memorial"):set(player:getName(), {
		level = player:getLevel(),
		vocation = player:getVocation():getName(),
		cause = cause or "unknown",
		time = os.time(),
	})
end

function Difficulty.playerInfo(player)
	local party = player:getParty()
	local guild = player:getGuild()
	return {
		guid = player:getGuid(),
		ip = player:getIp(),
		guildId = guild and guild:getId() or 0,
		partyId = party and party:getLeader():getGuid() or nil,
	}
end

-- Hardcore death penalties beyond XP (roadmap 2.14b) ---------------------
-- Skills: the engine takes its normal loss; Hardcore adds half of that again as a "skill debt" that eats your
-- next training of that skill (the engine has no way to remove skill progress from a script).
-- Items: Hardcore rolls a second, equal chance for every equipped item (backpack excluded) to fall into the corpse.
Difficulty.HARDCORE_SKILL_EXTRA = 0.5
Difficulty.ITEM_DROP_BASE = 10 -- percent per item with no blessings; each of 5 blessings removes a fifth

-- Pure: total progress lost between two (level, tries) states. req(level) = tries needed to REACH that level.
function Difficulty.lostTries(req, levelBefore, triesBefore, levelAfter, triesAfter)
	local lost = triesBefore - triesAfter
	for l = levelAfter + 1, levelBefore do
		lost = lost + req(l)
	end
	return math.max(0, lost)
end

-- Pure: extra skill debt for a death that lost `lost` tries
function Difficulty.skillDebt(mode, lost)
	if mode ~= Difficulty.HARDCORE then
		return 0
	end
	return math.floor(lost * Difficulty.HARDCORE_SKILL_EXTRA)
end

-- Pure: incoming training pays the debt first. Returns tries that still count, debt left.
function Difficulty.payDebt(debt, tries)
	if not debt or debt <= 0 then
		return tries, 0
	end
	if tries <= debt then
		return 0, debt - tries
	end
	return tries - debt, 0
end

-- Pure: Hardcore's extra drop chance (percent) per equipped item
function Difficulty.extraItemDropChance(mode, blessings, hasAmuletOfLoss, redOrBlackSkull, inArena)
	if mode ~= Difficulty.HARDCORE or hasAmuletOfLoss or redOrBlackSkull or inArena then
		return 0 -- red/black skulls already drop everything; arenas never drop
	end
	local b = math.max(0, math.min(5, blessings or 0))
	return Difficulty.ITEM_DROP_BASE * (5 - b) / 5
end
