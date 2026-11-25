-- FLOOR1_REVIEW.md F1-10: every regular Floor 1 monster does something besides walking up and biting
local FLOOR1 = { "Field Rat", "Hopper Toad", "Sproutling", "Meadow Wasp", "Bristle Boar", "Meadow Wolf", "Burrow Mole",
	"Reed Snapper", "Road Bandit", "Thornsnap", "Field Shardling", "Ruin Archer", "Ruin Sentinel" }

SpireTest.add("monsters: every regular Floor 1 monster has a behaviour of its own", function()
	local plain = {}
	for _, name in ipairs(FLOOR1) do
		local mt = MonsterType(name)
		SpireTest.eq(mt ~= nil, true, name .. " exists")
		local attacks = #mt:getAttackList()
		local defenses = #mt:getDefenseList()
		local runs = mt:runHealth() > 0
		local poison = false
		for _, a in ipairs(mt:getAttackList()) do
			if a.conditionType and a.conditionType ~= 0 then poison = true end
		end
		if attacks < 2 and defenses == 0 and not runs and not poison then
			table.insert(plain, name)
		end
	end
	SpireTest.eq(table.concat(plain, ", "), "", "monsters that only bite")
end)

-- P6 second pass: the four tricks that need a script (scripts/spirebound/monster_tricks.lua)
SpireTest.add("monsters: a sproutling mends a hurt sproutling next to it", function()
	local base = WorldPoints.centre_boar_meadow
	local a = Game.createMonster("Sproutling", base, true, true)
	local b = Game.createMonster("Sproutling", Position(base.x + 1, base.y, base.z), true, true)
	SpireTest.eq(a ~= nil and b ~= nil, true, "two sproutlings made")
	b:addHealth(-25)
	local before = b:getHealth()
	SpireTest.eq(SpireTricks.mend(a), true, "the healer found a hurt friend")
	SpireTest.eq(b:getHealth() > before, true, "the friend got health back")
	a:remove()
	b:remove()
end)

SpireTest.add("monsters: the ruin sentinel's shield only blocks from the front", function()
	local base = WorldPoints.centre_boar_meadow
	local s = Game.createMonster("Ruin Sentinel", base, true, true)
	local front = Game.createMonster("Field Rat", Position(base.x, base.y + 2, base.z), true, true)
	local back = Game.createMonster("Field Rat", Position(base.x, base.y - 2, base.z), true, true)
	s:setDirection(DIRECTION_SOUTH)
	SpireTest.eq(SpireTricks.inFront(s, front), true, "a hit from the south is in front of a south-facing sentinel")
	SpireTest.eq(SpireTricks.inFront(s, back), false, "a hit from behind gets through")
	for _, m in ipairs({ s, front, back }) do
		m:remove()
	end
end)

SpireTest.add("monsters: a thieving rat drops what it stole", function()
	local base = WorldPoints.centre_boar_meadow
	local r = Game.createMonster("Field Rat", base, true, true)
	SpireTricks.stolen[r:getId()] = 7
	local pos = r:getPosition()
	SpireTest.eq(SpireTricks.dropStolen(r, nil), 7, "it gives back 7 gold")
	local tile = Tile(pos)
	local coins = tile and tile:getItemById(3031)
	SpireTest.eq(coins ~= nil and coins:getCount() == 7, true, "the 7 gold lies where it fell")
	SpireTest.eq(SpireTricks.stolen[r:getId()], nil, "the theft is forgotten")
	if coins then
		coins:remove()
	end
	r:remove()
end)

-- S5: packs keep together
SpireTest.add("monsters: wolves follow the nearest alpha, or the eldest wolf", function()
	local base = WorldPoints.centre_boar_meadow
	local w1 = Game.createMonster("Meadow Wolf", Position(base.x + 2, base.y + 1, base.z), true, true)
	local w2 = Game.createMonster("Meadow Wolf", Position(base.x + 3, base.y + 1, base.z), true, true)
	SpireTest.eq(SpirePack.leaderOf(w2) == w1, true, "without an alpha the eldest wolf leads")
	SpireTest.eq(SpirePack.leaderOf(w1), nil, "the eldest has no leader")
	local a = Game.createMonster("Grey Alpha", Position(base.x + 6, base.y + 1, base.z), true, true)
	SpireTest.eq(SpirePack.leaderOf(w1) == a and SpirePack.leaderOf(w2) == a, true, "the alpha leads them all")
	SpireTest.eq(SpirePack.leaderOf(a), nil, "the alpha follows nobody")
	SpireTest.eq(SpirePack.stepToward(Position(10, 10, 7), Position(15, 11, 7)), DIRECTION_EAST, "a step toward the leader")
	SpireTest.eq(SpirePack.stepToward(Position(10, 10, 7), Position(11, 11, 7)), nil, "already beside it")
	for _, m in ipairs({ w1, w2, a }) do
		m:remove()
	end
end)
