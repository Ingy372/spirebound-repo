-- P9 (FLOOR1_REVIEW.md F1-20): the things the new Floor 1 quests need, put on the map at start-up so the map file
-- doesn't change: the six builders' stones (The Builders' Stones, Vesper), the old sluice's three levers and the stone
-- that gives their order (The Old Sluice, Fisher Corwin), and Fence Marrow by the Bandit Road (Flour for the Gate).
-- Quest rules: lib/spirebound/quests.lua (kind = "collect" / "deliver").

SpireQuestObjects = SpireQuestObjects or { placed = {} }

local STONE = 2199 -- an obelisk: solid, can't be carried off
local LEVER, LEVER_PULLED = 2772, 2773
local AID_STONE, AID_LEVER, AID_HINT = 47100, 47120, 47130

-- The builders' stones: one per ground, near the ground's third loop. The text is the reward.
SpireQuestObjects.STONES = {
	{ id = "boar_meadow", near = "loop_boar_meadow_b",
		text = "We were the Wardwrights. We did not raise the Spire to reach the sky. We raised it to hold something down." },
	{ id = "wolf_copse", near = "loop_wolf_copse_c",
		text = "Ten floors, ten seals. A keeper guards each seal. When a keeper falls, its seal opens, and the way up with it." },
	{ id = "reed_marsh", near = "loop_reed_marsh_c",
		text = "The river was our road. Stone came down it from the northern quarries, a thousand barges a season, and the sluices fed the mortar pits." },
	{ id = "thornsnap_hollow", near = "loop_thornsnap_hollow_c",
		text = "When the thorns came, we were already leaving. The last of us did not go out. We went up." },
	{ id = "shard_fields", near = "loop_shard_fields_d",
		text = "The shards in this field are what is left of the first seal. It broke before the tower was finished. We built faster after that." },
	{ id = "burrow_hills", near = "loop_burrow_hills_c",
		text = "To whoever climbs: the blue light at the top is not a beacon. It is a warning. We are sorry." },
}

-- The old sluice in Reedmarsh: three levers (left to right: fish, sun, reed); the carved stone says sun, reed, fish.
SpireQuestObjects.SLUICE = {
	near = "loop_reed_marsh_d",
	hint = "loop_reed_marsh_b",
	marks = { "a fish", "a sun", "a reed" },
	order = { 2, 3, 1 },
	hintText = "Carved by the old sluice-keepers: \"First the sun dries the gate, then the reed bends, and last the fish swims free.\"",
}

local function open(pos)
	local t = Tile(pos)
	if not t or not t:getGround() or t:hasFlag(TILESTATE_PROTECTIONZONE) or t:getTopCreature() then
		return false
	end
	if not t:isWalkable(false, false, false, false, true) then
		return false
	end
	return #(t:getItems() or {}) == 0
end

-- open space: the tile and all eight neighbours free, so a solid object never closes a path
local function roomy(pos)
	for dx = -1, 1 do
		for dy = -1, 1 do
			if not open(Position(pos.x + dx, pos.y + dy, pos.z)) then
				return false
			end
		end
	end
	return true
end

-- the nearest roomy tile within r of the centre (rings outward, from distance 2 so the point itself stays clear)
function SpireQuestObjects.findSpot(centre, r, width)
	width = width or 1
	for d = 2, r do
		for dx = -d, d do
			for dy = -d, d do
				if math.max(math.abs(dx), math.abs(dy)) == d then
					local ok = true
					for i = 0, width - 1 do
						if not roomy(Position(centre.x + dx + i, centre.y + dy, centre.z)) then
							ok = false
							break
						end
					end
					if ok then
						return Position(centre.x + dx, centre.y + dy, centre.z)
					end
				end
			end
		end
	end
end

local function put(id, pos, aid, desc)
	local item = Game.createItem(id, 1, pos)
	if item then
		item:setActionId(aid)
		if desc then
			item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, desc)
		end
	end
	return item
end

