-- Season Path: kill counting and the !path window
local kill = CreatureEvent("SpirePathKill")
function kill.onKill(player, target)
	if not target or not target:isMonster() or target:getMaster() then
		return true
	end
	SpirePath.progress(player, "kill", 1)
	if SpireBoss and SpireBoss.defs[target:getName()] then
		SpirePath.progress(player, "boss", 1)
	end
	return true
end
kill:register()

local login = CreatureEvent("SpirePathLogin")
function login.onLogin(player)
	player:registerEvent("SpirePathKill")
	return true
end
login:register()

local cmd = TalkAction("!path")
function cmd.onSay(player, words, param)
	local st = SpirePath.state(player)
	local tier = SpirePath.tierFor(st.points)
	local nextReward = SpirePath.REWARDS[tier + 1]
	local text = string.format("Season Path - Season %d\nPoints: %d   Tier: %d of %d\n", SpireSeason.current(), st.points or 0, tier, #SpirePath.REWARDS)
	if nextReward then
		text = text .. string.format("Next tier at %d points: %s\n", (tier + 1) * SpirePath.TIER_POINTS, nextReward.title and ("the title \"" .. nextReward.title .. "\"") or nextReward.name)
	end
	text = text .. "\n" .. table.concat(SpirePath.lines(st, os.time()), "\n") .. "\n\nRewards are cosmetic only. Botting doesn't count."
	player:showTextDialog(2821, text)
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()
