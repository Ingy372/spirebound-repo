-- Jay's playtest (2026-11-13): Rangers need a quiver; the bow only fires from one.
SpireTest.add("quiver: Rangers get a real quiver that holds arrows", function()
	local it = ItemType(SpireQuiver.ID)
	SpireTest.eq(it:isQuiver(), true, "item " .. SpireQuiver.ID .. " is a quiver to the engine")
	local q = Game.createItem(SpireQuiver.ID, 1, WorldPoints.temple_hearthgate)
	SpireTest.eq(q ~= nil and q:addItem(3447, 100) ~= nil, true, "100 arrows fit inside")
	q:remove()
end)
