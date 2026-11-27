-- Treasure maps (roadmap AD5; adventure design 4.5). A "Tattered map" drops from bandits and ruin guards (1%) and Bandit
-- Captains (10%). Using it picks one of 24 dig spots in the level 12-30 grounds (kept on the map, so it can be traded)
-- and reads a clue: the ground, a real landmark next to the spot, and where it lies from the ground's rest camp. Using it
-- again inside that ground says how close you are ("far to the north-east", "close", "right here"). Then dig with a
-- shovel (General Store): gold worth 5-10 minutes of that ground, a chance of shards and a Beacon Ember, a 4% keepsake
-- (six house pieces) with the shards' pity rule, and half the time 2-3 guards rise from the hole. Ten maps dug: the
-- title "Treasure Hunter".
-- The dig spots are placed at start-up from walkable points (as quest_objects.lua does), so the map file never changes.
-- Numbers: tools/gen_adventure.py. The game side: scripts/spirebound/treasure_maps.lua.
SpireTreasure = SpireTreasure or { spots = {}, byKey = {} }

local D = SpireAdventureData
local DIG_Z = 7 -- spots lie on the ground's main level, where the clue's landmarks are

-- ---------------------------------------------------------------- pure
-- Pure: compass direction from a step (dx east, dy south)
function SpireTreasure.direction(dx, dy)
	if dx == 0 and dy == 0 then
		return "here"
	end
	local ax, ay = math.abs(dx), math.abs(dy)
	local ns = dy < 0 and "north" or "south"
	local ew = dx > 0 and "east" or "west"
	if ax > 2 * ay then
		return ew
	elseif ay > 2 * ax then
		return ns
	end
	return ns .. "-" .. ew
end

-- Pure: the warmer/colder line for a player standing dx, dy away from the spot
function SpireTreasure.hint(dx, dy)
	local d = math.max(math.abs(dx), math.abs(dy))
	local dir = SpireTreasure.direction(dx, dy)
	if d <= 1 then
		return "Right here! Dig with a shovel."
	elseif d <= 4 then
		return "Very close now, just to the " .. dir .. "."
	elseif d <= 10 then
		return "Close. Keep going " .. dir .. "."
	end
	return "Far to the " .. dir .. "."
end

-- Pure: gold for a dig in this ground; roll in [0, 1]
function SpireTreasure.gold(gid, roll)
	local g = D.digs[gid].gold
	return math.floor(g[1] + (g[2] - g[1]) * roll + 0.5)
end

