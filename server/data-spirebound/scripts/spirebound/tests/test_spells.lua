-- Spell overhaul (docs/design/spells.md): counts, unlock curves, roles, the solo-difficulty rule, and real casts.

local function ownRows(v)
	local out = {}
	for _, row in ipairs(SpireSpells.list) do
		if row.voc ~= "all" and SpireSpells.allowed(row, v) then
			table.insert(out, row)
		end
	end
	return out
end

SpireTest.add("spells: every row registers with the engine at its level, mana and group", function()
	for _, row in ipairs(SpireSpells.list) do
		local s = Spell(row.name)
		if not s then
			error(row.name .. " not registered")
		end
		SpireTest.eq(s:level(), SpireSpells.minLevel(row), row.name .. " engine level")
		SpireTest.eq(s:mana(), row.mana, row.name .. " mana")
		if s:needLearn() then
			error(row.name .. " still needs to be learned")
		end
	end
end)

SpireTest.add("spells: 26-32 own spells per vocation, 2 Lost Arts each, at most 38 with shared", function()
	for v = 1, 4 do
		local own, lost, total = 0, 0, 0
		for _, row in ipairs(SpireSpells.list) do
			if SpireSpells.allowed(row, v) then
				total = total + 1
				if row.voc ~= "all" then
					own = own + 1
				end
				if row.lostArt then
					lost = lost + 1
				end
			end
		end
		SpireTest.eq(own >= 26 and own <= 32, true, "vocation " .. v .. " has " .. own .. " own spells")
		SpireTest.eq(total <= 38, true, "vocation " .. v .. " has " .. total .. " spells in all")
		SpireTest.eq(lost, 2, "lost arts for vocation " .. v)
	end
	local voc0 = 0
	for _, row in ipairs(SpireSpells.list) do
		if SpireSpells.allowed(row, 0) then
			voc0 = voc0 + 1
		end
	end
	SpireTest.eq(voc0, 0, "no vocation yet: no spells")
end)

SpireTest.add("spells: each vocation has its own unlock curve, and every role mix", function()
	local curves = {}
	for v = 1, 4 do
		local levels = {}
		local kinds = { attack = 0, healing = 0, support = 0 }
		for _, row in ipairs(SpireSpells.list) do
			if SpireSpells.allowed(row, v) and not row.lostArt then
				table.insert(levels, SpireSpells.levelFor(row, v))
				kinds[SpireSpells.group(row)] = kinds[SpireSpells.group(row)] + 1
			end
		end
		table.sort(levels)
		curves[v] = table.concat(levels, ",")
		SpireTest.eq(kinds.attack >= 2 and kinds.healing >= 1 and kinds.support >= 6, true, "vocation " .. v .. " has attack, healing and support/utility spells")
	end
	for a = 1, 4 do
		for b = a + 1, 4 do
			SpireTest.eq(curves[a] ~= curves[b], true, "vocations " .. a .. " and " .. b .. " unlock differently")
		end
	end
	-- shared spells come at different levels per vocation
	local kindle
	for _, row in ipairs(SpireSpells.list) do
		if row.name == "Kindle" then kindle = row end
	end
	SpireTest.eq(SpireSpells.levelFor(kindle, 4) ~= SpireSpells.levelFor(kindle, 1), true, "Kindle: Vanguard and Arcanist differ")
	local names = {}
	for _, r in ipairs(SpireSpells.unlockedAt(14, 1)) do
		names[r.name] = true
	end
	SpireTest.eq(names["Mana Ward"] and names["Hearth Ration"] and names["Quickstep"] and not names["Thorn Strike"], true, "arcanist level 14 unlocks")
	for _, r in ipairs(SpireSpells.unlockedAt(120, 1)) do
		if r.lostArt then error("Lost Arts must not unlock by level") end
	end
	local row = { lostArt = 5 }
	SpireTest.eq(SpireSpells.knowsLostArt(row, function() return false end), false, "not yet earned")
	SpireTest.eq(SpireSpells.knowsLostArt(row, function(f) return f == 5 end), true, "earned on floor 5")
end)

-- Area "power" = tiles hit x average multiplier / cooldown. Every Vanguard area spell must be well under half of
-- every other vocation's first area spell (Tibia's solo curve: knights hardest), and it has only two: Whirlwind and
-- the late Faultline.
local function areaPower(row)
	return SpireSpells.areaSize(row.area) * (row.min + row.max) / 2 / row.cd
end

