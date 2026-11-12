-- Crafting orders (ECONOMY.md). Crafters turn monster materials plus a fee into things no shop sells, or into supplies
-- cheaper than the shop price. NPCs pay almost nothing for materials, so players buy them from each other: that is
-- what makes hunters trade. tools/gen_economy.py reads this table (keep one recipe per line, same field order).
SpireCraft = {}

SpireCraft.recipes = {
	{ npc = "Fletcher Tamsin", name = "sniper arrows", item = 7364, count = 50, gold = 60, needs = { { 5879, 3 }, { 5897, 2 } }, worth = 250 },
	{ npc = "Fletcher Tamsin", name = "piercing bolts", item = 7363, count = 50, gold = 80, needs = { { 11492, 3 }, { 5880, 2 } }, worth = 300 },
	{ npc = "Alchemist Ivo", name = "strong health potions", item = 236, count = 5, gold = 250, needs = { { 5902, 4 }, { 3738, 2 } }, worth = 500 },
	{ npc = "Alchemist Ivo", name = "strong mana potions", item = 237, count = 5, gold = 230, needs = { { 9640, 4 }, { 30975, 2 } }, worth = 465 },
	{ npc = "Runewright Mael", name = "blank runes", item = 3147, count = 20, gold = 50, needs = { { 3033, 2 } }, worth = 200 },
	{ npc = "Tailor Quill", name = "hunter hat", item = 129, count = 1, gold = 1000, needs = { { 903, 10 }, { 5897, 5 } }, worth = 3000, addon = 1, female = 137 },
	{ npc = "Tailor Quill", name = "hunter cloak", item = 129, count = 1, gold = 2000, needs = { { 5909, 4 }, { 3012, 1 }, { 5899, 2 } }, worth = 5000, addon = 2, female = 137 },
}

function SpireCraft.forNpc(npcName)
	local out = {}
	for _, r in ipairs(SpireCraft.recipes) do
		if r.npc == npcName then
			table.insert(out, r)
		end
	end
	return out
end

local function itemName(id, count)
	local it = ItemType(id)
	local n = it and it:getName() or ("item " .. id)
	return count .. " " .. n
end

-- Pure: what is missing? have(itemId) -> count the player carries, money = gold the player can pay
function SpireCraft.missing(r, have, money)
	local miss = {}
	for _, need in ipairs(r.needs) do
		local got = have(need[1])
		if got < need[2] then
			table.insert(miss, { need[1], need[2] - got })
		end
	end
	if money < r.gold then
		table.insert(miss, { "gold", r.gold - money })
	end
	return miss
end

function SpireCraft.describe(r)
	local parts = {}
	for _, need in ipairs(r.needs) do
		table.insert(parts, itemName(need[1], need[2]))
	end
	local what = r.addon and ("the " .. r.name .. " (an outfit addon)") or (r.count .. " " .. r.name)
	return what .. " for " .. table.concat(parts, ", ") .. " and " .. r.gold .. " gold"
end

-- NPC hook: returns true when it handled the message
function SpireCraft.talk(npc, npcHandler, player, msg, npcName)
	local list = SpireCraft.forNpc(npcName)
	if #list == 0 then
		return false
	end
	local lower = msg:lower()
	if MsgContains(lower, "craft") or MsgContains(lower, "materials") or MsgContains(lower, "make") then
		local lines = {}
		for _, r in ipairs(list) do
			table.insert(lines, "{" .. r.name .. "}: " .. SpireCraft.describe(r))
		end
		npcHandler:say("Bring me materials and I'll make you something no shop sells. " .. table.concat(lines, ". ") .. ". Say what you want.", npc, player)
		return true
	end
	for _, r in ipairs(list) do
		if lower:find(r.name, 1, true) then
			local have = function(id)
				return player:getItemCount(id)
			end
			local miss = SpireCraft.missing(r, have, player:getMoney() + player:getBankBalance())
			if #miss > 0 then
				local parts = {}
				for _, m in ipairs(miss) do
					table.insert(parts, m[1] == "gold" and (m[2] .. " gold") or itemName(m[1], m[2]))
				end
				npcHandler:say("For that I still need " .. table.concat(parts, ", ") .. ". Hunters sell materials on the market.", npc, player)
				return true
			end
			for _, need in ipairs(r.needs) do
				player:removeItem(need[1], need[2])
			end
			player:removeMoneyBank(r.gold)
			if r.addon then
				player:addOutfitAddon(r.item, r.addon)
				player:addOutfitAddon(r.female, r.addon)
				npcHandler:say("There: your " .. r.name .. ". Wear it well. Change your outfit to see it.", npc, player)
			else
				player:addItem(r.item, r.count)
				npcHandler:say("Here you are: " .. r.count .. " " .. r.name .. ".", npc, player)
			end
			return true
		end
	end
	return false
end
