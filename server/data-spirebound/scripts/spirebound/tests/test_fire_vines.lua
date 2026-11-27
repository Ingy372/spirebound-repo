-- J15b / FD2b: fire (spells and the fire rune) burns Thornsnap Hollow's vine walls.
SpireTest.add("fire burns a Thornsnap vine wall (J15b)", function()
	local c = SpireFeatures.conf("thornsnap_hollow", "vines")
	local p = WorldPoints["feat_vine_1_1"]
	SpireTest.eq(c ~= nil and p ~= nil, true, "Thornsnap Hollow has vine walls")
	local pos = Position(p.x, p.y, p.z)
	-- clear whatever stands there now, then raise one vine on the wall's first tile
	SpireFeatures.clearVineWall(pos, c.vine)
	local v = Game.createItem(c.vine, 1, pos)
	v:setActionId(SpireFeatures.AID.vine)
	SpireTest.eq(SpireSpells.burnVines(pos), true, "a fire hit burns it")
	local left = false
	for _, it in ipairs(Tile(pos):getItems() or {}) do
		if it:getId() == c.vine and it:getActionId() == SpireFeatures.AID.vine then
			left = true
		end
	end
	SpireTest.eq(left, false, "the vine is gone")
	SpireTest.eq(SpireSpells.burnVines(pos), false, "nothing left to burn")
	local f = io.open("data/scripts/runes/great_fireball.lua", "r")
	local text = f and f:read("*a") or ""
	if f then f:close() end
	SpireTest.eq(text:find("SpireSpells.burnVines", 1, true) ~= nil, true, "the fire rune burns vines where it bursts")
end)
