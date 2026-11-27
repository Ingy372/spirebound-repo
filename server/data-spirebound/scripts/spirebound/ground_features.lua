-- The Floor 1 ground features in the game (roadmap FD2). Rules and numbers: lib/spirebound/ground_features.lua and
-- tools/gen_depth.py; the spots: maps/floor1_features.py. Every object a feature uses carries an action id in
-- 47201-47216 and cannot be moved (playerOnMoveItem below).
local F = SpireFeatures
local A = F.AID
local cool = F.cool
local st = F.state

local function now()
	return os.time()
end

local function say(player, text)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
end

local function P(p)
	return p and Position(p.x, p.y, p.z) or nil
end

local function topItem(pos, id)
	local t = pos and Tile(pos)
	if not t then
		return nil
	end
	for _, it in ipairs(t:getItems() or {}) do
		if not id or it:getId() == id then
			return it
		end
	end
end

local function tagPoint(name, aid, id, desc)
	local it = topItem(P(WorldPoints[name]), id)
	if it then
		it:setActionId(aid)
		if desc then
			it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, desc)
		end
		-- a grass-edge piece the map laid over the object is what the client clicks first (client test 2026-11-27):
		-- it carries the same action
		local t = Tile(it:getPosition())
		for _, other in ipairs(t and t:getItems() or {}) do
			if other ~= it and not ItemType(other:getId()):isPickupable() and other:getActionId() == 0 then
				other:setActionId(aid)
			end
		end
	end
	return it
end

local function spawn(name, pos, near)
	local m = Game.createMonster(name, pos, true, true)
	if m and near then
		m:addTarget(near, true)
		m:selectTarget(near)
	end
	return m
end

local function groundRect(gid)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == gid then
			return g
		end
	end
end

-- monsters of the given names standing in a ground on level z
local function monstersIn(gid, z, names)
	local g = groundRect(gid)
	if not g then
		return {}
	end
	local cx, cy = math.floor((g.x1 + g.x2) / 2), math.floor((g.y1 + g.y2) / 2)
	local rx, ry = math.ceil((g.x2 - g.x1) / 2) + 1, math.ceil((g.y2 - g.y1) / 2) + 1
	local out = {}
	for _, c in ipairs(Game.getSpectators(Position(cx, cy, z), false, false, rx, rx, ry, ry) or {}) do
		if c:isMonster() and (not names or names[c:getName()]) and not c:getMaster() then
			table.insert(out, c)
		end
	end
	return out
end

local function cooldown(player, key, secs)
	local k = player:getGuid() .. ":" .. key
	local ok, left = F.ready(cool, k, now())
	if not ok then
		return false, left
	end
	cool[k] = now() + secs
	return true
end

local function removeLater(list, secs)
	local ids = {}
	for _, m in ipairs(list) do
		table.insert(ids, m:getId())
	end
	addEvent(function()
		for _, id in ipairs(ids) do
			local m = Monster(id)
			if m then
				m:getPosition():sendMagicEffect(CONST_ME_POFF)
				m:remove()
			end
		end
	end, secs * 1000)
end

-- the nearest walkable tile round `pos` that is not water (to put someone ashore)
local function dryNear(pos, avoid)
	for r = 1, 4 do
		for dx = -r, r do
			for dy = -r, r do
				local p = Position(pos.x + dx, pos.y + dy, pos.z)
				local t = Tile(p)
				if t and t:getGround() and not (avoid and avoid[p.x .. "," .. p.y]) and not t:hasFlag(TILESTATE_BLOCKSOLID)
					and not t:hasProperty(CONST_PROP_BLOCKSOLID) and not t:getTopCreature() then
					return p
				end
			end
		end
	end
	return pos
end

