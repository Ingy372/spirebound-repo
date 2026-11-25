-- Spire Chronicle (DESIGN.md 4; roadmap M3; Jay 2026-11-25: "love the idea"). A five-chapter journey per season, shared
-- by every character on an account. Chapters 1-2 teach the game; 3-5 ask for bosses, the Underkeep and secrets.
-- Finishing it gives a permanent seal and title (they grow with every season finished), a line on the Monument, a
-- house trophy and a mark in the Hall of Seasons. No experience or power: it is cosmetic, and seasons stay a fair race.
--
-- Progress lives on the ACCOUNT, keyed by season (kv account.<id>.spirebound-chronicle, "season-<n>"), so the season
-- wipe (which only clears player.* keys) keeps old seasons and a new season simply starts a new record.
-- Wiring: scripts/spirebound/chronicle.lua plus one line where each kind of progress happens.
SpireChronicle = {
	TROPHY = 5805, -- renamed "Chronicle Cup" by tools/gen_gear.py
	-- "add" tracks count up across all the account's characters; "max" tracks keep the best any character reached
	MAX_TRACKS = { level = true, floor = true, path = true },
	CHAPTERS = {
		{ name = "Arrival", text = "Learn the ways of the tower.", goals = {
			{ track = "level", need = 8, text = "Reach level 8" },
			{ track = "path", need = 1, text = "Choose a path at the Registrar" },
			{ track = "kill", need = 100, text = "Defeat 100 monsters" },
			{ track = "quest", need = 1, text = "Finish a quest" },
		} },
		{ name = "The Climber's Trade", text = "Make a living below the Spire.", goals = {
			{ track = "level", need = 20, text = "Reach level 20" },
			{ track = "task", need = 1, text = "Finish a hunting task" },
			{ track = "fish", need = 5, text = "Catch 5 fish" },
			{ track = "secret", need = 1, text = "Discover a secret" },
		} },
		{ name = "Through the Pass", text = "Break the guardians and climb.", goals = {
			{ track = "fieldboss", need = 1, text = "Defeat a field boss" },
			{ track = "floorboss", need = 1, text = "Defeat a floor boss" },
			{ track = "floor", need = 2, text = "Stand on Floor 2" },
			{ track = "beacon", need = 1, text = "Light a fire on a town's Beacon" },
		} },
		{ name = "Under the Keep", text = "Find what the tower hides.", goals = {
			{ track = "underkeep", need = 1, text = "Find the way into the Underkeep" },
			{ track = "secret", need = 5, text = "Discover 5 secrets" },
			{ track = "miniboss", need = 1, text = "Defeat a hidden beast" },
			{ track = "level", need = 50, text = "Reach level 50" },
		} },
		{ name = "The Season's Climb", text = "Leave your name on this season.", goals = {
			{ track = "floor", need = 4, text = "Stand on Floor 4" },
			{ track = "floorboss", need = 5, text = "Defeat 5 floor bosses" },
			{ track = "secret", need = 12, text = "Discover 12 secrets" },
			{ track = "level", need = 100, text = "Reach level 100" },
		} },
	},
	-- the seal's title by how many seasons' Chronicles the account has finished
	TITLES = { "Chronicler", "Seasoned Chronicler", "Elder Chronicler", "Grand Chronicler" },
}

