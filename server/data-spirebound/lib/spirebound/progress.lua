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
function SpireProgress.onDealt(attacker, target, amount, origin)
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
	local mark = SpireBuffs and SpireBuffs.mark and SpireBuffs.mark[target:getId()]
	local ctx = { distance = player:getPosition():getDistance(target:getPosition()), shield = SpireProgress.holdsShield(player),
		area = SpireSpells and SpireSpells.areaNow == true, unmarked = not (mark and mark.untilTime >= os.time()) }
	local view = SpireStyle.get(player)
	local out = SpireProgress.dealtPure(amount, w, view, ctx, SpireProgress.trophyBonus(player, ctx))
	local crit = SpireStyle.critChance(view) -- Deadeye (ST1)
	if crit > 0 and math.random() < crit then
		out = math.floor(out * (1 + (SpireGearData.CRIT_BONUS or 0.5)) + 0.5)
		target:getPosition():sendMagicEffect(CONST_ME_CRITICAL_DAMAGE or CONST_ME_EXPLOSIONHIT)
	end
	-- Bloodedge (ST1): below half health you hit 10% harder
	if view.final == "bloodedge" and view.stage >= 3 and player:getHealth() * 2 < player:getMaxHealth() then
		out = math.floor(out * (1 + SpireProgress.BLOODEDGE_LOW) + 0.5)
	end
	if origin == ORIGIN_MELEE and attacker:getId() == player:getId() then
		SpireProgress.afterMelee(player, target, view, out)
	end
	return sign * out
end

SpireProgress.BLOODEDGE_LOW, SpireProgress.BLOODEDGE_LEECH = 0.10, 0.10

-- ST1: what a melee hit sets off. The Reaver's off-hand blade strikes (Bloodedge heals from it), Stormbreaker's hit
-- also lands on the monsters beside the target. They come a moment later as their own hits (ORIGIN_NONE, so they never
-- set anything off again).
function SpireProgress.afterMelee(player, target, view, dealt)
	local share = SpireStyle.offhandShare(view)
	local strike = 0
	if share > 0 and not SpireProgress.holdsShield(player) then
		local main = player:getSlotItem(CONST_SLOT_LEFT)
		local it = main and ItemType(main:getId())
		local two = it ~= nil and bit.band(it:getSlotPosition(), SLOTP_TWO_HAND) ~= 0
		local mainAtk = main and (main:getAttribute(ITEM_ATTRIBUTE_ATTACK) or 0) or 0
		if mainAtk <= 0 and it then
			mainAtk = it:getAttack()
		end
		strike = SpireOffhand.strike(dealt, mainAtk, SpireOffhand.attackOf(player:getSlotItem(CONST_SLOT_RIGHT)), share, two)
	end
	local cleave = SpireStyle.cleaveShare(view)
	if strike <= 0 and cleave <= 0 then
		return
	end
	local pid, tid, heal = player:getId(), target:getId(), view.final == "bloodedge" and view.stage >= 3
	addEvent(function()
		local p, t = Player(pid), Creature(tid)
		if not p or not t then
			return
		end
		if strike > 0 and t:getHealth() > 0 then
			doTargetCombatHealth(p, t, COMBAT_PHYSICALDAMAGE, -strike, -strike, CONST_ME_HITAREA, ORIGIN_NONE)
			if heal then
				p:addHealth(math.max(1, math.floor(strike * SpireProgress.BLOODEDGE_LEECH)))
			end
		end
		if cleave > 0 then
			local hit = math.max(1, math.floor(dealt * cleave + 0.5))
			for _, c in ipairs(Game.getSpectators(t:getPosition(), false, false, 1, 1, 1, 1)) do
				if c ~= t and c:isMonster() and not c:getMaster() and c:getHealth() > 0 then
					doTargetCombatHealth(p, c, COMBAT_PHYSICALDAMAGE, -hit, -hit, CONST_ME_BLOCKHIT, ORIGIN_NONE)
				end
			end
		end
	end, 200)
end

-- Is a shield (not a quiver, not an off-hand blade) in the shield hand? (Bulwark's passive needs one, ST1)
function SpireProgress.holdsShield(player)
	local it = player:getSlotItem(CONST_SLOT_RIGHT)
	return it ~= nil and ItemType(it:getId()):getWeaponType() == WEAPON_SHIELD and not (SpireOffhand and SpireOffhand.is(it))
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
