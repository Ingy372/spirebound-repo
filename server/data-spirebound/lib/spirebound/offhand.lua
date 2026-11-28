-- Off-hand blades (style trees v2, spec 7.3; Jay: "reaver should be able to equip a second weapon to forgo defense in
-- favor of damage"). A shield-hand item our scripts treat as a second weapon: the Tibia client can't hold two weapons,
-- so the base item (the silver dagger, used nowhere else) is made a plain item at build time (tools/build_server.py)
-- and its attack lives on the item. Only a Reaver's off-hand strikes (SpireStyle.offhandShare); for anyone else it is
-- just something held. Clearly weaker than a main weapon: about two thirds of the floor's melee attack.
SpireOffhand = SpireOffhand or {}
SpireOffhand.BASE = 3290 -- silver dagger
SpireOffhand.A_ATTACK = "sb_offhand"
SpireOffhand.SHARE_OF_MAIN = 2 / 3
SpireOffhand.BLADES = {
	-- id, name, floor, attack (two thirds of Floor 1's melee attack 20), price at Weaponsmith Garrick
	{ id = "climbers_dirk", name = "Climber's Dirk", floor = 1, attack = 13, price = 800 },
}

function SpireOffhand.def(id)
	for _, b in ipairs(SpireOffhand.BLADES) do
		if b.id == id then
			return b
		end
	end
end

-- Pure-ish: the off-hand attack written on an item, or nil if it is not an off-hand blade
function SpireOffhand.attackOf(item)
	if not item or not item.getCustomAttribute then
		return nil
	end
	return tonumber(item:getCustomAttribute(SpireOffhand.A_ATTACK))
end

function SpireOffhand.is(item)
	return SpireOffhand.attackOf(item) ~= nil
end

function SpireOffhand.create(id)
	local b = SpireOffhand.def(id)
	local item = b and Game.createItem(SpireOffhand.BASE, 1)
	if not item then
		return nil
	end
	item:setCustomAttribute(SpireOffhand.A_ATTACK, b.attack)
	item:setAttribute(ITEM_ATTRIBUTE_NAME, b.name)
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, string.format("Off-hand blade (Atk:%d), held in the shield hand. A Reaver's off-hand strikes after each melee hit.", b.attack))
	return item
end

-- Pure: the off-hand strike after a melee hit. dealt = the main hit's size; mainAttack / offAttack = the weapons'
-- attack values; share = SpireStyle.offhandShare; twoHanded: a Reaver with a two-handed weapon gets the same share of
-- the main hit instead (spec 7.3). Returns the strike's size (0 = none).
function SpireOffhand.strike(dealt, mainAttack, offAttack, share, twoHanded)
	if share <= 0 or dealt <= 0 then
		return 0
	end
	if twoHanded then
		return math.floor(dealt * share + 0.5)
	end
	if not offAttack or offAttack <= 0 or not mainAttack or mainAttack <= 0 then
		return 0
	end
	return math.floor(dealt * (offAttack / mainAttack) * share + 0.5)
end
