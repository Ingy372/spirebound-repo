-- Roadmap R6: the Hardcore death item drop, through the real death handler (SpireHardcore.onDeath, which the
-- onDeath event calls). The dying character is a stand-in with the same methods the handler uses; the items and
-- the corpse are real items on the map, and they really move.

local function standIn(blessings, skull, pos)
	local slots = {}
	for _, s in ipairs({ CONST_SLOT_HEAD, CONST_SLOT_ARMOR, CONST_SLOT_LEGS, CONST_SLOT_FEET }) do
		slots[s] = Game.createItem(3355, 1, pos) -- a leather helmet each: real items lying on the map
	end
	return {
		getSlotItem = function(_, s) return slots[s] end,
		hasBlessing = function(_, b) return b <= blessings end,
		getSkull = function() return skull end,
		getPosition = function() return pos end,
		sendTextMessage = function() end,
	}, slots
end

local function corpseAt(pos)
	return Game.createItem(2853, 1, pos) -- a bag stands in for the corpse container
end

SpireTest.add("hardcore: the death item drop uses blessings and never errors on a skulled death", function()
	local pos = WorldPoints.temple_hearthgate
	local realRandom = math.random
	math.random = function() return 1 end -- every roll succeeds, so the chance alone decides
	local ok, err = pcall(function()
		local p = standIn(0, SKULL_NONE, pos)
		local bag = corpseAt(pos)
		SpireTest.eq(SpireHardcore.onDeath(p, bag, Difficulty.HARDCORE), 4, "no blessings: the extra roll can take every item")
		SpireTest.eq(bag:getSize(), 4, "the items really fell into the corpse")
		bag:remove()

		p = standIn(5, SKULL_NONE, pos)
		bag = corpseAt(pos)
		SpireTest.eq(SpireHardcore.onDeath(p, bag, Difficulty.HARDCORE), 0, "five blessings: no extra drop")
		bag:remove()

		p = standIn(0, SKULL_RED, pos)
		bag = corpseAt(pos)
		SpireTest.eq(SpireHardcore.onDeath(p, bag, Difficulty.HARDCORE), 0, "red skull: no error, no extra roll (it already drops everything)")
		bag:remove()

		p = standIn(0, SKULL_NONE, pos)
		bag = corpseAt(pos)
		SpireTest.eq(SpireHardcore.onDeath(p, bag, Difficulty.NORMAL), 0, "Normal characters never get the extra roll")
		bag:remove()
	end)
	math.random = realRandom
	if not ok then
		error(err)
	end
	SpireTest.eq(Difficulty.extraItemDropChance(Difficulty.HARDCORE, 2, false, false, false), 6, "two blessings: 6% per item")
end)
