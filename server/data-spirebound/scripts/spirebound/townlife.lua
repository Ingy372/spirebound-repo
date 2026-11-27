-- Hearthgate feels alive (roadmap P3): townsfolk walk about Hearth Plaza (npc/town_*.lua, tools/gen_townsfolk.py)
-- and the fountain sprays now and then when someone is near. Spawned at start-up, so the map file doesn't change.
SpireTownlife = SpireTownlife or { placed = {} }
SpireTownlife.FOUNTAIN = Position(1225, 1268, 7) -- maps/hearthgate_plan.py FOUNTAIN: Hearth Plaza's fountain

local startup = GlobalEvent("SpireTownlifeStartup")
function startup.onStartup()
	for _, f in ipairs(SpireTownsfolk or {}) do
		local spot = SpireQuestObjects.findSpot(f.near, 6, 1, true)
		if spot then
			Game.createNpc(f.name, spot, false, true)
			SpireTownlife.placed[f.name] = spot
		else
			logger.warn("[townlife] no room for {}", f.name)
		end
	end
	return true
end
startup:register()

local spray = GlobalEvent("SpireTownlifeFountain")
function spray.onThink(interval)
	local f = SpireTownlife.FOUNTAIN
	if #Game.getSpectators(f, false, true, 8, 8, 6, 6) > 0 then
		local d = math.random(0, 3)
		local offs = { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 } }
		Position(f.x + offs[d + 1][1], f.y + offs[d + 1][2], f.z):sendMagicEffect(CONST_ME_WATERSPLASH)
	end
	return true
end
spray:interval(4000)
spray:register()
