-- Gear in the game: rare alternative weapons from each floor's harder monsters (gear progression spec 4.5).
-- Rules: lib/spirebound/gear.lua. Data: lib/spirebound/gear_data.lua (tools/gen_gear.py).

local drops = EventCallback("SpireGearDrops")
function drops.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	if not owner or not corpse:isContainer() then
		return
	end
	local shards = SpireGearData.shardMonsters[monster:getName()]
	if shards and not monster:getMaster() then -- Hearth Shards (spec 4.4)
		local kv = owner:kv():scoped("spirebound")
		for grade in pairs(shards) do
			local key = "shard_since_" .. grade
			local since = kv:get(key) or 0
			local chance = type(shards[grade]) == "number" and shards[grade] or SpireGearData.SHARD_CHANCE[grade]   -- the Ram's own rate
			if SpireGear.shardRoll(chance, since, math.random()) then
				corpse:addItem(SpireGearData.tokens[1][grade], 1)
				kv:set(key, 0)
				-- the rare-drop moment (F1-42): a sparkle on the corpse and a line of its own
				corpse:getPosition():sendMagicEffect(CONST_ME_GIFT_WRAPS)
				owner:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("A %s glints in the remains!", SpireGearData.tokenNames[SpireGearData.tokens[1][grade]][1]))
			else
				kv:set(key, since + 1)
			end
		end
	end
	-- a rare weapon (review B4-2: elites and the Ram only, the looter's own class twice as likely)
	local d = not monster:getMaster() and SpireGear.rareDrop(monster:getName(), owner:getVocation():getBaseId(), math.random(), math.random())
	if SpireGear.forceRare and SpireGear.forceRare[owner:getId()] and SpireFinds and SpireFinds.isElite(monster:getName()) then
		SpireGear.forceRare[owner:getId()] = nil -- (tests only: scripts/spirebound/dev_adventure.lua "/adv rare on")
		local cls = ({ "arcanist", "mystic", "ranger", "vanguard" })[owner:getVocation():getBaseId()]
		d = cls and SpireGear.def("f1_" .. cls .. "_drop") or d
	end
	if d and SpireGear.make(corpse, d.id) then
		corpse:getPosition():sendMagicEffect(CONST_ME_GIFT_WRAPS)
		owner:sendTextMessage(MESSAGE_EVENT_ADVANCE, "A rare weapon lies in the remains: " .. d.name .. "!")
		if SpireFinds then -- adventure layer 4.2: the whole server hears it
			SpireFinds.announce("rare_weapon", { owner }, { item = d.name, from = monster:getName() })
		end
	end
	-- adventure layer: elites count on the Discoveries page and for season firsts (everyone who hurt it)
	if SpireFinds and SpireFinds.isElite(monster:getName()) and not monster:getMaster() then
		local credit = SpireFinds.creditList(monster)
		for _, p in ipairs(credit) do
			SpireDiscoveries.mark(p, "elite", monster:getName())
		end
		SpireFinds.first("elite", monster:getName(), credit, monster:getName())
	end
end
drops:register()

-- ---------------------------------------------------------------- Weaponsmith talk: upgrade, reforge, replace
local pending = {} -- player id -> function to run on "yes"
SpireCleanup.add(function(pid) pending[pid] = nil end)
SpireGear.WEAPONSMITH = "Weaponsmith Garrick"

local function armourPiece(player)
	for _, slot in ipairs({ CONST_SLOT_ARMOR, CONST_SLOT_LEGS, CONST_SLOT_HEAD, CONST_SLOT_FEET }) do
		local it = player:getSlotItem(slot)
		local d = SpireGear.defOf(it)
		if d and d.kind == "armour" then
			return it
		end
	end
end

-- Pure-ish: the weapon this player earned on a floor and whether it carries one now
function SpireGear.earnedMain(player, floor)
	return player:kv():scoped("spirebound"):get("gear_main_" .. floor)
end

function SpireGear.carriesMain(player, floor)
	for _, it in ipairs(SpireGear.carried(player)) do
		local d = SpireGear.defOf(it)
		if d and d.kind == "weapon" and d.floor == floor and d.source == "main" then
			return true
		end
	end
	return false
end

function SpireGear.talk(npc, handler, player, msg, npcName)
	if msg:sub(1, 1) == "!" then
		return false -- a player command said near an NPC (e.g. !upgrade) is not talk
	end
	if SpireRumours and SpireRumours.talk(npc, handler, player, msg, npcName) then
		return true -- adventure layer 4.7: innkeepers answer "rumour" (every generated NPC passes its talk through here)
	end
	if npcName ~= SpireGear.WEAPONSMITH then
		return false
	end
	local pid = player:getId()
	local lower = msg:lower()
	local say = function(text) handler:say(text, npc, player) end
	if MsgContains(lower, "yes") and pending[pid] then
		local run = pending[pid]
		pending[pid] = nil
		say(run())
		return true
	end
	if MsgContains(lower, "upgrade") then
		local item = (MsgContains(lower, "armour") or MsgContains(lower, "armor")) and armourPiece(player) or SpireGear.mainWeapon(player)
		if not item then
			say("Hold your Spirebound weapon in your hand and I'll look at it. For your armour, wear it and say {upgrade armour}.")
			return true
		end
		local ok, cost = SpireGear.upgradeCheck(item, SpireGear.playerWallet(player))
		if not ok then
			say(cost)
			return true
		end
		pending[pid] = function()
			local done, text = SpireGear.upgradeWith(item, SpireGear.playerWallet(player))
			if done then
				player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
			end
			return text
		end
		say(string.format("%s to tier %d: %d %s and %d gold. Shall I? Say {yes}.", item:getName(), cost.tier, cost.count,
			SpireGearData.tokenNames[cost.shard][2], cost.gold))
		return true
	end
	if MsgContains(lower, "reforge") then
		local item, d = SpireGear.mainWeapon(player)
		if not item then
			say("Hold the weapon you want reforged.")
			return true
		end
		local family = lower:match("reforge%s+(%a+)")
		if not family then
			say(string.format("Into what? Say {reforge} and a family: %s. It costs %d gold; the tier stays, familiarity starts again.",
				SpireGear.familiesOf(d.vocation, d.floor), SpireGearData.REFORGE_FEE * d.floor))
			return true
		end
		pending[pid] = function()
			local new, text = SpireGear.reforgeWith(item, family, SpireGear.playerWallet(player), player)
			return text
		end
		say(string.format("Reforge %s into a %s for %d gold? Its familiarity starts again. Say {yes}.", item:getName(), family,
			SpireGearData.REFORGE_FEE * d.floor))
		return true
	end
	if MsgContains(lower, "replace") then
		local id = SpireGear.earnedMain(player, 1)
		if not id then
			say("You have no weapon from Captain Dorrow yet. Reach level 10 and see him at Hearthgate's north gate.")
			return true
		end
		if SpireGear.carriesMain(player, 1) then
			say("You still carry your weapon. I only replace a lost one.")
			return true
		end
		local fee = SpireGearData.REISSUE_FEE
		pending[pid] = function()
			if not SpireGear.playerWallet(player).pay(fee) then
				return string.format("A new one costs %d gold.", fee)
			end
			local item, where = SpireGear.equip(player, id)
			if not item then
				player:setBankBalance(player:getBankBalance() + fee) -- never keep the money for nothing
				return "You have no room for it. I've put your gold back in your bank account."
			end
			return "Here: a new " .. item:getName() .. ", tier 0. Look after this one." .. SpireGear.whereLine(where)
		end
		say(string.format("Lost it? I can make you a new one, tier 0, for %d gold. Say {yes}.", fee))
		return true
	end
	return false
end

-- ---------------------------------------------------------------- Captain Dorrow: the barracks' weapon at level 10
local choosing = {} -- player id -> true while picking a family
SpireCleanup.add(function(pid) choosing[pid] = nil end)

function SpireGear.giveMain(player, family)
	local voc = player:getVocation():getBaseId()
	local d = SpireGear.mainFor(voc, 1, family)
	if not d then
		return nil
	end
	local item, where = SpireGear.equip(player, d.id)
	if item then
		player:kv():scoped("spirebound"):set("gear_main_1", d.id)
		player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	end
	return item, where
end

-- Party playtest 2026-11-26 (hand-off P1-5, P2-8): Mastery and familiarity only grow while the barracks weapon is in
-- hand, and a tank who never moved it out of the backpack had no Mastery at level 21. So the weapon goes straight into
-- the weapon hand; whatever was there moves to the backpack. If that can't be done (no room for the old weapon, or a
-- two-handed weapon and a full shield hand), it goes to the backpack (or the Store Inbox) as before.
-- Second result: "hand", "bag" or "inbox".
function SpireGear.equip(player, id)
	local backpack = player:getSlotItem(CONST_SLOT_BACKPACK)
	local old = player:getSlotItem(CONST_SLOT_LEFT)
	if old and backpack and backpack:isContainer() and backpack:getEmptySlots(false) > 0 then
		old:moveTo(backpack)
		old = player:getSlotItem(CONST_SLOT_LEFT)
	end
	if not old then
		local item = SpireGear.create(id)
		-- worn slots check carrying weight even with FLAG_NOLIMIT (lib/spirebound/give.lua), and the client check on
		-- 2026-11-26 found an overloaded Vanguard with an empty hand: lift the limit for this one moment
		local cap = player.getCapacity and player:getCapacity()
		if cap then
			player:setCapacity(cap + 1000000 * 100)
		end
		local ret = item and player:addItemEx(item, false, CONST_SLOT_LEFT, FLAG_NOLIMIT)
		if cap then
			player:setCapacity(cap)
		end
		if ret == RETURNVALUE_NOERROR then
			return item, "hand"
		end
		if item then
			item:remove()
		end
	end
	return SpireGear.make(player, id)
