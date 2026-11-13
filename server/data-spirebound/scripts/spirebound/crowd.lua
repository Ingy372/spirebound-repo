-- The crowd system's 30-second tick (rules: lib/spirebound/crowd.lua).
local tick = GlobalEvent("SpireCrowdTick")
function tick.onThink(interval)
	SpireCrowd.tick(os.time())
	return true
end
tick:interval(SpireCrowd.TICK * 1000)
tick:register()
