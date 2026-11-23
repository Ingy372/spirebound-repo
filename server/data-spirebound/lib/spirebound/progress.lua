-- Kills feed weapon familiarity and the style tree; both add damage (gear progression spec 4.2-4.3).
-- Events: scripts/spirebound/progression.lua. Pure functions first, so the tests and the events share one source.
SpireProgress = SpireProgress or {}

SpireProgress.NOT_COUNTED = { ["Pen Rat"] = true } -- the Arrival Yard's tutorial rats
SpireProgress.PARTY_RANGE = 30

-- Pure: one member's share of a kill's raw experience
function SpireProgress.killShare(rawXp, partySize)
	return rawXp / math.max(1, partySize or 1)
end

-- Pure: does this kill count? target = { isPlayer, summoned, name }; weaponVoc = vocation of the Spirebound weapon held
function SpireProgress.countsPure(target, playerVoc, weaponVoc)
	if target.isPlayer or target.summoned or SpireProgress.NOT_COUNTED[target.name] then
		return false
	end
	return weaponVoc ~= nil and weaponVoc == playerVoc
end

-- Pure: damage after the weapon's power, the style passives and trophy bonuses
function SpireProgress.dealtPure(amount, weaponState, styleView, ctx, trophyBonus)
	local mult = SpireGear.power(weaponState) * (1 + SpireStyle.damageBonus(styleView, ctx) + (trophyBonus or 0))
	return math.floor(amount * mult + 0.5)
end

-- The player behind a damage source (summons count for their master)
function SpireProgress.owner(creature)
	if not creature then
		return nil
	end
	local p = creature:getPlayer()
	if p then
		return p
	end
	local m = creature:getMaster()
	return m and m:getPlayer() or nil
end

-- Trophy bonuses are added by lib/spirebound/trophies.lua when it exists
function SpireProgress.trophyBonus(player, ctx)
	return SpireTrophies and SpireTrophies.bonus and SpireTrophies.bonus(player, ctx) or 0
end

-- Damage a player deals to a monster
function SpireProgress.onDealt(attacker, target, amount)
	local player = SpireProgress.owner(attacker)
	if not player or amount <= 0 then
		return amount
	end
	local item, d = SpireGear.mainWeapon(player)
	local w = nil
	if item and d.vocation == player:getVocation():getBaseId() then
		w = SpireGear.state(item)
	end
	local ctx = { distance = player:getPosition():getDistance(target:getPosition()), race = target:isMonster() and target:getType():race() or nil }
	return SpireProgress.dealtPure(amount, w, SpireStyle.get(player), ctx, SpireProgress.trophyBonus(player, ctx))
end

-- Members who share a kill: the killer's party on the same floor within range, or the killer alone
function SpireProgress.sharers(killer, where)
	local party = killer:getParty()
	if not party then
		return { killer }
	end
	local out = {}
	local members = party:getMembers()
	table.insert(members, party:getLeader())
	for _, m in ipairs(members) do
		local pos = m:getPosition()
		if pos.z == where.z and pos:getDistance(where) <= SpireProgress.PARTY_RANGE then
			table.insert(out, m)
		end
	end
	return #out > 0 and out or { killer }
end

-- Give one member its share: familiarity to the weapon in hand, points to the style tree
function SpireProgress.credit(player, target, share)
	local item, d = SpireGear.mainWeapon(player)
	local voc = player:getVocation():getBaseId()
	local t = { isPlayer = target:isPlayer(), summoned = target:getMaster() ~= nil, name = target:getName() }
	if not SpireProgress.countsPure(t, voc, d and d.vocation) then
		return
	end
	SpireStyle.addPoints(player, share)
	local s = SpireGear.state(item)
	if not s.shop then
		local before = s.fam
		SpireGear.setState(item, { famPoints = s.famPoints + share })
		local after = SpireGear.state(item).fam
		if after > before then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s: familiarity %d/10.", item:getName(), after))
		end
	end
end
