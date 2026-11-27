-- Spirebound's experience and skill modifiers, applied where the engine really uses the result.
-- Floor 1 review, 2026-11-26: the EventCallback versions (playerOnGainExperience, playerOnGainSkillTries) are "void"
-- in Canary 3.6.1, so every factor returned from them was thrown away. tools/build_server.py appends
-- server/core-patches/player_events_append.lua to the engine's data/events/scripts/player.lua, whose
-- Player:onGainExperience / onGainSkillTries the engine does honour; they call the two functions below.
-- A script adds its factor with SpireHooks.xp(name, fn) or SpireHooks.skill(name, fn); fn returns the new amount.
-- Order: the order the scripts are named in ORDER (so the bookkeeping of the difficulty bonus sees the same amounts
-- on every start), then any others by name.
SpireHooks = SpireHooks or { xpFns = {}, skillFns = {} }

local ORDER = { boost = 1, beacons = 2, events = 3, difficulty = 4 }

local function sorted(fns)
	local names = {}
	for name in pairs(fns) do
		table.insert(names, name)
	end
	table.sort(names, function(a, b)
		local oa, ob = ORDER[a] or 99, ORDER[b] or 99
		if oa ~= ob then
			return oa < ob
		end
		return a < b
	end)
	return names
end

function SpireHooks.xp(name, fn)
	SpireHooks.xpFns[name] = fn
end

function SpireHooks.skill(name, fn)
	SpireHooks.skillFns[name] = fn
end

-- Experience from a monster kill, after the engine's own rates. Returns a whole number.
function SpireHooks.gainExperience(player, target, exp, rawExp)
	for _, name in ipairs(sorted(SpireHooks.xpFns)) do
		exp = SpireHooks.xpFns[name](player, target, exp, rawExp) or exp
	end
	return math.floor(exp + 0.5)
end

function SpireHooks.gainSkillTries(player, skill, tries)
	for _, name in ipairs(sorted(SpireHooks.skillFns)) do
		tries = SpireHooks.skillFns[name](player, skill, tries) or tries
	end
	return tries
end
