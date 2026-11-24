-- Monster tricks that need a script (FLOOR1_REVIEW.md F1-10). The simple ones (slows, charges, burrowing, fleeing)
-- are plain monster spells in tools/gen_monsters.py.

-- Shardlings die in a burst: a flash where they fall, then a second later everyone next to the body takes energy
-- damage. Melee players learn to step back. Damage scales with the shardling's experience (Prism Shardling hits harder).
local burst = CreatureEvent("SpireShardBurst")
function burst.onDeath(creature, corpse)
	local pos = creature:getPosition()
	local power = math.max(20, math.floor(creature:getType():experience() / 3))
	pos:sendMagicEffect(CONST_ME_ENERGYHIT)
	addEvent(function()
		local here = Position(pos.x, pos.y, pos.z)
		here:sendMagicEffect(CONST_ME_ENERGYAREA)
		for _, c in ipairs(Game.getSpectators(here, false, true, 1, 1, 1, 1)) do
			doTargetCombatHealth(0, c, COMBAT_ENERGYDAMAGE, -math.floor(power / 2), -power, CONST_ME_ENERGYHIT)
		end
	end, 1000)
	return true
end
burst:register()
