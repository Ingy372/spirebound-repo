-- Season remix (DESIGN.md 4). Roadmap 8.2.
-- Each new season changes what veterans "know", automatically from the season number (season 1 = as designed):
--   * field bosses and floor bosses swap mechanics among themselves (Azhrakkar's ruin dance stays his),
--   * on every floor the big, medium and small rewards move between that floor's secrets (locations and hints stay,
--     special secrets like the Underkeep or Old Tusk keep their own reward).
-- New Underkeep wings and new floors are map work: MAP_REQUESTS.md.
SpireRemix = {}

-- Pure: tiny deterministic generator (same season -> same plan on every server start)
local function lcg(seed)
	local s = seed % 2147483647
	if s <= 0 then
		s = s + 2147483646
	end
	return function(n)
		s = (s * 16807) % 2147483647
		return (s % n) + 1
	end
end

-- Pure: shuffle a list for a season; season 1 returns it unchanged. Tries to move every element.
function SpireRemix.shuffle(list, season, salt)
	local out = {}
	for i, v in ipairs(list) do
		out[i] = v
	end
	if season <= 1 or #out < 2 then
		return out
	end
	local rnd = lcg(season * 7919 + (salt or 0))
	for _ = 1, 10 do
		for i = #out, 2, -1 do
			local j = rnd(i)
			out[i], out[j] = out[j], out[i]
		end
		local moved = true
		for i = 1, #out do
			if out[i] == list[i] then
				moved = false
			end
		end
		if moved then
			break
		end
	end
	return out
end

-- Pure: new field/boss patterns for a boss table { [floor] = { fieldPattern, bossPattern } }
function SpireRemix.bossPlan(bosses, season)
	local floors, fieldList, bossList, bossFloors = {}, {}, {}, {}
	for n in pairs(bosses) do
		table.insert(floors, n)
	end
	table.sort(floors)
	for _, n in ipairs(floors) do
		table.insert(fieldList, bosses[n].fieldPattern)
		if bosses[n].bossPattern ~= "ruin" then
			table.insert(bossList, bosses[n].bossPattern)
			table.insert(bossFloors, n)
		end
	end
	local f2 = SpireRemix.shuffle(fieldList, season, 1)
	local b2 = SpireRemix.shuffle(bossList, season, 2)
	local plan = {}
	for i, n in ipairs(floors) do
		plan[n] = { fieldPattern = f2[i], bossPattern = bosses[n].bossPattern }
	end
	for i, n in ipairs(bossFloors) do
		plan[n].bossPattern = b2[i]
	end
	return plan
end

function SpireRemix.applyBosses(bosses, season)
	for n, p in pairs(SpireRemix.bossPlan(bosses, season)) do
		bosses[n].fieldPattern = p.fieldPattern
		bosses[n].bossPattern = p.bossPattern
	end
end

-- Pure: secrets list -> { [id] = { tier, reward } } moves for a season (only plain gold/item rewards move)
function SpireRemix.secretPlan(list, season)
	local byFloor = {}
	for _, s in ipairs(list) do
		if type(s.reward) == "table" then
			byFloor[s.floor] = byFloor[s.floor] or {}
			table.insert(byFloor[s.floor], s)
		end
	end
	local plan = {}
	for floor, secrets in pairs(byFloor) do
		local prizes = {}
		for i, s in ipairs(secrets) do
			prizes[i] = i
		end
		local order = SpireRemix.shuffle(prizes, season, 100 + floor)
		for i, s in ipairs(secrets) do
			local from = secrets[order[i]]
			plan[s.id] = { tier = from.tier, reward = from.reward }
		end
	end
	return plan
end

function SpireRemix.applySecrets(list, season)
	local plan = SpireRemix.secretPlan(list, season)
	for _, s in ipairs(list) do
		local p = plan[s.id]
		if p then
			s.tier, s.reward = p.tier, p.reward
		end
	end
end
