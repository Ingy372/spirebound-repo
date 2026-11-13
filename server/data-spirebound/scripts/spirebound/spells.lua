-- Builds every row of SpireSpells.list (lib/spirebound/spells.lua) into a Canary spell.
-- Spells need no learning: they work as soon as the character reaches the level (Jay, 2026-11-08).

local VOC_NAMES = {
	[1] = { "arcanist;true", "high arcanist;true" },
	[2] = { "mystic;true", "elder mystic;true" },
	[3] = { "ranger;true", "far warden;true" },
	[4] = { "vanguard;true", "blade warden;true" },
}

local AREAS = {
	wave = { { 1, 1, 1 }, { 1, 1, 1 }, { 0, 1, 0 }, { 0, 3, 0 } },
	beam = { { 1 }, { 1 }, { 1 }, { 1 }, { 1 }, { 3 } },
	ring2 = { { 0, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1 }, { 1, 1, 2, 1, 1 }, { 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 0 } },
}

local function formula(row, player)
	local level, ml = player:getLevel(), player:getMagicLevel()
	local base = row.base or 5
	return math.floor(level / 5 + ml * row.min + base), math.floor(level / 5 + ml * row.max + base * 2)
end

local function partyAround(player, radius)
	local out = { player }
	local party = player:getParty()
	if party then
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

-- Each kind returns true if the spell happened
local KINDS = {}

KINDS.light = function(row, player)
	local c = Condition(CONDITION_LIGHT)
	c:setParameter(CONDITION_PARAM_LIGHT_LEVEL, row.lightLevel)
	c:setParameter(CONDITION_PARAM_LIGHT_COLOR, 215)
	c:setTicks(row.duration * 1000)
	player:addCondition(c)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

KINDS.find_person = function(row, player, var)
	local target = Player(var:getString())
	if not target then
		player:sendCancelMessage("Say: wayfinder <name>. That player is not online.")
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
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

KINDS.heal_self = function(row, player)
	local mn, mx = formula(row, player)
	player:addHealth(math.random(mn, mx))
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

KINDS.heal_target = function(row, player, var)
	local target = Creature(var:getNumber()) or Player(var:getString()) or player
	if target:isMonster() then
		target = player
	end
	local mn, mx = formula(row, player)
	target:addHealth(math.random(mn, mx))
	target:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	return true
end

