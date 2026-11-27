-- Floor 1's two hidden places (roadmap AD5; adventure design 4.5): secrets s14 and s15 and their hidden beasts.
-- Added with table.insert (as floor_content.lua does), so secrets.lua and trophies.lua stay Session A's files.
-- The map: maps/hidden_places.py. The game side: scripts/spirebound/hidden_places.lua.
-- GM notes on where they are: docs/gm/floor1_minibosses.md (never in player docs).
SpireHidden = SpireHidden or {}

-- Riddles only (Jay, 2026-11-27): no place name, no direction, no NPC name; the reward is never named.
table.insert(SpireSecrets.list, { id = "s14", floor = 1, tier = "large", name = "Smugglers' Vault", reward = {},
	hint = "Below the place where thieves count their take, a deeper purse sleeps behind iron. Its key hangs only from the belts of those who give the orders." })
table.insert(SpireSecrets.list, { id = "s15", floor = 1, tier = "large", name = "The Sealed Cut", reward = {},
	hint = "The masons signed three broken places before they walled up their last cut. Carry all three signatures to the stone mouth, and it will remember how to open." })

-- Hidden beasts: woken when someone steps on the secret's trigger (SpireTrophies.onSecret), 1-3 hours' rest, a
-- trophy once per character. gold / armour are new kinds of bonus, applied by scripts/spirebound/hidden_places.lua.
table.insert(SpireTrophies.LIST, { id = "ironpurse", boss = "Ironpurse", secret = "s14", spawn = "ironpurse_spawn",
	name = "Ironpurse's Tally", text = "+2% gold from kills", gold = 0.02 })
table.insert(SpireTrophies.LIST, { id = "the_unfinished", boss = "The Unfinished", secret = "s15", spawn = "unfinished_spawn",
	name = "Unfinished Hand", text = "+1 armour", armour = 1 })

SpireHidden.KEY = SpireAdventureData.vaultKey
SpireHidden.RUBBINGS = SpireAdventureData.rubbings          -- ground id -> rubbing item
SpireHidden.RUBBING_GROUNDS = { "old_quarry", "fallen_bastion", "shard_fields" }
SpireHidden.PARTY_REACH = 3                                 -- party members this close go through with you

-- Pure: the bonuses a character's trophies give (have = { [trophy id] = time })
function SpireHidden.goldBonus(have)
	local b = 0
	for _, t in ipairs(SpireTrophies.LIST) do
		if have[t.id] and t.gold then b = b + t.gold end
	end
	return b
end

function SpireHidden.armourBonus(have)
	local b = 0
	for _, t in ipairs(SpireTrophies.LIST) do
		if have[t.id] and t.armour then b = b + t.armour end
	end
	return b
end

-- Pure: which rubbings are missing. count(itemId) -> how many the player carries
function SpireHidden.missingRubbings(count)
	local out = {}
	for _, gid in ipairs(SpireHidden.RUBBING_GROUNDS) do
		if count(SpireHidden.RUBBINGS[gid]) < 1 then
			table.insert(out, gid)
		end
	end
	return out
end

-- Pure: a physical hit after the armour trophy (the engine hands damage over as negative numbers: keep the sign)
function SpireHidden.armoured(amount, armour)
	if armour <= 0 or amount == 0 then
		return amount
	end
	local sign = amount < 0 and -1 or 1
	return sign * math.max(0, math.abs(amount) - armour)
end
