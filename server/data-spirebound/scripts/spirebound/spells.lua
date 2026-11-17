-- Builds every row of SpireSpells.list (lib/spirebound/spells.lua) into a Canary spell.
-- Spells need no learning: they work as soon as the character reaches the level (Jay, 2026-11-08).

local VOC_NAMES = {
	[1] = { "arcanist;true", "high arcanist;true" },
	[2] = { "mystic;true", "elder mystic;true" },
	[3] = { "ranger;true", "far warden;true" },
	[4] = { "vanguard;true", "blade warden;true" },
}

local AREAS, DIRECTIONAL, ON_TARGET = SpireSpells.AREAS, SpireSpells.DIRECTIONAL, SpireSpells.ON_TARGET

-- the value a row's numbers grow with
local function stat(row, player)
	if row.scale == "distance" then
		return player:getEffectiveSkillLevel(SKILL_DISTANCE)
	elseif row.scale == "melee" then
		return math.max(player:getEffectiveSkillLevel(SKILL_SWORD), player:getEffectiveSkillLevel(SKILL_AXE), player:getEffectiveSkillLevel(SKILL_CLUB))
	elseif row.scale == "level" then
		return player:getLevel()
	end
	return player:getMagicLevel()
end

local function formula(row, player)
	return SpireSpells.range(row, player:getLevel(), stat(row, player))
end

local function fx(pos, effect)
	if effect and effect ~= 0 then
		pos:sendMagicEffect(effect)
	end
end

local function shootFx(from, to, anim)
	if anim and from ~= to then
		from:sendDistanceEffect(to, anim)
	end
end

local function partyAround(player, radius)
	local out = { player }
	local party = player:getParty()
	if party and radius > 0 then
		local members = party:getMembers()
		table.insert(members, party:getLeader())
		out = {}
		for _, m in ipairs(members) do
			if m:getPosition():getDistance(player:getPosition()) <= radius and m:getPosition().z == player:getPosition().z then
				table.insert(out, m)
			end
		end
	end
	return out
end

-- The ally a targeted support spell lands on: nobody named = yourself; a name = that player, who must be within 7
-- tiles, on your floor and in sight (otherwise the spell is refused with a message and costs nothing).
-- Names with a space go in quotes, as in Tibia: mend other "Some Name".
local function allyTarget(player, var)
	local c = Creature(var:getNumber())
	if c and c:isPlayer() then
		return c
	end
	local name = var:getString()
	if not name or name == "" then
		return player
	end
	local t = Player(name)
	local a = player:getPosition()
	if not t or t:getPosition().z ~= a.z or a:getDistance(t:getPosition()) > 7 or not a:isSightClear(t:getPosition()) then
		player:sendCancelMessage(name .. " is not close enough to reach.")
		return nil
	end
	return t
end
SpireSpells.allyTarget = allyTarget

local BAD_CONDITIONS = { CONDITION_POISON, CONDITION_FIRE, CONDITION_ENERGY, CONDITION_BLEEDING, CONDITION_PARALYZE, CONDITION_DROWN, CONDITION_FREEZING, CONDITION_DAZZLED, CONDITION_CURSED }

local function stepToward(from, to)
	local dx = to.x == from.x and 0 or (to.x > from.x and 1 or -1)
	local dy = to.y == from.y and 0 or (to.y > from.y and 1 or -1)
	return dx, dy
end

local function walkable(pos)
	local t = Tile(pos)
	return t and t:getGround() and not t:hasFlag(TILESTATE_BLOCKSOLID) and not t:getTopCreature() and not t:hasFlag(TILESTATE_FLOORCHANGE)
end

-- Each kind returns true if the spell happened. Visuals: row.cast on the caster (sent before the kind runs),
-- row.shoot as a projectile to the target, row.effect on whoever/wherever the spell lands.
local KINDS = {}
SpireSpells.KINDS = KINDS -- tests drive kinds directly

KINDS.light = function(row, player)
	local c = Condition(CONDITION_LIGHT)
	c:setParameter(CONDITION_PARAM_LIGHT_LEVEL, row.lightLevel)
	c:setParameter(CONDITION_PARAM_LIGHT_COLOR, 215)
	c:setTicks(row.duration * 1000)
	player:addCondition(c)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.find_person = function(row, player, var)
	local target = Player(var:getString())
	if not target then
		player:sendCancelMessage('Say: wayfinder name (in quotes if it has a space: wayfinder "Some Name"). That player is not online.')
		return false
	end
	local a, b = player:getPosition(), target:getPosition()
	local dist = math.max(math.abs(a.x - b.x), math.abs(a.y - b.y))
	local dir = ""
	if b.y < a.y - 2 then dir = dir .. "north" elseif b.y > a.y + 2 then dir = dir .. "south" end
	if b.x < a.x - 2 then dir = dir .. "west" elseif b.x > a.x + 2 then dir = dir .. "east" end
	local level = b.z < a.z and " above you" or (b.z > a.z and " below you" or "")
	local how = dist < 5 and "standing next to you" or (dist < 100 and "to the " .. dir or "far to the " .. dir)
	player:sendTextMessage(MESSAGE_INFO_DESCR, target:getName() .. " is " .. how .. level .. ".")
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.heal_self = function(row, player)
	local mn, mx = formula(row, player)
	player:addHealth(math.random(mn, mx))
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.heal_target = function(row, player, var)
	local target = allyTarget(player, var)
	if not target then
		return false
	end
	local mn, mx = formula(row, player)
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	target:addHealth(math.random(mn, mx))
	fx(target:getPosition(), row.effect)
	return true
end

