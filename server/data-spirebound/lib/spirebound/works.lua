-- Town Works (roadmap FD5; docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.5).
-- A Works Board beside the notice board in the Hearth shows one project at a time. Everyone gives gold toward it by
-- dropping coins on the board (the gold is destroyed: a sink). When it fills, the map changes for the rest of the season
-- (pieces from maps/floor1_features.py -> works_pieces.lua, laid again at every start), givers go on its plaque, the top
-- giver gets the project's title, and the next project opens. Size follows the accounts active in the last week.
-- Numbers: tools/gen_depth.py (SpireDepthData.works). The game side: scripts/spirebound/works.lua.
SpireWorks = SpireWorks or {}
local W = SpireDepthData.works

SpireWorks.COINS = { [3031] = 1, [3035] = 100, [3043] = 10000 }

local function store()
	return kv.scoped("spirebound-works")
end

-- ---------------------------------------------------------------- pure
-- Pure: a project's size for `accounts` active accounts (index = 1..5)
function SpireWorks.size(index, accounts)
	local base = math.max(W.minSize, accounts * W.perAccountDay * W.fillDays)
	return math.floor(base * (W.step[index] or 1) / 100 + 0.5) * 100
end

-- Pure: how much of `amount` an account may still give today, with `givenToday` given already
function SpireWorks.allowed(size, givenToday, amount)
	local cap = SpireWorks.noCap and size or math.floor(size * W.dailyCap) -- noCap: test servers only (/depth works nocap)
	return math.max(0, math.min(amount, cap - givenToday)), cap
end

-- Pure: the gold value of a stack of coins (nil if not coins)
function SpireWorks.coinValue(itemId, count)
	local v = SpireWorks.COINS[itemId]
	return v and v * count or nil
end

-- Pure: givers {key -> {name, amount}} -> sorted list, biggest first
function SpireWorks.ranked(givers)
	local list = {}
	for k, g in pairs(givers or {}) do
		table.insert(list, { key = k, name = g.name, amount = g.amount })
	end
	table.sort(list, function(a, b)
		if a.amount ~= b.amount then
			return a.amount > b.amount
		end
		return a.name < b.name
	end)
	return list
end

-- Pure: split `gold` into coins { crystal, platinum, gold }
function SpireWorks.change(gold)
	return math.floor(gold / 10000), math.floor((gold % 10000) / 100), gold % 100
end

-- ---------------------------------------------------------------- state
function SpireWorks.state()
	local s = store():get("state")
	local season = SpireSeason and SpireSeason.current() or 1
	if not s or s.season ~= season then
		s = { season = season, current = 1, given = 0, givers = {}, daily = {}, finished = {} }
		SpireWorks.save(s)
	end
	return s
end

function SpireWorks.save(s)
	store():set("state", s)
end

function SpireWorks.activeAccounts()
	local q = db.storeQuery("SELECT COUNT(DISTINCT `account_id`) AS `n` FROM `players` WHERE `group_id` < 4 AND `lastlogin` > " .. (os.time() - 7 * 86400))
	local n = 0
	if q then
		n = Result.getNumber(q, "n")
		Result.free(q)
	end
	return math.max(1, n)
end

function SpireWorks.project(s)
	return W.projects[s.current]
end

-- open the current project's size if it has none yet
function SpireWorks.ensureSize(s)
	if s.current <= #W.projects and not s.size then
		s.size = SpireWorks.size(s.current, SpireWorks.activeAccounts())
		SpireWorks.save(s)
	end
	return s.size
end

-- ---------------------------------------------------------------- the map pieces
local function applyPiece(p)
	local pos = Position(p.x, p.y, p.z)
	local tile = Tile(pos)
	if not tile then
		return false
	end
	if p.op == "ground" then
		local g = tile:getGround()
		if g and g:getId() ~= p.id then
			g:transform(p.id)
		end
	elseif p.op == "transform" then
		for _, it in ipairs(tile:getItems() or {}) do
			if it:getId() == p.src then
				it:transform(p.id)
			end
		end
	elseif p.op == "item" then
		for _, it in ipairs(tile:getItems() or {}) do
			if it:getId() == p.id then
				return true
			end
		end
		Game.createItem(p.id, 1, pos)
	elseif p.op == "clearblock" then -- only what blocks the way (shoreline stones), not the grass edges
		for _, it in ipairs(tile:getItems() or {}) do
			if not ItemType(it:getId()):isPickupable() and ItemType(it:getId()):isBlocking() then
				it:remove()
			end
		end
	elseif p.op == "clear" then
		for _, it in ipairs(tile:getItems() or {}) do
			it:remove()
		end
	end
	return true
end

function SpireWorks.layPieces(list)
	local n = 0
	for _, p in ipairs(list or {}) do
		if applyPiece(p) then
			n = n + 1
		end
	end
	return n
end

