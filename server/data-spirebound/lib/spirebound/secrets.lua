-- Secrets and the Info Broker (DESIGN.md 8.1, Jay's rules). Roadmap 2.7 / 2.8.
-- 1. Touching a secret's trigger records it as YOUR discovery.
-- 2. You may sell it to the Info Broker (Vesper): you get paid, it becomes public (announcement + broker list).
-- 3. Keeping it private never locks anyone out. Others can still find it themselves.
-- 4. Once public it can't be sold again; earlier finders keep their discovery record (it counts for titles).

SpireSecrets = {
	FLOOR_BASE = { [1] = 1500, [2] = 3500, [3] = 6000, [4] = 10000, [5] = 16000, [6] = 22000, [7] = 30000, [8] = 40000, [9] = 52000, [10] = 66000 },
	TIER = { small = 1, medium = 2, large = 4 },
	TITLES = { { 10, "Wanderer" }, { 50, "Pathfinder" }, { 100, "Cartographer of the Spire" } },
	list = {}, -- filled below
	byPos = {}, -- "x:y:z" -> secret (built at startup from WorldPoints)
}

-- reward: function(player, secret) run once, the first time this character finds it
SpireSecrets.list = {
	{ id = "s1", floor = 1, tier = "large", name = "The Underkeep", hint = "Something echoes beneath the drain grate in Hearthgate's south-west corner.", reward = "underkeep" },
	{ id = "s2", floor = 1, tier = "large", name = "Old Tusk", hint = "East of the boar meadow, a mud wallow nobody dares to step in.", reward = "old_tusk" },
	{ id = "s3", floor = 1, tier = "medium", name = "Miller's Race", hint = "Something hides under the Millcross mill.", reward = { gold = 800 } },
	{ id = "s4", floor = 1, tier = "medium", name = "Inn Smith", hint = "The Millcross inn's pantry shelf is not what it seems.", reward = { items = { { 236, 3 } } } },
	{ id = "s5", floor = 1, tier = "small", name = "North Crack", hint = "A crack in the old quarry's wall leads somewhere useful.", reward = "north_crack" },
	{ id = "s6", floor = 1, tier = "small", name = "Firefly Hollow", hint = "Behind the Millcross well, after dark.", night = true, reward = { items = { { 2915, 1 } } } },
	{ id = "s7", floor = 1, tier = "medium", name = "Sealed Shrine", hint = "A ruined shrine along the bandit road. Bring friends.", reward = "sealed_shrine" },
	{ id = "s8", floor = 1, tier = "medium", name = "Dye Well", hint = "Odd stone plates in the shard fields.", reward = { gold = 1200 } },
	{ id = "s9", floor = 1, tier = "small", name = "Empty Camp", hint = "An abandoned bedroll deep in the wolf copse.", reward = { gold = 300, text = "A torn diary: \"The Axe-Lord's book lies. When he drops the axe, run.\"" } },
	{ id = "s10", floor = 1, tier = "medium", name = "Well Vein", hint = "The ruined well in the far south-east corner of the plains.", reward = { items = { { 3035, 10 } } } },
	{ id = "s11", floor = 1, tier = "small", name = "Coward Pup", hint = "Inside the bramble ring of the thornsnap hollow.", reward = { items = { { 3577, 5 } } } },
	{ id = "s12", floor = 1, tier = "small", name = "Gate Balcony", hint = "A broken stair on a ruined tower near the Pass. What a view.", reward = { gold = 400 } },
}

-- Pure helpers ---------------------------------------------------------
function SpireSecrets.payout(secret)
	return (SpireSecrets.FLOOR_BASE[secret.floor] or 1500) * (SpireSecrets.TIER[secret.tier] or 1)
end

-- Can `sellerFound` (bool: this player found it) sell, given `publicBy` (nil or seller name)?
function SpireSecrets.canSell(sellerFound, publicBy)
	if not sellerFound then
		return false, "You haven't found that one yourself."
	end
	if publicBy then
		return false, "Everyone knows that one already. " .. publicBy .. " sold it."
	end
	return true
end

function SpireSecrets.titleFor(count)
	local t = nil
	for _, row in ipairs(SpireSecrets.TITLES) do
		if count >= row[1] then
			t = row[2]
		end
	end
	return t
end

function SpireSecrets.isNight(hour)
	return hour >= 20 or hour < 5
end

function SpireSecrets.get(id)
	for _, s in ipairs(SpireSecrets.list) do
		if s.id == id then
			return s
		end
	end
	return nil
end

-- Storage ---------------------------------------------------------------
local function mine(player)
	return player:kv():scoped("spirebound-secrets")
end

local function public()
	return kv.scoped("spirebound-secrets-public")
end

function SpireSecrets.hasFound(player, id)
	return mine(player):get(id) ~= nil
end

function SpireSecrets.foundList(player)
	local out = {}
	for _, s in ipairs(SpireSecrets.list) do
		if SpireSecrets.hasFound(player, s.id) then
			table.insert(out, s)
		end
	end
	return out
end

function SpireSecrets.publicBy(id)
	local r = public():get(id)
	return r and r.by or nil
end

function SpireSecrets.markPublic(id, sellerName)
	public():set(id, { by = sellerName, at = os.time() })
	SpireSave.now("secret sold") -- R8: a sale (and its gold) is never lost to a crash
end

function SpireSecrets.unpublish(id)
	public():remove(id)
end

function SpireSecrets.forget(player, id)
	mine(player):remove(id)
end

function SpireSecrets.record(player, secret)
	mine(player):set(secret.id, os.time())
	local count = #SpireSecrets.foundList(player)
	local title = SpireSecrets.titleFor(count)
	if title then
		player:kv():scoped("spirebound-titles"):set(title, os.time())
	end
	return count
end
