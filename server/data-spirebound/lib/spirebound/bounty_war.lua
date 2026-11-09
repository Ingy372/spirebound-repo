-- Bounties on murderers and consent-based guild wars (DESIGN.md 6.4, items 5 and 6). Roadmap 2.5 / 2.6.

SpireBounty = {
	FINE_PER_LEVEL = 1000, -- system bounty: the murderer is fined up to level x 1000 gold from their bank
	MIN_PLAYER_BOUNTY = 1000,
}

-- Pure: can `killer` collect the bounty on `target`? Both: { guid, ip, guildId, partyId, partiedRecently = {guid=true} }
function SpireBounty.validClaimer(target, killer)
	if not killer or killer.guid == target.guid then
		return false, "self"
	end
	if target.ip and target.ip ~= 0 and killer.ip == target.ip then
		return false, "same computer"
	end
	if target.guildId and target.guildId ~= 0 and killer.guildId == target.guildId then
		return false, "same guild"
	end
	if target.partyId and killer.partyId == target.partyId then
		return false, "same party"
	end
	if target.partiedRecently and target.partiedRecently[killer.guid] then
		return false, "partied together in the last 24 hours"
	end
	return true
end

-- Pure: system fine for a new murderer
function SpireBounty.fine(level, bankBalance)
	return math.max(0, math.min(bankBalance, level * SpireBounty.FINE_PER_LEVEL))
end

local function store()
	return kv.scoped("spirebound-bounties")
end

function SpireBounty.get(guid)
	return store():get(tostring(guid)) or { total = 0 }
end

function SpireBounty.add(guid, name, amount, from)
	local b = SpireBounty.get(guid)
	b.total = (b.total or 0) + amount
	b.name = name
	b.contributors = b.contributors or {}
	b.contributors[from] = (b.contributors[from] or 0) + amount
	store():set(tostring(guid), b)
	return b.total
end

function SpireBounty.clear(guid)
	store():remove(tostring(guid))
end

function SpireBounty.list()
	local out = {}
	local ok, keys = pcall(function() return store():keys() end)
	for _, key in ipairs(ok and keys or {}) do
		local b = store():get(key)
		if b and (b.total or 0) > 0 then
			table.insert(out, b)
		end
	end
	table.sort(out, function(a, b) return a.total > b.total end)
	return out
end

-- Called when someone becomes red or black (scripts/spirebound/pvp.lua)
function SpireBounty.onMurderer(player)
	local fine = SpireBounty.fine(player:getLevel(), player:getBankBalance())
	if fine > 0 then
		player:setBankBalance(player:getBankBalance() - fine)
	end
	local total = SpireBounty.add(player:getGuid(), player:getName(), math.max(fine, SpireBounty.MIN_PLAYER_BOUNTY), "the tower")
	Game.broadcastMessage(string.format("A bounty of %d gold is on %s's head.", total, player:getName()), MESSAGE_EVENT_ADVANCE)
end

-- Guild wars ----------------------------------------------------------
SpireWar = { FEE = 10000, MIN_DAYS = 1, MAX_DAYS = 14, COOLDOWN = 7 * 86400 }

-- Pure: validate war terms
function SpireWar.validTerms(days, fragsLimit)
	if not days or days < SpireWar.MIN_DAYS or days > SpireWar.MAX_DAYS then
		return false, "A war lasts 1 to 14 days."
	end
	if fragsLimit and (fragsLimit < 0 or fragsLimit > 1000) then
		return false, "The kill limit must be between 0 (none) and 1000."
	end
	return true
end

-- Pure: is a new war allowed given the last war's end time between the same guilds?
function SpireWar.cooldownOver(lastEnded, now)
	return not lastEnded or lastEnded == 0 or now - lastEnded >= SpireWar.COOLDOWN
end

function SpireWar.guildByName(name)
	local q = db.storeQuery("SELECT `id`, `name` FROM `guilds` WHERE `name` = " .. db.escapeString(name))
	if not q then
		return nil
	end
	local id, gname = Result.getNumber(q, "id"), Result.getString(q, "name")
	Result.free(q)
	return id, gname
end

function SpireWar.lastEnded(g1, g2)
	local q = db.storeQuery(string.format("SELECT MAX(`ended`) AS e FROM `guild_wars` WHERE `status` = 4 AND ((`guild1` = %d AND `guild2` = %d) OR (`guild1` = %d AND `guild2` = %d))", g1, g2, g2, g1))
	if not q then
		return 0
	end
	local e = Result.getNumber(q, "e")
	Result.free(q)
	return e or 0
end

function SpireWar.active(g1, g2)
	local q = db.storeQuery(string.format("SELECT `id` FROM `guild_wars` WHERE `status` IN (0, 1) AND ((`guild1` = %d AND `guild2` = %d) OR (`guild1` = %d AND `guild2` = %d))", g1, g2, g2, g1))
	if not q then
		return false
	end
	Result.free(q)
	return true
end
