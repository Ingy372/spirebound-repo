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

-- Construction kits and house fixtures (roadmap 3.5) ---------------------
-- Our own kit: the exercise dummy (Canary's house dummy). Furniture kits use the stock construction_kits action.
SpireHouses.KITS = { [23398] = 28559 }
-- Furniture kits the stock action builds (used to check Season Path rewards and the Housewright's shop)
SpireHouses.FURNITURE_KITS = {}
for id = 2775, 2812 do
	SpireHouses.FURNITURE_KITS[id] = true
end
SpireHouses.MANNEQUIN_SLOTS = 3
SpireHouses.POND_BAIT_BASE = 5

-- Pure: may a kit be built here? onFloor = not in a container; houseAccess = owner/subowner of the house on that tile
function SpireHouses.canBuild(kitId, onFloor, isHouseTile, houseAccess)
	if not SpireHouses.KITS[kitId] then
		return false, "This is not a construction kit."
	end
	if not onFloor then
		return false, "Put the kit on the floor of your house first."
	end
	if not isHouseTile then
		return false, "You can only build this inside a house."
	end
	if not houseAccess then
		return false, "Only the owner or a subowner can build here."
	end
	return true
end

-- Pure: trophy hall lines from { [boss] = { first = time, kills = n } }
function SpireHouses.trophyLines(trophies)
	local list = {}
	for boss, t in pairs(trophies or {}) do
		table.insert(list, { boss = boss, first = t.first or 0, kills = t.kills or 1 })
	end
	table.sort(list, function(a, b) return a.first < b.first end)
	local out = {}
	for i, t in ipairs(list) do
		out[i] = string.format("%s - first beaten %s, %d time%s", t.boss, os.date("%Y-%m-%d", t.first), t.kills, t.kills == 1 and "" or "s")
	end
	return out
end

-- Pure: daily bait from the pond: 5 worms + 1 per fish kind stocked (max 20). lastDay = day number last collected
function SpireHouses.pondBait(kinds, lastDay, today)
	if lastDay == today then
		return 0
	end
	return math.min(20, SpireHouses.POND_BAIT_BASE + (kinds or 0))
end
