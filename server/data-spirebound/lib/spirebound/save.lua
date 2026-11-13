-- Saving at the big moments (roadmap R8, REVIEW 7.2). A crash should never lose a floor clear, a Death Game
-- retirement, a shop purchase or a secret sale, so each of those saves the whole server at once. Between them the
-- server saves every 10 minutes (scripts/spirebound/save.lua; Canary's own interval save only runs at the daily
-- save time).

SpireSave = SpireSave or { INTERVAL_MINUTES = 10, count = 0, last = nil, minGap = 5 }

-- Save everything now. Big moments close together (a whole party getting credit) share one save.
function SpireSave.now(reason)
	local now = os.time()
	if SpireSave.lastTime and now - SpireSave.lastTime < SpireSave.minGap then
		SpireSave.pending = reason
		return false
	end
	SpireSave.lastTime = now
	SpireSave.count = SpireSave.count + 1
	SpireSave.last = reason
	saveServer()
	logger.info("[Spirebound] saved the server: {}", reason or "interval")
	return true
end
