-- Canary 3.6.1 data/scripts/actions/items/blueberry_bush.lua with one Spirebound hook (server/core-overrides, copied
-- over data/): in the Bramble Run the berries are the ground's feature (roadmap FD2, scripts/spirebound/ground_features.lua).
local blueberryBush = Action()

function blueberryBush.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	item:transform(3700)
	item:decay()
	Game.createItem(3588, 3, fromPosition)
	player:addAchievementProgress("Bluebarian", 500)
	if SpireFeatures and SpireFeatures.berryPicked then
		SpireFeatures.berryPicked(player, fromPosition)
	end
	return true
end

blueberryBush:id(3699)
blueberryBush:register()
