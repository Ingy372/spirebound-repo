-- Kill counting (roadmap N8). The engine's onKill creature event is deprecated in Canary 3.6.1 and writes a warning
-- line to the server log for every registered script on every kill (7-8 lines a kill, ~150,000 an hour at 100
-- players). Instead, one monster-death callback (scripts/spirebound/kills.lua) calls every script that counts kills,
-- once per kill, with the player who owns the corpse (the top damage dealer, or the master of a summon that was).
-- A script adds itself with SpireKills.on(name, fn(player, target)); target is the dead monster (still readable).
-- Party sharing stays each script's own business (SpireProgress.killCredit / sharers), as before.
SpireKills = SpireKills or { handlers = {}, order = {} }

function SpireKills.on(name, fn)
	if not SpireKills.handlers[name] then
		table.insert(SpireKills.order, name)
	end
	SpireKills.handlers[name] = fn
end

function SpireKills.report(name, err)
	logger.error("[Spirebound] kill counter {} failed: {}", name, tostring(err))
end

-- One failing script must not stop the others from counting the kill.
function SpireKills.fire(player, target)
	local done = 0
	for _, name in ipairs(SpireKills.order) do
		local ok, err = pcall(SpireKills.handlers[name], player, target)
		if ok then
			done = done + 1
		else
			SpireKills.report(name, err)
		end
	end
	return done
end