KINDS.heal_party = function(row, player)
	local mn, mx = formula(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		m:addHealth(math.random(mn, mx))
		if row.ward then
			SpireBuffs.addReduction(m:getId(), row.ward.pct, row.ward.duration)
		end
		if row.purify then
			for _, c in ipairs(BAD_CONDITIONS) do
				m:removeCondition(c)
			end
		end
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.hot_target = function(row, player, var)
	local target = allyTarget(player, var)
	if not target then
		return false
	end
	local c = Condition(CONDITION_REGENERATION)
	c:setParameter(CONDITION_PARAM_SUBID, 77)
	c:setParameter(CONDITION_PARAM_HEALTHGAIN, math.floor(player:getLevel() / 5 + player:getMagicLevel() * 1.2 + 10))
	c:setParameter(CONDITION_PARAM_HEALTHTICKS, 1000)
	c:setTicks(row.duration * 1000)
	target:addCondition(c)
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	fx(target:getPosition(), row.effect)
	return true
end

KINDS.mana_party = function(row, player)
	local gain = math.floor(player:getLevel() / 4 + player:getMagicLevel() * 0.8 + 10)
	for _, m in ipairs(partyAround(player, row.radius)) do
		local c = Condition(CONDITION_REGENERATION)
		c:setParameter(CONDITION_PARAM_SUBID, 79)
		c:setParameter(CONDITION_PARAM_MANAGAIN, gain)
		c:setParameter(CONDITION_PARAM_MANATICKS, 2000)
		c:setTicks(row.duration * 1000)
		m:addCondition(c)
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.cleanse = function(row, player)
	for _, c in ipairs(BAD_CONDITIONS) do
		player:removeCondition(c)
	end
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.purify = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		for _, c in ipairs(BAD_CONDITIONS) do
			m:removeCondition(c)
		end
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.levitate = function(row, player, var)
	local param = var:getString():lower()
	local from = player:getPosition()
	if param ~= "up" and param ~= "down" then
		player:sendCancelMessage("Say: skystep up, or skystep down.")
		return false
	end
	local to = Position(from)
	to:getNextPosition(player:getDirection())
	local dz = param == "up" and -1 or 1
	local tile = Tile(Position(to.x, to.y, to.z + dz))
	-- You can only climb through a gap: going up, nothing may be above your head; going down, the tile in front of
	-- you must have no floor. Without this, Skystep passed through solid floors and ceilings.
	local gapPos = param == "up" and Position(from.x, from.y, from.z - 1) or Position(to.x, to.y, to.z)
	local gapTile = Tile(gapPos)
	local gapFree = SpireSpells.levitateGapFree(gapTile ~= nil and gapTile:getGround() ~= nil)
	local destZone = SpirePvP and SpirePvP.zoneAt(Position(to.x, to.y, to.z + dz)) or "open"
	if gapFree and destZone ~= "bossroom" and tile and tile:getGround() and not tile:hasFlag(bit.bor(TILESTATE_IMMOVABLEBLOCKSOLID, TILESTATE_FLOORCHANGE)) then
		if player:move(tile, bit.bor(FLAG_IGNOREBLOCKITEM, FLAG_IGNOREBLOCKCREATURE)) == RETURNVALUE_NOERROR then
			fx(player:getPosition(), row.effect)
			return true
		end
	end
	player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
	return false
end

KINDS.food = function(row, player)
	local foods = { 3582, 3577, 3600, 3725, 3606 }
	player:addItem(foods[math.random(#foods)], 1)
	fx(player:getPosition(), row.effect)
	return true
end

-- Haste also breaks slows and roots (as in Tibia): the everyday counter to a Mystic's roots (DESIGN 6.7)
KINDS.haste = function(row, player)
	player:removeCondition(CONDITION_PARALYZE)
	local c = Condition(CONDITION_HASTE)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	SpireSpells.setSpeed(c, row.speed)
	player:addCondition(c)
	fx(player:getPosition(), row.effect)
	return true
end

-- Tailwind: haste for the whole party nearby, which also frees them from slows and roots
KINDS.party_haste = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		m:removeCondition(CONDITION_PARALYZE)
		local c = Condition(CONDITION_HASTE)
		c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
		SpireSpells.setSpeed(c, row.speed)
		m:addCondition(c)
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.taunt = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if c:isMonster() and not c:getMaster() then
			c:setTarget(player)
			fx(c:getPosition(), row.effect)
		end
	end
	return true
end

KINDS.dash = function(row, player)
	local target = player:getTarget()
	if not target then
		player:sendCancelMessage("You need a target to charge.")
		return false
	end
	if player:getPosition():getDistance(target:getPosition()) <= 1 then
		player:sendCancelMessage("You are already next to your target.")
		return false
	end
	local pos = player:getPosition()
	for _ = 1, row.tiles do
		local dx, dy = stepToward(pos, target:getPosition())
		local nxt = Position(pos.x + dx, pos.y + dy, pos.z)
		if (dx == 0 and dy == 0) or not walkable(nxt) then
			break
		end
		pos = nxt
	end
	if pos == player:getPosition() then
		player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
		return false
	end
	player:teleportTo(pos, true)
	fx(pos, row.effect)
	return true
end

KINDS.leap_away = function(row, player)
	local target = player:getTarget()
	local pos = player:getPosition()
	local dx, dy
	if target then
		dx, dy = stepToward(target:getPosition(), pos)
	else
		local d = player:getDirection()
		dx = d == DIRECTION_EAST and -1 or (d == DIRECTION_WEST and 1 or 0)
		dy = d == DIRECTION_SOUTH and -1 or (d == DIRECTION_NORTH and 1 or 0)
	end
	if dx == 0 and dy == 0 then
		dy = 1
	end
	local dest = pos
	for _ = 1, row.tiles do
		local nxt = Position(dest.x + dx, dest.y + dy, dest.z)
		if not walkable(nxt) then
			break
		end
		dest = nxt
	end
	if dest == pos then
		player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
		return false
	end
	player:teleportTo(dest, true)
	fx(dest, row.effect)
	return true
end

KINDS.blink = function(row, player)
	local pos = player:getPosition()
	local dest = pos
	for _ = 1, row.tiles do
		local nxt = Position(dest)
		nxt:getNextPosition(player:getDirection())
		if not walkable(nxt) then
			break
		end
		dest = nxt
	end
	if dest == pos then
		player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
		return false
	end
	player:teleportTo(dest, true)
	fx(dest, row.effect)
	return true
end

KINDS.dr_self = function(row, player)
	SpireBuffs.addReduction(player:getId(), row.pct, row.duration)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.dr_target = function(row, player, var)
	local target = allyTarget(player, var)
	if not target then
		return false
	end
	SpireBuffs.addReduction(target:getId(), row.pct, row.duration)
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	fx(target:getPosition(), row.effect)
	return true
end

KINDS.dr_party = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		SpireBuffs.addReduction(m:getId(), row.pct, row.duration)
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.dr_adjacent = function(row, player)
	for _, m in ipairs(partyAround(player, 1)) do
		if m ~= player then
			SpireBuffs.addReduction(m:getId(), row.pct, row.duration)
			fx(m:getPosition(), row.effect)
		end
	end
	SpireBuffs.addReduction(player:getId(), math.floor(row.pct / 2), row.duration)
	return true
end

KINDS.undying = function(row, player)
	SpireBuffs.undying[player:getId()] = os.time() + row.duration
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.party_buff = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius or 5)) do
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, 88)
		c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
		if row.buff == "melee" then
			c:setParameter(CONDITION_PARAM_SKILL_MELEEPERCENT, 100 + row.amount)
		elseif row.buff == "distance" then
			c:setParameter(CONDITION_PARAM_SKILL_DISTANCEPERCENT, 100 + row.amount)
		elseif row.buff == "crit" then
			c:setParameter(CONDITION_PARAM_SKILL_CRITICAL_HIT_CHANCE, row.amount * 100)
		elseif row.buff == "magic" then
			c:setParameter(CONDITION_PARAM_STAT_MAGICPOINTSPERCENT, 100 + row.amount)
		end
		c:setParameter(CONDITION_PARAM_BUFF_SPELL, true)
		m:addCondition(c)
		fx(m:getPosition(), row.effect)
	end
	return true
end

KINDS.slow_area = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if SpireSpells.affects(c, player) and SpireSpells.pin(c, row.duration, 0.45) then
			fx(c:getPosition(), row.effect)
		end
	end
	return true
end

KINDS.root = function(row, player)
	local target = player:getTarget()
	if not target then
		player:sendCancelMessage("You need a target.")
		return false
	end
	SpireSpells.pin(target, row.duration, 0.9)
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	fx(target:getPosition(), row.effect)
	return true
end

KINDS.reveal = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if c:isMonster() and c:getCondition(CONDITION_INVISIBLE) then
			c:removeCondition(CONDITION_INVISIBLE)
			fx(c:getPosition(), row.effect)
		end
	end
	return true
end

KINDS.mark = function(row, player)
	local target = player:getTarget()
	if not target or not target:isMonster() then
		player:sendCancelMessage("You need a monster as your target.")
		return false
	end
	SpireBuffs.addMark(target:getId(), row.pct, row.duration)
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	fx(target:getPosition(), row.effect)
	return true
end

KINDS.invisible = function(row, player)
	local c = Condition(CONDITION_INVISIBLE)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	player:addCondition(c)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.manashield = function(row, player)
	local c = Condition(CONDITION_MANASHIELD)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	player:addCondition(c)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.heal_last_stand = function(row, player)
	local mn, mx = formula(row, player)
	local missing = 1 - player:getHealth() / player:getMaxHealth()
	player:addHealth(math.floor(math.random(mn, mx) * (1 + missing * 2)))
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.heal_zone = function(row, player)
	local center = player:getPosition()
	local pid = player:getId()
	for tick = 0, row.duration - 1 do
		addEvent(function()
			local caster = Player(pid)
			if not caster then
				return
			end
			local mn, mx = formula(row, caster)
			for _, c in ipairs(Game.getSpectators(center, false, true, row.radius, row.radius, row.radius, row.radius)) do
				local party = caster:getParty()
				if c == caster or (party and c:getParty() == party) then
					c:addHealth(math.random(mn, mx))
					fx(c:getPosition(), CONST_ME_MAGIC_GREEN)
				end
			end
			fx(center, row.effect)
		end, tick * 1000)
	end
	return true
end

KINDS.break_free = function(row, player)
	player:removeCondition(CONDITION_PARALYZE)
	player:removeCondition(CONDITION_ROOTED)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.decoy = function(row, player)
	local m = Game.createMonster(row.monster, player:getPosition(), true, false)
	if not m then
		player:sendCancelMessage(RETURNVALUE_NOTENOUGHROOM)
		return false
	end
	local pos = m:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, 4, 4, 4, 4)) do
		if c:isMonster() and c ~= m and not c:getMaster() then
			c:setTarget(m)
		end
	end
	fx(pos, row.effect)
	local mid = m:getId()
	addEvent(function()
		local d = Creature(mid)
		if d then
			d:getPosition():sendMagicEffect(CONST_ME_POFF)
			d:remove()
		end
	end, row.duration * 1000)
	return true
