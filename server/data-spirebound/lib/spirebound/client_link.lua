-- Server -> Spirebound client messages (extended opcode, JSON). Client side: client/modules/game_spirebound.
-- Messages: {t="floor", n, name} {t="difficulty", mode, name} {t="skills", family, list={...}} {t="cast", name, cd}
SpireClient = { OPCODE = 210, CLIENT_VERSION = 3 } -- CLIENT_VERSION: see scripts/spirebound/client_version.lua

local function encode(v)
	local t = type(v)
	if t == "table" then
		if #v > 0 or next(v) == nil then
			local parts = {}
			for _, x in ipairs(v) do
				table.insert(parts, encode(x))
			end
			return "[" .. table.concat(parts, ",") .. "]"
		end
		local parts = {}
		for k, x in pairs(v) do
			table.insert(parts, string.format("%q:%s", tostring(k), encode(x)))
		end
		table.sort(parts)
		return "{" .. table.concat(parts, ",") .. "}"
	elseif t == "string" then
		return '"' .. v:gsub('[%c"\\]', function(c)
			return string.format("\\u%04x", c:byte())
		end) .. '"'
	elseif t == "number" then
		return tostring(v)
	elseif t == "boolean" then
		return v and "true" or "false"
	end
	return "null"
end
SpireClient.encode = encode

function SpireClient.send(player, msg)
	return player:sendExtendedOpcode(SpireClient.OPCODE, encode(msg))
end

-- Which floor is a position on? (coordinate plan: maps/layout_floor1.py)
Floors.areas = {
	{ floor = 1, x1 = 1000, y1 = 1000, x2 = 1399, y2 = 1399 },
	-- floors 2-10 are added by lib/spirebound/floor_content.lua
}
function Floors.at(pos)
	for _, a in ipairs(Floors.areas) do
		if pos.x >= a.x1 and pos.x <= a.x2 and pos.y >= a.y1 and pos.y <= a.y2 then
			return a.floor
		end
	end
	return 0
end

function SpireClient.skillList(player)
	local fam = SwordSkills.heldFamily(player)
	local list = {}
	if player:getVocation():getId() == 0 then
		return fam or "", list -- weapon skills need a path: before the Registrar the bar stays empty (Grok session 2)
	end
	local twin = SwordSkills.hasTwinFang(player)
	for _, d in ipairs(SwordSkills.list) do
		if d.family == fam and (d.level or 1) <= player:getLevel() and (not d.twinFang or twin) then
			table.insert(list, { name = d.name, words = d.words, cd = d.cd, tag = d.tag })
		end
	end
	return fam or "", list
end

-- The floor label's place name: the floor's own name, or a named place on it (C3, Claude's playtest 2026-11-25: the
-- Proving, a hall under the Registrar, was labelled "Hearthgate Plains").
function SpireClient.placeName(pos)
	if SpireTutorial and SpireTutorial.inYard(pos) then
		return "Arrival Yard"
	end
	local lo, hi = WorldPoints.proving_pit_1_nw, WorldPoints.proving_pit_3_se
	local top = WorldPoints.proving_skip
	if lo and hi and top and pos.z == lo.z and pos.x >= lo.x - 8 and pos.x <= hi.x + 8 and pos.y >= top.y - 8 and pos.y <= hi.y + 2 then
		return "The Proving"
	end
	return Floors.names[Floors.at(pos)] or ""
end

function SpireClient.sendFloor(player)
	local pos = player:getPosition()
	local n, name = Floors.at(pos), SpireClient.placeName(pos)
	SpireClient.send(player, { t = "floor", n = n, name = name })
	return n .. "|" .. name
end

function SpireClient.sendAll(player)
	SpireClient.sendFloor(player)
	local mode = Difficulty.get(player)
	SpireClient.send(player, { t = "difficulty", mode = mode, name = Difficulty.names[mode] or "" })
	local fam, list = SpireClient.skillList(player)
	SpireClient.send(player, { t = "skills", family = fam, list = list })
end

-- Each path's first attack spell and heal (G1, Grok playtest 2026-11-24). The client puts them on action bar 1,
-- buttons 3 and 4 (where the stock client left three Tibia spell words), once per character.
SpireClient.FIRST_SPELLS = {
	[4] = { "heavy strike", "second wind" },
	[3] = { "piercing shot", "field dressing" },
	[1] = { "ember strike", "mending spark" },
	[2] = { "frost strike", "dewfall" },
}

function SpireClient.seedSpellBar(player, force)
	local base = player:getVocation():getBaseId()
	local list = SpireClient.FIRST_SPELLS[base]
	local kv = player:kv():scoped("spirebound-notices")
	if not list or (kv:get("spellbar") == true and not force) then
		return false
	end
	kv:set("spellbar", true)
	SpireClient.send(player, { t = "spellbar", list = list })
	return true
end

