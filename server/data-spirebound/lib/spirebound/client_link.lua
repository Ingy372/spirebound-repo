-- Server -> Spirebound client messages (extended opcode, JSON). Client side: client/modules/game_spirebound.
-- Messages: {t="floor", n, name} {t="difficulty", mode, name} {t="skills", family, list={...}} {t="cast", name, cd}
SpireClient = { OPCODE = 210 }

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
	{ floor = 2, x1 = 2000, y1 = 1000, x2 = 2399, y2 = 1399 },
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
	for _, d in ipairs(SwordSkills.list) do
		if d.family == fam then
			table.insert(list, { name = d.name, words = d.words, cd = d.cd, tag = d.tag })
		end
	end
	return fam or "", list
end

function SpireClient.sendAll(player)
	local n = Floors.at(player:getPosition())
	SpireClient.send(player, { t = "floor", n = n, name = Floors.names[n] or "" })
	local mode = Difficulty.get(player)
	SpireClient.send(player, { t = "difficulty", mode = mode, name = Difficulty.names[mode] or "" })
	local fam, list = SpireClient.skillList(player)
	SpireClient.send(player, { t = "skills", family = fam, list = list })
end
