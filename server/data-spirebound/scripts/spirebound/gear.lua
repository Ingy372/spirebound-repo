-- Gear in the game: rare alternative weapons from each floor's harder monsters (gear progression spec 4.5).
-- Rules: lib/spirebound/gear.lua. Data: lib/spirebound/gear_data.lua (tools/gen_gear.py).

local function floorOfDropper(name)
	for floor, list in pairs(SpireGearData.dropFrom) do
		for _, n in ipairs(list) do
			if n == name then
				return floor
			end
		end
	end
end

local drops = EventCallback("SpireGearDrops")
function drops.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	if not owner or not corpse:isContainer() then
		return
	end
	local floor = floorOfDropper(monster:getName())
	if floor and math.random() < SpireGearData.DROP_CHANCE then
		local d = SpireGear.find(math.random(1, 4), floor, "drop", "weapon")
		if d then
			SpireGear.make(corpse, d.id)
		end
	end
end
drops:register()
