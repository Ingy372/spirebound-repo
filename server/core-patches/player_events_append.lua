
-- ---------------------------------------------------------------- Spirebound (appended by tools/build_server.py)
-- Canary 3.6.1 ignores what EventCallback playerOnGainExperience / playerOnGainSkillTries functions return (they are
-- "void": data/scripts/eventcallbacks/README.md), so none of Spirebound's experience or skill modifiers reached the
-- player (measured on a real character, Floor 1 review 2026-11-26: Death Game, the cavebot, Beacons, weekend events
-- and the boosted creature all gave exactly the plain amount). The engine does use what these two functions return,
-- so Spirebound's factors are applied here, after the engine's own (lib/spirebound/hooks.lua).
local spireBaseGainExperience = Player.onGainExperience
function Player:onGainExperience(target, exp, rawExp)
	local out = spireBaseGainExperience(self, target, exp, rawExp)
	if SpireHooks and target and target:isMonster() then -- kills only: quest rewards and corrections stay as given
		-- Jay, Q83 (2026-11-27): "Yes, 11-15 hours". The engine's hidden 1.5x below level 50 is taken back out here;
		-- Tibia's own rested-stamina bonus stays.
		local boost = self:getXpBoostTime() > 0 and self:getXpBoostPercent() or 0
		out = SpireHooks.withoutLowLevelBonus(out, boost, self:getFinalLowLevelBonus())
		return SpireHooks.gainExperience(self, target, out, rawExp)
	end
	return out
end

local spireBaseGainSkillTries = Player.onGainSkillTries
function Player:onGainSkillTries(skill, tries)
	local out = spireBaseGainSkillTries(self, skill, tries)
	if SpireHooks then
		return SpireHooks.gainSkillTries(self, skill, out)
	end
	return out
end
