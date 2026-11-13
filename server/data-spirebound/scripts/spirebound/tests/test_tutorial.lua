-- Roadmap R11: the Arrival Yard's gates, the yard boundary and the Journal's "How do I..." page.
local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

SpireTest.add("tutorial: each gate opens only after its step and the ones before it", function()
	local done = {}
	local function d(s)
		return done[s] == true
	end
	SpireTest.eq((SpireTutorial.gateOpen("kill", d)), false, "gate 1 is shut before a rat falls")
	local _, missing = SpireTutorial.gateOpen("potion", d)
	SpireTest.eq(missing, "kill", "the hint names the first thing still to do")
	done.kill = true
	SpireTest.eq((SpireTutorial.gateOpen("kill", d)), true, "gate 1 opens after the kill")
	SpireTest.eq((SpireTutorial.gateOpen("loot", d)), false, "gate 2 still needs the loot")
	done.loot, done.spells = true, true
	SpireTest.eq((SpireTutorial.gateOpen("spells", d)), true, "gate 3 opens after !spells")
	SpireTest.eq((SpireTutorial.gateOpen("potion", d)), false, "gate 4 needs the potion")
	done.potion = true
	SpireTest.eq((SpireTutorial.gateOpen("potion", d)), true, "the last gate opens")
end)

SpireTest.add("tutorial: the gates stand on the path, and the yard holds the Registrar", function()
	for _, step in ipairs(SpireTutorial.STEPS) do
		for i = 1, 2 do
			local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
			SpireTest.eq(p ~= nil and walkable(p), true, step .. " gate door " .. i .. " is an open door on the path")
		end
	end
	SpireTest.eq(SpireTutorial.inYard(WorldPoints.tutorial_spawn), true, "the spawn is in the yard")
	SpireTest.eq(SpireTutorial.inYard(WorldPoints.tutorial_registrar), true, "the Registrar is in the yard")
	SpireTest.eq(SpireTutorial.inYard(WorldPoints.temple_hearthgate), false, "Hearthgate is not")
	local a, b = WorldPoints.tutorial_gate_kill_1, WorldPoints.tutorial_gate_potion_1
	SpireTest.eq(a.x < b.x and b.x < WorldPoints.tutorial_registrar.x, true, "gates run west to east, the Registrar last")
end)

SpireTest.add("tutorial: the Journal has a How do I page", function()
	local r = SpireJournal.build({}, "howto")
	SpireTest.eq(r and r.title, "How do I...", "the page exists")
	SpireTest.eq(#(r.lines or {}) >= 10, true, "it answers at least ten questions")
end)
