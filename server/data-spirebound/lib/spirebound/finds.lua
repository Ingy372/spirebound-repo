-- Rare finds are loud and visible (adventure layer 4.2, roadmap AD1) and season firsts (4.3, AD3).
-- docs/superpowers/specs/2026-11-27-adventure-layer-design.md
--
-- The seam other scripts call (always guarded with `if SpireFinds then`):
--   SpireFinds.announce(kind, names, thing, groundName)  server-wide line + notice-board entry, rate-limited
--   SpireFinds.first(category, id, players, label)        records a season first; true if this was the first
-- kind: rare_weapon, fish, secret, beast, roamer_seen, roamer_killed, keepsake
-- names: a list of character names (or Player objects); thing: a string, or for rare_weapon { item = , from = },
-- for fish { name = , kg = }; groundName: the ground ("the Wolf Copse" or "Wolf Copse"); for secret and beast the floor
-- number only (Jay, 2026-11-27: a secret's place is never announced).
SpireFinds = SpireFinds or {}
SpireFinds.GAP = 20                 -- at most one find line every 20 seconds; the rest go to the board only
SpireFinds.BOARD_DAYS = 7           -- a board entry stays a week
SpireFinds.BOARD_MAX = 40
SpireFinds.FIRST_TITLES = { { 1, "First Finder" }, { 3, "Trailblazer" }, { 6, "Pathbreaker" } }
SpireFinds.WAKE_AT = 3              -- firsts this season for the Trailblazer's Wake aura
SpireFinds.CATEGORY_NAMES = { secret = "Secret", beast = "Hidden beast", elite = "Elite", roamer = "Rare roamer",
	fish = "Legendary fish", keepsake = "Keepsake", chest = "Ground chest", stone = "Builders' stone" }
SpireFinds.lastLine = 0             -- os.time() of the last server-wide line

-- ---------------------------------------------------------------- pure helpers
function SpireFinds.article(word)
	if not word or word == "" then
		return ""
	end
	if word:match("^[Tt]he ") then
		return ""
	end
	return word:match("^[AEIOUaeiou]") and "an " or "a "
end

-- "the Wolf Copse" from "Wolf Copse" or "the Wolf Copse"; nil stays nil
SpireFinds.NO_ARTICLE = { Hearthgate = true, Millcross = true, Reedmarsh = true }
function SpireFinds.theGround(g)
	if not g or g == "" then
		return nil
	end
	if g:match("^[Tt]he ") then
		return "the " .. g:sub(5)
	end
	if SpireFinds.NO_ARTICLE[g] or g:match("^Floor ") then
		return g
	end
	return "the " .. g
end

-- "the Frenzied Boar" / "the Paymaster" (from "The Paymaster")
function SpireFinds.theThing(t)
	if t:match("^[Tt]he ") then
		return "the " .. t:sub(5)
	end
	return "the " .. t
end

-- names (already made anonymous where asked) -> "Ana", "Ana and Bo", "Ana, Bo and Cy"; "Someone" when empty
function SpireFinds.joinNames(names)
	local shown, hidden = {}, 0
	for _, n in ipairs(names or {}) do
		if n then
			table.insert(shown, n)
		else
			hidden = hidden + 1
		end
	end
	if hidden > 0 then
		table.insert(shown, hidden == 1 and (#shown == 0 and "Someone" or "one other") or (hidden .. " others"))
	end
	if #shown == 0 then
		return "Someone"
	elseif #shown == 1 then
		return shown[1]
	end
	return table.concat(shown, ", ", 1, #shown - 1) .. " and " .. shown[#shown]
end

-- Pure: the line itself. names = list of strings, false for a hidden name.
function SpireFinds.line(kind, names, thing, ground)
	local who = SpireFinds.joinNames(names)
	if kind == "rare_weapon" then
		local item = type(thing) == "table" and thing.item or tostring(thing)
		local from = type(thing) == "table" and thing.from
		if from then
			return string.format("%s found %s%s on %s%s!", who, SpireFinds.article(item), item, SpireFinds.article(from), from)
		end
		return string.format("%s found %s%s!", who, SpireFinds.article(item), item)
	elseif kind == "fish" then
		local name = type(thing) == "table" and thing.name or tostring(thing)
		local kg = type(thing) == "table" and thing.kg
		return kg and string.format("%s landed %s (%.1f kg)!", who, name, kg) or string.format("%s landed %s!", who, name)
	elseif kind == "secret" then -- Jay, 2026-11-27: never the location; only the floor
		return string.format("Someone has found a secret on Floor %s.", tostring(tonumber(ground) or 1))
	elseif kind == "beast" then
		return string.format("A hidden beast has fallen somewhere on Floor %s.", tostring(ground or 1))
	elseif kind == "roamer_seen" then
		local g = SpireFinds.theGround(ground)
		local t = tostring(thing)
		local subject = t:match("^[Tt]he ") and ("The " .. t:sub(5)) or ("A " .. t)
		return g and string.format("%s has been sighted in %s!", subject, g) or (subject .. " has been sighted!")
	elseif kind == "roamer_killed" then
		return string.format("%s brought down %s!", who, SpireFinds.theThing(tostring(thing)))
	elseif kind == "keepsake" then
		local t = tostring(thing)
		return string.format("%s dug up %s%s!", who, SpireFinds.article(t), t)
	end
	return nil
end

-- Pure: may a server-wide line go out now? (last = time of the last one)
function SpireFinds.mayShout(last, now)
	return (now - (last or 0)) >= SpireFinds.GAP
end

-- Pure: keep the board to a week and BOARD_MAX entries, newest first
function SpireFinds.prune(list, now)
	local out = {}
	for _, e in ipairs(list or {}) do
		if now - (e.at or 0) <= SpireFinds.BOARD_DAYS * 86400 and #out < SpireFinds.BOARD_MAX then
			table.insert(out, e)
		end
	end
	return out
end

-- Pure: first-finder title for a number of firsts
function SpireFinds.firstTitle(count)
	local t = nil
	for _, row in ipairs(SpireFinds.FIRST_TITLES) do
		if count >= row[1] then
			t = row[2]
		end
	end
	return t
end

-- ---------------------------------------------------------------- storage
local function store()
	return kv.scoped("spirebound-finds")
end

local function firstsStore(season)
	return kv.scoped("spirebound-firsts"):scoped("s" .. tostring(season or (SpireSeason and SpireSeason.current() or 1)))
end

function SpireFinds.board()
	return SpireFinds.prune(store():get("board") or {}, os.time())
end

function SpireFinds.addBoard(text)
	local list = SpireFinds.board()
	table.insert(list, 1, { at = os.time(), text = text })
	store():set("board", SpireFinds.prune(list, os.time()))
end

function SpireFinds.clearBoard()
	store():remove("board")
end

-- Is this character hiding its name from find lines? (!finds anonymous)
function SpireFinds.isAnonymous(player)
	return player and player:kv():scoped("spirebound"):get("finds_anonymous") == true
end

function SpireFinds.setAnonymous(player, on)
	player:kv():scoped("spirebound"):set("finds_anonymous", on and true or false)
end

local function nameOf(x)
	if type(x) == "string" then
		local p = Player(x)
		if p and SpireFinds.isAnonymous(p) then
			return false
		end
		return x
	end
	if x and x.getName then
		return not SpireFinds.isAnonymous(x) and x:getName() or false
	end
	return false
end

-- The seam: server-wide line (rate-limited) and a board entry. Returns the line, and whether it was shouted.
function SpireFinds.announce(kind, names, thing, groundName)
	local shown = {}
	for _, n in ipairs(names or {}) do
		table.insert(shown, nameOf(n))
	end
	local text = SpireFinds.line(kind, shown, thing, groundName)
	if not text then
		return nil, false
	end
	SpireFinds.addBoard(text)
	local now = os.time()
	local shout = SpireFinds.mayShout(SpireFinds.lastLine, now)
	if shout then
		SpireFinds.lastLine = now
		Game.broadcastMessage(text, MESSAGE_EVENT_ADVANCE)
	end
	logger.info("[Spirebound] find: {}{}", text, shout and "" or " (board only)")
	return text, shout
end

-- ---------------------------------------------------------------- season firsts
-- Staff and the autopilot's test characters never take a first (same rule as floor clears)
function SpireFinds.isTester(player)
	if not player then
		return true
	end
	if player:getGroup():getAccess() or player:getGroup():getId() >= 4 then
		return true
	end
	if SpireFinds.testerOverride ~= nil then -- tests only
		return SpireFinds.testerOverride(player)
	end
	return Floors.onlyTesters({ player:getName() })
end

function SpireFinds.getFirst(category, id, season)
	return firstsStore(season):get(category .. ":" .. id)
end

function SpireFinds.allFirsts(season)
	local s = firstsStore(season)
	local out = {}
	local ok, keys = pcall(function() return s:keys() end)
	for _, k in ipairs(ok and keys or {}) do
		local r = s:get(k)
		if r then
			local cat, id = k:match("^([^:]+):(.+)$")
			table.insert(out, { category = cat, id = id, names = r.names or {}, at = r.at or 0, label = r.label or id })
		end
	end
	table.sort(out, function(a, b) return a.at > b.at end)
	return out
end

function SpireFinds.resetFirst(category, id, season)
	firstsStore(season):remove(category .. ":" .. id)
end

-- this character's firsts this season
function SpireFinds.firstCount(player, season)
	return player:kv():scoped("spirebound-firsts"):get("s" .. tostring(season or SpireSeason.current())) or 0
end

local function creditFirst(player)
	local season = SpireSeason.current()
	local n = SpireFinds.firstCount(player, season) + 1
	player:kv():scoped("spirebound-firsts"):set("s" .. season, n)
	local total = (player:kv():scoped("spirebound-firsts"):get("all") or 0) + 1 -- account history across seasons
	player:kv():scoped("spirebound-firsts"):set("all", total)
	local title = SpireFinds.firstTitle(n)
	local titles = player:kv():scoped("spirebound-titles")
	if title and not titles:get(title) then
		titles:set(title, os.time())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. title .. ".")
	end
	if n >= SpireFinds.WAKE_AT and SpireAuras then
		SpireAuras.give(player, "trailblazers_wake")
	end
	return n
end

-- The seam: record the first finder(s) of this season. players: list of Player objects (names of online players are
-- accepted). Test characters and staff are left out; if nobody real is left, nothing is recorded. True if first.
function SpireFinds.first(category, id, players, label)
	if SpireFinds.getFirst(category, id) then
		return false
	end
	local real, names = {}, {}
	for _, p in ipairs(players or {}) do
		if type(p) == "string" then
			p = Player(p)
		end
		if p and not SpireFinds.isTester(p) then
			table.insert(real, p)
			table.insert(names, p:getName())
		end
	end
	if #real == 0 then
		return false
	end
	firstsStore():set(category .. ":" .. id, { names = names, at = os.time(), label = label or id })
	for _, p in ipairs(real) do
		local n = creditFirst(p)
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("First this season! Your name goes on the Monument (%d first%s this season).", n, n == 1 and "" or "s"))
	end
	SpireSave.now("season first")
	return true
end

-- Pure-ish: board lines for the firsts of this season
function SpireFinds.firstLines(list, limit)
	local lines = {}
	for i, f in ipairs(list) do
		if limit and i > limit then
			break
		end
		local names = f.names or {}
		local who = #names > 3 and (table.concat(names, ", ", 1, 3) .. " and " .. (#names - 3) .. " more") or table.concat(names, ", ")
		table.insert(lines, string.format("  %s: %s (%s)", f.label or f.id, who, os.date("%d %b", f.at or 0)))
	end
	return lines
end
