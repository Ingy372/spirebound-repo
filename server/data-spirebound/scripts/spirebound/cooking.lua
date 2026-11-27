-- Cooking in the game (roadmap FD4). Rules: lib/spirebound/cooking.lua. Eating goes through the foods override
-- (server/core-overrides/scripts/actions/items/foods.lua); cooking is dropping an ingredient on a fire.

-- dropping things on a fire
local drop = EventCallback("SpireCookingDrop")
function drop.playerOnItemMoved(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if toPosition and toPosition.x ~= CONTAINER_POSITION and item and SpireCooking.isIngredient(item:getId()) then
		SpireCooking.onDrop(player, item, Position(toPosition.x, toPosition.y, toPosition.z))
	end
end
drop:register()

-- the comforts: a tick for everyone with a dish
local tick = GlobalEvent("SpireCookingTick")
function tick.onThink(interval)
	for pid in pairs(SpireCooking.active) do
		local p = Player(pid)
		if p then
			SpireCooking.tick(p)
		else
			SpireCooking.active[pid] = nil
		end
	end
	return true
end
tick:interval(SpireDepthData.cooking.tick * 1000)
tick:register()

local login = CreatureEvent("SpireCookingLogin")
function login.onLogin(player)
	SpireCooking.restore(player)
	return true
end
login:register()

-- a capacity bonus must leave before the character is saved for good (it is put back at the next login)
local logout = CreatureEvent("SpireCookingLogout")
function logout.onLogout(player)
	local a = SpireCooking.active[player:getId()]
	SpireCooking.active[player:getId()] = nil
	if a then
		-- keep the stored record (with its cap) so the login restores or removes it
		player:kv():scoped("spirebound-dish"):set("now", { id = a.id, ["until"] = a["until"], cap = a.cap })
	end
	return true
end
logout:register()

-- the Cookbook rows on the Discoveries page
local startup = GlobalEvent("SpireCookingStartup")
function startup.onStartup()
	if SpireDiscoveries and SpireDiscoveries.register then
		for _, d in ipairs(SpireDepthData.cooking.dishes) do
			SpireDiscoveries.register("cookbook", d.id, d.name, 1)
		end
	end
	return true
end
startup:register()
