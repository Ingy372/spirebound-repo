-- Waycrystals (Jay's idea, 2026-11-26; DESIGN.md 3.7, Q95). Data: crystals_data.lua (tools/crystals.py via
-- tools/balance.py). The game side is scripts/spirebound/waycrystal.lua; the rules here are pure so they can be tested.

SpireCrystals = SpireCrystals or {}
SpireCrystals.WINDOW = 7301 -- the menu's window id (fixed, so tests can answer it)

-- Pure: why a crystal may not be used now, or nil. s = { zone, tutorial, cave, fight, floorOpen }
function SpireCrystals.refusal(s)
	if s.tutorial then
		return "The crystal stays dark until you have chosen your path at the Registrar."
	end
	if s.zone == "bossroom" or s.zone == "arena" or s.zone == "siege" or s.zone == "deadzone" then
		return "The tower's magic is too strong here: the crystal won't work."
	end
	if s.cave then
		return "The crystal won't work this deep in a party cave."
	end
	if s.fight then
		return "You can't use a Waycrystal in a fight. Get clear first."
	end
	if not s.floorOpen then
		return "That floor is still sealed: its crystal won't work yet."
	end
	return nil
end

-- Pure: the menu for a floor and a level: the town first, then each ground whose band the level has reached.
-- Returns { { text, pos = {x, y, z} or nil (= the town), id } ... }
function SpireCrystals.choices(floor, level, townName)
	local out = { { text = townName, id = "town" } }
	for _, g in ipairs((SpireCrystalData.grounds or {})[floor] or {}) do
		if level >= g.lo then
			table.insert(out, { text = string.format("%s (levels %d-%d)", g.title, g.lo, g.hi), pos = g.pos, id = g.id })
		end
	end
	return out
end

-- Is this position inside a walled ground's party cave (below its surface)?
function SpireCrystals.inCave(pos)
	if pos.z <= 7 then
		return false
	end
	for _, g in ipairs((SpireWilds and SpireWilds.grounds) or {}) do
		if g.zs and g.zs[pos.z] and pos.x >= g.x1 and pos.x <= g.x2 and pos.y >= g.y1 and pos.y <= g.y2 then
			return true
		end
	end
	return false
end

function SpireCrystals.townPos(def)
	return WorldPoints[def.town]
end
