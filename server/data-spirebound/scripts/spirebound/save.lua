-- Saves the server every 10 minutes, quietly (roadmap R8). Rules: lib/spirebound/save.lua.
local tick = GlobalEvent("SpireSaveInterval")
function tick.onThink(interval)
	SpireSave.lastTime = nil -- the interval save always runs
	SpireSave.now("every " .. SpireSave.INTERVAL_MINUTES .. " minutes")
	return true
end
tick:interval(SpireSave.INTERVAL_MINUTES * 60 * 1000)
tick:register()