end

-- What Dorrow / Garrick add about where the weapon went
function SpireGear.whereLine(where)
	if where == "hand" then
		return " I've put it in your hand; anything you held is in your backpack. Keep holding it: your familiarity and Mastery only grow while it's in your hand."
	elseif where == "inbox" then
		return " Your backpack was full, so it's in your Store Inbox. Hold it in your hand: your familiarity and Mastery only grow while you do."
	end
	return " It's in your backpack: drag it into your weapon hand. Your familiarity and Mastery only grow while you hold it."
end

function SpireGear.dorrowTalk(npc, handler, player, msg)
	if msg:sub(1, 1) == "!" then
		return false -- a player command said near an NPC (e.g. !upgrade) is not talk
	end
	local lower = msg:lower()
	local pid = player:getId()
	local voc = player:getVocation():getBaseId()
	local say = function(text) handler:say(text, npc, player) end
	if choosing[pid] then
		for family in SpireGear.familiesOf(voc, 1):gmatch("%a+") do
			if MsgContains(lower, family) or (family == "club" and MsgContains(lower, "mace")) then
				choosing[pid] = nil
				local item, where = SpireGear.giveMain(player, family)
				if item then
					say("The " .. item:getName() .. ". It's yours: the more you fight with it, the better you'll know it." .. SpireGear.whereLine(where) .. " When you're ready, ask me for a {quest} to temper it.")
				else
					say("Make room in your backpack first, then ask me for a {weapon} again.")
				end
				return true
			end
		end
	end
	local offer = SpireGear.dorrowOffer(player:getLevel(), voc, SpireGear.earnedMain(player, 1))
	local asksWeapon = MsgContains(lower, "weapon")
	local asksQuest = MsgContains(lower, "quest") or MsgContains(lower, "mission") or MsgContains(lower, "help")
	if offer == "offer" and (asksWeapon or asksQuest) then
		local fams, only = {}, nil
		for family in SpireGear.familiesOf(voc, 1):gmatch("%a+") do
			table.insert(fams, "{" .. family .. "}")
			only = family
		end
		if #fams == 1 then -- party playtest 2026-11-26 (hand-off P2-9): "Which kind: {rod}?" with one choice
			local item, where = SpireGear.giveMain(player, only)
			if item then
				say("Level " .. player:getLevel() .. "! Every climber who gets this far earns a weapon from the barracks. Here: the " .. item:getName() .. ". It's yours: the more you fight with it, the better you'll know it." .. SpireGear.whereLine(where) .. " When you're ready, ask me for a {quest} to temper it.")
			else
				say("Make room in your backpack first, then ask me for a {weapon} again.")
			end
			return true
		end
		choosing[pid] = true
		say("Level " .. player:getLevel() .. "! Every climber who gets this far earns a weapon from the barracks. Which kind: " .. table.concat(fams, " or ") .. "?")
		return true
	end
	if asksWeapon then
		if offer == "too_low" then
			say("Come back at level " .. SpireGear.MAIN_LEVEL .. " and the barracks will give you a weapon of your own.")
		elseif offer == "has" then
			say("You already have the barracks' weapon. Weaponsmith Garrick can {upgrade} it with Hearth Shards, or {replace} it if you lost it.")
		else
			say("Choose your path with Registrar Maelis first.")
		end
		return true
	end
	return false
end

-- Gear a character already owns picks up changed numbers when they log in (Floor 1 review B4-1: the barracks' melee
-- weapons got an attack of their own, and weapons made before that still carried the plain sword's).
local refresh = CreatureEvent("SpireGearRefresh")
function refresh.onLogin(player)
	for _, it in ipairs(SpireGear.carried(player)) do
		if SpireGear.defOf(it) then
			SpireGear.setState(it, {})
		end
	end
	return true
end
refresh:register()
