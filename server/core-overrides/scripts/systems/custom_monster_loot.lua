-- Drops custom loot for all monsters
-- Spirebound: no global extra loot (Canary's example added an item to every monster).
local allLootConfig = {}

-- Custom loot for specific monsters (this has the same usage options as normal monster loot)
-- Spirebound: empty; monster loot lives in each monster file.
local customLootConfig = {}

local customMonsterLoot = GlobalEvent("CreateCustomMonsterLoot")

function customMonsterLoot.onStartup()
	for monsterName, lootTable in pairs(customLootConfig) do
		local mtype = Game.getMonsterTypeByName(monsterName)
		if mtype then
			if lootTable and lootTable.items and #lootTable.items > 0 then
				mtype:createLoot(lootTable.items)
				logger.debug("[customMonsterLoot.onStartup] - Custom loot registered for monster: {}", mtype:getName())
			end
		else
			logger.error("[customMonsterLoot.onStartup] - Monster type not found: {}", monsterName)
		end
	end

	if #allLootConfig > 0 then
		for monsterName, mtype in pairs(Game.getMonsterTypes()) do
			mtype:createLoot(allLootConfig)
			logger.debug("[customMonsterLoot.onStartup] - Global loot registered for monster: {}", mtype:getName())
		end
	end
end

customMonsterLoot:register()
