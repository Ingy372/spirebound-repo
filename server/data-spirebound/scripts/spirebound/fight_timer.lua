-- The fight lock ends shortly after the last real hit (Grok session 3, SB3-02).
-- The engine keeps a player "in a fight" (no logout) for as long as any monster has picked them as its target, even
-- one that can never reach them: respawning pen rats behind the fence kept new characters from logging out for 6 to
-- 13 minutes, and one was killed by a wandering boar while stuck. Now the lock lifts once nothing has hit the player,
-- and the player has attacked nothing, for SpireFightTimer.QUIET seconds. A player-killing lock (the skull timer)
-- is never touched: that one belongs to PvP.
SpireFightTimer = { QUIET = 15 }

local lastHit = {} -- player guid -> os.time() of the last damage taken or the last moment with a target

local hits = CreatureEvent("SpireFightTimerHit")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	if attacker and (primaryType ~= COMBAT_HEALING) and (primaryDamage ~= 0 or secondaryDamage ~= 0) then -- (either sign: see bosses_floor1.lua)
		lastHit[creature:getGuid()] = os.time()
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hits:register()

local login = CreatureEvent("SpireFightTimerLogin")
function login.onLogin(player)
	player:registerEvent("SpireFightTimerHit")
	return true
end
login:register()

-- pure, for the tests: may this lock be lifted?
function SpireFightTimer.quiet(now, last, hasTarget, pzLocked)
	return not hasTarget and not pzLocked and now - (last or 0) >= SpireFightTimer.QUIET
end

local tick = GlobalEvent("SpireFightTimerTick")
function tick.onThink(interval)
	local now = os.time()
	for _, p in ipairs(Game.getPlayers()) do
		local g = p:getGuid()
		local target = p:getTarget()
		if target then
			lastHit[g] = now
		end
		if p:getCondition(CONDITION_INFIGHT, CONDITIONID_DEFAULT)
			and SpireFightTimer.quiet(now, lastHit[g], target ~= nil, p:isPzLocked()) then
			p:removeCondition(CONDITION_INFIGHT)
		end
	end
	return true
end
tick:interval(2000)
tick:register()

if SpireCleanup then
	SpireCleanup.add(function(pid, guid) lastHit[guid] = nil end)
end