function SpireQuestObjects.place()
	local placed = {}
	for i, s in ipairs(SpireQuestObjects.STONES) do
		local c = WorldPoints[s.near]
		local spot = c and SpireQuestObjects.findSpot(c, 12)
		if spot then
			put(STONE, spot, AID_STONE + i, "A weathered stone covered in old carving. Use it to read it.")
			placed["stone_" .. s.id] = spot
		else
			logger.warn("[quest objects] no room for the builders' stone in {}", s.id)
		end
	end
	local sl = SpireQuestObjects.SLUICE
	local c = WorldPoints[sl.near]
	local spot = c and SpireQuestObjects.findSpot(c, 10, 3)
	if spot then
		for i = 1, 3 do
			put(LEVER, Position(spot.x + i - 1, spot.y, spot.z), AID_LEVER + i, "An old sluice lever. Its handle is marked with " .. sl.marks[i] .. ".")
		end
		placed.sluice = spot
	else
		logger.warn("[quest objects] no room for the sluice levers")
	end
	local h = WorldPoints[sl.hint]
	local hspot = h and SpireQuestObjects.findSpot(h, 8)
	if hspot then
		put(STONE, hspot, AID_HINT, "A stone carved by the old sluice-keepers. Use it to read it.")
		placed.sluice_hint = hspot
	end
	local gate = WorldPoints.camp_bandit_road
	local mspot = gate and SpireQuestObjects.findSpot(gate, 6)
	if mspot then
		Game.createNpc("Fence Marrow", mspot, false, true)
		placed.marrow = mspot
	end
	SpireQuestObjects.placed = placed
	for k, pos in pairs(placed) do -- (the autopilot routes read these from the server log)
		logger.info("[quest objects] {} at {}, {}, {}", k, pos.x, pos.y, pos.z)
	end
	return placed
end

local startup = GlobalEvent("SpireQuestObjectsStartup")
function startup.onStartup()
	SpireQuestObjects.place()
	return true
end
startup:register()

-- reading a stone
local stones = Action()
function stones.onUse(player, item)
	local s = SpireQuestObjects.STONES[item:getActionId() - AID_STONE]
	if not s then
		return false
	end
	player:showTextDialog(STONE, s.text)
	if SpireQuests.find(player, "builders", s.id) then
		local n = SpireQuests.collectedCount(player, "builders")
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You read a builders' stone (%d of 6). Vesper in Hearthgate buys stories like this.", n))
		item:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	end
	return true
end
for i = 1, #SpireQuestObjects.STONES do
	stones:aid(AID_STONE + i)
end
stones:register()

local hint = Action()
function hint.onUse(player, item)
	player:showTextDialog(STONE, SpireQuestObjects.SLUICE.hintText)
	return true
end
hint:aid(AID_HINT)
hint:register()

-- the sluice: pulls are remembered per player; a wrong lever resets all three
local pulls = {}
SpireCleanup.add(function(pid) pulls[pid] = nil end)

local function resetLevers(base)
	addEvent(function()
		for i = 1, 3 do
			local t = Tile(Position(base.x + i - 1, base.y, base.z))
			local l = t and t:getItemById(LEVER_PULLED)
			if l then
				l:transform(LEVER)
			end
		end
	end, 2000)
end

-- Pure: given the levers pulled so far and the next one, what happens? ("next", "wrong" or "solved")
function SpireQuestObjects.pull(sofar, lever)
	local order = SpireQuestObjects.SLUICE.order
	local want = order[#sofar + 1]
	if lever ~= want then
		return "wrong"
	end
	return #sofar + 1 == #order and "solved" or "next"
end

local levers = Action()
function levers.onUse(player, item)
	local n = item:getActionId() - AID_LEVER
	if n < 1 or n > 3 then
		return false
	end
	local base = SpireQuestObjects.placed.sluice
	if item:getId() == LEVER then
		item:transform(LEVER_PULLED)
	end
	local pid = player:getId()
	local sofar = pulls[pid] or {}
	local result = SpireQuestObjects.pull(sofar, n)
	if result == "wrong" then
		pulls[pid] = nil
		player:sendTextMessage(MESSAGE_STATUS, "The levers clank back into place. That was not the order.")
		if base then
			resetLevers(base)
		end
		return true
	end
	table.insert(sofar, n)
	pulls[pid] = sofar
	if result == "next" then
		player:sendTextMessage(MESSAGE_STATUS, "The lever locks with a heavy clunk.")
		return true
	end
	pulls[pid] = nil
	if base then
		resetLevers(base)
	end
	item:getPosition():sendMagicEffect(CONST_ME_WATERSPLASH)
	if SpireQuests.find(player, "sluice", "gate") then
		player:addMoney(600)
		if SpireGearData and SpireGearData.tokens and SpireGearData.tokens[1] then
			player:addItem(SpireGearData.tokens[1].rough, 1)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The sluice gate grinds open and the water drains away. In the mud lies an old strongbox: 600 gold and a rough Hearth Shard.")
	else
		player:sendTextMessage(MESSAGE_STATUS, "The sluice gate grinds open, but the strongbox beneath is already empty.")
	end
	return true
end
for i = 1, 3 do
	levers:aid(AID_LEVER + i)
end
levers:register()