-- Pure: which keepsake (index) a lucky dig gives: one the character lacks first. have = { [id] = true }; rand(n) 1..n
function SpireTreasure.pickKeepsake(have, rand)
	local missing = {}
	for i, k in ipairs(D.treasureKeepsakes) do
		if not have[k.id] then
			table.insert(missing, i)
		end
	end
	if #missing == 0 then
		return rand(#D.treasureKeepsakes)
	end
	return missing[rand(#missing)]
end

-- ---------------------------------------------------------------- placing the 24 spots (start-up)
local BORING = { [""] = true, grass = true, earth = true, dirt = true, ["dirt floor"] = true, gravel = true, sand = true }

local function openTile(pos)
	local t = Tile(pos)
	if not t or not t:getGround() or t:hasFlag(TILESTATE_PROTECTIONZONE) or t:hasFlag(TILESTATE_HOUSE) then
		return false
	end
	if not t:isWalkable(false, false, false, false, true) then
		return false
	end
	return #(t:getItems() or {}) == 0
end

-- the nearest thing worth naming next to a spot (a tree, a rock, a cart...), as "a fir tree"
local function landmark(pos)
	for d = 1, 3 do
		for dx = -d, d do
			for dy = -d, d do
				if math.max(math.abs(dx), math.abs(dy)) == d then
					local t = Tile(Position(pos.x + dx, pos.y + dy, pos.z))
					for _, it in ipairs(t and t:getItems() or {}) do
						local ty = ItemType(it:getId())
						local name = ty:getName()
						if not BORING[name] and not ty:isMovable() and name ~= "" then
							local art = ty:getArticle()
							return (art ~= "" and (art .. " ") or "") .. name
						end
					end
				end
			end
		end
	end
	return nil
end

local function caveAt(gid, pos)
	for _, c in ipairs(SpireWilds.caves or {}) do
		if c.id == gid and pos.z == c.z and pos.x >= c.x1 and pos.x <= c.x2 and pos.y >= c.y1 and pos.y <= c.y2 then
			return true
		end
	end
	return false
end

-- candidate anchors of a ground, in a fixed order (the same spots every start while the map stays the same)
local function anchors(gid)
	local out = {}
	for _, l in ipairs({ "a", "b", "c", "d", "e", "f" }) do
		local p = WorldPoints["loop_" .. gid .. "_" .. l]
		if p then
			table.insert(out, p)
		end
	end
	for _, name in ipairs({ "chest_" .. gid, "centre_" .. gid }) do
		if WorldPoints[name] then
			table.insert(out, WorldPoints[name])
		end
	end
	return out
end

local function spotNear(gid, anchor, taken)
	local gate = WorldPoints["gate_" .. gid]
	local camp = WorldPoints["camp_" .. gid]
	for d = 2, 7 do
		for dx = -d, d do
			for dy = -d, d do
				if math.max(math.abs(dx), math.abs(dy)) == d then
					local p = Position(anchor.x + dx, anchor.y + dy, DIG_Z)
					local far = true
					for _, q in ipairs(taken) do
						if math.max(math.abs(q.x - p.x), math.abs(q.y - p.y)) < 8 then
							far = false
							break
						end
					end
					local fromGate = not gate or math.max(math.abs(p.x - gate.x), math.abs(p.y - gate.y)) >= 8
					local fromCamp = not camp or math.max(math.abs(p.x - camp.x), math.abs(p.y - camp.y)) >= 4
					if far and fromGate and fromCamp and SpireRoamers.groundAt(p) == gid and not caveAt(gid, p)
						and openTile(p) and landmark(p) then
						return p
					end
				end
			end
		end
	end
end

function SpireTreasure.clue(spot)
	local g = SpireRoamers.ground(spot.gid)
	local title = g and g.title or spot.gid
	local camp = WorldPoints["camp_" .. spot.gid]
	local where = ""
	if camp then
		local dx, dy = spot.pos.x - camp.x, spot.pos.y - camp.y
		where = string.format(", about %d paces %s of the rest camp", math.max(math.abs(dx), math.abs(dy)),
			SpireTreasure.direction(dx, dy))
	end
	return string.format("%s: dig beside %s%s.", title, spot.landmark or "open ground", where)
end

function SpireTreasure.place()
	SpireTreasure.spots, SpireTreasure.byKey = {}, {}
	for _, gid in ipairs({ "burrow_hills", "wolf_copse", "reed_marsh", "bramble_run", "thornsnap_hollow",
		"shard_fields", "bandit_road", "smugglers_ridge", "old_quarry", "fallen_bastion" }) do
		local want = D.digs[gid] and D.digs[gid].spots or 0
		local taken = {}
		for _, a in ipairs(anchors(gid)) do
			if #taken >= want then
				break
			end
			local p = spotNear(gid, a, taken)
			if p then
				table.insert(taken, p)
				local s = { key = gid .. ":" .. #taken, gid = gid, pos = p, landmark = landmark(p) }
				s.clue = SpireTreasure.clue(s)
				table.insert(SpireTreasure.spots, s)
				SpireTreasure.byKey[s.key] = s
			end
		end
		if #taken < want then
			logger.warn("[Spirebound] treasure maps: only {} of {} dig spots fit in {}", #taken, want, gid)
		end
	end
	return #SpireTreasure.spots
end

-- the spot whose tile this is (a step either way still counts: clicking the exact tile is fiddly)
function SpireTreasure.spotAt(pos)
	for _, s in ipairs(SpireTreasure.spots) do
		if s.pos.z == pos.z and math.max(math.abs(s.pos.x - pos.x), math.abs(s.pos.y - pos.y)) <= 1 then
			return s
		end
	end
end

-- ---------------------------------------------------------------- the character
local function kv(player)
	return player:kv():scoped("spirebound-treasure")
end

function SpireTreasure.dug(player)
	return kv(player):get("dug") or 0
end

function SpireTreasure.keepsakes(player)
	local out = {}
	for _, k in ipairs(D.treasureKeepsakes) do
		if kv(player):get("keepsake_" .. k.id) then
			out[k.id] = true
		end
	end
	return out
end