function SpireWorks.layFinished(s)
	local n = 0
	for i = 1, #W.projects do
		if s.finished[tostring(i)] then
			n = n + SpireWorks.layPieces(SpireWorksPieces and SpireWorksPieces[i])
			if SpireWorks.afterLay then
				SpireWorks.afterLay(i, s)
			end
		end
	end
	return n
end

-- ---------------------------------------------------------------- giving
-- A player gives `gold`. Returns accepted gold and a line to say.
function SpireWorks.give(player, gold)
	local s = SpireWorks.state()
	local proj = SpireWorks.project(s)
	if not proj then
		return 0, "Every project of this season is finished. Thank you, climber."
	end
	local size = SpireWorks.ensureSize(s)
	local today = os.date("%Y%m%d")
	local dkey = player:getAccountId() .. ":" .. today
	local left = size - s.given
	local ok, cap = SpireWorks.allowed(size, s.daily[dkey] or 0, math.min(gold, left))
	if ok <= 0 then
		return 0, string.format("Your account has given its share for today (%d gold a day). Thank you: come back tomorrow.", cap)
	end
	s.given = s.given + ok
	s.daily = { [dkey] = (s.daily[dkey] or 0) + ok } -- only today's entries are kept
	for k, v in pairs(store():get("state").daily or {}) do
		if k:sub(-8) == today and k ~= dkey then
			s.daily[k] = v
		end
	end
	local gk = tostring(player:getGuid())
	s.givers[gk] = { name = player:getName(), amount = ((s.givers[gk] and s.givers[gk].amount) or 0) + ok }
	SpireWorks.save(s)
	local line = string.format("You give %d gold to %s: %d of %d (%d%%).", ok, proj.name, s.given, size, math.floor(s.given * 100 / size))
	if s.given >= size then
		SpireWorks.finish(s)
	end
	return ok, line
end

-- The project is full: lay its pieces, give the title, open the next one
function SpireWorks.finish(s)
	local i = s.current
	local proj = W.projects[i]
	local ranked = SpireWorks.ranked(s.givers)
	local names = {}
	for _, g in ipairs(ranked) do
		table.insert(names, g.name)
	end
	s.finished[tostring(i)] = { at = os.time(), top = ranked[1] and ranked[1].name, names = names }
	if ranked[1] then
		local guid = tonumber(ranked[1].key)
		local p = Player(ranked[1].name)
		if p then
			p:kv():scoped("spirebound-titles"):set(proj.title, os.time())
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You gave the most to " .. proj.name .. " and earned the title " .. proj.title .. " for this season.")
		elseif guid then
			kv.scoped("player"):scoped(tostring(guid)):scoped("spirebound-titles"):set(proj.title, os.time())
		end
	end
	s.current, s.given, s.givers, s.size = i + 1, 0, {}, nil
	SpireWorks.save(s)
	SpireWorks.layPieces(SpireWorksPieces and SpireWorksPieces[i])
	if SpireWorks.afterLay then
		SpireWorks.afterLay(i, s)
	end
	local nxt = W.projects[i + 1]
	Game.broadcastMessage(string.format("Town Works: %s is finished! %s%s", proj.name, proj.done,
		nxt and (" Next on the Works Board: " .. nxt.name .. ".") or ""), MESSAGE_EVENT_ADVANCE)
	return true
end

-- The board's text: this project, the top givers, the next one, the finished plaques
function SpireWorks.lines()
	local s = SpireWorks.state()
	local L = { "THE WORKS BOARD", "" }
	local proj = SpireWorks.project(s)
	if proj then
		local size = SpireWorks.ensureSize(s)
		table.insert(L, string.format("Now building: %s. %d of %d gold (%d%%).", proj.name, s.given, size, math.floor(s.given * 100 / size)))
		table.insert(L, "When it is done: " .. proj.done)
		table.insert(L, string.format("Drop coins on this board to give. The gold goes into the work. One account gives at most %d gold a day.",
			math.floor(size * W.dailyCap)))
		local r = SpireWorks.ranked(s.givers)
		if #r > 0 then
			local top = {}
			for i = 1, math.min(5, #r) do
				table.insert(top, string.format("%s %d", r[i].name, r[i].amount))
			end
			table.insert(L, "Top givers: " .. table.concat(top, ", ") .. ". The top giver earns the title " .. proj.title .. ".")
		else
			table.insert(L, "Nobody has given yet. The top giver earns the title " .. proj.title .. ".")
		end
		local nxt = W.projects[s.current + 1]
		if nxt then
			table.insert(L, "After that: " .. nxt.name .. ".")
		end
	else
		table.insert(L, "Every project of this season is finished.")
	end
	for i, p in ipairs(W.projects) do
		local f = s.finished[tostring(i)]
		if f then
			table.insert(L, "")
			table.insert(L, string.format("%s, finished %s. Built by: %s.", p.name, os.date("%d %b", f.at), table.concat(f.names or {}, ", ")))
		end
	end
	return L
end
