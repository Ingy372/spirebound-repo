-- One thing only that ground has (roadmap FD2; docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.2).
-- Every Floor 1 hunting ground has one feature that is used, not just seen. The map places what stands still
-- (maps/floor1_features.py, spots named "feat_..."); scripts/spirebound/ground_features.lua runs them.
-- Numbers: tools/gen_depth.py (SpireDepthData.features). The first use of each marks a "Ground lore" row.
SpireFeatures = SpireFeatures or { cool = {}, state = {} }

SpireFeatures.AID = { bell = 47201, nest = 47202, truffle = 47203, mole = 47204, howl = 47205, tidenest = 47206,
	tidechest = 47207, vine = 47208, chime = 47209, cache = 47210, poster = 47211, winch = 47212, signal = 47213,
	stash = 47214, ballista = 47215, seedling = 47216 }
SpireFeatures.AID_MIN, SpireFeatures.AID_MAX = 47200, 47299

SpireFeatures.byGround = {}
for _, f in ipairs(SpireDepthData.features) do
	SpireFeatures.byGround[f.id] = f
end

function SpireFeatures.conf(gid, key)
	local f = SpireFeatures.byGround[gid]
	return f and f[key]
end

-- ---------------------------------------------------------------- pure
-- Pure: may `who` use `what` again? cool = table key -> time it frees up
function SpireFeatures.ready(cool, key, now)
	local t = cool[key]
	return not t or t <= now, t and math.max(0, t - now) or 0
end

-- Pure: minutes, rounded up, for a "come back in" line
function SpireFeatures.minutes(secs)
	return math.max(1, math.ceil(secs / 60))
end

-- Pure: is the tide low at `now`? (every `every` seconds, low for the first `low` of them)
function SpireFeatures.tideLow(now, every, low)
	return (now % every) < low
end

-- Pure: the chime order for a wind (a shuffle of 1..4 from a seed)
function SpireFeatures.windOrder(seed)
	local order, r = { 1, 2, 3, 4 }, seed
	for i = 4, 2, -1 do
		r = (r * 1103515245 + 12345) % 2147483648
		local j = (r % i) + 1
		order[i], order[j] = order[j], order[i]
	end
	return order
end

-- Pure: does `played` (a list) follow `order` so far? -> "wrong" | "more" | "done"
function SpireFeatures.chimeStep(order, played)
	for i, n in ipairs(played) do
		if order[i] ~= n then
			return "wrong"
		end
	end
	return #played >= #order and "done" or "more"
end

-- Pure: pick which vine walls stand this time (share of `n`, at least one open, at least one closed); rand(n) -> 1..n
function SpireFeatures.pickVines(n, share, rand)
	local want = math.max(1, math.min(n - 1, math.floor(n * share + 0.5)))
	local idx = {}
	for i = 1, n do
		idx[i] = i
	end
	for i = n, 2, -1 do
		local j = rand(i)
		idx[i], idx[j] = idx[j], idx[i]
	end
	local out = {}
	for i = 1, want do
		out[idx[i]] = true
	end
	return out
end

-- Pure: the night, by the game's clock (the secrets' rule)
function SpireFeatures.isNight()
	return SpireSecrets and SpireSecrets.isNight(SpireSecrets.gameHour()) or false
end

-- ---------------------------------------------------------------- the map's spots
function SpireFeatures.points(prefix)
	local out, i = {}, 1
	while WorldPoints[prefix .. i] do
		table.insert(out, WorldPoints[prefix .. i])
		i = i + 1
	end
	return out
end

-- ---------------------------------------------------------------- ground lore
function SpireFeatures.lore(player, gid)
	if not player or not SpireDiscoveries then
		return false
	end
	local first = SpireDiscoveries.mark(player, "groundlore", gid)
	if first then
		local f = SpireFeatures.byGround[gid]
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Ground lore: %s. A new row on your Discoveries page.", f and f.name or gid))
	end
	return first
end