SpireTest.add("spells: the Vanguard's area attacks are few, late and weak next to the others' first one", function()
	local vAreas = {}
	for _, row in ipairs(ownRows(4)) do
		if row.kind == "attack_area" or row.kind == "zone" or row.kind == "trail_dash" then table.insert(vAreas, row) end
	end
	table.sort(vAreas, function(a, b) return a.level < b.level end)
	SpireTest.eq(#vAreas, 2, "Vanguard has exactly two damaging area spells")
	SpireTest.eq(vAreas[1].name .. "/" .. vAreas[2].name, "Whirlwind/Faultline", "which ones")
	SpireTest.eq(vAreas[2].level >= 150, true, "the second comes late")
	for v = 1, 3 do
		local first
		for _, row in ipairs(ownRows(v)) do
			if row.kind == "attack_area" and row.min >= 0.6 and (not first or row.level < first.level) then
				first = row
			end
		end
		for _, va in ipairs(vAreas) do
			SpireTest.eq(areaPower(va) < areaPower(first) * 0.5, true, va.name .. " vs " .. first.name)
		end
		SpireTest.eq(vAreas[1].level > first.level, true, "Vanguard gets its area spell later than " .. first.name)
	end
end)

-- The 2026-11-16 pass: staged areas, evolving looks, riders and Elemental Clash
local function rowNamed(name)
	for _, r in ipairs(SpireSpells.list) do
		if r.name == name then return r end
	end
	error("no spell called " .. name)
end

SpireTest.add("spells: area shapes turn with the caster and play out in stages", function()
	SpireTest.eq(SpireSpells.areaSize("ring1"), 8, "ring1 tiles")
	SpireTest.eq(SpireSpells.areaSize("ring2"), 20, "ring2 tiles")
	SpireTest.eq(SpireSpells.areaSize("wave"), 7, "wave tiles")
	SpireTest.eq(SpireSpells.areaSize("target1"), 9, "target1 includes the target's own tile")
	-- a beam facing east runs along +x
	for _, t in ipairs(SpireSpells.areaOffsets("beam", 1)) do
		SpireTest.eq(t.dy == 0 and t.dx >= 1 and t.dx <= 5, true, "beam east tile " .. t.dx .. "," .. t.dy)
	end
	for _, t in ipairs(SpireSpells.areaOffsets("beam", 2)) do
		SpireTest.eq(t.dx == 0 and t.dy >= 1, true, "beam south tile")
	end
	local function fixed(n) return n end
	local stages, step = SpireSpells.stages(rowNamed("Inferno Core"), 0, fixed)
	SpireTest.eq(#stages, 2, "a 2-ring burst has two stages")
	SpireTest.eq(#stages[1] .. "+" .. #stages[2], "8+12", "inner ring first, then the outer")
	SpireTest.eq(step > 0, true, "with a pause between")
	stages = SpireSpells.stages(rowNamed("Arc Beam"), 0, fixed)
	SpireTest.eq(#stages, 5, "a beam sweeps tile by tile")
	stages = SpireSpells.stages(rowNamed("Whirlwind"), 0, fixed)
	SpireTest.eq(#stages, 8, "Whirlwind goes round one tile at a time")
	local n = 0
	for _, st in ipairs((SpireSpells.stages(rowNamed("Stormcall"), 0, fixed))) do n = n + #st end
	SpireTest.eq(n, 20, "a rain still lands on every tile once")
	for _, row in ipairs(SpireSpells.list) do
		if row.area then
			if not SpireSpells.AREAS[row.area] then error(row.name .. " uses an unknown area") end
			local total = 0
			for _, st in ipairs((SpireSpells.stages(row, 0, fixed))) do total = total + #st end
			SpireTest.eq(total, SpireSpells.areaSize(row.area), row.name .. " stages cover its area")
		end
	end
end)

SpireTest.add("spells: looks evolve with level, riders add up, the next unlock is announced", function()
	local ember = rowNamed("Ember Strike")
	SpireTest.eq(SpireSpells.visuals(ember, 10).impact2, nil, "plain at level 10")
	SpireTest.eq(SpireSpells.visuals(ember, 60).impact2, CONST_ME_EXPLOSIONHIT, "second look at 50")
	SpireTest.eq(SpireSpells.visuals(ember, 150).effect, SpireFx.EMBER_PILLAR, "third look at 120")
	local mercy, ambush = rowNamed("Mercy Shot"), rowNamed("Ambush Shot")
	SpireTest.eq(SpireSpells.riderBonus(mercy, 0.25), 0.75, "Mercy Shot on a wounded target")
	SpireTest.eq(SpireSpells.riderBonus(mercy, 0.8), 0, "Mercy Shot on a healthy target")
	SpireTest.eq(SpireSpells.riderBonus(ambush, 1), 0.6, "Ambush Shot on an untouched target")
	SpireTest.eq(SpireSpells.riderBonus(ambush, 0.99), 0, "Ambush Shot once it is hurt")
	local level, names = SpireSpells.nextUnlock(8, 1)
	SpireTest.eq(level .. ":" .. table.concat(names, ","), "9:Mending Spark", "Arcanist at 8 learns next at 9")
	SpireTest.eq(SpireSpells.nextUnlock(100000, 1), nil, "nothing after the last spell")
	-- every custom effect id is unique and above the engine's own
	local seen = {}
	for name, id in pairs(SpireFx) do
		SpireTest.eq(id > 309 and not seen[id], true, "effect " .. name)
		seen[id] = true
	end
	-- there is always a next spell to look forward to: no gap longer than 70 levels up to the level 300 capstone
	for v = 1, 4 do
		local levels = {}
		for _, row in ipairs(SpireSpells.list) do
			if SpireSpells.allowed(row, v) and not row.lostArt then table.insert(levels, SpireSpells.levelFor(row, v)) end
		end
		table.sort(levels)
		for i = 2, #levels do
			SpireTest.eq(levels[i] - levels[i - 1] <= 70, true, "vocation " .. v .. " gap before level " .. levels[i])
		end
		SpireTest.eq(levels[#levels], 300, "vocation " .. v .. " capstone")
	end
end)

SpireTest.add("spells: Elemental Clash rules", function()
	local bonus, mark, name = SpireClash.resolve(nil, "fire")
	SpireTest.eq(bonus .. "/" .. tostring(mark), "0/fire", "fire on a clean monster leaves a fire mark")
	bonus, mark, name = SpireClash.resolve("fire", "fire")
	SpireTest.eq(bonus .. "/" .. tostring(mark), "0/fire", "same element: no clash, mark renewed")
	bonus, mark, name = SpireClash.resolve("fire", "energy")
	SpireTest.eq(bonus .. "/" .. tostring(mark) .. "/" .. name, "25/false/Flashfire", "fire then energy clashes")
	bonus, mark, name = SpireClash.resolve("energy", "fire")
	SpireTest.eq(name, "Flashfire", "either order")
	bonus, mark, name = SpireClash.resolve("ice", "physical")
	SpireTest.eq(bonus .. "/" .. name, "25/Breaker", "a weapon blow breaks a mark")
	bonus, mark = SpireClash.resolve(nil, "physical")
	SpireTest.eq(bonus .. "/" .. tostring(mark), "0/nil", "a weapon blow leaves no mark")
	bonus, mark = SpireClash.resolve("ice", nil)
	SpireTest.eq(bonus .. "/" .. tostring(mark), "0/nil", "other damage does nothing")
	local els = { "fire", "energy", "ice", "earth", "holy" }
	for i = 1, #els do
		for j = i + 1, #els do
			local _, _, n = SpireClash.resolve(els[i], els[j])
			SpireTest.eq(n ~= nil and n ~= "Breaker", true, els[i] .. " + " .. els[j] .. " has its own name")
		end
	end
end)

SpireTest.add("spells: knock-back and Lifeseed on a real monster, bosses stay put", function()
	local spot = WorldPoints.centre_boar_meadow
	local m = Game.createMonster("Field Rat", spot, true, true)
	if not m then error("could not place a test monster") end
	local id = m:getId()
	SpireTest.eq(SpireSpells.movable(m), true, "an ordinary monster can be moved")
	local from = m:getPosition()
	local moved = 0
	for _, d in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }) do
		moved = SpireSpells.shove(m, d[1], d[2], 2)
		if moved > 0 then break end
	end
	SpireTest.eq(moved > 0 and m:getPosition():getDistance(from) == moved, true, "the monster slid " .. moved .. " tiles")
	-- Lifeseed: a killing blow leaves it on 1 health and uses the seed up
	SpireBuffs.seed[id] = { pct = 35, untilTime = os.time() + 5 }
	doTargetCombatHealth(0, m, COMBAT_PHYSICALDAMAGE, -99999, -99999, CONST_ME_NONE, ORIGIN_SPELL)
	local alive = Creature(id)
	SpireTest.eq(alive and alive:getHealth() or "dead", 1, "the seeded creature survives on 1 health")
	SpireTest.eq(SpireBuffs.seed[id], nil, "the seed is used up")
	if alive then alive:remove() end
	local bossType = MonsterType("Axe-Lord of the Stair")
	SpireTest.eq(bossType ~= nil and bossType:canPushCreatures(), true, "bosses are marked as too heavy to drag")
end)

SpireTest.add("spells: every kind has code, targeted spells ask for a target, groups are right", function()
	for _, row in ipairs(SpireSpells.list) do
		local isAttack = row.kind == "attack_target" or row.kind == "attack_area"
		if not isAttack and not SpireSpells.KINDS[row.kind] then
			error(row.name .. " has no code for kind " .. row.kind)
		end
	end
	SpireTest.eq(SpireSpells.group(rowNamed("Emberfield")), "attack", "a burning zone is an attack")
	SpireTest.eq(SpireSpells.group(rowNamed("Caltrops")), "support", "a slowing zone is support")
	SpireTest.eq(SpireSpells.group(rowNamed("Bloomburst")), "healing", "Bloomburst is a heal first")
	SpireTest.eq(SpireSpells.aggressive(rowNamed("Iron Reach")), true, "dragging a monster is an attack on it")
	SpireTest.eq(SpireSpells.aggressive(rowNamed("Lifeseed")), false, "Lifeseed is friendly")
end)

SpireTest.add("spells: damage numbers at sample levels", function()
	local function row(name)
		for _, r in ipairs(SpireSpells.list) do
			if r.name == name then return r end
		end
	end
	-- level 30 Arcanist with magic level 20: Ember Strike 6 + 24 + 5 .. 6 + 40 + 10
	local mn, mx = SpireSpells.range(row("Ember Strike"), 30, 20)
	SpireTest.eq(mn .. "-" .. mx, "35-56", "Ember Strike at level 30, magic 20")
	-- level 40 Vanguard with sword 60: Heavy Strike 8 + 48 + 5 .. 8 + 90 + 10
	mn, mx = SpireSpells.range(row("Heavy Strike"), 40, 60)
	SpireTest.eq(mn .. "-" .. mx, "61-108", "Heavy Strike at level 40, sword 60")
	-- Second Wind grows with level: 30 * 1.0 + 20 .. 30 * 1.6 + 40
	mn, mx = SpireSpells.range(row("Second Wind"), 30, 30)
	SpireTest.eq(mn .. "-" .. mx, "50-88", "Second Wind at level 30")
end)

-- A stand-in caster with a real backpack (the test boot has no logged-in players)
local function fakeCaster(tag)
	local pos = WorldPoints.temple_hearthgate
	local bp = Game.createItem(2854, 1, pos)
	local p = { bp = bp, msgs = {} }
	function p:addItem(id, n) return bp:addItem(id, n) end
	function p:removeItem(id, n)
		for i = 0, bp:getSize() - 1 do
			local it = bp:getItem(i)
			if it and it:getId() == id then
				return it:remove(n)
			end
		end
		return false
	end
	function p:sendCancelMessage(m) table.insert(self.msgs, m) end
	function p:getPosition() return pos end
	return p
end

local function countIn(bp, id)
	local n = 0
	for i = 0, bp:getSize() - 1 do
		local it = bp:getItem(i)
		if it and it:getId() == id then n = n + it:getCount() end
	end
	return n
end

SpireTest.add("spells: conjuring uses up a blank rune (cast through the real spell code)", function()
	local fire
	for _, r in ipairs(SpireSpells.list) do
		if r.name == "Conjure Fire Rune" then fire = r end
	end
	local p = fakeCaster("conjure")
	SpireTest.eq(SpireSpells.KINDS.conjure(fire, p), false, "no blank rune: refused")
	SpireTest.eq(p.msgs[1]:find("blank rune", 1, true) ~= nil, true, "tells you why")
	p:addItem(SpireSpells.BLANK_RUNE, 1)
	SpireTest.eq(SpireSpells.KINDS.conjure(fire, p), true, "with a blank rune: works")
	SpireTest.eq(countIn(p.bp, SpireSpells.BLANK_RUNE), 0, "blank rune used up")
	SpireTest.eq(countIn(p.bp, fire.item) >= 1, true, "fire runes made")
	p.bp:remove()
	for _, r in ipairs(SpireSpells.list) do
		if r.kind == "conjure" and (r.item == 3447 or r.item == 3446 or r.item == 3277) then
			error(r.name .. " conjures ammunition")
		end
	end
end)

SpireTest.add("spells: Undying Oath and damage reduction work on a real creature", function()
	SpireTest.eq(SpireBuffs.undyingClamp(100, 250), 99, "lethal hit leaves 1")
	SpireTest.eq(SpireBuffs.undyingClamp(100, 40), 40, "small hit unchanged")
	SpireTest.eq(SpireBuffs.apply(100, 30, 0), 70, "30% reduction")
	SpireTest.eq(SpireBuffs.apply(100, 0, 10), 110, "10% mark")
	local m = Game.createMonster("Field Rat", WorldPoints.centre_boar_meadow, true, true) -- open ground, not a protection zone
	if not m then
		error("could not place a test monster")
	end
	local id = m:getId()
	local full = m:getHealth()
	doTargetCombatHealth(0, m, COMBAT_PHYSICALDAMAGE, -1, -1, CONST_ME_NONE, ORIGIN_SPELL)
	SpireTest.eq(m:getHealth(), full - 1, "a plain 1-damage hit lands")
	SpireBuffs.undying[id] = os.time() + 5
	doTargetCombatHealth(0, m, COMBAT_PHYSICALDAMAGE, -99999, -99999, CONST_ME_NONE, ORIGIN_SPELL)
	local alive = Creature(id)
	SpireTest.eq(alive and alive:getHealth() or "dead", 1, "undying creature survives a lethal hit on 1 HP")
	SpireBuffs.undying[id] = nil
	if alive then
		alive:addHealth(alive:getMaxHealth())
		SpireBuffs.addReduction(id, 50, 5)
		local before = alive:getHealth()
		doTargetCombatHealth(0, alive, COMBAT_PHYSICALDAMAGE, -10, -10, CONST_ME_NONE, ORIGIN_SPELL)
		SpireTest.eq(before - alive:getHealth(), 5, "50% reduction halves a 10 damage hit")
		SpireBuffs.reduce[id] = nil
		alive:remove()
	end
end)

-- Playtest-sized bug found by the in-client spell test (2026-11-17): ally spells were registered with the engine's
-- "player name" parameter, which refuses the spell when no name is given, so "mend other" or "field dressing" on
-- yourself never ran. The name is optional: no name = yourself.
SpireTest.add("spells: ally spells can be cast with no name (on yourself)", function()
	local ally = { heal_target = true, hot_target = true, dr_target = true, seed = true, heal_chain = true, heal_burst = true }
	local n = 0
	for _, row in ipairs(SpireSpells.list) do
		if ally[row.kind] then
			local s = Spell(row.name)
			SpireTest.eq(s:hasPlayerNameParam(), false, row.name .. " must not demand a player name")
			SpireTest.eq(s:hasParams(), true, row.name .. " still takes an optional name")
			n = n + 1
		end
	end
	SpireTest.eq(n >= 7, true, "ally spells checked: " .. n)
end)

-- Jay's playtest (2026-11-17): "the last time I tested the haste spell it actually made my character slower".
-- The engine's speed formula gives the new speed, not the change; checked here on a real monster.
SpireTest.add("spells: haste makes you faster and slows slow (they don't freeze)", function()
	SpireTest.eq(SpireSpells.speedAfter(200, 0.3), 260, "Quickstep at base speed 200")
	SpireTest.eq(SpireSpells.speedAfter(200, -0.45), 110, "a 45% slow at base speed 200")
	SpireTest.eq(SpireSpells.speedAfter(200, -0.99), 40, "never below walking speed 40")
	local m = Game.createMonster("Field Rat", WorldPoints.centre_boar_meadow, true, true)
	if not m then error("could not place a test monster") end
	local base = m:getSpeed()
	local haste = Condition(CONDITION_HASTE)
	haste:setParameter(CONDITION_PARAM_TICKS, 5000)
	m:addCondition(SpireSpells.setSpeed(haste, 0.3))
	local fast = m:getSpeed()
	m:removeCondition(CONDITION_HASTE)
	local slow = Condition(CONDITION_PARALYZE)
	slow:setParameter(CONDITION_PARAM_TICKS, 5000)
	m:addCondition(SpireSpells.setSpeed(slow, -0.45))
	local slowed = m:getSpeed()
	m:remove()
	SpireTest.eq(fast > base * 1.2, true, "haste: base " .. base .. ", hasted " .. fast)
	SpireTest.eq(slowed < base * 0.7 and slowed > base * 0.4, true, "slow: base " .. base .. ", slowed " .. slowed)
	-- and every haste spell in the table really is faster
	for _, row in ipairs(SpireSpells.list) do
		if row.speed then
			SpireTest.eq(SpireSpells.speedAfter(250, row.speed) > 250, true, row.name .. " is faster")
		end
	end
end)
