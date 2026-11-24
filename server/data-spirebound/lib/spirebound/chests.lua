-- Ground chests (FLOOR1_REVIEW.md F1-20): one treasure chest in the deepest quiet spot of every rebuilt hunting ground.
-- The first time a character opens it: gold, potions and a rough Hearth Shard. After that, a smaller daily chest every
-- 20 hours (Cyntara's daily chests were one of the reasons players came back). Placed by scripts/spirebound/chests.lua
-- at the map's chest_<ground> points (maps/designed.py picks them).
SpireChests = SpireChests or {}
SpireChests.ITEM = 4073          -- a treasure chest that can't be moved or walked through
SpireChests.AID = 59100          -- action ids 59101.. (one per chest)
SpireChests.DAILY = 20 * 3600

-- Pure: what a chest gives, by its ground's level band
function SpireChests.reward(lo, hi)
	local mid = math.floor((lo + hi) / 2)
	local potions = mid >= 14 and { 236, 3 } or { 266, 5 } -- strong health potions from the level 14 grounds up
	return { gold = 150 * mid, potions = potions, shard = true }
end

function SpireChests.daily(lo, hi)
	return { gold = 20 * math.floor((lo + hi) / 2) }
end

-- Pure: rec = { first = time or nil, last = time or nil }. Returns "first", "daily", or nil and seconds to wait.
function SpireChests.claim(rec, now)
	if not rec or not rec.first then
		return "first"
	end
	local since = now - (rec.last or rec.first)
	if since >= SpireChests.DAILY then
		return "daily"
	end
	return nil, SpireChests.DAILY - since
end
