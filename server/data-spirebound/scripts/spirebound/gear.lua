-- Gear in the game: rare alternative weapons from each floor's harder monsters (gear progression spec 4.5).
-- Rules: lib/spirebound/gear.lua. Data: lib/spirebound/gear_data.lua (tools/gen_gear.py).

local function floorOfDropper(name)
	for floor, list in pairs(SpireGearData.dropFrom) do
		for _, n in ipairs(list) do
			if n == name then
				return floor
			end
		end
	end
end

local drops = EventCallback("SpireGearDrops")
function drops.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	if not owner or not corpse:isContainer() then
		return
	end
	local shards = SpireGearData.shardMonsters[monster:getName()]
	if shards and not monster:getMaster() then -- Hearth Shards (spec 4.4)
		for grade in pairs(shards) do
			if math.random() < SpireGearData.SHARD_CHANCE[grade] then
				corpse:addItem(SpireGearData.tokens[1][grade], 1)
			end
		end
	end
	local floor = floorOfDropper(monster:getName())
	if floor and math.random() < SpireGearData.DROP_CHANCE then
		local d = SpireGear.find(math.random(1, 4), floor, "drop", "weapon")
		if d then
			SpireGear.make(corpse, d.id)
		end
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
			say("Hold your Spirebound weapon in your hand (or wear your Spirebound armour and say {upgrade armour}), and I'll look at it.")
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
			local item = SpireGear.make(player, id)
			return item and ("Here: a new " .. item:getName() .. ", tier 0. Look after this one.") or "You have no room for it."
		end
		say(string.format("Lost it? I can make you a new one, tier 0, for %d gold. Say {yes}.", fee))
		return true
	end
	return false
end
