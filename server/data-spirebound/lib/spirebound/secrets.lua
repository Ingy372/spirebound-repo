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

-- reward: a string = a special reward run by scripts/spirebound/secrets.lua every time (the way in, a beast, a fight);
-- a table = what this character keeps, given once: title, aura (lib/spirebound/auras.lua), keepsake (a house piece),
-- gear (a secret-only ring, amulet or boots: SpireGearData.secretGear), items, text. Every secret also pays the
-- floor's purse once per account (adventure layer 4.1; Jay, 2026-11-27: "(always) a medium gold reward").
-- title on the secret itself stays with the place even when the season remix moves the table rewards (roadmap 8.4).
-- hint: a riddle (Jay, 2026-11-27: "the only hints i want for the secrets need to be coded in thick riddles"): no place
-- name, no direction, no NPC name. Nobody sees it unless the secret was sold (Vesper's list) or a message bottle gave it.
-- Rewards are never named in a hint, on Vesper's list or on the Discoveries page.
SpireSecrets.list = {
	{ id = "s1", floor = 1, tier = "large", name = "The Underkeep", title = "Underkeeper", reward = "underkeep",
		hint = "Where buyers haggle and boast, iron teeth drink the rain. Follow the water where it goes, and you will hear the old cells breathing." },
	{ id = "s2", floor = 1, tier = "large", name = "Old Tusk", reward = "old_tusk",
		hint = "The bristled ones roll in every bath but one. That one they leave alone, and so should you, unless you want to wake the grandfather." },
	{ id = "s3", floor = 1, tier = "large", name = "Miller's Race", reward = { gear = "millrace_boots" },
		hint = "A wheel that never tires turns above a road that no cart has ever used. Go beneath the grinding and run where the water ran." },
	{ id = "s4", floor = 1, tier = "medium", name = "Inn Smith", reward = { title = "Regular", keepsake = "inn_tankard" },
		hint = "Where the weary eat and sleep, the bread is not all that is kept on the shelf. Push past the larder and listen for a hammer." },
	{ id = "s5", floor = 1, tier = "small", name = "North Crack", title = "Cragfinder", reward = "north_crack",
		hint = "Men cut the hill down to its bones, and the hill cut back. One seam is too thin for a cart, but wide enough for a climber." },
	{ id = "s6", floor = 1, tier = "small", name = "Firefly Hollow", night = true, reward = { aura = "fireflies", items = { { 2915, 1 } } },
		hint = "Toss no coin and wish for nothing. Walk around behind the cold stone throat when the sky is black, and the little lanterns will meet you." },
	{ id = "s7", floor = 1, tier = "large", name = "Sealed Shrine", reward = "sealed_shrine",
		hint = "The ones who pray to nobody have pitched their tents beside a house of prayer. Its door was shut for a reason. Do not knock alone." },
	{ id = "s8", floor = 1, tier = "medium", name = "Dye Well", reward = { aura = "dyers_drift" },
		hint = "Among a field of broken glitter, some stones were laid by hands, not by the fall. Read their colours, and drink where they point." },
	{ id = "s9", floor = 1, tier = "small", name = "Empty Camp", reward = { text = "A torn diary: \"The Axe-Lord's book lies. When he drops the axe, run.\"" },
		hint = "A sleeper left his bed where the grey ones run together. He never came back for it. Something else did." },
	{ id = "s10", floor = 1, tier = "medium", name = "Well Vein", reward = {}, -- tester 2026-11-26: was 10 platinum as an item, paid to every character
		hint = "Where the green runs out of names, a dry stone throat still swallows. Whatever lives below it has learned to breathe water." },
	{ id = "s11", floor = 1, tier = "small", name = "Coward Pup", reward = { items = { { 3577, 5 } } },
		hint = "Inside a ring of teeth that flower, the smallest thing hides from everyone. Be kind to it, or meet its mother." },
	{ id = "s13", floor = 1, tier = "large", name = "Forgotten Cell", reward = { gear = "wardens_signet" },
		hint = "A jailer's mistake was mortared over and forgotten. Where keys once turned, find the wall that is younger than the rest." },
	{ id = "s12", floor = 1, tier = "small", name = "Gate Balcony", reward = { title = "Skywatcher", keepsake = "brass_spyglass" },
		hint = "A stair that leads nowhere still leads somewhere. Climb what is broken beside the way up, and look down on all of it." },
}

-- The purse every secret pays once per account: the floor's medium payout divided by three (1,000 gold on Floor 1)
function SpireSecrets.purse(floor)
	return math.floor((SpireSecrets.FLOOR_BASE[floor] or 1500) * SpireSecrets.TIER.medium / 3 + 0.5)
end

-- Riddles a character holds from message bottles (adventure layer 4.7)
function SpireSecrets.heldRiddles(player)
	return player:kv():scoped("spirebound-riddles")
end

function SpireSecrets.holdsRiddle(player, id)
	return SpireSecrets.heldRiddles(player):get(id) ~= nil
end

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

-- R17: night is the game's own night (the client's light), not the server's clock
function SpireSecrets.gameHour()
	return math.floor((getWorldTime and getWorldTime() or (tonumber(os.date("%H")) * 60)) / 60) % 24
end

-- R17: a secret's gold is paid once per ACCOUNT (a second character finding it gets the discovery, not the gold)
function SpireSecrets.goldPaid(accountId, id)
	return kv.scoped("account"):scoped(tostring(accountId)):scoped("spirebound-secretgold"):get(id) ~= nil
end

function SpireSecrets.markGoldPaid(accountId, id)
	kv.scoped("account"):scoped(tostring(accountId)):scoped("spirebound-secretgold"):set(id, os.time())
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
