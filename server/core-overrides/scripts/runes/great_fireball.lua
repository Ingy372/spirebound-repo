-- Canary 3.6.1's great fireball rune (Spirebound's "fire rune", conjured by Arcanists), copied over data/scripts/runes/
-- by tools/build_server.py. One change (roadmap J15b / FD2b): where it bursts, fire burns vine walls (the Mystic's
-- wild growth and Thornsnap Hollow's vine walls), the same as Spirebound's fire spells.
local combat = Combat()
combat:setParameter(COMBAT_PARAM_TYPE, COMBAT_FIREDAMAGE)
combat:setParameter(COMBAT_PARAM_EFFECT, CONST_ME_FIREAREA)
combat:setParameter(COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_FIRE)
combat:setArea(createCombatArea(AREA_CIRCLE3X3))

function onGetFormulaValues(player, level, maglevel)
	local min = (level / 5) + (maglevel * 1.2) + 7
	local max = (level / 5) + (maglevel * 2.8) + 17
	return -min, -max
end

combat:setCallback(CALLBACK_PARAM_LEVELMAGICVALUE, "onGetFormulaValues")

-- the tiles of AREA_CIRCLE3X3 around the burst: a 5 x 5 square without its four corners
local function burstTiles(center)
	local out = {}
	for dx = -2, 2 do
		for dy = -2, 2 do
			if not (math.abs(dx) == 2 and math.abs(dy) == 2) then
				table.insert(out, Position(center.x + dx, center.y + dy, center.z))
			end
		end
	end
	return out
end

local rune = Spell("rune")

function rune.onCastSpell(creature, var, isHotkey)
	local center = var:getPosition()
	if (not center or center.x == 0) and var:getNumber() ~= 0 then
		local target = Creature(var:getNumber())
		center = target and target:getPosition() or center
	end
	local ok = combat:execute(creature, var)
	if ok and center and center.x ~= 0 and SpireSpells and SpireSpells.burnVines then
		for _, pos in ipairs(burstTiles(center)) do
			SpireSpells.burnVines(pos)
		end
	end
	return ok
end

rune:id(16)
rune:group("attack")
rune:name("great fireball rune")
rune:castSound(SOUND_EFFECT_TYPE_SPELL_OR_RUNE)
rune:impactSound(SOUND_EFFECT_TYPE_SPELL_GREAT_FIREBALL_RUNE)
rune:runeId(3191)
rune:allowFarUse(true)
rune:charges(4)
rune:level(30)
rune:magicLevel(4)
rune:cooldown(2 * 1000)
rune:groupCooldown(2 * 1000)
rune:isBlocking(false) -- True = Solid / False = Creature
rune:register()