end

-- Conjuring turns one blank rune (sold by the Runewright) into runes, as ECONOMY.md assumes
KINDS.conjure = function(row, player)
	if not player:removeItem(SpireSpells.BLANK_RUNE, 1) then
		player:sendCancelMessage("You need a blank rune. The Runewright sells them.")
		return false
	end
	player:addItem(row.item, row.count)
	fx(player:getPosition(), row.effect)
	return true
end

KINDS.summon = function(row, player)
	if #player:getSummons() >= 1 then
		player:sendCancelMessage("You already have a companion.")
		return false
	end
	local m = Game.createMonster(row.monster, player:getPosition(), true, false)
	if not m then
		player:sendCancelMessage(RETURNVALUE_NOTENOUGHROOM)
		return false
	end
	m:setMaster(player)
	fx(m:getPosition(), row.effect)
	return true
end

-- ---------------------------------------------------------------------------------------------------------------
-- Attacks. Every hit goes through a Combat object, so damage follows the normal PvP and armour rules. The numbers
-- of the hit being dealt right now sit in `cast` (set just before the Combat runs), which lets one spell deal
-- several different hits: stages of an area, chain jumps with falloff, execute bonuses.
local cast = { mn = 0, mx = 0 }

local function makeCombat(row, tag)
	local combat = Combat()
	combat:setParameter(COMBAT_PARAM_TYPE, row.element)
	if row.element == COMBAT_PHYSICALDAMAGE then
		combat:setParameter(COMBAT_PARAM_BLOCKARMOR, true)
	end
	local fname = "SpireSpellFormula_" .. tag
	_G[fname] = function()
		return -cast.mn, -cast.mx
	end
	combat:setCallback(CALLBACK_PARAM_LEVELMAGICVALUE, fname)
	return combat
end

-- Bosses cannot be dragged or thrown around (the monster generator marks them as "pushes creatures")
local function movable(c)
	return c and c:isMonster() and not c:getType():canPushCreatures()
end
SpireSpells.movable = movable

