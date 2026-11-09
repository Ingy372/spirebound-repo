-- The Twin Fang trial and the off-hand strike (DESIGN.md 5.6).
-- Engine limit: a character can't hold two weapons, so the Twin Fang works with one sword and an EMPTY shield hand;
-- the "second blade" is an extra off-hand strike at 50% damage on every melee hit, plus three exclusive sword skills.

local function holders()
	return kv.scoped("spirebound-twinfang"):get("holders") or {}
end

local challenger = {} -- warden creature id -> player guid

local tick = GlobalEvent("SpireTwinFangTrial")
function tick.onThink(interval)
	local tp = WorldPoints.twin_fang_trial
	if not tp then
		return true
	end
	local tile = Tile(tp)
	local p = tile and tile:getTopCreature()
	p = p and p:getPlayer()
	if not p or SwordSkills.hasTwinFang(p) then
		return true
	end
	for _, pid in pairs(challenger) do
		if pid == p:getGuid() then
			return true -- already fighting
		end
	end
	local combos = p:kv():scoped("spirebound-twinfang"):get("combos") or 0
	local ok, why = SwordSkills.twinFangEligible(p:getVocation():getBaseId(), p:getSkillLevel(SKILL_SWORD), combos, #holders())
	if SpireCavebot.active(p) then
		ok, why = false, "The trial won't answer a cavebot."
	end
	if not ok then
		p:sendCancelMessage(why)
		p:teleportTo(Position(tp.x, tp.y + 2, tp.z))
		return true
	end
	local w = Game.createMonster("Twin Fang Warden", Position(tp.x, tp.y - 2, tp.z), true, true)
	if w then
		challenger[w:getId()] = p:getGuid()
		w:setTarget(p)
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Twin Fang Warden rises. Defeat it alone to earn the second blade.")
	end
	return true
end
tick:interval(2000)
tick:register()

local death = CreatureEvent("SpireTwinFangDeath")
function death.onDeath(creature, corpse, killer, mostDamageKiller)
	local guid = challenger[creature:getId()]
	challenger[creature:getId()] = nil
	local p = guid and Player(guid)
	if not p then
		return true
	end
	local list = holders()
	if #list >= SwordSkills.TWIN_FANG.MAX_HOLDERS then
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Too late. The third Twin Fang was claimed moments ago.")
		return true
	end
	table.insert(list, p:getName())
	kv.scoped("spirebound-twinfang"):set("holders", list)
	p:kv():scoped("spirebound-twinfang"):set("holder", true)
	p:kv():scoped("spirebound-titles"):set("Twin Fang", os.time())
	Game.broadcastMessage(string.format("%s has earned the Twin Fang! (%d of %d this season)", p:getName(), #list, SwordSkills.TWIN_FANG.MAX_HOLDERS), MESSAGE_EVENT_ADVANCE)
	if #list >= SwordSkills.TWIN_FANG.MAX_HOLDERS then
		Game.broadcastMessage("The Twin Fang trial seals itself until next season.", MESSAGE_EVENT_ADVANCE)
	end
	return true
end
death:register()

-- Off-hand strike: Twin Fang holders with a sword and an empty shield hand hit again at 50% on each melee hit
local offhand = CreatureEvent("SpireTwinFangOffhand")
function offhand.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local p = attacker and attacker:getPlayer()
	if p and origin == ORIGIN_MELEE and primaryDamage > 0 and SwordSkills.hasTwinFang(p) then
		local left, right = p:getSlotItem(CONST_SLOT_LEFT), p:getSlotItem(CONST_SLOT_RIGHT)
		local sword = (left and left:getType():getWeaponType() == WEAPON_SWORD) or (right and right:getType():getWeaponType() == WEAPON_SWORD)
		local free = not left or not right
		if sword and free then
			local dmg = math.max(1, math.floor(primaryDamage * SwordSkills.TWIN_FANG.OFFHAND))
			local pid, cid = p:getId(), creature:getId()
			addEvent(function()
				local a, c = Player(pid), Creature(cid)
				if a and c then
					doTargetCombatHealth(a, c, COMBAT_PHYSICALDAMAGE, -dmg, -dmg, CONST_ME_HITAREA, ORIGIN_SPELL)
				end
			end, 250)
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
offhand:register()
