-- The gear ladder in the game (roadmap R12). Table: lib/spirebound/gear.lua (tools/gen_gear.py).
-- Rare drops on the floors' harder monsters, quest pieces from the hand-written quest lines (lib/spirebound/quests.lua),
-- and the boss piece, which the floor boss drops for its top fighter.

-- Pure: the piece for a vocation (base id 1-4, promotions count as their base), floor and source
function SpireGear.find(vocation, floor, source)
	for _, g in ipairs(SpireGear.list) do
		if g.vocation == vocation and g.floor == floor and g.source == source then
			return g
		end
	end
end

-- Make a piece: its own name and its bonus on top of the base item. `into` is a player or a container.
function SpireGear.make(into, piece)
	local item = into:addItem(piece.base, 1)
	if not item then
		return nil
	end
	item:setAttribute(ITEM_ATTRIBUTE_NAME, piece.name)
	local it = ItemType(piece.base)
	if piece.kind == "attack" then
		item:setAttribute(ITEM_ATTRIBUTE_ATTACK, it:getAttack() + piece.bonus)
	else
		item:setAttribute(ITEM_ATTRIBUTE_ARMOR, it:getArmor() + piece.bonus)
	end
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, string.format("Spirebound gear, Floor %d (%s).", piece.floor,
		({ drop = "a rare find", quest = "a quest reward", boss = "the floor's best" })[piece.source]))
	return item
end

function SpireGear.give(player, floor, source)
	local voc = player:getVocation():getBaseId()
	local piece = SpireGear.find(voc, floor, source)
	if not piece then
		return nil
	end
	local item = SpireGear.make(player, piece)
	if item then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You received " .. piece.name .. ".")
	end
	return item
end

local function floorOfDropper(name)
	for floor, list in pairs(SpireGear.dropFrom) do
		for _, n in ipairs(list) do
			if n == name then
				return floor
			end
		end
	end
end

-- rare drops, and the boss piece for the top fighter
local drops = EventCallback("SpireGearDrops")
function drops.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	if not owner or not corpse:isContainer() then
		return
	end
	local name = monster:getName()
	local floor = floorOfDropper(name)
	if floor and math.random() < SpireGear.DROP_CHANCE then
		local piece = SpireGear.find(math.random(1, 4), floor, "drop")
		if piece then
			SpireGear.make(corpse, piece)
		end
	end
	for f, boss in pairs(SpireGear.bosses) do
		if boss == name then
			local top = SpireGear.lastTopFighter and SpireGear.lastTopFighter[name]
			local p = top and Player(top) or owner
			local piece = SpireGear.find(p:getVocation():getBaseId(), f, "boss")
			if piece then
				SpireGear.make(corpse, piece)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, name .. " dropped " .. piece.name .. " for you, its fiercest foe.")
			end
		end
	end
end
drops:register()
