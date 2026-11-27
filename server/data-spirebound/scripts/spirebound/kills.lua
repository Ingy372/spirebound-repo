-- N8: every kill reaches the scripts that count kills (lib/spirebound/kills.lua) through one death callback instead
-- of the engine's deprecated onKill event (which logged a warning per script per kill).
local deaths = EventCallback("SpireKillCounters")
function deaths.monsterOnDropLoot(monster, corpse)
	if not monster or not corpse then
		return
	end
	local owner = Player(corpse:getCorpseOwner())
	if owner then
		SpireKills.fire(owner, monster)
	end
end
deaths:register()