KINDS.heal_party = function(row, player)
	local mn, mx = formula(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		m:addHealth(math.random(mn, mx))
		m:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	end
	return true
end

KINDS.hot_target = function(row, player, var)
	local target = Creature(var:getNumber()) or player
	if target:isMonster() then
		target = player
	end
	local c = Condition(CONDITION_REGENERATION)
	c:setParameter(CONDITION_PARAM_SUBID, 77)
	c:setParameter(CONDITION_PARAM_HEALTHGAIN, math.floor(player:getLevel() / 5 + player:getMagicLevel() * 1.2 + 10))
	c:setParameter(CONDITION_PARAM_HEALTHTICKS, 1000)
	c:setTicks(row.duration * 1000)
	target:addCondition(c)
	target:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	return true
end

KINDS.cleanse = function(row, player)
	for _, c in ipairs(BAD_CONDITIONS) do
		player:removeCondition(c)
	end
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

KINDS.purify = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		for _, c in ipairs(BAD_CONDITIONS) do
			m:removeCondition(c)
		end
		m:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
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
			player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
			return true
		end
	end
	player:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
	return false
end

KINDS.food = function(row, player)
	local foods = { 3582, 3577, 3600, 3725, 3606 }
	player:addItem(foods[math.random(#foods)], 1)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	return true
end

KINDS.haste = function(row, player)
	local c = Condition(CONDITION_HASTE)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	c:setFormula(row.speed, -40, row.speed, 40)
	player:addCondition(c)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	return true
end

KINDS.taunt = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if c:isMonster() and not c:getMaster() then
			c:setTarget(player)
			c:getPosition():sendMagicEffect(CONST_ME_SOUND_RED)
		end
	end
	pos:sendMagicEffect(CONST_ME_YELLOW_RINGS)
	return true
end

KINDS.dash = function(row, player)
	local target = player:getTarget()
	if not target then
		player:sendCancelMessage("You need a target to charge.")
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
	pos:sendMagicEffect(CONST_ME_GROUNDSHAKER)
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
	dest:sendMagicEffect(CONST_ME_POFF)
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
	pos:sendMagicEffect(CONST_ME_ENERGYAREA)
	player:teleportTo(dest, true)
	dest:sendMagicEffect(CONST_ME_ENERGYAREA)
	return true
end

KINDS.dr_self = function(row, player)
	SpireBuffs.addReduction(player:getId(), row.pct, row.duration)
	player:getPosition():sendMagicEffect(CONST_ME_BLOCKHIT)
	return true
end

KINDS.dr_party = function(row, player)
	for _, m in ipairs(partyAround(player, row.radius)) do
		SpireBuffs.addReduction(m:getId(), row.pct, row.duration)
		m:getPosition():sendMagicEffect(CONST_ME_SMALLPLANTS)
	end
	return true
end

KINDS.dr_adjacent = function(row, player)
	for _, m in ipairs(partyAround(player, 1)) do
		if m ~= player then
			SpireBuffs.addReduction(m:getId(), row.pct, row.duration)
			m:getPosition():sendMagicEffect(CONST_ME_BLOCKHIT)
		end
	end
	SpireBuffs.addReduction(player:getId(), math.floor(row.pct / 2), row.duration)
	player:getPosition():sendMagicEffect(CONST_ME_YELLOW_RINGS)
	return true
end

KINDS.party_buff = function(row, player)
	for _, m in ipairs(partyAround(player, 5)) do
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
		m:getPosition():sendMagicEffect(CONST_ME_MAGIC_RED)
	end
	return true
end

KINDS.slow_area = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if c:isMonster() and not c:getMaster() then
			local cond = Condition(CONDITION_PARALYZE)
			cond:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
			cond:setFormula(-0.4, 0, -0.5, 0)
			c:addCondition(cond)
			c:getPosition():sendMagicEffect(CONST_ME_STUN)
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
	local cond = Condition(CONDITION_PARALYZE)
	-- players are only slowed (DESIGN: crowd control on players is weaker)
	local secs = target:isPlayer() and math.floor(row.duration / 2) or row.duration
	cond:setParameter(CONDITION_PARAM_TICKS, secs * 1000)
	cond:setFormula(-0.9, 0, -0.95, 0)
	target:addCondition(cond)
	target:getPosition():sendMagicEffect(CONST_ME_SMALLPLANTS)
	return true
end

KINDS.reveal = function(row, player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, row.radius, row.radius, row.radius, row.radius)) do
		if c:isMonster() and c:getCondition(CONDITION_INVISIBLE) then
			c:removeCondition(CONDITION_INVISIBLE)
			c:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
		end
	end
	pos:sendMagicEffect(CONST_ME_BLUE_RINGS)
	return true
end

KINDS.mark = function(row, player)
	local target = player:getTarget()
	if not target or not target:isMonster() then
		player:sendCancelMessage("You need a monster as your target.")
		return false
	end
	SpireBuffs.addMark(target:getId(), row.pct, row.duration)
	target:getPosition():sendMagicEffect(CONST_ME_REDSMOKE)
	return true
end

KINDS.invisible = function(row, player)
	local c = Condition(CONDITION_INVISIBLE)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	player:addCondition(c)
	player:getPosition():sendMagicEffect(CONST_ME_SMALLPLANTS)
	return true
end

KINDS.manashield = function(row, player)
	local c = Condition(CONDITION_MANASHIELD)
	c:setParameter(CONDITION_PARAM_TICKS, row.duration * 1000)
	player:addCondition(c)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

KINDS.heal_last_stand = function(row, player)
	local mn, mx = formula(row, player)
	local missing = 1 - player:getHealth() / player:getMaxHealth()
	player:addHealth(math.floor(math.random(mn, mx) * (1 + missing * 2)))
	player:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
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
					c:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
				end
			end
			center:sendMagicEffect(CONST_ME_HOLYAREA)
		end, tick * 1000)
	end
	return true
end

KINDS.break_free = function(row, player)
	player:removeCondition(CONDITION_PARALYZE)
	player:removeCondition(CONDITION_ROOTED)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_RED)
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

KINDS.conjure = function(row, player)
	player:addItem(row.item, row.count)
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_RED)
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
	m:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	return true
