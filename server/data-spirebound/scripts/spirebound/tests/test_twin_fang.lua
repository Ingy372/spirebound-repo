-- Roadmap 5.3: the Twin Fang trial.
SpireTest.add("twin fang: eligibility, 3 holders per season, trial point", function()
	local e = SwordSkills.twinFangEligible
	SpireTest.eq((e(4, 90, 1200, 0)), true, "qualified vanguard")
	SpireTest.eq((e(3, 90, 1200, 0)), false, "rangers can't")
	SpireTest.eq((e(4, 70, 1200, 0)), false, "sword skill too low")
	SpireTest.eq((e(4, 90, 500, 0)), false, "not enough combos")
	SpireTest.eq((e(4, 90, 1200, 3)), false, "4th attempt refused: three holders already")
	if not WorldPoints.twin_fang_trial then error("no trial point on floor 8") end
	SpireTest.eq(Floors.at(WorldPoints.twin_fang_trial), 8, "the trial is on floor 8")
	local n = 0
	for _, d in ipairs(SwordSkills.list) do
		if d.twinFang then n = n + 1 end
	end
	SpireTest.eq(n, 3, "three exclusive Twin Fang skills")
	if not MonsterType("Twin Fang Warden") then error("no trial warden") end
end)
