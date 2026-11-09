-- Spirebound experience, skill and magic stages (DESIGN.md 5.5).
-- Copied over Canary's data/stages.lua by tools/build_server.py.
-- Medium rates: faster early, slower later. No level cap.

experienceStages = {
	{ minlevel = 1, maxlevel = 50, multiplier = 25 },
	{ minlevel = 51, maxlevel = 100, multiplier = 15 },
	{ minlevel = 101, maxlevel = 150, multiplier = 10 },
	{ minlevel = 151, maxlevel = 200, multiplier = 7 },
	{ minlevel = 201, maxlevel = 300, multiplier = 5 },
	{ minlevel = 301, maxlevel = 400, multiplier = 3 },
	{ minlevel = 401, multiplier = 2 },
}

-- Skills (sword/axe/club/distance/shielding/fishing): flat 10x.
skillsStages = {
	{ minlevel = 0, multiplier = 10 },
}

-- Magic level: flat 5x.
magicLevelStages = {
	{ minlevel = 0, multiplier = 5 },
}