end

-- Attack spells use Combat objects so damage follows the normal PvP and armor rules
local function makeCombat(row, i)
	local combat = Combat()
	combat:setParameter(COMBAT_PARAM_TYPE, row.element)
	combat:setParameter(COMBAT_PARAM_EFFECT, row.effect)
	if row.shoot then
		combat:setParameter(COMBAT_PARAM_DISTANCEEFFECT, row.shoot)
	end
	if row.area then
		combat:setArea(createCombatArea(AREAS[row.area]))
	end
	local fname = "SpireSpellFormula_" .. i
	_G[fname] = function(player, level, magicLevel)
		local mn, mx = formula(row, player)
		return -mn, -mx
	end
	combat:setCallback(CALLBACK_PARAM_LEVELMAGICVALUE, fname)
	return combat
end

for i, row in ipairs(SpireSpells.list) do
	local spell = Spell("instant")
	local combat = (row.kind == "attack_target" or row.kind == "attack_area") and makeCombat(row, i) or nil
	function spell.onCastSpell(creature, var)
		local player = creature:getPlayer()
		if not player then
			return false
		end
		if row.lostArt and not SpireSpells.knowsLostArt(row, function(f) return SpireQuests.floorStoryDone(player, f) end) then
			player:sendCancelMessage(row.name .. " is a Lost Art. Finish every story quest on Floor " .. row.lostArt .. " to learn it.")
			return false
		end
		if combat then
			return combat:execute(creature, var)
		end
		return KINDS[row.kind](row, player, var)
	end
	spell:name(row.name)
	spell:words(row.words)
	spell:id(300 + i) -- Spirebound spell ids start at 301
	spell:group(combat and "attack" or (row.kind:find("heal") and "healing" or "support"))
	spell:cooldown(row.cd * 1000)
	spell:groupCooldown(1000)
	spell:level(row.level)
	spell:mana(row.mana)
	spell:needLearn(false)
	spell:isPremium(false)
	spell:isAggressive(combat ~= nil or row.kind == "root" or row.kind == "mark")
	if row.kind == "attack_target" or row.kind == "root" or row.kind == "mark" then
		spell:needTarget(true)
		spell:range(row.kind == "attack_target" and 5 or 7)
	elseif row.kind == "heal_target" or row.kind == "hot_target" then
		spell:needCasterTargetOrDirection(false)
		spell:hasPlayerNameParam(true)
		spell:hasParams(true)
	elseif row.kind == "find_person" or row.kind == "levitate" then
		spell:hasParams(true)
	elseif row.area == "ring2" then
		-- centred on the caster, no target needed
	elseif row.area == "wave" or row.area == "beam" then
		spell:needDirection(true)
	end
	spell:blockWalls(true)
	if row.voc == "all" then
		spell:vocation("arcanist;true", "high arcanist;true", "mystic;true", "elder mystic;true", "ranger;true", "far warden;true", "vanguard;true", "blade warden;true")
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

-- Damage reduction buffs and marks (applies to every player and monster that registers the event)
local buffs = CreatureEvent("SpireBuffDamage")
function buffs.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	if primaryType == COMBAT_HEALING then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local now = os.time()
	local r = SpireBuffs.reduce[creature:getId()]
	local m = SpireBuffs.mark[creature:getId()]
	local rp = (r and r.untilTime >= now) and r.pct or 0
	local mp = (m and m.untilTime >= now and attacker and attacker:isPlayer()) and m.pct or 0
	if rp > 0 or mp > 0 then
		primaryDamage = SpireBuffs.apply(primaryDamage, rp, mp)
		secondaryDamage = SpireBuffs.apply(secondaryDamage, rp, mp)
	end
	if SpirePerks and SpirePerks.onDealt and creature:isMonster() then -- floor perks (R12)
		primaryDamage = SpirePerks.onDealt(attacker, creature, primaryDamage)
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
	for level = oldLevel + 1, newLevel do
		for _, row in ipairs(SpireSpells.unlockedAt(level, base)) do
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("New spell: %s. Say \"%s\" to cast it.", row.name, row.words))
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
