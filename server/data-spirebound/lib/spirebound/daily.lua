-- A daily login streak (FLOOR1_REVIEW.md F1-60): a small reason to come back every day. Never power: gold and potions.
-- Days are counted as whole UTC days (os.time() // 86400). Event: scripts/spirebound/daily.lua.
SpireDaily = SpireDaily or {}

-- Pure: the streak day this login earns, or nil if today was already paid.
function SpireDaily.next(lastDay, streak, today)
	if lastDay == today then
		return nil
	end
	if lastDay and today == lastDay + 1 and (streak or 0) < 7 then
		return (streak or 0) + 1
	end
	return 1
end

-- Pure: what a streak day pays
function SpireDaily.reward(day)
	if day >= 7 then
		return { gold = 1000, potions = 5 }
	end
	return { gold = 100 * day, potions = 0 }
end

-- The hourly lucky climber (FLOOR1_REVIEW.md F1-63). list = { { name, level, staff } }, last = last winner's name,
-- roll in [0, 1). Pure: returns the winner's name or nil.
SpireDaily.LUCKY_MIN_LEVEL = 8
function SpireDaily.luckyPick(list, last, roll)
	local pool = {}
	for _, p in ipairs(list) do
		if not p.staff and p.level >= SpireDaily.LUCKY_MIN_LEVEL and p.name ~= last then
			table.insert(pool, p.name)
		end
	end
	if #pool == 0 then
		return nil
	end
	return pool[math.floor(roll * #pool) + 1]
end

function SpireDaily.luckyGold(level)
	return math.min(5000, 20 * level)
end

-- P12 (FLOOR1_REVIEW.md F1-64): every 6 hours the strongest climber online who can be attacked carries a bounty paid by
-- the tower. Only climbers in open PvP range (level 50+) qualify, so nobody below the PvP line is ever made a target.
SpireDaily.TOP_BOUNTY_MIN_LEVEL = 50
function SpireDaily.topBountyPick(list)
	local best
	for _, p in ipairs(list) do
		if not p.staff and p.level >= SpireDaily.TOP_BOUNTY_MIN_LEVEL then
			if not best or p.level > best.level or (p.level == best.level and p.name < best.name) then
				best = p
			end
		end
	end
	return best and best.name or nil
end

function SpireDaily.topBountyGold(level)
	return math.min(50000, 100 * level)
end
