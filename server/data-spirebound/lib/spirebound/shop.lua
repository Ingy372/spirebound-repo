-- Donation shop (DESIGN.md 11). Roadmap 7.2. OFF until public launch (SpireShop.ENABLED).
-- Only cosmetics, house decorations and conveniences. Never power: the catalog test fails the build if an item
-- has any attack, defense or armor, or if shop items could be bet. Prices are placeholders until Jay picks (7.3).
SpireShop = {
	ENABLED = false,
	CURRENCY = "Spire Coins", -- account-wide; granted by the payment system (7.3) or by the owner with /shopgrant
	KINDS = { furniture = true, outfit = true, mount = true, decoration = true, house = true, gear = true, respec = true },
	RESPEC_ITEM = 28650, -- the Mastery Respec Scroll (named by tools/gen_gear.py)
}

-- kind: furniture/decoration = a takeable item (item id); outfit = lookType (+addons 3); mount = mount id.
SpireShop.catalog = {
	{ id = "sofa_pair", kind = "furniture", name = "a sofa chair kit", price = 50, item = 2779 },
	{ id = "grand_piano", kind = "furniture", name = "a piano kit", price = 150, item = 2807 },
	{ id = "harp", kind = "furniture", name = "a harp kit", price = 100, item = 2808 },
	{ id = "telescope", kind = "furniture", name = "a telescope kit", price = 80, item = 2799 },
	{ id = "goblin_statue", kind = "decoration", name = "a goblin statue kit", price = 60, item = 2804 },
	{ id = "minotaur_statue", kind = "decoration", name = "a minotaur statue kit", price = 60, item = 2803 },
	{ id = "candelabrum", kind = "decoration", name = "a candelabrum", price = 40, item = 2911 },
	{ id = "red_tapestry", kind = "decoration", name = "a red tapestry", price = 30, item = 2656 },
	{ id = "outfit_hearth_cloak", kind = "outfit", name = "Hearth Cloak outfit", price = 400, lookType = 129 }, -- placeholder look until art arrives
	{ id = "outfit_tower_mantle", kind = "outfit", name = "Tower Mantle outfit", price = 400, lookType = 130 },
	{ id = "mount_stone_hound", kind = "mount", name = "Stone Hound mount", price = 500, mount = 1 },
	-- Gear progression (Jay, 2026-11-23: "the shop should have some gear that gets outclassed later"; respecs "the only way to acquire one").
	-- The starter set (weapon + armour for the buyer's class) cannot be upgraded and is beaten by the Floor 1 weapon at tier 2.
	{ id = "starter_set", kind = "gear", name = "the Climber's starter set (weapon and armour for your class, levels 1-15)", price = 300 },
	{ id = "mastery_respec", kind = "respec", name = "a Mastery Respec Scroll (choose your style again)", price = 500, item = 28650 },
	-- Spire Manor: the only way to own it (Jay, 2026-11-11: "pay to obtain only"). Cosmetic: no stats, no bonuses.
	{ id = "spire_manor", kind = "house", name = "the deed to Spire Manor (Hearthgate)", price = 5000, house = "Spire Manor" },
}

-- Houses that only the shop can hand out (!buyhouse refuses them)
SpireShop.SHOP_HOUSES = { ["Spire Manor"] = true }

-- Pure: may this player take this shop house? owner guid of the house (0 = free), does the player own a house already,
-- and (review S-1) the Manor's first refusal: last = { account, season } of its last buyer, or nil.
SpireShop.MANOR_REFUSAL_DAYS = 7
function SpireShop.houseAvailable(ownerGuid, playerHasHouse, accountId, last, season, seasonStartedAt, now)
	if (ownerGuid or 0) ~= 0 then
		return false, "Spire Manor already has an owner this season."
	end
	if playerHasHouse then
		return false, "Leave your current house first: a climber can own one house."
	end
	if last and accountId and last.account ~= accountId and (last.season or 0) < (season or 0)
		and (now or 0) < (seasonStartedAt or 0) + SpireShop.MANOR_REFUSAL_DAYS * 86400 then
		return false, "Spire Manor is held for last season's owner for the first " .. SpireShop.MANOR_REFUSAL_DAYS
			.. " days of the season."
	end
	return true
end

-- Review S-1: a season wipe deletes characters, so takeable shop items (furniture, decorations) would be lost with
-- them. Each purchase is counted on the ACCOUNT (kept by the wipe); the first character to log in in a new season gets
-- them all again in its Store Inbox. Pure: what to hand back. bought = { [id] = count }, deliveredSeason = the season
-- they were last handed over (or bought) in.
SpireShop.REDELIVER = { furniture = true, decoration = true }
function SpireShop.toRedeliver(bought, deliveredSeason, season)
	if (deliveredSeason or 0) >= season then
		return {}
	end
	local out = {}
	for _, e in ipairs(SpireShop.catalog) do
		local n = bought and tonumber(bought[e.id]) or 0
		if SpireShop.REDELIVER[e.kind] and n > 0 then
			table.insert(out, { entry = e, count = n })
		end
	end
	return out
end

local GOLD_COINS = { [3031] = true, [3035] = true, [3043] = true } -- gold, platinum, crystal

function SpireShop.get(id)
	for _, e in ipairs(SpireShop.catalog) do
		if e.id == id then
			return e
		end
	end
end

-- Pure: can this balance buy it? Returns ok, reason.
function SpireShop.canBuy(balance, entry)
	if not entry then
		return false, "There is no such item."
	end
	if (balance or 0) < entry.price then
		return false, string.format("You need %d %s; you have %d.", entry.price, SpireShop.CURRENCY, balance or 0)
	end
	return true
end

-- Pure: one catalog line for the list
function SpireShop.line(entry)
	return string.format("%s - %s (%d %s)", entry.id, entry.name, entry.price, SpireShop.CURRENCY)
end

-- Pure: could this item id be a shop item? (the Fortune Hall refuses to bet any of them)
function SpireShop.isShopItem(itemId)
	for _, e in ipairs(SpireShop.catalog) do
		if e.item == itemId then
			return true
		end
	end
	return false
end

local function scope(player)
	return kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-shop")
end

function SpireShop.coinsOf(player)
	return scope(player):get("coins") or 0
end

function SpireShop.setCoins(player, n)
	scope(player):set("coins", n)
end

-- Outfits and mounts are re-granted at login so they follow the account
function SpireShop.owned(player)
	return scope(player):scoped("owned")
end

-- Takeable items bought by the account: { [id] = count }, and the season they were last handed over in (review S-1)
function SpireShop.bought(player)
	return scope(player):get("bought") or {}, scope(player):get("deliveredSeason")
end

function SpireShop.noteBought(player, id)
	local b = scope(player):get("bought") or {}
	b[id] = (tonumber(b[id]) or 0) + 1
	scope(player):set("bought", b)
	scope(player):set("deliveredSeason", SpireSeason.current())
end

function SpireShop.markDelivered(player)
	scope(player):set("deliveredSeason", SpireSeason.current())
end

-- The Manor's last buyer (kept across seasons: not in season_wipe.sql's list)
function SpireShop.manorLast()
	return kv.scoped("spirebound-shop-manor"):get("last")
end

function SpireShop.setManorLast(accountId)
	kv.scoped("spirebound-shop-manor"):set("last", { account = accountId, season = SpireSeason.current() })
end

function SpireShop.isGold(itemId)
	return GOLD_COINS[itemId] == true
end