-- a wild monster (not somebody's companion)
local function wild(c)
	return c:isMonster() and not c:getMaster()
end

-- Who a slow, pull or zone may affect: wild monsters, and other players only during a Wild PvP arena event
function SpireSpells.affects(c, caster)
	return wild(c) or (c:isPlayer() and c ~= caster and SpireSpells.wildAt(c:getPosition()))
end

-- May this spell move this creature? Monsters (not bosses) always; players only by the Vanguard's spells or in
-- Wild PvP. Damaging spells only get here after the hit landed, so the PvP rules already allowed the attack.
local function canMove(c, row, caster)
	if c:isMonster() then
		return movable(c)
	end
	return c:isPlayer() and c ~= caster and (row.pvpMove == true or SpireSpells.wildAt(c:getPosition()))
end

-- Slide a creature up to `tiles` steps in a direction; stops at walls and other creatures. Returns steps moved.
local function shove(c, dx, dy, tiles, allowed)
	if allowed == nil then
		allowed = movable(c)
	end
	if not allowed or (dx == 0 and dy == 0) then
		return 0
	end
	local pos, moved = c:getPosition(), 0
	for _ = 1, tiles do
		local nxt = Position(pos.x + dx, pos.y + dy, pos.z)
		if not walkable(nxt) then
			break
		end
		pos, moved = nxt, moved + 1
	end
	if moved > 0 then
		c:teleportTo(pos, true)
	end
	return moved
end
SpireSpells.shove = shove

-- move a creature onto a free tile next to the caster (Iron Reach)
local function pullNextTo(player, target)
	local ppos, tpos = player:getPosition(), target:getPosition()
	if ppos:getDistance(tpos) <= 1 then
		return true
	end
	local dx, dy = stepToward(ppos, tpos)
	local spots = { { dx, dy }, { dx, 0 }, { 0, dy }, { dx, -dy }, { -dx, dy }, { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 }, { 1, 1 }, { -1, -1 }, { 1, -1 }, { -1, 1 } }
	for _, sp in ipairs(spots) do
		local pos = Position(ppos.x + sp[1], ppos.y + sp[2], ppos.z)
		if (sp[1] ~= 0 or sp[2] ~= 0) and walkable(pos) then
			target:teleportTo(pos, true)
			fx(pos, CONST_ME_GROUNDSHAKER)
			return true
		end
	end
	return false
end

local function pin(c, seconds, strength)
	-- players: half as long, then a few seconds when they can't be held again (DESIGN 6.7); full in Wild PvP
	local now = os.time()
	local secs, heldUntil = SpireSpells.holdSeconds(c:isPlayer(), seconds, SpireBuffs.held[c:getId()], now, SpireSpells.wildAt(c:getPosition()))
	if secs <= 0 then
		return false
	end
	if heldUntil then
		SpireBuffs.held[c:getId()] = heldUntil
	end
	local cond = Condition(CONDITION_PARALYZE)
	cond:setParameter(CONDITION_PARAM_TICKS, secs * 1000)
	SpireSpells.setSpeed(cond, -strength)
	c:addCondition(cond)
	return true
end
SpireSpells.pin = pin

-- Bleeding / burning after the hit (Rending Blow, Searing Brand): each tick is a share of the spell's average hit
local function applyDot(row, player, target)
	if not row.dot or not target or target:getHealth() <= 0 then
		return
	end
	local mn, mx = formula(row, player)
	local per = math.max(1, math.floor((mn + mx) / 2 * row.dot.pct))
	if target:isPlayer() then -- the engine halves every hit between players (as Tibia does); ticks too
		per = math.max(1, math.floor(per / 2))
	end
	local cond = Condition(row.dot.type)
	cond:setParameter(CONDITION_PARAM_DELAYED, true)
	cond:setParameter(CONDITION_PARAM_OWNER, player:getId())
	cond:addDamage(row.dot.ticks, row.dot.interval, -per)
	target:addCondition(cond)
end

-- What a hit does besides damage. target may be nil (it died); from = where the blow came from (for knock-back).
local function riders(player, row, target, dealt, from)
	if row.leech and dealt > 0 then
		player:addHealth(math.floor(dealt * row.leech))
		fx(player:getPosition(), CONST_ME_MAGIC_RED)
	end
	if not target or target:getHealth() <= 0 then
		return
	end
	applyDot(row, player, target)
	if row.vuln and target:isMonster() then
		SpireBuffs.addMark(target:getId(), row.vuln.pct, row.vuln.duration)
	end
	if row.push and from then
		local dx, dy = stepToward(from, target:getPosition())
		shove(target, dx, dy, row.push, canMove(target, row, player))
	end
	if row.pull and canMove(target, row, player) then
		pullNextTo(player, target)
		if target:isMonster() then
			target:setTarget(player)
		end
	end
	if row.root and pin(target, row.root, 0.9) then
		fx(target:getPosition(), CONST_ME_ROOTS)
	end
	if row.slow and SpireSpells.affects(target, player) then
		pin(target, 2, 0.3)
	end
end

-- One hit on one creature. Returns the damage dealt.
local function hitCreature(player, row, combat, target, mult, vis, from)
	local tid, tpos = target:getId(), target:getPosition()
	local before = target:getHealth()
	local mn, mx = formula(row, player)
	cast.mn, cast.mx = math.floor(mn * mult), math.floor(mx * mult)
	combat:execute(player, Variant(tid))
	fx(tpos, vis.effect)
	fx(tpos, vis.impact2)
	local after = Creature(tid)
	local dealt = before - (after and after:getHealth() or 0)
	if dealt > 0 then
		riders(player, row, after, dealt, from or player:getPosition())
	end
	return dealt
end

-- One hit on everything standing on a tile (walls and tiles out of sight are skipped). Returns the damage dealt.
local function hitTile(player, row, combat, pos, mult, vis, from)
	local tile = Tile(pos)
	if not tile or not tile:getGround() or tile:hasProperty(CONST_PROP_BLOCKPROJECTILE) or not from:isSightClear(pos) then
		return 0
	end
	local seen = {}
	for _, c in ipairs(tile:getCreatures() or {}) do
		if c ~= player then
			table.insert(seen, { id = c:getId(), hp = c:getHealth() })
		end
	end
	if row.element == COMBAT_FIREDAMAGE then
		SpireSpells.burnVines(pos) -- fire burns the Mystic's vine walls (DESIGN 6.7)
	end
	local mn, mx = formula(row, player)
	cast.mn, cast.mx = math.floor(mn * mult), math.floor(mx * mult)
	combat:execute(player, Variant(pos))
	fx(pos, vis.effect)
	local total = 0
	for _, s in ipairs(seen) do
		local c = Creature(s.id)
		local dealt = s.hp - (c and c:getHealth() or 0)
		if dealt > 0 then
			total = total + dealt
			riders(player, row, c, dealt, from)
		end
	end
	return total
end

-- run fn now (no wait) or later; the caster is looked up again when it runs, because they may have left
local function later(ms, pid, fn)
	if ms <= 0 then
		fn(Player(pid))
		return
	end
	addEvent(function()
		local caster = Player(pid)
		if caster then
			fn(caster)
		end
	end, ms)
end

-- Area attacks play out in stages (SpireSpells.stages): rings outward, rows away from you, a spiral, or a rain.
local function castArea(player, row, combat, var)
	local origin = player:getPosition()
	local centre, dir, from = origin, 0, origin
	if ON_TARGET[row.area] then
		local target = Creature(var:getNumber()) or player:getTarget()
		if not target then
			return false
		end
		centre, from = target:getPosition(), target:getPosition()
	elseif DIRECTIONAL[row.area] then
		dir = player:getDirection()
	end
	local vis = SpireSpells.visuals(row, player:getLevel())
	local stages, step = SpireSpells.stages(row, dir, math.random)
	local delay = row.delay or 0
	if row.skyshot then -- the shot goes up and comes down later
		shootFx(origin, Position(origin.x - 2, origin.y - 6, origin.z), row.skyshot)
	elseif delay == 0 then
		shootFx(origin, centre, vis.shoot)
	end
	if row.warn then
		for _, stage in ipairs(stages) do
			for _, t in ipairs(stage) do
				local pos = Position(centre.x + t.dx, centre.y + t.dy, centre.z)
				if Tile(pos) and from:isSightClear(pos) then
					fx(pos, row.warn)
				end
			end
		end
	end
	local pid = player:getId()
	for i, stage in ipairs(stages) do
		later(delay + (i - 1) * step, pid, function(caster)
			for _, t in ipairs(stage) do
				local pos = Position(centre.x + t.dx, centre.y + t.dy, centre.z)
				if delay > 0 and row.shoot then -- delayed strikes fall from the sky
					shootFx(Position(pos.x - 3, pos.y - 5, pos.z), pos, row.shoot)
				end
				hitTile(caster, row, combat, pos, 1, vis, from)
			end
		end)
	end
	return true
end

-- the nearest wild monster to `pos` within `range` that is not in `done`
local function nextInChain(pos, range, done)
	local best, bestDist
	for _, c in ipairs(Game.getSpectators(pos, false, false, range, range, range, range)) do
		if wild(c) and not done[c:getId()] and c:getHealth() > 0 and pos:isSightClear(c:getPosition()) then
			local d = pos:getDistance(c:getPosition())
			if not best or d < bestDist then
				best, bestDist = c, d
			end
		end
	end
	return best
end

local function dashNextTo(player, target, tiles)
	local pos = player:getPosition()
	for _ = 1, tiles do
		local dx, dy = stepToward(pos, target:getPosition())
		local nxt = Position(pos.x + dx, pos.y + dy, pos.z)
		if (dx == 0 and dy == 0) or not walkable(nxt) then
			break
		end
		pos = nxt
	end
	if pos ~= player:getPosition() then
		fx(player:getPosition(), CONST_ME_BLOODYSTEPS)
		player:teleportTo(pos, true)
	end
end

-- Single-target attacks: one hit, several hits in a row, a chain, with optional leap, execute and opener bonuses.
local function castTarget(player, row, combat, var)
	local target = Creature(var:getNumber()) or player:getTarget()
	if not target then
		return false
	end
	local vis = SpireSpells.visuals(row, player:getLevel())
	if row.dashTo then
		dashNextTo(player, target, row.range or 4)
	end
	local bonus = SpireSpells.pvpBonus(SpireSpells.riderBonus(row, target:getHealth() / math.max(1, target:getMaxHealth())), target:isPlayer())
	local mult = 1 + bonus
	local pid, tid = player:getId(), target:getId()
	shootFx(player:getPosition(), target:getPosition(), vis.shoot)
	if bonus > 0 then
		fx(target:getPosition(), CONST_ME_CRITICAL_DAMAGE)
	end
	if row.ringFx then
		for _, t in ipairs(SpireSpells.areaOffsets("ring1", 0)) do
			fx(Position(target:getPosition().x + t.dx, target:getPosition().y + t.dy, target:getPosition().z), row.ringFx)
		end
	end
	local lastPos = target:getPosition()
	hitCreature(player, row, combat, target, mult, vis)
	for h = 2, row.hits or 1 do
		later((h - 1) * (row.hitGap or 150), pid, function(caster)
			local t = Creature(tid)
			if t and t:getHealth() > 0 and t:getPosition().z == caster:getPosition().z and caster:getPosition():getDistance(t:getPosition()) <= 8 then
				shootFx(caster:getPosition(), t:getPosition(), vis.shoot)
				hitCreature(caster, row, combat, t, mult, vis)
			end
		end)
	end
	if row.chain then
		local done = { [tid] = true }
		local function jump(n, m)
			later(140, pid, function(caster)
				local nxt = nextInChain(lastPos, row.chain.range, done)
				if not nxt then
					return
				end
				done[nxt:getId()] = true
				shootFx(lastPos, nxt:getPosition(), vis.shoot)
				lastPos = nxt:getPosition()
				hitCreature(caster, row, combat, nxt, m, vis)
				if n < row.chain.jumps then
					jump(n + 1, m * row.chain.falloff)
				end
			end)
		end
		jump(1, mult * row.chain.falloff)
	end
	return true
end

-- Zones: tiles that keep hurting (and/or slowing) for a few seconds. One tick a second, the first at once.
local function runZone(player, row, combat, tiles)
	local vis = SpireSpells.visuals(row, player:getLevel())
	local pid = player:getId()
	for tick = 0, row.duration - 1 do
		later(tick * 1000, pid, function(caster)
			for _, pos in ipairs(tiles) do
				if combat then
					hitTile(caster, row, combat, pos, 1, vis, pos)
				else
					fx(pos, vis.effect)
				end
				if row.slowZone then
					local tile = Tile(pos)
					for _, c in ipairs(tile and tile:getCreatures() or {}) do
						if SpireSpells.affects(c, caster) then
							pin(c, 2, 0.5)
						end
					end
				end
			end
		end)
		-- the picture is refreshed between damage ticks too, so burning or thorny ground never blinks out
		later(tick * 1000 + 500, pid, function()
			for _, pos in ipairs(tiles) do
				fx(pos, vis.effect)
			end
		end)
	end
end

local zoneCombat = {} -- row -> Combat, filled in the registration loop

KINDS.zone = function(row, player, var)
	local centre = player:getPosition()
	if row.at == "target" then
		local target = Creature(var:getNumber()) or player:getTarget()
		if not target then
			player:sendCancelMessage("You need a target.")
			return false
		end
		centre = target:getPosition()
		shootFx(player:getPosition(), centre, row.shoot)
	end
	local tiles = {}
	for _, t in ipairs(SpireSpells.areaOffsets(row.area, 0)) do
		local pos = Position(centre.x + t.dx, centre.y + t.dy, centre.z)
		local tile = Tile(pos)
		if tile and tile:getGround() and not tile:hasProperty(CONST_PROP_BLOCKPROJECTILE) and centre:isSightClear(pos) then
			table.insert(tiles, pos)
		end
	end
	runZone(player, row, zoneCombat[row], tiles)
	return true
end

-- Firewake: dash forward and leave the tiles behind you burning
KINDS.trail_dash = function(row, player)
	local pos = player:getPosition()
	local dest, trail = pos, { pos }
	for _ = 1, row.tiles do
		local nxt = Position(dest)
		nxt:getNextPosition(player:getDirection())
		if not walkable(nxt) then
			break
		end
		dest = nxt
		table.insert(trail, dest)
	end
	if dest == pos then
		player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
		return false
	end
	table.remove(trail) -- not the tile you land on
	player:teleportTo(dest, true)
	fx(dest, row.cast)
	runZone(player, row, zoneCombat[row], trail)
	return true
end

-- Iron Reach: drag a monster to your side (bosses are too heavy) and make it yours to fight
KINDS.pull_target = function(row, player, var)
	local target = Creature(var:getNumber()) or player:getTarget()
	if not target or not target:isMonster() then
		player:sendCancelMessage("You need a monster as your target.")
		return false
	end
	if not movable(target) then
		player:sendCancelMessage("It is too heavy to drag.")
		return false
	end
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	if pullNextTo(player, target) then
		target:setTarget(player)
		return true
	end
	player:sendCancelMessage(RETURNVALUE_NOTENOUGHROOM)
	return false
end

-- Vinewall (Mystic): a row of vines across your path, 2 tiles ahead; lasts 20 s; fire burns it, Breach Arrow breaks it
KINDS.vine_wall = function(row, player)
	local here = player:getPosition()
	local made = 0
	for _, t in ipairs(SpireSpells.wallTiles(here.x, here.y, player:getDirection(), row.width, row.ahead)) do
		local pos = Position(t.x, t.y, here.z)
		local tile = Tile(pos)
		if tile and walkable(pos) and not tile:hasFlag(TILESTATE_PROTECTIONZONE) and here:isSightClear(pos) then
			local it = Game.createItem(ITEM_WILDGROWTH, 1, pos)
			if it then
				it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "Grown by " .. player:getName() .. ".")
				it:decay()
				fx(pos, row.effect)
				made = made + 1
			end
		end
	end
	if made == 0 then
		player:sendCancelMessage("There is no room for vines there.")
		return false
	end
	return true
