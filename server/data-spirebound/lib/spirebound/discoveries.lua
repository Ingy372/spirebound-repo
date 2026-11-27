-- The Discoveries page (adventure layer 4.6, roadmap AD6): every findable thing of a floor as a row that reads "???"
-- until the character finds it. One registry, so each floor (and Session B's roamers and treasure keepsakes) adds rows:
--   SpireDiscoveries.register(category, id, name, floor)
--   SpireDiscoveries.mark(player, category, id)      call when the character finds / kills / digs it
-- Some categories already keep their own record (secrets, hidden beasts, fish, builders' stones, ground chests); those
-- are read through `sources`, so nothing has to be marked twice.
SpireDiscoveries = SpireDiscoveries or { rows = {} }
-- Floor 1 depth (2026-11-27): "record" (Session C's story records), "groundlore" (each ground's feature used once) and
-- "cookbook" (each dish made once) are row groups too.
SpireDiscoveries.ORDER = { "secret", "beast", "elite", "chest", "fish", "stone", "roamer", "keepsake", "record", "groundlore", "cookbook" }
SpireDiscoveries.LABEL = { secret = "Secrets", beast = "Hidden beasts", elite = "Elites", chest = "Ground chests",
	fish = "Fish", stone = "Builders' stones", roamer = "Rare roamers", keepsake = "Treasure keepsakes",
	record = "Records", groundlore = "Ground lore", cookbook = "Cookbook" }
SpireDiscoveries.sources = SpireDiscoveries.sources or {} -- category -> function(player, id) -> time found or nil
SpireDiscoveries.FLOOR_NAMES = { [1] = "the Plains" }

-- Milestones per floor: share of rows found -> reward (adventure layer 4.6)
SpireDiscoveries.MILESTONES = {
	[1] = {
		{ pct = 25, title = "Wanderer of the Plains" },
		{ pct = 50, trophy = "plains_map" },
		{ pct = 100, title = "Cartographer of the Plains", aura = "cartographers_compass" },
	},
}

-- ---------------------------------------------------------------- registry
function SpireDiscoveries.register(category, id, name, floor)
	floor = floor or 1
	SpireDiscoveries.rows[floor] = SpireDiscoveries.rows[floor] or {}
	local list = SpireDiscoveries.rows[floor]
	for _, r in ipairs(list) do
		if r.category == category and r.id == id then
			r.name = name
			return r
		end
	end
	local r = { category = category, id = id, name = name, floor = floor }
	table.insert(list, r)
	return r
end

function SpireDiscoveries.floorRows(floor)
	return SpireDiscoveries.rows[floor or 1] or {}
end

function SpireDiscoveries.find(category, id)
	for floor, list in pairs(SpireDiscoveries.rows) do
		for _, r in ipairs(list) do
			if r.category == category and r.id == id then
				return r, floor
			end
		end
	end
end

-- ---------------------------------------------------------------- pure
-- Pure: rows + found(row) -> per-category counts and the floor total
function SpireDiscoveries.counts(rows, found)
	local per, got, total = {}, 0, 0
	for _, r in ipairs(rows) do
		per[r.category] = per[r.category] or { got = 0, total = 0 }
		per[r.category].total = per[r.category].total + 1
		total = total + 1
		if found(r) then
			per[r.category].got = per[r.category].got + 1
			got = got + 1
		end
	end
	return per, got, total
end

-- Pure: milestones reached at got/total
function SpireDiscoveries.reached(floor, got, total)
	local out = {}
	if total <= 0 then
		return out
	end
	for _, m in ipairs(SpireDiscoveries.MILESTONES[floor] or {}) do
		if got * 100 >= m.pct * total then
			table.insert(out, m)
		end
	end
	return out
end

-- Pure: one row's line. foundAt = time or nil; rumour = ground name or nil. Never names a reward.
function SpireDiscoveries.rowLine(row, foundAt, rumour)
	if foundAt then
		if type(foundAt) ~= "number" or foundAt <= 0 then
			return "  [x] " .. row.name
		end
		return string.format("  [x] %s (%s)", row.name, os.date("%d %b", foundAt))
	end
	if rumour then
		return string.format("  [ ] ??? (rumoured: %s)", rumour)
	end
	return "  [ ] ???"
end

-- ---------------------------------------------------------------- the character
local function marks(player)
	return player:kv():scoped("spirebound-discoveries")
end

local function rumours(player)
	return player:kv():scoped("spirebound-rumoured")
end

local function key(category, id)
	return category .. ":" .. id
end

function SpireDiscoveries.foundAt(player, category, id)
	local src = SpireDiscoveries.sources[category]
	if src then
		local ok, at = pcall(src, player, id)
		if ok and at then
			return at -- a time, or true when that record keeps no date
		end
	end
	return marks(player):get(key(category, id))
end

function SpireDiscoveries.rumoured(player, category, id)
	return rumours(player):get(key(category, id))
end

function SpireDiscoveries.setRumour(player, category, id, ground)
	rumours(player):set(key(category, id), ground)
end

function SpireDiscoveries.progress(player, floor)
	local rows = SpireDiscoveries.floorRows(floor)
	return SpireDiscoveries.counts(rows, function(r) return SpireDiscoveries.foundAt(player, r.category, r.id) ~= nil end)
end

-- Give the milestone rewards this character has reached and not yet had (safe to call any time)
function SpireDiscoveries.checkMilestones(player, floor)
	floor = floor or 1
	local _, got, total = SpireDiscoveries.progress(player, floor)
	local given = player:kv():scoped("spirebound-disc-milestones")
	for _, m in ipairs(SpireDiscoveries.reached(floor, got, total)) do
		local k = floor .. ":" .. m.pct
		if not given:get(k) then
			given:set(k, os.time())
			local where = SpireDiscoveries.FLOOR_NAMES[floor] or ("Floor " .. floor)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Discoveries: %d%% of %s found!", m.pct, where))
			if m.title then
				player:kv():scoped("spirebound-titles"):set(m.title, os.time())
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. m.title .. ".")
			end
			if m.trophy and SpireKeepsakes then
				SpireKeepsakes.give(player, m.trophy)
			end
			if m.aura and SpireAuras then
				SpireAuras.give(player, m.aura)
			end
		end
	end
end

-- The seam: this character found it. Returns true the first time.
function SpireDiscoveries.mark(player, category, id)
	if not player then
		return false
	end
	local k = key(category, id)
	if marks(player):get(k) then
		return false
	end
	marks(player):set(k, os.time())
	local _, floor = SpireDiscoveries.find(category, id)
	SpireDiscoveries.checkMilestones(player, floor or 1)
	return true
end

function SpireDiscoveries.unmark(player, category, id) -- tests
	marks(player):remove(key(category, id))
	rumours(player):remove(key(category, id))
end

-- The page: header, then each category with its count and rows
function SpireDiscoveries.lines(player, floor)
	floor = floor or 1
	local rows = SpireDiscoveries.floorRows(floor)
	local per, got, total = SpireDiscoveries.progress(player, floor)
	local where = SpireDiscoveries.FLOOR_NAMES[floor] or ("Floor " .. floor)
	local lines = { string.format("Floor %d Discoveries (%s): %d of %d found.", floor, where, got, total) }
	local nextM
	for _, m in ipairs(SpireDiscoveries.MILESTONES[floor] or {}) do
		if got * 100 < m.pct * total then
			nextM = m
			break
		end
	end
	if nextM then
		table.insert(lines, string.format("Next milestone at %d%%: %s.", nextM.pct, nextM.title and ("the title " .. nextM.title) or "a keepsake for your house"))
	else
		table.insert(lines, "Every discovery on this floor is yours.")
	end
	for _, cat in ipairs(SpireDiscoveries.ORDER) do
		local c = per[cat]
		if c then
			table.insert(lines, string.format("%s: %d of %d", SpireDiscoveries.LABEL[cat] or cat, c.got, c.total))
			for _, r in ipairs(rows) do
				if r.category == cat then
					local at = SpireDiscoveries.foundAt(player, cat, r.id)
					-- Jay, 2026-11-27: rumours never point at secrets or hidden beasts
					local rumour = (cat ~= "secret" and cat ~= "beast") and SpireDiscoveries.rumoured(player, cat, r.id) or nil
					table.insert(lines, SpireDiscoveries.rowLine(r, at, rumour))
					if cat == "secret" and not at and SpireSecrets.holdsRiddle(player, r.id) then
						local sec = SpireSecrets.get(r.id)
						if sec and sec.hint then
							table.insert(lines, "      a riddle from a bottle: \"" .. sec.hint .. "\"")
						end
					end
				end
			end
		end
	end
	return lines
end
