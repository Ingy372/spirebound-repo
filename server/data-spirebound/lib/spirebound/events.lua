-- World events and weekend bonuses (DESIGN.md 3.6 and 15). Roadmap 5.7 / 5.7b.
SpireEvents = {
	INTERVAL = 3 * 3600, -- a world event every 3 hours
	WARNING = 10 * 60,
	KINDS = {
		{ id = "frenzy", name = "Frenzy", minutes = 45, text = "The apex spawn of Floor %d is in a frenzy: more monsters, +25%% loot!" },
		{ id = "incursion", name = "Incursion", minutes = 30, text = "Elite packs are pouring into the camps of Floor %d!" },
		{ id = "fishing", name = "Fishing Frenzy", minutes = 45, text = "The fish of Floor %d are biting like mad: rare catches x3!" },
		{ id = "champion", name = "Wandering Champion", minutes = 60, text = "A champion roams Floor %d. Hunt it down!" },
	},
	WEEKEND = {
		{ id = "xp", name = "Double Experience" },
		{ id = "loot", name = "Double Loot" },
		{ id = "skill", name = "Double Skill Training" },
		{ id = "fishing", name = "Double Fishing Luck" },
		{ id = "respawn", name = "Rapid Respawn" }, -- R20: every ground packed, extra groups back twice as fast
	},
	active = nil, -- { kind = row, floor = n, untilTime = t }
	derby = nil, -- { untilTime, best = { name, kg } }
}

-- Pure: which weekend bonus runs this week (rotates by ISO-ish week number)? nil on weekdays.
-- wday: 1 = Sunday ... 7 = Saturday (os.date("*t").wday)
function SpireEvents.weekendBonus(wday, weekNumber)
	if wday ~= 1 and wday ~= 7 then
		return nil
	end
	return SpireEvents.WEEKEND[(weekNumber % #SpireEvents.WEEKEND) + 1]
end

function SpireEvents.currentWeekend()
	local t = os.date("*t")
	return SpireEvents.weekendBonus(t.wday, tonumber(os.date("%W")))
end

function SpireEvents.factor(id)
	local w = SpireEvents.currentWeekend()
	return (w and w.id == id) and 2 or 1
end

-- Pure: pick an event kind and floor from a random number in [0,1) and the highest open floor
function SpireEvents.pick(r, highestFloor)
	local kinds = SpireEvents.KINDS
	local k = kinds[math.floor(r * #kinds) + 1]
	local floor = math.floor((r * 997) % highestFloor) + 1
	return k, floor
end

function SpireEvents.isActive(id, floor)
	local a = SpireEvents.active
	return a and a.kind.id == id and (floor == nil or a.floor == floor) and os.time() < a.untilTime
end

-- Fishing luck multiplier for rare fish (Fishing Frenzy on that floor, or the weekend fishing bonus)
function SpireEvents.fishingLuck(floor)
	local m = SpireEvents.factor("fishing")
	if SpireEvents.isActive("fishing", floor) then
		m = m * 3
	end
	return m
end
