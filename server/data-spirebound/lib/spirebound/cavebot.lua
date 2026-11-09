-- Built-in cavebot penalty (DESIGN.md 12, Jay 2026-11-08). Roadmap 2.12.
-- The Spirebound client reports when its cavebot is switched on or off. While on, and for LINGER seconds after:
-- XP x0.45, loot x0.5, no secrets/rare rewards, no boss rooms. Auto-targeting alone costs nothing. No visible marker.
SpireCavebot = {
	XP = 0.45,
	LOOT = 0.50,
	LINGER = 10 * 60, -- QUESTIONS.md Q11 (Claude's recommendation until Jay answers)
	state = {}, -- playerGuid -> { on = bool, offAt = time }
}

-- Pure
function SpireCavebot.penaltyActive(st, now)
	if not st then
		return false
	end
	if st.on then
		return true
	end
	return st.offAt ~= nil and now - st.offAt < SpireCavebot.LINGER
end

function SpireCavebot.setState(guid, on, now)
	local st = SpireCavebot.state[guid] or {}
	if st.on and not on then
		st.offAt = now
	end
	st.on = on
	SpireCavebot.state[guid] = st
	return st
end

function SpireCavebot.active(player)
	return SpireCavebot.penaltyActive(SpireCavebot.state[player:getGuid()], os.time())
end

function SpireCavebot.blocksRewards(player)
	return SpireCavebot.active(player)
end

function SpireCavebot.xpFactor(player)
	return SpireCavebot.active(player) and SpireCavebot.XP or 1
end
