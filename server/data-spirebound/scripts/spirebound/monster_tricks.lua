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

-- Small helpers -------------------------------------------------------------------------------------------------
local function nowMs()
	return systemTime and systemTime() or os.time() * 1000
end

local function chance(pct)
	return math.random(100) <= pct
end

local function targetPlayer(mon)
	local t = mon:getTarget()
	return t and t:isPlayer() and t or nil
end

local function nextTo(a, b)
	local p, q = a:getPosition(), b:getPosition()
	return p.z == q.z and math.abs(p.x - q.x) <= 1 and math.abs(p.y - q.y) <= 1
end

-- Field Rat: snatches a few coins from your backpack and bolts. Killing it gets them back (they're in its body).
SpireTricks = SpireTricks or { stolen = {} }
local steal = CreatureEvent("SpireRatSteal")
function steal.onThink(creature, interval)
	local mon = creature:getMonster()
	local player = mon and targetPlayer(mon)
	if not player or SpireTricks.stolen[mon:getId()] or not nextTo(mon, player) or not chance(4) then
		return true
	end
	local carried = player:getMoney()
	if carried <= 0 then
		return true
	end
	local n = math.min(carried, math.random(3, 8))
	if not player:removeMoney(n) then
		return true
	end
	SpireTricks.stolen[mon:getId()] = n
	mon:say("Squeak! (the rat snatches " .. n .. " gold and bolts)", TALKTYPE_MONSTER_SAY)
	player:sendTextMessage(MESSAGE_STATUS, "A Field Rat stole " .. n .. " gold from you! Kill it to get it back.")
	mon:getPosition():sendMagicEffect(CONST_ME_POFF)
	local haste = Condition(CONDITION_HASTE)
	haste:setParameter(CONDITION_PARAM_TICKS, 6000)
	haste:setParameter(CONDITION_PARAM_SPEED, 120)
	mon:addCondition(haste)
	-- run away from the player for a few steps
	local id, from = mon:getId(), player:getPosition()
	for i = 1, 4 do
		addEvent(function()
			local m = Monster(id)
			if not m then
				return
			end
			local p = m:getPosition()
			local dx, dy = p.x - from.x, p.y - from.y
			local dir
			if math.abs(dx) >= math.abs(dy) then
				dir = dx >= 0 and DIRECTION_EAST or DIRECTION_WEST
			else
				dir = dy >= 0 and DIRECTION_SOUTH or DIRECTION_NORTH
			end
			m:move(dir)
		end, i * 350)
	end
	return true
end
steal:register()

local stealDeath = CreatureEvent("SpireRatStealDeath")
function stealDeath.onDeath(creature, corpse)
	SpireTricks.dropStolen(creature, corpse)
	return true
end

function SpireTricks.dropStolen(creature, corpse)
	local n = SpireTricks.stolen[creature:getId()]
	SpireTricks.stolen[creature:getId()] = nil
	if n and n > 0 then
		if corpse and corpse:isContainer() then
			corpse:addItem(3031, n)
		else
			Game.createItem(3031, n, creature:getPosition())
		end
	end
	return n or 0
end
stealDeath:register()

-- Meadow Wolf: when it is hurt, it howls once and every wolf nearby without a fight joins in on the same climber.
SpireTricks.howled = SpireTricks.howled or {}
local howl = CreatureEvent("SpireWolfCall")
function howl.onThink(creature, interval)
	local mon = creature:getMonster()
	local player = mon and targetPlayer(mon)
	if not player or SpireTricks.howled[mon:getId()] or mon:getHealth() > mon:getMaxHealth() * 0.6 then
		return true
	end
	SpireTricks.howled[mon:getId()] = true
	mon:say("AWOOOO! (the wolf calls its pack)", TALKTYPE_MONSTER_YELL)
	mon:getPosition():sendMagicEffect(CONST_ME_SOUND_WHITE)
	local joined = 0
	for _, c in ipairs(Game.getSpectators(mon:getPosition(), false, false, 7, 7, 5, 5)) do
		local other = c:getMonster()
		if other and other ~= mon and other:getName() == mon:getName() and not other:getTarget() and joined < 2 then
			if other.selectTarget then
				other:selectTarget(player)
			end
			other:getPosition():sendMagicEffect(CONST_ME_SOUND_WHITE)
			joined = joined + 1
		end
	end
	return true
end
howl:register()

local howlDeath = CreatureEvent("SpireWolfCallDeath")
function howlDeath.onDeath(creature)
	SpireTricks.howled[creature:getId()] = nil
	return true
end
howlDeath:register()

-- Sproutling: mends a hurt sproutling next to it now and then. Kill the healer first.
local mend = CreatureEvent("SpireSproutMend")
function mend.onThink(creature, interval)
	local mon = creature:getMonster()
	if mon and mon:getTarget() and chance(6) then
		SpireTricks.mend(mon)
	end
	return true
end
mend:register()

function SpireTricks.mend(mon)
	for _, c in ipairs(Game.getSpectators(mon:getPosition(), false, false, 3, 3, 3, 3)) do
		local other = c:getMonster()
		if other and other ~= mon and other:getName() == mon:getName() and other:getHealth() < other:getMaxHealth() * 0.7 then
			local amount = math.max(8, math.floor(other:getMaxHealth() * 0.3))
			other:addHealth(amount)
			other:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
			mon:say("*the sproutling hums; a friend's leaves grow back*", TALKTYPE_MONSTER_SAY)
			return true
		end
	end
	return false
end

-- Ruin Sentinel: raises its shield for 4 seconds. While it is up, hits from the front do half damage, so walk round it
-- (or wait). The front is the side the sentinel faces.
SpireTricks.shield = SpireTricks.shield or {}
local shieldUp = CreatureEvent("SpireShieldWall")
function shieldUp.onThink(creature, interval)
	local mon = creature:getMonster()
	local player = mon and targetPlayer(mon)
	local now = nowMs()
	local until_ = SpireTricks.shield[mon and mon:getId() or 0]
	if not player or (until_ and until_ > now - 6000) or not nextTo(mon, player) or not chance(8) then
		return true
	end
	SpireTricks.shield[mon:getId()] = now + 4000
	mon:say("*raises its shield*", TALKTYPE_MONSTER_SAY)
	mon:getPosition():sendMagicEffect(CONST_ME_BLOCKHIT)
	return true
end
shieldUp:register()

local DIR = { [DIRECTION_NORTH] = { 0, -1 }, [DIRECTION_SOUTH] = { 0, 1 }, [DIRECTION_EAST] = { 1, 0 }, [DIRECTION_WEST] = { -1, 0 } }
function SpireTricks.inFront(mon, attacker)
	local d = DIR[mon:getDirection()]
	if not d then
		return false
	end
	local p, q = mon:getPosition(), attacker:getPosition()
	local dx, dy = q.x - p.x, q.y - p.y
	return dx * d[1] + dy * d[2] > 0
end

local shieldHit = CreatureEvent("SpireShieldWallHit")
function shieldHit.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local until_ = SpireTricks.shield[creature:getId()]
	if until_ and until_ > nowMs() and attacker and primaryType ~= COMBAT_HEALING and SpireTricks.inFront(creature, attacker) then
		primaryDamage = math.floor(primaryDamage / 2)
		secondaryDamage = math.floor(secondaryDamage / 2)
		creature:getPosition():sendMagicEffect(CONST_ME_BLOCKHIT)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
shieldHit:register()

local shieldDeath = CreatureEvent("SpireShieldWallDeath")
function shieldDeath.onDeath(creature)
	SpireTricks.shield[creature:getId()] = nil
	return true
end
shieldDeath:register()
