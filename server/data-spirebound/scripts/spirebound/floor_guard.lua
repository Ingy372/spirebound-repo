-- Floor guard (DESIGN.md 3.2): a floor is sealed until the floor below is cleared. The map seals the stair, and this
-- is the second lock: anyone found standing on a floor that is not open yet is sent back to Hearthgate's temple,
-- whatever trick got them there. Staff are exempt so they can test.
local guard = GlobalEvent("SpireFloorGuard")
function guard.onThink(interval)
	local open = {}
	for _, p in ipairs(Game.getPlayers()) do
		local n = Floors.at(p:getPosition())
		if n > 1 then
			if open[n] == nil then
				open[n] = Floors.isOpen(n)
			end
			if not Floors.mayStandOn(n, open[n], p:getGroup():getAccess()) then
				local home = WorldPoints.temple_hearthgate
				p:teleportTo(Position(home.x, home.y, home.z))
				p:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Floor %d is still sealed. Its guardian on Floor %d must fall first.", n, n - 1))
				logger.info("[Spirebound] floor guard: {} was on sealed floor {} and was sent back", p:getName(), n)
			end
		end
	end
	return true
end
guard:interval(1000)
guard:register()
