-- Something to spend task points on (roadmap R10, REVIEW 3.12). Task points come from hunting tasks
-- (Taskmaster Ren, Hearthgate). Say !taskshop to see the list, !taskshop <number> to buy.

SpireTasks.shop = {
	{ name = "a temple teleport scroll", points = 3, give = function(p) return p:addItem(25718, 1) ~= nil end },
	{ name = "10 strong health potions", points = 2, give = function(p) return p:addItem(236, 10) ~= nil end },
	{ name = "one hour of Hunting Focus (+20% experience)", points = 5, give = function(p)
		local s = p:kv():scoped("spirebound")
		s:set("focusUntil", math.max(os.time(), s:get("focusUntil") or 0) + 3600)
		return true
	end },
	{ name = "the title Seasoned Hunter", points = 25, give = function(p)
		p:kv():scoped("spirebound-titles"):set("Seasoned Hunter", os.time())
		return true
	end },
}
SpireTasks.FOCUS_BONUS = 0.20

-- Pure: may a player with `have` points buy shop item i?
function SpireTasks.canBuy(i, have)
	local item = SpireTasks.shop[i]
	if not item then
		return false, "There is no item " .. tostring(i) .. ". Say !taskshop for the list."
	end
	if (have or 0) < item.points then
		return false, string.format("That costs %d task points; you have %d.", item.points, have or 0)
	end
	return true
end

function SpireTasks.focusFactor(player)
	local untilT = player:kv():scoped("spirebound"):get("focusUntil") or 0
	return untilT > os.time() and (1 + SpireTasks.FOCUS_BONUS) or 1
end

local shop = TalkAction("!taskshop")
function shop.onSay(player, words, param)
	local s = SpireTasks.scope(player)
	local have = s:get("points") or 0
	local i = tonumber(param)
	if not i then
		local lines = { "Task point shop (you have " .. have .. " points). Say !taskshop <number>:" }
		for n, item in ipairs(SpireTasks.shop) do
			table.insert(lines, string.format("%d. %s: %d points", n, item.name, item.points))
		end
		player:showTextDialog(2821, table.concat(lines, "\n"))
		return false
	end
	local ok, why = SpireTasks.canBuy(i, have)
	if not ok then
		player:sendCancelMessage(why)
		return false
	end
	local item = SpireTasks.shop[i]
	if not item.give(player) then
		player:sendCancelMessage("You have no room for that. Free some space and try again.")
		return false
	end
	s:set("points", have - item.points)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You traded %d task points for %s. %d left.", item.points, item.name, have - item.points))
	return false
end
shop:separator(" ")
shop:groupType("normal")
shop:register()
