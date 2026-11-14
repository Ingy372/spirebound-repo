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

SpireTest.add("spells: 15-25 own spells per vocation, 2 Lost Arts each, at most 25 with shared", function()
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
		SpireTest.eq(own >= 15 and own <= 25, true, "vocation " .. v .. " has " .. own .. " own spells")
		SpireTest.eq(total <= 25, true, "vocation " .. v .. " has " .. total .. " spells in all")
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

-- Area "power" = tiles hit x average multiplier / cooldown. The Vanguard's area spell must be well under half of
-- every other vocation's first area spell (Tibia's solo curve: knights hardest).
local TILES = { ring1 = 8, wave = 10, beam = 5 }
local function areaPower(row)
	return (TILES[row.area] or 0) * (row.min + row.max) / 2 / row.cd
end

SpireTest.add("spells: the Vanguard has one weak area attack, the others' first area attack is far stronger", function()
	local vAreas = {}
	for _, row in ipairs(ownRows(4)) do
		if row.kind == "attack_area" then table.insert(vAreas, row) end
	end
	SpireTest.eq(#vAreas, 1, "Vanguard has exactly one damaging area spell")
	local vPower = areaPower(vAreas[1])
	for v = 1, 3 do
		local first
		for _, row in ipairs(ownRows(v)) do
			if row.kind == "attack_area" and TILES[row.area] and (not first or row.level < first.level) then
				first = row
			end
		end
		SpireTest.eq(vPower < areaPower(first) * 0.5, true, "Vanguard Whirlwind vs " .. first.name)
		SpireTest.eq(vAreas[1].level > first.level, true, "Vanguard gets its area spell later than " .. first.name)
	end
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
