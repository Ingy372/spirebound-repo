-- Spire Siege (DESIGN.md 15). Roadmap 5.7d.
-- Weekly guild battle for the keep. Guild members sign up, everyone fights on equal footing (same health and mana,
-- fixed hits and heals, like the Arena), and a guild scores a point every 5 seconds while only its members stand in
-- the throne room. After 30 minutes the guild with the most points holds the keep for a week: +5% XP and loot for
-- its members and the "Keeper of the Spire" banner title for the guild leader.
SpireSiege = {
	HP = 1500, MANA = 1000,
	MIN_GUILDS = 2, MIN_MEMBERS = 2, MIN_LEVEL = 20,
	SIGNUP_TIME = 15 * 60, DURATION = 30 * 60, TICK = 5,
	BUFF = 0.05, HOLD_TIME = 7 * 86400,
	DAY = 1, HOUR = 20, -- Sunday (os.date %w: 0 = Sunday; here 1 = Lua wday Sunday), 20:00 server time; sign-ups 15 minutes earlier
	TITLE = "Keeper of the Spire",
}

function SpireSiege.new(now)
	return { phase = "signup", opened = now, players = {}, guilds = {}, score = {}, order = {} }
end

function SpireSiege.join(st, id, name, level, guildId)
	if st.phase ~= "signup" then
		return false, "Sign-ups are closed."
	end
	if not guildId or guildId == 0 then
		return false, "Only guild members can join the Siege."
	end
	if level < SpireSiege.MIN_LEVEL then
		return false, "You need level " .. SpireSiege.MIN_LEVEL .. " to fight in the Siege."
	end
	if st.players[id] then
		return false, "You are already signed up."
	end
	st.players[id] = { name = name, guild = guildId, alive = true }
	st.guilds[guildId] = (st.guilds[guildId] or 0) + 1
	table.insert(st.order, id)
	return true
end

function SpireSiege.leave(st, id)
	local p = st.players[id]
	if p and p.alive then
		p.alive = false
		st.guilds[p.guild] = st.guilds[p.guild] - 1
	end
end

-- Guilds with enough members take part; the rest are sent home. Returns true or false + reason.
function SpireSiege.start(st, now)
	local valid, n = {}, 0
	for g, count in pairs(st.guilds) do
		if count >= SpireSiege.MIN_MEMBERS then
			valid[g] = true
			n = n + 1
		end
	end
	if n < SpireSiege.MIN_GUILDS then
		st.phase = "cancelled"
		return false, "Fewer than two guilds brought enough fighters."
	end
	for _, id in ipairs(st.order) do
		local p = st.players[id]
		if not valid[p.guild] then
			p.alive = false
			p.dropped = true
		end
	end
	st.gates = {}
	local i = 0
	local gids = {}
	for g in pairs(valid) do
		table.insert(gids, g)
	end
	table.sort(gids)
	for _, g in ipairs(gids) do
		st.gates[g] = (i % 4) + 1
		st.score[g] = 0
		i = i + 1
	end
	st.phase = "running"
	st.started = now
	return true
end

function SpireSiege.canHit(st, aId, vId)
	local a, v = st and st.players[aId], st and st.players[vId]
	if not st or st.phase ~= "running" or not a or not v or not a.alive or not v.alive then
		return false
	end
	return a.guild ~= v.guild
end

-- Throne tick: ids standing in the throne room. Exactly one guild present scores. Returns that guild or nil.
function SpireSiege.tick(st, holders)
	local present, count = nil, 0
	local seen = {}
	for _, id in ipairs(holders) do
		local p = st.players[id]
		if p and p.alive and not seen[p.guild] then
			seen[p.guild] = true
			present = p.guild
			count = count + 1
		end
	end
	if count == 1 then
		st.score[present] = (st.score[present] or 0) + 1
		return present
	end
	return nil
end

-- Over? Returns the winning guild id, 0 for "nobody" (tie or no points), or nil while running.
-- previousHolder keeps the keep on a tie for the top score.
function SpireSiege.result(st, now, previousHolder)
	if st.phase ~= "running" then
		return nil
	end
	local standing = {}
	for _, id in ipairs(st.order) do
		local p = st.players[id]
		if p.alive then
			standing[p.guild] = true
		end
	end
	local left = 0
	local last
	for g in pairs(standing) do
		left = left + 1
		last = g
	end
	if left <= 1 then
		return last or 0 -- everyone else left
	end
	if now - st.started < SpireSiege.DURATION then
		return nil
	end
	local best, bestScore, tie = 0, 0, false
	for g, s in pairs(st.score) do
		if s > bestScore then
			best, bestScore, tie = g, s, false
		elseif s == bestScore and s > 0 then
			tie = true
		end
	end
	if tie then
		if previousHolder and st.score[previousHolder] == bestScore then
			return previousHolder
		end
		return 0
	end
	return best
end

-- Pure: buff factor for a player's guild given the holder record
function SpireSiege.buffFor(guildId, holder, now)
	if holder and guildId and guildId ~= 0 and holder.guild == guildId and now < holder.untilTime then
		return 1 + SpireSiege.BUFF
	end
	return 1
end

-- Live holder record (kv; cleared at season end via spirebound-siege prefix)
function SpireSiege.holder()
	return kv.scoped("spirebound-siege"):get("holder")
end

function SpireSiege.factor(player)
	local g = player:getGuild()
	return SpireSiege.buffFor(g and g:getId() or 0, SpireSiege.holder(), os.time())
end
