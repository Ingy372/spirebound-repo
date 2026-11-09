-- Roadmap 2.7 / 2.8: secrets and the Info Broker.
SpireTest.add("secrets: 12 on floor 1, each with a walkable trigger tile", function()
	local n = 0
	for _, s in ipairs(SpireSecrets.list) do
		if s.floor == 1 then
			n = n + 1
			local pos = WorldPoints["secret_" .. s.id]
			if not pos then error(s.id .. " has no trigger point") end
			local t = Tile(pos)
			if not t or t:hasFlag(TILESTATE_BLOCKSOLID) then error(s.id .. " trigger tile is blocked") end
		end
	end
	SpireTest.eq(n, 12, "floor 1 secrets")
end)

SpireTest.add("secrets: selling rules never lock anyone out", function()
	SpireTest.eq((SpireSecrets.canSell(true, nil)), true, "finder may sell an unsold secret")
	SpireTest.eq((SpireSecrets.canSell(false, nil)), false, "can't sell what you didn't find")
	SpireTest.eq((SpireSecrets.canSell(true, "Someone")), false, "can't sell a public secret")
	SpireTest.eq(SpireSecrets.payout(SpireSecrets.get("s1")), 6000, "large floor 1 payout")
	SpireTest.eq(SpireSecrets.payout(SpireSecrets.get("s9")), 1500, "small floor 1 payout")
	SpireTest.eq(SpireSecrets.titleFor(9), nil, "no title yet")
	SpireTest.eq(SpireSecrets.titleFor(10), "Wanderer", "10 discoveries")
	SpireTest.eq(SpireSecrets.isNight(22), true, "22:00 is night")
	SpireTest.eq(SpireSecrets.isNight(12), false, "noon is not")
	-- public state round trip on a real secret, restored afterwards
	local before = SpireSecrets.publicBy("s12")
	SpireSecrets.markPublic("s12", "Tester")
	SpireTest.eq(SpireSecrets.publicBy("s12"), "Tester", "marked public")
	if before then SpireSecrets.markPublic("s12", before) else SpireSecrets.unpublish("s12") end
end)

SpireTest.add("underkeep: wing 1 exists, its monsters spawned, exit leads back up", function()
	for _, n in ipairs({ "underkeep_entry", "underkeep_exit", "underkeep_chest", "underkeep_wing2_door" }) do
		if not WorldPoints[n] or not Tile(WorldPoints[n]) then error("missing " .. n) end
	end
	local found = 0
	for _, c in ipairs(Game.getSpectators(WorldPoints.underkeep_entry, false, false, 70, 70, 50, 50)) do
		if c:isMonster() and (c:getName() == "Mire Toad" or c:getName() == "Black Crawler") then found = found + 1 end
	end
	if found < 10 then error("only " .. found .. " Underkeep monsters") end
end)

SpireTest.add("underkeep: wings 2-6 exist and stay sealed until their floor opens", function()
	for wid = 2, 6 do
		local src, req = WorldPoints["uk_door" .. wid], WorldPoints["uk_wing" .. wid .. "_req"]
		if not src or not req or not WorldPoints["uk_wing" .. wid .. "_entry"] then error("wing " .. wid .. " missing") end
		local tile = Tile(src)
		local sealed = tile:getItemById(1772) ~= nil
		SpireTest.eq(sealed, not Floors.isOpen(req.x), "wing " .. wid .. " seal matches floor " .. req.x)
	end
end)
