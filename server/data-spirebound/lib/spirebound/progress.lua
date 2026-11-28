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
	local mult = SpireGear.power(weaponState) * (weaponState and weaponState.scale or 1) * (1 + SpireStyle.damageBonus(styleView, ctx) + (trophyBonus or 0))
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

-- Party playtest 2026-11-26: after losing his weapons the tank fought bare-handed for a long time and nothing said so.
-- Pure: is any of these weapon types a real weapon (not empty, a shield, ammunition or a quiver)?
function SpireProgress.armedPure(types)
	for _, wt in ipairs(types) do
		if wt and wt ~= WEAPON_NONE and wt ~= WEAPON_SHIELD and wt ~= (WEAPON_AMMO or -1) and wt ~= (WEAPON_QUIVER or -1) then
			return true
		end
	end
	return false
end

SpireProgress.UNARMED_WARN_EVERY = 300 -- seconds between reminders
local unarmedWarned = {} -- player id -> os.time() of the last reminder
function SpireProgress.warnUnarmed(player)
	if player:getVocation():getBaseId() == 0 then
		return false
	end
	local types = {}
	for _, slot in ipairs({ CONST_SLOT_LEFT, CONST_SLOT_RIGHT }) do
		local it = player:getSlotItem(slot)
		table.insert(types, it and ItemType(it:getId()):getWeaponType() or WEAPON_NONE)
	end
	if SpireProgress.armedPure(types) then
		return false
	end
	local pid, now = player:getId(), os.time()
	if unarmedWarned[pid] and now - unarmedWarned[pid] < SpireProgress.UNARMED_WARN_EVERY then
		return false
	end
	unarmedWarned[pid] = now
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You are fighting with no weapon in your hand! Put one in your weapon hand (lost yours? Weaponsmith Garrick sells them, and can replace the barracks weapon).")
	return true
end

-- Damage a player deals to a monster.
-- Floor 1 review B4-0 (2026-11-26, measured on a real character): the engine hands every hit over as a NEGATIVE
-- number, and this function returned early on "amount <= 0", so weapon tiers, familiarity, the awakening, style
-- passives and trophies added no damage at all in real play. Work on the size of the hit and keep its sign.
function SpireProgress.onDealt(attacker, target, amount)
	local player = SpireProgress.owner(attacker)
	if player and amount ~= 0 and attacker:getId() == player:getId() then -- the player's own hits, not a summon's
		SpireProgress.warnUnarmed(player)
	end
	if not player or amount == 0 then
		return amount
	end
	local sign = amount < 0 and -1 or 1
	amount = math.abs(amount)
	local item, d = SpireGear.mainWeapon(player)
	local w = nil
	if item and d.vocation == player:getVocation():getBaseId() then
		w = SpireGear.state(item)
	end
	local ctx = { distance = player:getPosition():getDistance(target:getPosition()) }
	return sign * SpireProgress.dealtPure(amount, w, SpireStyle.get(player), ctx, SpireProgress.trophyBonus(player, ctx))
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

-- Party playtest 2026-11-26 (hand-off P1-3): kill quests counted only for the engine's killer (most damage or last
-- hit), so in a party of three the tank finished Iron for the Stair and the other two were locked out of the Stair Key.
-- Now every member who shares the kill (SpireProgress.sharers) gets it, once per kill: onKill fires for both the last
-- hitter and the top damage dealer, so each counter (key) remembers who was already credited for that monster.
local creditedFor = {} -- key .. monster id -> { [player id] = true }
function SpireProgress.killCredit(key, killer, target)
	local k = key .. ":" .. target:getId()
	local done = creditedFor[k]
	if not done then
		done = {}
		creditedFor[k] = done
		addEvent(function() creditedFor[k] = nil end, 5000)
	end
	local out = {}
	for _, m in ipairs(SpireProgress.sharers(killer, target:getPosition())) do
		local id = m:getId()
		if not done[id] then
			done[id] = true
			table.insert(out, m)
		end
	end
	return out
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
	SpireGear.claim(item, player) -- WA1: another character's weapon starts again at familiarity 0 for this one
	local s = SpireGear.state(item)
	if not s.shop then
		local before = s.fam
		SpireGear.setState(item, { famPoints = s.famPoints + share })
		local after = SpireGear.state(item).fam
		if after > before then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s: familiarity %d/10.", item:getName(), after))
			player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN) -- seen, not just read (F1-41)
		end
	end
end