-- ================================================================ Ratwarren: the Ratcatcher's Bell
local bell = Action()
function bell.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("starter_west", "bell")
	local ok, left = cooldown(player, "bell", c.cooldown)
	if not ok then
		say(player, string.format("The bell is still humming. The rats will answer again in about %d minutes.", F.minutes(left)))
		return true
	end
	item:getPosition():sendMagicEffect(CONST_ME_SOUND_YELLOW)
	player:say("DONG! DONG! DONG!", TALKTYPE_MONSTER_SAY, false, nil, item:getPosition())
	local start = SpireWilds and WorldPoints["loop_starter_west_a"] or player:getPosition()
	local rats = {}
	for i = 1, c.rats do
		local m = spawn(c.monster, Position(start.x + math.random(-2, 2), start.y + math.random(-2, 2), start.z), player)
		if m then
			table.insert(rats, m)
		end
	end
	removeLater(rats, c.seconds)
	say(player, string.format("The walls squeal: %d rats pour out up the north-west loop for a minute!", #rats))
	F.lore(player, "starter_west")
	return true
end
bell:aid(A.bell)
bell:register()

-- ================================================================ Toad Pond: the night lilies
st.lilies = st.lilies or { up = false, ground = {}, toads = {} }
local function liliesUp(up)
	local L = st.lilies
	if L.up == up then
		return
	end
	local path = F.points("feat_lily_")
	-- the path's tiles, the shore it starts from and the island tiles: shoreline pieces and reeds on them are solid, so
	-- they are lifted off at night and put back at dawn (client test 2026-11-27)
	local clearTiles = {}
	for _, p in ipairs(path) do
		table.insert(clearTiles, p)
	end
	for _, name in ipairs({ "feat_lily_shore", "feat_island", "feat_island_2" }) do
		if WorldPoints[name] then
			table.insert(clearTiles, WorldPoints[name])
		end
	end
	local isle1 = WorldPoints.feat_island
	if isle1 then -- the island tile next to the path's last pad
		local last = path[#path]
		table.insert(clearTiles, { x = last and last.x - 1 or isle1.x, y = last and last.y or isle1.y, z = isle1.z })
	end
	if up then
		L.lifted = {}
		for _, p in ipairs(clearTiles) do
			local t = Tile(P(p))
			for _, it in ipairs(t and t:getItems() or {}) do
				local id = it:getId()
				if id ~= 39548 and not ItemType(id):isPickupable() and ItemType(id):isBlocking() then
					table.insert(L.lifted, { x = p.x, y = p.y, z = p.z, id = id })
					it:remove()
				end
			end
		end
		for _, p in ipairs(path) do
			local t = Tile(P(p))
			if t and t:getGround() then
				L.ground[p.x .. "," .. p.y] = t:getGround():getId()
				t:getGround():transform(17238) -- dark mud under the pads (swamp ground is "avoid": the client will not path over it)
				Game.createItem(39548, 1, P(p))
				P(p):sendMagicEffect(CONST_ME_GREEN_RINGS)
			end
		end
		local c = F.conf("starter_east", "lilies")
		for _, name in ipairs({ "feat_island", "feat_island_2" }) do
			local m = WorldPoints[name] and spawn(c.monster, P(WorldPoints[name]))
			if m then
				table.insert(L.toads, m:getId())
			end
		end
	else
		local shore = dryNear(P(WorldPoints.feat_lily_shore))
		local onIt = {}
		for _, p in ipairs(path) do
			onIt[p.x .. "," .. p.y] = true
		end
		for _, name in ipairs({ "feat_island", "feat_island_2" }) do
			local p = WorldPoints[name]
			if p then
				onIt[p.x .. "," .. p.y] = true
			end
		end
		-- anyone on the path or the island is helped ashore before the lilies sink
		for key in pairs(onIt) do
			local x, y = key:match("(%d+),(%d+)")
			local t = Tile(Position(tonumber(x), tonumber(y), shore.z))
			for _, c in ipairs(t and t:getCreatures() or {}) do
				if c:isPlayer() then
					c:teleportTo(shore)
					c:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Dawn: the lilies sink, and you wade back to the shore.")
				elseif c:isMonster() then
					c:remove()
				end
			end
		end
		for _, p in ipairs(path) do
			local it = topItem(P(p), 39548)
			if it then
				it:remove()
			end
			local t = Tile(P(p))
			local was = L.ground[p.x .. "," .. p.y]
			if t and t:getGround() and was then
				t:getGround():transform(was)
			end
		end
		for _, rec in ipairs(L.lifted or {}) do
			Game.createItem(rec.id, 1, Position(rec.x, rec.y, rec.z))
		end
		L.lifted = {}
		for _, id in ipairs(L.toads) do
			local m = Monster(id)
			if m then
				m:remove()
			end
		end
		L.toads = {}
	end
	L.up = up
end
F.liliesUp = liliesUp

-- the night fishing spot: fishing there gets the rare fish three times as often (read by the fishing script's luck)
function F.fishingLuck(pos)
	local p = WorldPoints.feat_nightfish
	if p and st.lilies.up and pos and pos.z == p.z and math.max(math.abs(pos.x - p.x), math.abs(pos.y - p.y)) <= 1 then
		return F.conf("starter_east", "lilies").luck
	end
	return 1
end

-- the island counts as using the feature
local isle = MoveEvent()
function isle.onStepIn(creature, item, position, fromPosition)
	if creature:isPlayer() and st.lilies.up then
		F.lore(creature, "starter_east")
	end
	return true
end
isle:type("stepin")
isle:aid(47217)
isle:register()

-- ================================================================ Sproutling Glade: seedlings
local function growSeedling(pos, itemId)
	local it = topItem(pos, itemId)
	if not it or it:getActionId() ~= A.seedling then
		return
	end
	it:remove()
	local c = F.conf("starter_south", "seedling")
	pos:sendMagicEffect(CONST_ME_SMALLPLANTS)
	spawn(c.elder, pos)
end

local seedling = Action()
function seedling.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	item:getPosition():sendMagicEffect(CONST_ME_POFF)
	item:remove()
	say(player, "You stamp the seedling flat before it can take root.")
	F.lore(player, "starter_south")
	return true
end
seedling:aid(A.seedling)
seedling:register()

-- ================================================================ deaths: seedlings, elders, the lieutenant, the queen
local deaths = EventCallback("SpireFeatureDeaths")
function deaths.monsterOnDropLoot(monster, corpse)
	local name = monster:getName()
	local pos = monster:getPosition()
	if name == "Sproutling" and SpireRoamers.groundAt(pos) == "starter_south" then
		local c = F.conf("starter_south", "seedling")
		if math.random() < c.chance then
			local tile = Tile(pos)
			if tile and not tile:hasFlag(TILESTATE_PROTECTIONZONE) then
				local it = Game.createItem(c.item, 1, pos)
				if it then
					it:setActionId(A.seedling)
					it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A sproutling seedling, already reaching for the light. Stamp it out (use it), or it will grow.")
					local p, id = Position(pos.x, pos.y, pos.z), c.item
					addEvent(growSeedling, c.grow * 1000, p, id)
				end
			end
		end
	end
	local owner = Player(corpse:getCorpseOwner())
	if owner then
		if name == "Elder Sproutling" then
			F.lore(owner, "starter_south")
		elseif name == "Nest Queen" then
			F.lore(owner, "wasp_fields")
		elseif name == "Bandit Lieutenant" then
			st.lieutenant = nil
			say(owner, "The Bandit Lieutenant is down. Bring his badge to the wanted poster by the Bandit Road's gate.")
		end
	end
	if name == "Bandit Lieutenant" then
		st.lieutenant = nil
	end
end
deaths:register()

-- ================================================================ Waspgrass Fields: nests
local TORCHES = { 2920, 2921, 2922, 2923, 2924, 2925, 2926 }
local function hasTorch(player)
	for _, id in ipairs(TORCHES) do
		if player:getItemCount(id) > 0 then
			return true
		end
	end
	return false
end
F.hasTorch = hasTorch

local nest = Action()
function nest.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("wasp_fields", "nests")
	if item:getCustomAttribute("burnt_until") and item:getCustomAttribute("burnt_until") > now() then
		say(player, "A burnt-out nest. The wasps will build it again before long.")
		return true
	end
	if not hasTorch(player) then
		say(player, "A wasp nest the size of a barrel, humming. A lit torch would smoke them out (the General Store sells torches).")
		return true
	end
	local pos = item:getPosition()
	pos:sendMagicEffect(CONST_ME_FIREAREA)
	item:setCustomAttribute("burnt_until", now() + c.regrow)
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A burnt-out wasp nest.")
	for i = 1, c.wasps do
		spawn(c.monster, Position(pos.x + math.random(-1, 1), pos.y + math.random(-1, 1), pos.z), player)
	end
	spawn(c.queen, Position(pos.x, pos.y + 1, pos.z), player)
	SpireGive.reward(player, 5902, c.honey)
	say(player, string.format("You hold the torch to the nest. Smoke pours out, and so do the wasps, and their queen! You break off %d honeycomb.", c.honey))
	F.lore(player, "wasp_fields")
	return true
end
nest:aid(A.nest)
nest:register()

-- ================================================================ Boar Meadow: truffles
local function truffleSpot(pos)
	local c = F.conf("boar_meadow", "truffles")
	local tile = Tile(pos)
	if not tile or tile:hasFlag(TILESTATE_PROTECTIONZONE) or topItem(pos, c.item) then
		return
	end
	local it = Game.createItem(c.item, 1, pos)
	if it then
		it:setActionId(A.truffle)
		it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "Fresh-turned earth where a boar has been rooting. Something here smells of rain. Dig with a shovel.")
		local p = Position(pos.x, pos.y, pos.z)
		addEvent(function()
			local x = topItem(p, c.item)
			if x and x:getActionId() == A.truffle then
				x:remove()
			end
		end, c.lasts * 1000)
	end
end

local function rootThink()
	local c = F.conf("boar_meadow", "truffles")
	for _, m in ipairs(monstersIn("boar_meadow", 7, { ["Bristle Boar"] = true })) do
		if not m:getTarget() and m:getHealth() >= m:getMaxHealth() and math.random() < c.chance then
			m:say("*snuffles and roots at the ground*", TALKTYPE_MONSTER_SAY)
			local id = m:getId()
			addEvent(function()
				local b = Monster(id)
				-- killed or hurt while rooting: no truffle (design: "kill it too early and there is none")
				if b and b:getHealth() >= b:getMaxHealth() then
					truffleSpot(b:getPosition())
				end
			end, c.root * 1000)
		end
	end
end

-- the shovel: on a truffle spot, a truffle; else whatever the shovel did before (treasure maps, holes)
local function wrapShovel()
	if F.shovelWrapped or not onUseShovel then
		return
	end
	F.shovelWrapped = true
	local plain = onUseShovel
	onUseShovel = function(player, item, fromPosition, target, toPosition, isHotkey)
		if toPosition and toPosition.x and toPosition.x ~= CONTAINER_POSITION then
			local c = F.conf("boar_meadow", "truffles")
			local spot = topItem(Position(toPosition.x, toPosition.y, toPosition.z), c.item)
			if spot and spot:getActionId() == A.truffle then
				spot:getPosition():sendMagicEffect(CONST_ME_POFF)
				spot:remove()
				say(player, "You dig where the boar was rooting and turn up a truffle.")
				SpireGive.reward(player, 3728, 1)
				F.lore(player, "boar_meadow")
				return true
			end
		end
		return plain(player, item, fromPosition, target, toPosition, isHotkey)
	end
end

-- ================================================================ Burrow Hills: mole tunnels
local mole = Action()
function mole.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("burrow_hills", "moles")
	local list = F.points("feat_mole_")
	local here = item:getPosition()
	local idx
	for i, p in ipairs(list) do
		if p.x == here.x and p.y == here.y and p.z == here.z then
			idx = i
		end
	end
	if not idx or #list < 2 then
		return false
	end
	if item:getCustomAttribute("closed_until") and item:getCustomAttribute("closed_until") > now() then
		say(player, "The tunnel has caved in. The moles will dig it out again in a minute.")
		return true
	end
	local dest = P(list[idx % #list + 1])
	local out = dryNear(dest)
	here:sendMagicEffect(CONST_ME_POFF)
	player:teleportTo(out)
	out:sendMagicEffect(CONST_ME_POFF)
	-- the mound you went down collapses behind you for a minute: a chase can be cut off
	item:setCustomAttribute("closed_until", now() + c.collapse)
	item:transform(c.closed)
	item:setActionId(A.mole)
	local p = Position(here.x, here.y, here.z)
	addEvent(function()
		local it = topItem(p, c.closed)
		if it and it:getActionId() == A.mole then
			it:transform(1787)
			it:setActionId(A.mole)
		end
	end, c.collapse * 1000)
	say(player, "You squeeze into the mole tunnel and crawl out by another loop. The mound caves in behind you.")
	F.lore(player, "burrow_hills")
	return true
end
mole:aid(A.mole)
mole:register()

-- ================================================================ Wolf Copse: the Howling Stone
local howl = Action()
function howl.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("wolf_copse", "howl")
	local gk = "howl_ground"
	if st[gk] and st[gk] > now() then
		say(player, "The stone is still ringing from the last howl. Give the wolves a moment.")
		return true
	end
	local ok, left = cooldown(player, "howl", c.cooldown)
	if not ok then
		say(player, string.format("Your throat is raw. You can howl again in about %d minutes.", F.minutes(left)))
		return true
	end
	st[gk] = now() + c.ground_gap
	player:say("AWOOOOOOOO!", TALKTYPE_MONSTER_YELL)
	item:getPosition():sendMagicEffect(CONST_ME_SOUND_RED)
	local n = 0
	for _, m in ipairs(monstersIn("wolf_copse", 7, { ["Meadow Wolf"] = true, ["Grey Alpha"] = true })) do
		m:addTarget(player, true)
		m:selectTarget(player)
		n = n + 1
	end
	if F.forceNight or (F.forceNight == nil and F.isNight()) then
		local start = WorldPoints["loop_wolf_copse_a"] or player:getPosition()
		local extra = {}
		for i = 1, c.night_extra do
			local m = spawn(c.monster, Position(start.x + math.random(-2, 2), start.y + math.random(-2, 2), start.z), player)
			if m then
				table.insert(extra, m)
			end
		end
		removeLater(extra, c.stay)
		n = n + #extra
	end
	say(player, string.format("You howl into the stone. Every wolf in the copse answers: %d of them are coming%s!", n,
		F.isNight() and ", and the night brings more" or ""))
	F.lore(player, "wolf_copse")
	return true
end
howl:aid(A.howl)
howl:register()

-- ================================================================ Reedmarsh: the tide
st.tide = st.tide or { low = false, ground = {}, items = {} }
local function tideSet(low)
	local T = st.tide
	if T.low == low then
		return
	end
	local c = F.conf("reed_marsh", "tide")
	local bars = F.points("feat_tide_")
	if low then
		T.round = (T.round or 0) + 1
		for _, p in ipairs(bars) do
			local t = Tile(P(p))
			if t and t:getGround() then
				T.ground[p.x .. "," .. p.y] = t:getGround():getId()
				t:getGround():transform(c.sand)
			end
		end
		-- turtle nests and a washed-up chest on random sandbars
		local pool = {}
		for i = 1, #bars do
			pool[i] = bars[i]
		end
		for i = #pool, 2, -1 do
			local j = math.random(i)
			pool[i], pool[j] = pool[j], pool[i]
		end
		for i = 1, math.min(#pool, c.nests + 1) do
			local isChest = i == c.nests + 1
			local it = Game.createItem(isChest and c.chest_item or c.nest_item, 1, P(pool[i]))
			if it then
				it:setActionId(isChest and A.tidechest or A.tidenest)
				it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, isChest and "A sea chest the tide left on the sandbar." or "A turtle nest in the wet sand.")
				table.insert(T.items, { pos = pool[i], id = isChest and c.chest_item or c.nest_item })
			end
		end
	else
		local wet = {}
		for _, p in ipairs(bars) do
			wet[p.x .. "," .. p.y] = true
		end
		for _, rec in ipairs(T.items) do
			local it = topItem(P(rec.pos), rec.id)
			if it then
				it:remove()
			end
		end
		T.items = {}
		for _, p in ipairs(bars) do
			local pos = P(p)
			local t = Tile(pos)
			for _, cr in ipairs(t and t:getCreatures() or {}) do
				local dry = dryNear(pos, wet)
				cr:teleportTo(dry)
				if cr:isPlayer() then
					cr:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The tide comes back in, and you splash ashore.")
				end
			end
			local was = T.ground[p.x .. "," .. p.y]
			if t and t:getGround() and was then
				t:getGround():transform(was)
			end
		end
	end
	T.low = low
end
F.tideSet = tideSet

local tideNest = Action()
function tideNest.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("reed_marsh", "tide")
	local key = "tide_nest_" .. (st.tide.round or 0) .. "_" .. item:getPosition().x .. "_" .. item:getPosition().y
	if item:getCustomAttribute(player:getGuid() .. key) then
		say(player, "You have already taken eggs from this nest. Leave the rest to hatch.")
		return true
	end
	item:setCustomAttribute(player:getGuid() .. key, 1)
	SpireGive.reward(player, 5678, c.eggs)
	say(player, string.format("You dig %d turtle eggs out of the warm sand.", c.eggs))
	F.lore(player, "reed_marsh")
	return true
end
tideNest:aid(A.tidenest)
tideNest:register()

local tideChest = Action()
function tideChest.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("reed_marsh", "tide")
	local k = "tidechest:" .. (st.tide.round or 0)
	local ok = cooldown(player, k, c.every)
	if not ok then
		say(player, "You have already emptied this chest. The next tide may bring another.")
		return true
	end
	player:addMoney(c.chest_gold)
	say(player, string.format("Inside the sea chest, between wet rope and shells: %d gold.", c.chest_gold))
	F.lore(player, "reed_marsh")
	return true
end
tideChest:aid(A.tidechest)
tideChest:register()

-- ================================================================ Thornsnap Hollow: the vine walls
local function vineWalls()
	local c = F.conf("thornsnap_hollow", "vines")
	local walls, i = {}, 1
	while WorldPoints["feat_vine_" .. i .. "_1"] do
		walls[i] = F.points("feat_vine_" .. i .. "_")
		i = i + 1
	end
	if #walls == 0 then
		return 0
	end
	local up = F.pickVines(#walls, c.share, math.random)
	local n = 0
	for wi, tiles in ipairs(walls) do
		for _, p in ipairs(tiles) do
			local pos = P(p)
			local v = topItem(pos, c.vine)
			if up[wi] then
				local t = Tile(pos)
				if not v and t and not t:getTopCreature() then
					v = Game.createItem(c.vine, 1, pos)
					if v then
						v:setActionId(A.vine)
						v:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A wall of thorny vines across the trail. Cut it with a sword or an axe, or burn it with a lit torch.")
					end
				end
				n = n + 1
			elseif v then
				v:remove()
			end
		end
	end
	return n
end
F.vineWalls = vineWalls

local function wieldsBlade(player)
	for _, slot in ipairs({ CONST_SLOT_LEFT, CONST_SLOT_RIGHT }) do
		local it = player:getSlotItem(slot)
		local wt = it and ItemType(it:getId()):getWeaponType()
		if wt == WEAPON_SWORD or wt == WEAPON_AXE then
			return true
		end
	end
	return false
end

local vine = Action()
function vine.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local pos = item:getPosition()
	local how
	if wieldsBlade(player) then
		how = "You hack through the vines."
		pos:sendMagicEffect(CONST_ME_GROUNDSHAKER)
	elseif hasTorch(player) then
		how = "You hold your torch to the vines and they shrivel away in a crackle of flame."
		pos:sendMagicEffect(CONST_ME_FIREAREA)
	else
		say(player, "Thorny vines block the trail. A sword or an axe would cut them, or a lit torch burn them.")
		return true
	end
	-- the whole wall goes (all its tiles)
	for i = 1, 20 do
		local first = WorldPoints["feat_vine_" .. i .. "_1"]
		if not first then
			break
		end
		local tiles = F.points("feat_vine_" .. i .. "_")
		local mine = false
		for _, p in ipairs(tiles) do
			if p.x == pos.x and p.y == pos.y then
				mine = true
			end
		end
		if mine then
			for _, p in ipairs(tiles) do
				local v = topItem(P(p), item:getId())
				if v then
					v:remove()
				end
			end
		end
	end
	say(player, how .. " They will grow back.")
	F.lore(player, "thornsnap_hollow")
	return true
end
vine:aid(A.vine)
vine:register()

-- ================================================================ Shard Fields: the chimes
st.chimes = st.chimes or { order = { 1, 2, 3, 4 }, played = {} }
local CHIME_FX = { CONST_ME_SOUND_BLUE, CONST_ME_SOUND_PURPLE, CONST_ME_SOUND_WHITE, CONST_ME_SOUND_RED }
local function wind()
	local S = st.chimes
	S.order = F.windOrder(os.time())
	local list = F.points("feat_chime_")
	for i, n in ipairs(S.order) do
		addEvent(function()
			if list[n] then
				P(list[n]):sendMagicEffect(CONST_ME_SPARKLING)
				P(list[n]):sendMagicEffect(CHIME_FX[n])
			end
		end, i * 1500)
	end
end
F.wind = wind

local chime = Action()
function chime.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local S = st.chimes
	local list = F.points("feat_chime_")
	local here, n = item:getPosition(), nil
	for i, p in ipairs(list) do
		if p.x == here.x and p.y == here.y then
			n = i
		end
	end
	if not n then
		return false
	end
	here:sendMagicEffect(CHIME_FX[n])
	local mine = S.played[player:getGuid()] or {}
	table.insert(mine, n)
	local step = F.chimeStep(S.order, mine)
	if step == "wrong" then
		S.played[player:getGuid()] = {}
		say(player, "The shard rings, but the note jars against the others. Wait for the wind and listen to its order.")
	elseif step == "more" then
		S.played[player:getGuid()] = mine
	else
		S.played[player:getGuid()] = {}
		local c = F.conf("shard_fields", "chimes")
		local key = "cache_" .. os.date("%Y%m%d")
		local done = player:kv():scoped("spirebound-features"):get(key)
		if done then
			say(player, "The four notes ring true together, but the cache stays shut for you today.")
		else
			player:kv():scoped("spirebound-features"):set(key, now())
			player:addMoney(c.cache_gold)
			if math.random() < c.shard_chance then
				SpireGive.reward(player, SpireAdventureData and SpireAdventureData.cut or 16119, 1)
			end
			local cache = WorldPoints.feat_cache
			if cache then
				P(cache):sendMagicEffect(CONST_ME_GIFT_WRAPS)
			end
			say(player, string.format("The four notes ring true together, and the cache by the shards springs open: %d gold. Once a day.", c.cache_gold))
		end
		F.lore(player, "shard_fields")
	end
	return true
end
chime:aid(A.chime)
chime:register()

local cache = Action()
function cache.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	say(player, "A crystal-crusted cache, locked tight. The shards beside it seem to be waiting for something.")
	return true
end
cache:aid(A.cache)
cache:register()

-- ================================================================ The Bandit Road: the wanted poster
local LOOP_NAMES = { a = "north-west", b = "north-east", c = "middle", d = "far" }
local function lieutenantOut()
	local c = F.conf("bandit_road", "poster")
	local L = st.lieutenant and Monster(st.lieutenant.id)
	if L then
		return
	end
	local g = groundRect("bandit_road")
	local gate = WorldPoints.gate_bandit_road
	local spots = {}
	for _, s in ipairs(g and g.spots or {}) do
		if s.z == 7 and (not gate or math.max(math.abs(s.x - gate.x), math.abs(s.y - gate.y)) >= 10) then
			table.insert(spots, s)
		end
	end
	if #spots == 0 then
		return
	end
	local s = spots[math.random(#spots)]
	local m = spawn(c.monster, Position(s.x, s.y, s.z))
	if m then
		st.lieutenant = { id = m:getId(), loop = s.loop, at = now() }
		local id = m:getId()
		addEvent(function()
			local x = Monster(id)
			if x then
				x:remove()
				if st.lieutenant and st.lieutenant.id == id then
					st.lieutenant = nil
				end
			end
		end, c.stays * 1000)
	end
end
F.lieutenantOut = lieutenantOut

local poster = Action()
function poster.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("bandit_road", "poster")
	if player:getItemCount(c.badge) > 0 then
		player:removeItem(c.badge, 1)
		player:addMoney(c.bounty)
		say(player, string.format("You pin the lieutenant's badge to the poster and take the bounty from the box beneath it: %d gold.", c.bounty))
		F.lore(player, "bandit_road")
		return true
	end
	local L = st.lieutenant and Monster(st.lieutenant.id)
	if L then
		say(player, string.format("WANTED: a Bandit Lieutenant. Someone has scrawled underneath: \"seen on the %s loop\". Bring his badge here for the bounty (%d gold).",
			LOOP_NAMES[st.lieutenant.loop] or "far", c.bounty))
	else
		say(player, "WANTED: a Bandit Lieutenant. The newest notice says he is lying low; a new one is out on the road every hour.")
	end
	return true
end
poster:aid(A.poster)
poster:register()

-- ================================================================ The Old Quarry: the lift
local winch = Action()
function winch.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local plat, top = P(WorldPoints.feat_lift_platform), P(WorldPoints.feat_lift_top)
	if not plat or not top then
		return false
	end
	local here = player:getPosition()
	if here.x == plat.x and here.y == plat.y and here.z == plat.z then
		say(player, "You cannot turn the winch from the platform. A friend has to work it.")
		return true
	end
	local rider
	for _, c in ipairs(Tile(plat):getCreatures() or {}) do
		if c:isPlayer() then
			rider = c
		end
	end
	if not rider then
		say(player, "The winch creaks. The rope runs up to the ledge above. Someone has to stand on the platform beside it to ride up.")
		return true
	end
	item:transform(item:getId() == 2772 and 2773 or 2772)
	item:setActionId(A.winch)
	plat:sendMagicEffect(CONST_ME_POFF)
	rider:teleportTo(top)
	top:sendMagicEffect(CONST_ME_TELEPORT)
	rider:sendTextMessage(MESSAGE_EVENT_ADVANCE, player:getName() .. " turns the winch and the platform hauls you up to the upper ledge.")
	say(player, "You heave the winch round, and " .. rider:getName() .. " rides up to the ledge.")
	F.lore(player, "old_quarry")
	F.lore(rider, "old_quarry")
	return true
end
winch:aid(A.winch)
winch:register()

-- ================================================================ The Old Watchtower: the signal fire
st.signal = st.signal or {}
local function inKeep(pos)
	local nw, se = WorldPoints.feat_signal_nw, WorldPoints.feat_signal_se
	return nw and pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end
F.inKeep = inKeep

function F.signalBurning()
	return st.signal.burnsUntil and st.signal.burnsUntil > now()
end

local function signalEnd(text)
	st.signal = { cooldownUntil = now() + 60 }
	if text then
		Game.broadcastMessage(text, MESSAGE_EVENT_ADVANCE)
	end
end

local function holdTick(guid, waveN)
	local S = st.signal
	if not S.holding or S.holder ~= guid then
		return
	end
	local c = F.conf("apex_watchtower", "signal")
	local p = Player(guid)
	if not p or not inKeep(p:getPosition()) then
		S.holding = nil
		local b = P(WorldPoints.feat_signal)
		if b then
			b:sendMagicEffect(CONST_ME_POFF)
		end
		if p then
			say(p, "You left the keep and the signal fire gutters out.")
		end
		return
	end
	if waveN * c.wave_every >= c.hold then
		S.holding = nil
		S.burnsUntil = now() + c.burns
		S.lighter = p:getName()
		S.party = {}
		local party = p:getParty()
		if party then
			for _, m in ipairs(party:getMembers() or {}) do
				S.party[m:getGuid()] = true
			end
			S.party[party:getLeader():getGuid()] = true
		end
		S.party[guid] = true
		F.lore(p, "apex_watchtower")
		local text = string.format("%s has lit the signal fire of the Old Watchtower! For %d minutes everyone hunting there finds a little more gold.",
			p:getName(), math.floor(c.burns / 60))
		if SpireFinds and SpireFinds.announce then
			pcall(SpireFinds.announce, "secret", nil, text, nil)
		end
		Game.broadcastMessage(text, MESSAGE_EVENT_ADVANCE)
		return
	end
	local b = P(WorldPoints.feat_signal)
	b:sendMagicEffect(CONST_ME_FIREAREA)
	for i = 1, c.wave do
		spawn(c.monster, Position(b.x + math.random(-6, 6), b.y + math.random(-6, 6), b.z), p)
	end
	say(p, string.format("The signal fire roars and the ruin answers! Hold the keep: %d seconds to go.", c.hold - waveN * c.wave_every))
	addEvent(holdTick, c.wave_every * 1000, guid, waveN + 1)
end

local signal = Action()
function signal.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local S = st.signal
	if F.signalBurning() then
		if S.party and S.party[player:getGuid()] then
			say(player, string.format("The signal fire burns for another %d minutes.", F.minutes(S.burnsUntil - now())))
		else
			signalEnd(player:getName() .. " has put out the signal fire of the Old Watchtower!")
		end
		return true
	end
	if S.holding then
		say(player, "Someone is already holding the keep for the signal fire.")
		return true
	end
	if S.cooldownUntil and S.cooldownUntil > now() then
		say(player, "The brazier's coals are still too hot to relight. Wait a moment.")
		return true
	end
	S.holding, S.holder = true, player:getGuid()
	say(player, "You light the signal brazier. Now hold the keep until the fire takes!")
	holdTick(player:getGuid(), 0)
	return true
end
signal:aid(A.signal)
signal:register()

-- a lit signal fire: a little more gold from the tower's monsters (like the Beacon, much smaller)
local richer = EventCallback("SpireSignalGold")
function richer.monsterOnDropLoot(monster, corpse)
	if not F.signalBurning() or not corpse:isContainer() then
		return
	end
	local pos = monster:getPosition()
	local nw = WorldPoints.feat_signal_nw
	local g = nw and { x1 = nw.x - 13, y1 = nw.y - 13, x2 = nw.x + 31, y2 = nw.y + 31 }
	if not g or pos.x < g.x1 or pos.x > g.x2 or pos.y < g.y1 or pos.y > g.y2 then
		return
	end
	local coins = 0
	for i = 0, corpse:getSize() - 1 do
		local it = corpse:getItem(i)
		if it and it:getId() == 3031 then coins = coins + it:getCount() end
		if it and it:getId() == 3035 then coins = coins + 100 * it:getCount() end
	end
	local extra = math.floor(coins * F.conf("apex_watchtower", "signal").gold_bonus + math.random())
	if extra > 0 then
		corpse:addItem(3031, math.min(100, extra))
	end
end
richer:register()

-- ================================================================ Smugglers' Ridge: the contraband stashes
st.stash = st.stash or {}
local function stashPick()
	local list = F.points("feat_stash_")
	if #list == 0 then
		return
	end
	st.stash = { idx = math.random(#list), round = (st.stash.round or 0) + 1, taken = {} }
end

local stash = Action()
function stash.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("smugglers_ridge", "stash")
	local list = F.points("feat_stash_")
	local here, n = item:getPosition(), nil
	for i, p in ipairs(list) do
		if p.x == here.x and p.y == here.y then
			n = i
		end
	end
	if n ~= st.stash.idx then
		say(player, "You heave the stone aside. Nothing underneath but beetles.")
		return true
	end
	if st.stash.taken[player:getGuid()] then
		say(player, "You have already emptied this stash. The smugglers will hide the next one somewhere else.")
		return true
	end
	st.stash.taken[player:getGuid()] = true
	player:addMoney(c.gold)
	for i = 1, c.guards do
		spawn(c.monster, Position(here.x + math.random(-3, 3), here.y + math.random(-3, 3), here.z), player)
	end
	say(player, string.format("Under the loose stone: a smugglers' stash, %d gold! And here come its owners.", c.gold))
	F.lore(player, "smugglers_ridge")
	return true
end
stash:aid(A.stash)
stash:register()

-- ================================================================ The Fallen Bastion: the old ballista
local ballista = Action()
function ballista.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local c = F.conf("fallen_bastion", "ballista")
	local here = item:getPosition()
	local best, bd
	for _, m in ipairs(Game.getSpectators(here, false, false, c.reach, c.reach, c.reach, c.reach) or {}) do
		if m:isMonster() and not m:getMaster() then
			local q = m:getPosition()
			local d = math.max(math.abs(q.x - here.x), math.abs(q.y - here.y))
			local t = Tile(q)
			if t and not t:hasFlag(TILESTATE_PROTECTIONZONE) and (not bd or d < bd) then
				best, bd = m, d
			end
		end
	end
	if not best then
		say(player, "You swing the ballista round, but there is nothing in range to shoot at.")
		return true
	end
	local ok, left = cooldown(player, "ballista", c.cooldown)
	if not ok then
		say(player, string.format("You are still winding the ballista back. Ready in about %d minutes.", F.minutes(left)))
		return true
	end
	local at = best:getPosition()
	here:sendDistanceEffect(at, CONST_ANI_HUNTINGSPEAR)
	at:sendMagicEffect(CONST_ME_EXPLOSIONAREA)
	for _, m in ipairs(Game.getSpectators(at, false, false, 1, 1, 1, 1) or {}) do
		if m:isMonster() and not m:getMaster() then
			doTargetCombatHealth(player, m, COMBAT_PHYSICALDAMAGE, -c.dmg[1], -c.dmg[2], CONST_ME_DRAWBLOOD)
		end
	end
	say(player, "THUNK! The old ballista looses a bolt as long as a man.")
	F.lore(player, "fallen_bastion")
	return true
end
ballista:aid(A.ballista)
ballista:register()

-- ================================================================ feature objects never move
local fixed = EventCallback("SpireFeatureFixed")
function fixed.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	local aid = item:getActionId()
	if aid >= F.AID_MIN and aid <= F.AID_MAX and aid ~= A.seedling then
		player:sendCancelMessage(RETURNVALUE_NOTMOVABLE)
		return false
	end
	return true
end
fixed:register()

-- ================================================================ the clock: lilies, tide, vines, wind, lieutenant, stash, truffles
local clock = GlobalEvent("SpireFeatureClock")
function clock.onThink(interval)
	local t = now()
	local night = F.forceNight
	if night == nil then
		night = F.isNight()
	end
	pcall(liliesUp, night)
	local tc = F.conf("reed_marsh", "tide")
	local low = F.forceTide
	if low == nil then
		low = F.tideLow(t, tc.every, tc.low)
	end
	pcall(tideSet, low)
	local vc = F.conf("thornsnap_hollow", "vines")
	if not st.vinesAt or t >= st.vinesAt then
		st.vinesAt = t + vc.every
		pcall(vineWalls)
	end
	local cc = F.conf("shard_fields", "chimes")
	if not st.windAt or t >= st.windAt then
		st.windAt = t + cc.wind
		pcall(wind)
	end
	local pc = F.conf("bandit_road", "poster")
	if not st.ltAt or t >= st.ltAt then
		st.ltAt = t + pc.every
		pcall(lieutenantOut)
	end
	local sc = F.conf("smugglers_ridge", "stash")
	if not st.stashAt or t >= st.stashAt then
		st.stashAt = t + sc.every
		stashPick()
	end
	if not st.glintAt or t >= st.glintAt then
		st.glintAt = t + sc.glint
		local list = F.points("feat_stash_")
		local p = st.stash.idx and list[st.stash.idx]
		if p then
			P(p):sendMagicEffect(CONST_ME_SPARKLING)
		end
	end
	local trc = F.conf("boar_meadow", "truffles")
	if not st.rootAt or t >= st.rootAt then
		st.rootAt = t + trc.every
		pcall(rootThink)
	end
	if F.signalBurning() and (st.signal.fxAt or 0) <= t then
		st.signal.fxAt = t + 5
		local b = P(WorldPoints.feat_signal)
		if b then
			b:sendMagicEffect(CONST_ME_HITBYFIRE)
		end
	end
	return true
end
clock:interval(5000)
clock:register()

-- ================================================================ start-up: tag the objects, the rows
function F.place()
	local n = 0
	local function tag(name, aid, id, desc)
		if tagPoint(name, aid, id, desc) then
			n = n + 1
		else
			logger.warn("[Spirebound] ground features: nothing to tag at {}", name)
		end
	end
	tag("feat_bell", A.bell, nil, "The Ratcatcher's Bell, green with age. The rats of the warren still answer it.")
	for i, _ in ipairs(F.points("feat_nest_")) do
		tag("feat_nest_" .. i, A.nest, nil, "A wasp nest the size of a barrel, humming. A lit torch would smoke them out.")
	end
	for i, p in ipairs(F.points("feat_mole_")) do
		tag("feat_mole_" .. i, A.mole, nil, "A mole mound with a tunnel big enough to squeeze into.")
	end
	tag("feat_howl", A.howl, nil, "The Howling Stone. Hollows worn into it moan when the wind blows. Howl into it and the wolves will hear.")
	for i, _ in ipairs(F.points("feat_chime_")) do
		tag("feat_chime_" .. i, A.chime, nil, "A tall shard that rings when struck.")
	end
	tag("feat_cache", A.cache, nil, "A crystal-crusted cache, locked tight.")
	tag("feat_poster", A.poster)
	tag("feat_lift_winch", A.winch, nil, "An old quarry winch. Its rope runs up to the ledge above a platform.")
	tag("feat_signal", A.signal, nil, "The Old Watchtower's signal brazier.")
	for i, _ in ipairs(F.points("feat_stash_")) do
		tag("feat_stash_" .. i, A.stash, nil, "A heavy stone. Is it loose?")
	end
	tag("feat_ballista", A.ballista, nil, "The bastion's old ballista. It still turns, and there is a bolt in the groove.")
	-- the island's two tiles count as visiting the night lilies
	for _, name in ipairs({ "feat_island", "feat_island_2" }) do
		local p = WorldPoints[name]
		local t = p and Tile(P(p))
		if t and t:getGround() then
			t:getGround():setActionId(47217)
		end
	end
	return n
end

local startup = GlobalEvent("SpireFeaturesStartup")
function startup.onStartup()
	logger.info("[Spirebound] ground features: {} objects ready", F.place())
	wrapShovel()
	if SpireDiscoveries and SpireDiscoveries.register then
		for _, f in ipairs(SpireDepthData.features) do
			SpireDiscoveries.register("groundlore", f.id, f.name, 1)
		end
	end
	return true
end
startup:register()

-- ================================================================ The Bramble Run: bramble berries (core bush script hook)
function F.berryPicked(player, pos)
	if not pos or SpireRoamers.groundAt(pos) ~= "bramble_run" then
		return
	end
	F.lore(player, "bramble_run")
	local c = F.conf("bramble_run", "berries")
	if math.random() < c.rouse then
		spawn(c.monster, Position(pos.x, pos.y + 1, pos.z), player)
		say(player, "Something under the bush did not like being disturbed!")
	end
end

F.stashPick, F.truffleSpot, F.rootThink = stashPick, truffleSpot, rootThink
