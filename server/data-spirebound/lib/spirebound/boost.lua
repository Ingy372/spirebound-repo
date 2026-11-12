-- Boosted creature of the day (roadmap J7, from the top-server research): one hunting-ground monster each day gives
-- +50% experience and a second loot roll. Canary's own version picks from the official bestiary, which our monsters are
-- not part of, so Spirebound picks its own. The day turns over at the 10:00 server save.
SpireBoost = {
	candidates = { "Field Rat", "Hopper Toad", "Sproutling", "Meadow Wasp", "Bristle Boar", "Burrow Mole", "Meadow Wolf",
		"Thornsnap", "Reed Snapper", "Field Shardling", "Road Bandit", "Ruin Sentinel", "Ruin Archer" },
	XP = 1.5,
	LOOT_BONUS = 1.0, -- one extra loot roll
}

function SpireBoost.dayNumber(t)
	return math.floor(((t or os.time()) - 10 * 3600) / 86400)
end

-- Pure: 13 candidates and a step of 7 visit every monster once before any repeats
function SpireBoost.pick(day)
	local c = SpireBoost.candidates
	return c[(day * 7 + 3) % #c + 1]
end

function SpireBoost.today()
	return SpireBoost.pick(SpireBoost.dayNumber())
end

function SpireBoost.isBoosted(name)
	return name == SpireBoost.today()
end
