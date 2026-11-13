-- What is switched on for the friends test (roadmap R13, REVIEW 1.3 and 9.2; Q22 assumed "yes"):
-- Floors 1-2 only (3-10 stay sealed even if Floor 2's boss falls), and the Arena, the Spire Siege, the shop and the
-- Season Path are off. The owner can change it in game with /scope. For the public launch set FRIENDS_TEST = false.

SpireScope = SpireScope or {
	FRIENDS_TEST = true,
	MAX_FLOOR = 2,
	OFF = { arena = true, siege = true, shop = true, seasonpath = true },
}

local function store()
	return kv.scoped("spirebound-scope")
end

function SpireScope.active()
	local v = store():get("friendsTest")
	if v == nil then
		return SpireScope.FRIENDS_TEST
	end
	return v == true
end

-- Is a feature switched off right now?
function SpireScope.off(feature)
	return SpireScope.active() and SpireScope.OFF[feature] == true
end

-- Is floor n beyond what this test allows?
function SpireScope.floorSealed(n)
	return SpireScope.active() and n > SpireScope.MAX_FLOOR and n <= 10
end