end

-- Breach Arrow (Ranger): breaks the first vine wall or barrier straight ahead, up to 6 tiles
KINDS.breach = function(row, player)
	local here = player:getPosition()
	local hit = SpireSpells.breakFirstWall(here, player:getDirection(), row.tiles)
	if not hit then
		player:sendCancelMessage("There is no wall ahead to break.")
		return false
	end
	shootFx(here, hit, row.shoot)
	fx(hit, row.effect)
	fx(hit, CONST_ME_BLOCKHIT)
	return true
end

-- Gravity Well: everything near the target is dragged toward it and slowed, ready for an area spell
KINDS.gravity = function(row, player, var)
	local target = Creature(var:getNumber()) or player:getTarget()
	if not target then
		player:sendCancelMessage("You need a target.")
		return false
	end
	local centre = target:getPosition()
	shootFx(player:getPosition(), centre, row.shoot)
	fx(centre, row.effect)
	local r = row.radius
	local list = Game.getSpectators(centre, false, false, r, r, r, r)
	-- nearest first, so the ones in front make room for the ones behind
	table.sort(list, function(a, b)
		return centre:getDistance(a:getPosition()) < centre:getDistance(b:getPosition())
	end)
	for _, c in ipairs(list) do
		if SpireSpells.affects(c, player) and centre:isSightClear(c:getPosition()) then
			for _ = 1, row.tiles do
				local dx, dy = stepToward(c:getPosition(), centre)
				if shove(c, dx, dy, 1, c:isPlayer() or movable(c)) == 0 then
					break
				end
			end
			pin(c, row.duration, 0.5)
			fx(c:getPosition(), CONST_ME_PURPLEENERGY)
		end
	end
	return true
