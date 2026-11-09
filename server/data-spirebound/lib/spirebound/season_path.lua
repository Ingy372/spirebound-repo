-- Season Path (DESIGN.md 15): a free reward track. Daily and weekly goals give points; every 100 points is a
-- tier with a cosmetic reward (house furniture, tapestries, titles). Never power. Resets with the season.
SpirePath = { TIER_POINTS = 100 }

SpirePath.GOALS = {
	{ id = "d_hunt", period = "day", track = "kill", need = 300, pts = 10, text = "Defeat 300 monsters" },
	{ id = "d_combo", period = "day", track = "combo", need = 25, pts = 10, text = "Land 25 sword-skill combos" },
	{ id = "d_fish", period = "day", track = "fish", need = 5, pts = 10, text = "Catch 5 fish" },
	{ id = "w_hunt", period = "week", track = "kill", need = 3000, pts = 40, text = "Defeat 3,000 monsters" },
	{ id = "w_boss", period = "week", track = "boss", need = 3, pts = 40, text = "Defeat 3 bosses" },
	{ id = "w_task", period = "week", track = "task", need = 2, pts = 40, text = "Finish 2 hunting tasks" },
	{ id = "w_secret", period = "week", track = "secret", need = 1, pts = 40, text = "Discover a secret" },
}

-- tier -> reward. item = takeable furniture kit / decoration (checked against appearances.dat); title = account-free title
SpirePath.REWARDS = {
	{ item = 2785, name = "a big table kit" }, { item = 2779, name = "a sofa chair kit" }, { item = 2659, name = "a blue tapestry" },
	{ item = 2798, name = "a table lamp kit" }, { title = "Pathwalker" },
	{ item = 2811, name = "an indoor plant kit" }, { item = 2790, name = "a dresser kit" }, { item = 2664, name = "a cuckoo clock" },
	{ item = 2797, name = "a globe kit" }, { title = "Trailblazer" },
	{ item = 2796, name = "a birdcage kit" }, { item = 2656, name = "a red tapestry" }, { item = 2800, name = "a rocking horse kit" },
	{ item = 2799, name = "a telescope kit" }, { title = "Wayfarer of the Spire" },
	{ item = 2801, name = "a pendulum clock kit" }, { item = 2808, name = "a harp kit" }, { item = 2647, name = "a green tapestry" },
	{ item = 2805, name = "a large amphora kit" }, { title = "Summit Seeker" },
	{ item = 2802, name = "a knight statue kit" }, { item = 2803, name = "a minotaur statue kit" }, { item = 2667, name = "a white tapestry" },
	{ item = 2911, name = "a candelabrum" }, { title = "Pilgrim of the Spire" },
	{ item = 2807, name = "a piano kit" }, { item = 872, name = "a trophy stand" }, { item = 2644, name = "a purple tapestry" },
	{ item = 2806, name = "a coal basin kit" }, { title = "Path Champion" },
}

-- Pure: period number for "day" or "week" (weeks start on Monday, server time)
function SpirePath.periodOf(kind, now)
	local day = math.floor(now / 86400)
	if kind == "week" then
		return math.floor((day + 3) / 7) -- 1970-01-01 was a Thursday
	end
	return day
end

-- Pure: add n to every goal that follows `track`. state = { points, buckets = { [goalId] = {p, c, done} } }.
-- Returns points earned and the goals finished by this step.
function SpirePath.advance(state, track, n, now)
	state.points = state.points or 0
	state.buckets = state.buckets or {}
	local earned, finished = 0, {}
	for _, g in ipairs(SpirePath.GOALS) do
		if g.track == track then
			local p = SpirePath.periodOf(g.period, now)
			local b = state.buckets[g.id]
			if not b or b.p ~= p then
				b = { p = p, c = 0, done = false }
			end
			b.c = b.c + n
			if not b.done and b.c >= g.need then
				b.done = true
				earned = earned + g.pts
				table.insert(finished, g)
			end
			state.buckets[g.id] = b
		end
	end
	state.points = state.points + earned
	return earned, finished
end

-- Pure: tiers unlocked by a point total
function SpirePath.tierFor(points)
	return math.min(#SpirePath.REWARDS, math.floor((points or 0) / SpirePath.TIER_POINTS))
end

-- Pure: progress lines for the !path window
function SpirePath.lines(state, now)
	local out = {}
	for _, g in ipairs(SpirePath.GOALS) do
		local b = (state.buckets or {})[g.id]
		local c, done = 0, false
		if b and b.p == SpirePath.periodOf(g.period, now) then
			c, done = b.c, b.done
		end
		table.insert(out, string.format("[%s] %s (%s): %d/%d  +%d", done and "x" or " ", g.text, g.period == "day" and "today" or "this week", math.min(c, g.need), g.need, g.pts))
	end
	return out
end

-- Live state ---------------------------------------------------------------
local function store(player)
	return player:kv():scoped("spirebound-path")
end

function SpirePath.state(player)
	return store(player):get("state") or { points = 0, buckets = {}, claimed = 0 }
end

local function grant(player, reward, tier)
	if reward.title then
		player:kv():scoped("spirebound-titles"):set(reward.title, os.time())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Season Path tier %d: you earned the title \"%s\".", tier, reward.title))
		return
	end
	local inbox = player.getStoreInbox and player:getStoreInbox()
	local ok = inbox and inbox:addItem(reward.item, 1) or player:addItem(reward.item, 1)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Season Path tier %d: %s%s.", tier, reward.name, ok and " (in your store inbox)" or ""))
end

-- Count progress for a player. Botting (built-in cavebot) never counts towards the Path.
function SpirePath.progress(player, track, n)
	if SpireCavebot and SpireCavebot.blocksRewards(player) then
		return
	end
	local st = SpirePath.state(player)
	st.claimed = st.claimed or 0
	local earned, finished = SpirePath.advance(st, track, n or 1, os.time())
	for _, g in ipairs(finished) do
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Season Path goal done: %s (+%d points, %d total).", g.text, g.pts, st.points))
	end
	local tier = SpirePath.tierFor(st.points)
	while st.claimed < tier do
		st.claimed = st.claimed + 1
		grant(player, SpirePath.REWARDS[st.claimed], st.claimed)
	end
	if earned > 0 or n then
		store(player):set("state", st)
	end
end