-- Pure: the title for n finished Chronicles (n >= 1)
function SpireChronicle.titleFor(n)
	local t = SpireChronicle.TITLES
	return t[math.min(math.max(n, 1), #t)]
end

-- Pure: is goal g met by these counts?
function SpireChronicle.goalDone(counts, g)
	return (counts[g.track] or 0) >= g.need
end

-- Pure: record a step. rec = { counts = {}, chapter = 1.., finishedAt }. kind "add" adds n; "max" keeps the larger.
-- Returns the chapters finished by this step (a list of chapter numbers) and whether the whole Chronicle just finished.
function SpireChronicle.step(rec, track, n, now)
	rec.counts = rec.counts or {}
	rec.chapter = rec.chapter or 1
	if SpireChronicle.MAX_TRACKS[track] then
		if n > (rec.counts[track] or 0) then
			rec.counts[track] = n
		end
	else
		rec.counts[track] = (rec.counts[track] or 0) + n
	end
	local finished, done = {}, false
	while rec.chapter <= #SpireChronicle.CHAPTERS do
		local ch = SpireChronicle.CHAPTERS[rec.chapter]
		for _, g in ipairs(ch.goals) do
			if not SpireChronicle.goalDone(rec.counts, g) then
				return finished, done
			end
		end
		table.insert(finished, rec.chapter)
		rec.chapter = rec.chapter + 1
		if rec.chapter > #SpireChronicle.CHAPTERS then
			rec.finishedAt = now
			done = true
		end
	end
	return finished, done
end

-- Pure: the Journal's Chronicle tab. legacy = number of Chronicles finished in earlier seasons.
function SpireChronicle.lines(rec, season, legacy)
	local out = { string.format("Season %d. Shared by every character on your account. Cosmetic rewards only.", season) }
	if legacy and legacy > 0 then
		table.insert(out, string.format("Your seal: %s (%d season%s finished).", SpireChronicle.titleFor(legacy), legacy, legacy == 1 and "" or "s"))
	end
	local counts, chapter = rec.counts or {}, rec.chapter or 1
	for i, ch in ipairs(SpireChronicle.CHAPTERS) do
		local mark = i < chapter and "[done]" or (i == chapter and "[now]" or "[later]")
		table.insert(out, string.format("%s Chapter %d: %s. %s", mark, i, ch.name, ch.text))
		if i == chapter then
			for _, g in ipairs(ch.goals) do
				local have = math.min(counts[g.track] or 0, g.need)
				table.insert(out, string.format("[%s] %s (%d/%d)", have >= g.need and "x" or " ", g.text, have, g.need))
			end
		end
	end
	if chapter > #SpireChronicle.CHAPTERS then
		table.insert(out, "You finished this season's Chronicle. Your name is on the Monument.")
	else
		table.insert(out, "Finish all five for the Chronicle seal, a title, a line on the Monument and a Chronicle Cup for your house.")
	end
	return out
end

-- Live state ---------------------------------------------------------------
local function accountStore(accountId)
	return kv.scoped("account"):scoped(tostring(accountId)):scoped("spirebound-chronicle")
end

function SpireChronicle.get(accountId, season)
	return accountStore(accountId):get("season-" .. (season or SpireSeason.current())) or { counts = {}, chapter = 1 }
end

function SpireChronicle.put(accountId, rec, season)
	accountStore(accountId):set("season-" .. (season or SpireSeason.current()), rec)
end

-- Chronicles this account finished in earlier seasons (and this one, once done)
function SpireChronicle.legacyCount(accountId)
	return #(SpireSeason.accountKv(accountId):get("chronicles") or {})
end

-- names who finished this season's Chronicle, for the Monument
local function finishers(season)
	return kv.scoped("spirebound-chronicle-finishers"):get("season-" .. season) or {}
end
SpireChronicle.finishers = finishers

local function reward(player, season)
	local acc = SpireSeason.accountKv(player:getAccountId())
	local list = acc:get("chronicles") or {}
	table.insert(list, season)
	acc:set("chronicles", list)
	local title = SpireChronicle.titleFor(#list)
	local titles = acc:get("titles") or {} -- account-wide: every character, every season (SpireSeason.applyLegacy)
	titles[title] = titles[title] or season
	acc:set("titles", titles)
	player:kv():scoped("spirebound-titles"):set(title, os.time())
	local names = finishers(season)
	table.insert(names, player:getName())
	kv.scoped("spirebound-chronicle-finishers"):set("season-" .. season, names)
	local inbox = player.getStoreInbox and player:getStoreInbox()
	local cup = (inbox and inbox:addItem(SpireChronicle.TROPHY, 1)) or player:addItem(SpireChronicle.TROPHY, 1)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You finished the Spire Chronicle of Season %d! Your seal: \"%s\". Your name is carved on the Monument%s.",
		season, title, cup and ", and a Chronicle Cup waits for your house" or ""))
	Game.broadcastMessage(string.format("%s has finished the Spire Chronicle of Season %d!", player:getName(), season), MESSAGE_EVENT_ADVANCE)
	player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
end

-- Count progress for a player's account. Botting (built-in cavebot) never counts, like the Season Path.
function SpireChronicle.add(player, track, n)
	if not player or not player.getAccountId then
		return
	end
	if SpireCavebot and SpireCavebot.blocksRewards(player) then
		return
	end
	local acc, season = player:getAccountId(), SpireSeason.current()
	local rec = SpireChronicle.get(acc, season)
	if rec.finishedAt then
		return
	end
	local before = rec.counts and rec.counts[track] or 0
	local finished, done = SpireChronicle.step(rec, track, n or 1, os.time())
	if (rec.counts[track] or 0) == before and #finished == 0 then
		return -- nothing changed (a "max" track below the best): no write
	end
	SpireChronicle.put(acc, rec, season)
	for _, c in ipairs(finished) do
		local ch = SpireChronicle.CHAPTERS[c]
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Spire Chronicle: chapter %d, \"%s\", is done!%s", c, ch.name,
			SpireChronicle.CHAPTERS[c + 1] and (" Next: \"" .. SpireChronicle.CHAPTERS[c + 1].name .. "\" (Journal, Chronicle tab).") or ""))
	end
	if done then
		reward(player, season)
	end
end

-- Shortcut for "max" tracks
function SpireChronicle.reach(player, track, value)
	SpireChronicle.add(player, track, value)
end