end

-- Standard of Defiance: a banner that keeps calling the monsters around it onto you
KINDS.banner = function(row, player)
	local pos, pid = player:getPosition(), player:getId()
	local r = row.radius
	for t = 0, row.duration - 1 do
		later(t * 1000, pid, function(caster)
			fx(pos, row.effect)
			if t % 2 == 0 and caster:getPosition().z == pos.z and caster:getPosition():getDistance(pos) <= r + 2 then
				for _, c in ipairs(Game.getSpectators(pos, false, false, r, r, r, r)) do
					if wild(c) then
						c:setTarget(caster)
						fx(c:getPosition(), CONST_ME_SOUND_RED)
					end
				end
			end
		end)
	end
	return true
end

-- Counterguard: part of every blow a monster lands on you is thrown back at it
KINDS.reflect = function(row, player)
	SpireBuffs.reflect[player:getId()] = { pct = row.pct, untilTime = os.time() + row.duration }
	fx(player:getPosition(), row.effect)
	return true
end

-- Lifeseed: the next blow that would kill this player leaves them alive, and the seed heals them
KINDS.seed = function(row, player, var)
	local target = allyTarget(player, var)
	if not target then
		return false
	end
	SpireBuffs.seed[target:getId()] = { pct = row.pct, untilTime = os.time() + row.duration }
	shootFx(player:getPosition(), target:getPosition(), row.shoot)
	fx(target:getPosition(), row.effect)
	return true
end

-- Linked Mend: the heal jumps on to the most wounded party members nearby
KINDS.heal_chain = function(row, player, var)
	local first = allyTarget(player, var)
	if not first then
		return false
	end
	local mn, mx = formula(row, player)
	local pid = player:getId()
	local done = { [first:getId()] = true }
	shootFx(player:getPosition(), first:getPosition(), row.shoot)
	first:addHealth(math.random(mn, mx))
	fx(first:getPosition(), row.effect)
	local lastPos = first:getPosition()
	local function jump(n, mult)
		later(160, pid, function(caster)
			local best, bestShare
			for _, m in ipairs(partyAround(caster, 30)) do
				local share = m:getHealth() / math.max(1, m:getMaxHealth())
				if not done[m:getId()] and share < 1 and m:getPosition().z == lastPos.z and m:getPosition():getDistance(lastPos) <= row.range and (not best or share < bestShare) then
					best, bestShare = m, share
				end
			end
			if not best then
				return
			end
			done[best:getId()] = true
			shootFx(lastPos, best:getPosition(), row.shoot)
			lastPos = best:getPosition()
			best:addHealth(math.floor(math.random(mn, mx) * mult))
			fx(lastPos, row.effect)
			if n < row.jumps then
				jump(n + 1, mult * row.falloff)
			end
		end)
	end
	jump(1, row.falloff)
	return true
end

-- Bloomburst: heal an ally; the bloom bursts and hurts the monsters next to them
KINDS.heal_burst = function(row, player, var)
	local target = allyTarget(player, var)
	if not target then
		return false
	end
	local mn, mx = formula(row, player)
	local centre = target:getPosition()
	shootFx(player:getPosition(), centre, row.shoot)
	target:addHealth(math.random(mn, mx))
	fx(centre, row.effect)
	local vis = { effect = row.burstEffect }
	for _, t in ipairs(SpireSpells.areaOffsets("ring1", 0)) do
		hitTile(player, row, zoneCombat[row], Position(centre.x + t.dx, centre.y + t.dy, centre.z), row.burst, vis, centre)
	end
	return true
end

