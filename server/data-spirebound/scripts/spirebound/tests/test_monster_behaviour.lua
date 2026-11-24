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
