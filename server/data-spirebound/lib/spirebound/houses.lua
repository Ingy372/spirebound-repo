-- Houses that do things (DESIGN.md 7.3 - 7.5). Roadmap phase 3.
SpireHouses = {
	HEAD_START = 60 * 60, -- credited first-clear players get one hour to buy in the new floor's town
	PORTAL_CHANGES = 3, -- a house portal destination can only ever be set 3 times (per character per season)
	PORTAL_BOSS_DISTANCE = 20,
	SUMMON_MIN_SIZE = 30, -- house tiles needed for a Summoning Circle
	DICE_MAX_BET = 1000000,
	DICE_CUT = 0.05, -- the hall keeps 5%, destroyed (gold sink)
	LICENSE_COST = 250000, -- Fortune Hall license
	OPEN_HOUSE_TIME = 2 * 3600,
	floorTown = { [2] = 3 }, -- floor -> town id whose district opens with it
}

-- Head start ------------------------------------------------------------
local function hs()
	return kv.scoped("spirebound-headstart")
end

function SpireHouses.startHeadStart(townId, creditNames, districtSize, now)
	hs():set(tostring(townId), { untilTime = now + SpireHouses.HEAD_START, credited = creditNames, cap = math.ceil(districtSize / 2), sold = 0 })
end

-- Pure: may `name` buy now? rec = head start record or nil
function SpireHouses.headStartAllows(rec, name, now)
	if not rec or now >= rec.untilTime then
		return true
	end
	if rec.sold >= rec.cap then
		return false, "The head-start houses are all taken. The district opens to everyone within the hour."
	end
	for _, n in ipairs(rec.credited or {}) do
		if n == name then
			return true
		end
	end
	return false, "This district is reserved for the floor's first clearers for one hour."
end

function SpireHouses.headStartRecord(townId)
	return hs():get(tostring(townId))
end

function SpireHouses.noteHeadStartSale(townId)
	local rec = hs():get(tostring(townId))
	if rec and os.time() < rec.untilTime then
		rec.sold = rec.sold + 1
		hs():set(tostring(townId), rec)
	end
end

-- House portal ----------------------------------------------------------
-- Pure: is this a legal portal target? zone = PvP zone tier; nearBoss = within PORTAL_BOSS_DISTANCE of a boss room
function SpireHouses.portalTargetAllowed(zone, nearBoss, isSecretTile, isHouseTile)
	if zone == "bossroom" or zone == "deadzone" then
		return false, "The portal can't reach boss rooms or Deadzones."
	end
	if nearBoss then
		return false, "Too close to a floor boss."
	end
	if isSecretTile then
		return false, "Secrets can't be portal targets."
	end
	if isHouseTile then
		return false, "Choose a spot outside of houses."
	end
	return true
end

function SpireHouses.portalChangesLeft(used)
	return math.max(0, SpireHouses.PORTAL_CHANGES - (used or 0))
end

-- Fortune Hall dice ------------------------------------------------------
-- Pure: payout to a winning bettor and the destroyed cut
function SpireHouses.dicePayout(bet)
	local gross = bet * 2
	local cut = math.floor(gross * SpireHouses.DICE_CUT)
	return gross - cut, cut
end

-- Pure: high = 4-6, low = 1-3
function SpireHouses.diceWins(call, roll)
	if call == "high" then
		return roll >= 4
	end
	return roll <= 3
end

-- Relist announcements (roadmap 3.1b) ------------------------------------
-- Pure: which houses were owned in `before` (id -> true) but are free in `now` (id -> true if owned)?
function SpireHouses.freedHouses(before, now)
	local freed = {}
	for id, _ in pairs(before or {}) do
		if not now[id] then
			table.insert(freed, id)
		end
	end
	table.sort(freed)
	return freed
end

-- Pure: the announcement text for freed houses (names = list of "House (Town)"), nil if none
function SpireHouses.relistText(names)
	if #names == 0 then
		return nil
	end
	if #names <= 3 then
		return "Back on the market: " .. table.concat(names, ", ") .. ". Say !buyhouse at the door."
	end
	return string.format("%d houses are back on the market, including %s. Say !buyhouse at the door.", #names, table.concat({ names[1], names[2], names[3] }, ", "))
end