-- Forms: for a short time the caster is something more. An aura plays every second, and the form pulses:
-- it strikes nearby monsters, heals the party, or calls monsters onto the caster.
local function formPulse(caster, row)
	local p = row.pulse
	local pos = caster:getPosition()
	local r = p.radius
	if p.kind == "taunt" then
		for _, c in ipairs(Game.getSpectators(pos, false, false, r, r, r, r)) do
			if wild(c) then
				c:setTarget(caster)
				fx(c:getPosition(), p.effect)
			end
		end
	elseif p.kind == "heal" then
		local mn, mx = formula(p, caster)
		for _, m in ipairs(partyAround(caster, r)) do
			m:addHealth(math.random(mn, mx))
			fx(m:getPosition(), p.effect)
		end
	elseif p.kind == "strike" then
		local pool = {}
		for _, c in ipairs(Game.getSpectators(pos, false, false, r, r, r, r)) do
			if wild(c) and c:getHealth() > 0 and pos:isSightClear(c:getPosition()) then
				table.insert(pool, c)
			end
		end
		for _ = 1, math.min(p.count, #pool) do
			local c = table.remove(pool, math.random(#pool))
			shootFx(pos, c:getPosition(), p.shoot)
			hitCreature(caster, p, zoneCombat[row], c, 1, p)
		end
	end
end

KINDS.form = function(row, player)
	local pid = player:getId()
	if row.dr then
		SpireBuffs.addReduction(pid, row.dr, row.duration)
	end
	if row.buff then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, 89)
		c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
		if row.buff == "melee" then
			c:setParameter(CONDITION_PARAM_SKILL_MELEEPERCENT, 100 + row.amount)
		elseif row.buff == "distance" then
			c:setParameter(CONDITION_PARAM_SKILL_DISTANCEPERCENT, 100 + row.amount)
		elseif row.buff == "magic" then
			c:setParameter(CONDITION_PARAM_STAT_MAGICPOINTSPERCENT, 100 + row.amount)
		end
		c:setParameter(CONDITION_PARAM_BUFF_SPELL, true)
		player:addCondition(c)
	end
	if row.speed then
		local c = Condition(CONDITION_HASTE)
		c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
		SpireSpells.setSpeed(c, row.speed)
		player:addCondition(c)
	end
	local every = row.pulse and row.pulse.every or 1
	for t = 0, row.duration - 1 do
		later(t * 1000, pid, function(caster)
			fx(caster:getPosition(), row.aura)
			if row.pulse and t % every == 0 then
				formPulse(caster, row)
			end
		end)
	end
	return true
end

-- Spell tests (autopilot spell routes after "/pilot trace on", dev account only): log what each cast really did
-- 2.5 s later (after staged and delayed parts have landed), then refill the caster for the next spell.
SpireSpells.TRACE = {}
local function traceCast(row, player, var, cast)
	local pid = player:getId()
	local before = {}
	for _, c in ipairs(Game.getSpectators(player:getPosition(), false, false, 9, 9, 7, 7)) do
		if c:isMonster() then
			before[c:getId()] = { hp = c:getHealth(), pos = c:getPosition() }
		end
	end
	local hp0, pos0 = player:getHealth(), player:getPosition()
	local ok = cast(player, var)
	addEvent(function()
		local p = Player(pid)
		if not p then
			return
		end
		local hit, dmg, moved, died = 0, 0, 0, 0
		for id, b in pairs(before) do
			local c = Creature(id)
			if not c then
				died = died + 1
			else
				if c:getHealth() < b.hp then
					hit, dmg = hit + 1, dmg + b.hp - c:getHealth()
				end
				if c:getPosition() ~= b.pos then
					moved = moved + 1
				end
			end
		end
		local stepped = p:getPosition() ~= pos0 and (" moved you " .. pos0:getDistance(p:getPosition()) .. " tiles") or ""
		logger.info(string.format("[SPELLTRACE] %s | %s | %s: hit %d monsters for %d, %d gone, %d moved, your health %+d%s",
			p:getName(), row.name, ok and "CAST" or "REFUSED", hit, dmg, died, moved, p:getHealth() - hp0, stepped))
		p:addHealth(p:getMaxHealth())
		p:addMana(p:getMaxMana())
	end, 2500)
	return ok
end

local VOC_ALL = { "arcanist;true", "high arcanist;true", "mystic;true", "elder mystic;true", "ranger;true", "far warden;true", "vanguard;true", "blade warden;true" }

local NEEDS_TARGET = { attack_target = true, root = true, mark = true, pull_target = true, gravity = true }
local ALLY_PARAM = { heal_target = true, hot_target = true, dr_target = true, seed = true, heal_chain = true, heal_burst = true }

for i, row in ipairs(SpireSpells.list) do
	local spell = Spell("instant")
	local isAttack = row.kind == "attack_target" or row.kind == "attack_area"
	local combat = isAttack and makeCombat(row, i) or nil
	if not isAttack and row.element then -- zones, trails and blooms deal their damage through a Combat too
		zoneCombat[row] = makeCombat(row, i)
	end
	if row.pulse and row.pulse.element then
		row.pulse.scale = row.scale
		zoneCombat[row] = makeCombat(row.pulse, i .. "p")
	elseif row.pulse then
		row.pulse.scale = row.scale
	end
	local function cast(player, var)
		local need = SpireSpells.levelFor(row, player:getVocation():getBaseId())
		if player:getLevel() < need then -- shared spells: each vocation has its own level
			player:sendCancelMessage(string.format("You learn %s at level %d.", row.name, need))
			return false
		end
		if row.lostArt and not SpireSpells.TRACE[player:getId()] and not SpireSpells.knowsLostArt(row, function(f) return SpireQuests.floorStoryDone(player, f) end) then
			player:sendCancelMessage(row.name .. " is a Lost Art. Finish every story quest on Floor " .. row.lostArt .. " to learn it.")
			return false
		end
		local vis = SpireSpells.visuals(row, player:getLevel())
		if row.kind == "attack_area" then
			fx(player:getPosition(), vis.cast)
			return castArea(player, row, combat, var)
		elseif row.kind == "attack_target" then
			fx(player:getPosition(), vis.cast)
			return castTarget(player, row, combat, var)
		end
		if row.kind ~= "trail_dash" then
			fx(player:getPosition(), vis.cast)
		end
		return KINDS[row.kind](row, player, var)
	end
	function spell.onCastSpell(creature, var)
		local player = creature:getPlayer()
		if not player then
			return false
		end
		if not SpireSpells.TRACE[player:getId()] then
			return cast(player, var)
		end
		return traceCast(row, player, var, cast)
	end
	local group = SpireSpells.group(row)
	spell:name(row.name)
	spell:words(row.words)
	spell:id(300 + i) -- Spirebound spell ids start at 301
	spell:group(group)
	spell:cooldown(row.cd * 1000)
	spell:groupCooldown(SpireSpells.GROUP_COOLDOWN[group])
	spell:level(SpireSpells.minLevel(row))
	spell:mana(row.mana)
	spell:needLearn(false)
	spell:isPremium(false)
	spell:isAggressive(SpireSpells.aggressive(row))
	if NEEDS_TARGET[row.kind] or ON_TARGET[row.area] or row.at == "target" then
		spell:needTarget(true)
		spell:range(row.range or (row.kind == "attack_target" and 5 or 7))
	elseif ALLY_PARAM[row.kind] then
		-- the name is optional (no name = yourself), so it is a plain parameter: the engine's "player name" parameter
		-- refuses the spell when no name is given
		spell:hasParams(true)
	elseif row.kind == "find_person" or row.kind == "levitate" then
		spell:hasParams(true)
	elseif DIRECTIONAL[row.area] then
		spell:needDirection(true)
	end
	spell:blockWalls(true)
	if row.voc == "all" then
		spell:vocation(unpack(VOC_ALL))
	else
		local names = {}
		for _, v in ipairs(row.voc) do
			for _, n in ipairs(VOC_NAMES[v]) do
				table.insert(names, n)
			end
		end
		spell:vocation(unpack(names))
	end
	spell:register()
end

-- Everything that changes damage as it lands: Elemental Clash, damage reduction, marks, Counterguard, Lifeseed and
-- Undying Oath (applies to every player and monster that registers the event)
local CLASH_ELEMENT = {
	[COMBAT_FIREDAMAGE] = "fire", [COMBAT_ENERGYDAMAGE] = "energy", [COMBAT_ICEDAMAGE] = "ice",
	[COMBAT_EARTHDAMAGE] = "earth", [COMBAT_HOLYDAMAGE] = "holy", [COMBAT_PHYSICALDAMAGE] = "physical",
}

-- Leave a creature on 1 health if this damage would kill it. Returns the new primary and secondary damage and
-- whether anything was held back. Damage can arrive as negative numbers here: work on sizes and keep the sign.
local function holdAtOne(creature, primaryDamage, secondaryDamage)
	local sign = (primaryDamage < 0 or secondaryDamage < 0) and -1 or 1
	local p, s = math.abs(primaryDamage), math.abs(secondaryDamage)
	local allowed = SpireBuffs.undyingClamp(creature:getHealth(), p + s)
	if allowed < p + s then
		s = math.min(s, allowed)
		return sign * (allowed - s), sign * s, true
	end
	return primaryDamage, secondaryDamage, false
end

local buffs = CreatureEvent("SpireBuffDamage")
function buffs.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	if primaryType == COMBAT_HEALING then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local now = os.time()
	local cid = creature:getId()
	-- Elemental Clash: spells (and weapon arts) from players on monsters
	if origin == ORIGIN_SPELL and attacker and attacker:isPlayer() and creature:isMonster() then
		local st = SpireClash.state[cid]
		local bonus, newMark, name = SpireClash.resolve(st and st.untilTime >= now and st.el or nil, CLASH_ELEMENT[primaryType])
		if bonus > 0 then
			primaryDamage = math.floor(primaryDamage * (1 + bonus / 100))
			creature:getPosition():sendMagicEffect(SpireFx.CLASH)
			creature:say(name .. "!", TALKTYPE_MONSTER_SAY)
		end
		if newMark == false then
			SpireClash.state[cid] = nil
		elseif newMark then
			SpireClash.state[cid] = { el = newMark, untilTime = now + SpireClash.SECONDS }
		end
	end
	local r = SpireBuffs.reduce[cid]
	local m = SpireBuffs.mark[cid]
	local rp = (r and r.untilTime >= now) and r.pct or 0
	local mp = (m and m.untilTime >= now and attacker and attacker:isPlayer()) and m.pct or 0
	if rp > 0 or mp > 0 then
		primaryDamage = SpireBuffs.apply(primaryDamage, rp, mp)
		secondaryDamage = SpireBuffs.apply(secondaryDamage, rp, mp)
	end
	if SpirePerks and SpirePerks.onDealt and creature:isMonster() then -- floor perks (R12)
		primaryDamage = SpirePerks.onDealt(attacker, creature, primaryDamage)
	end
	-- Counterguard: a share of a monster's physical blow goes back to it (a moment later, never inside this event)
	local rf = SpireBuffs.reflect[cid]
	if rf and rf.untilTime >= now and attacker and attacker:isMonster() and primaryType == COMBAT_PHYSICALDAMAGE then
		local back = math.floor(math.abs(primaryDamage) * rf.pct / 100)
		if back > 0 then
			addEvent(function(pid, aid, dmg)
				local p, a = Player(pid), Creature(aid)
				if p and a then
					doTargetCombatHealth(p, a, COMBAT_PHYSICALDAMAGE, -dmg, -dmg, CONST_ME_BLOCKHIT, ORIGIN_NONE)
				end
			end, 50, cid, attacker:getId(), back)
		end
	end
	local held
	local seed = SpireBuffs.seed[cid]
	local byPlayer = attacker and (attacker:isPlayer() or (attacker:getMaster() and attacker:getMaster():isPlayer()))
	if seed and seed.untilTime >= now and not byPlayer then -- Lifeseed saves from monsters only (DESIGN 6.7)
		primaryDamage, secondaryDamage, held = holdAtOne(creature, primaryDamage, secondaryDamage)
		if held then
			SpireBuffs.seed[cid] = nil
			creature:getPosition():sendMagicEffect(SpireFx.LEAF_WARD)
			addEvent(function(id, pct)
				local c = Creature(id)
				if c then
					c:addHealth(math.floor(c:getMaxHealth() * pct / 100))
					c:getPosition():sendMagicEffect(SpireFx.BLOOM)
				end
			end, 50, cid, seed.pct)
		end
	end
	local u = SpireBuffs.undying[cid]
	if u and u >= now then
		primaryDamage, secondaryDamage, held = holdAtOne(creature, primaryDamage, secondaryDamage)
		if held then
			creature:getPosition():sendMagicEffect(SpireFx.OATH_HALO)
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
buffs:register()

-- "You learned" message on level up; buff event on login
local advance = CreatureEvent("SpireSpellUnlock")
function advance.onAdvance(player, skill, oldLevel, newLevel)
	if skill ~= SKILL_LEVEL then
		return true
	end
	local base = player:getVocation():getBaseId()
	local learned = false
	for level = oldLevel + 1, newLevel do
		for _, row in ipairs(SpireSpells.unlockedAt(level, base)) do
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("New spell: %s. Say \"%s\" to cast it.", row.name, row.words))
			learned = true
		end
	end
	if learned then
		fx(player:getPosition(), CONST_ME_OPENING_MAGIC_BOOK)
		local nextLevel, names = SpireSpells.nextUnlock(newLevel, base)
		if nextLevel then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Next spell at level %d: %s.", nextLevel, table.concat(names, ", ")))
		end
	end
	return true
end
advance:register()

local login = CreatureEvent("SpireSpellLogin")
function login.onLogin(player)
	player:registerEvent("SpireSpellUnlock")
	player:registerEvent("SpireBuffDamage")
	return true
end
login:register()

-- Forget timed buffs when a creature leaves the game
SpireCleanup.add(function(cid)
	SpireBuffs.reduce[cid], SpireBuffs.mark[cid], SpireBuffs.undying[cid] = nil, nil, nil
	SpireBuffs.reflect[cid], SpireBuffs.seed[cid], SpireClash.state[cid] = nil, nil, nil
	SpireBuffs.held[cid] = nil
end)
