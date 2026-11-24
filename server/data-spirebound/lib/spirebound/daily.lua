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
