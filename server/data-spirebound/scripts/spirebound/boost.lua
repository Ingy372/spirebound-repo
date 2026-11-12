-- Wires the boosted creature of the day (lib/spirebound/boost.lua) into experience and loot.
local xp = EventCallback("SpireBoostXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	if target and target:isMonster() and SpireBoost.isBoosted(target:getName()) then
		return math.floor(exp * SpireBoost.XP)
	end
	return exp
end
xp:register()

local loot = EventCallback("SpireBoostLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	local mType = monster:getType()
	if owner and mType and SpireBoost.isBoosted(monster:getName()) then
		corpse:addLoot(mType:generateLootRoll({ factor = SpireBoost.LOOT_BONUS, gut = false }, {}, owner))
	end
end
loot:register()
