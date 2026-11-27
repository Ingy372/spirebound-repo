-- Spire Manor: the one house sold only in the Spire Shop (DESIGN.md 7.6; Jay, 2026-11-26: "it needs to feel premium,
-- and also have features that players would want to pay for, but not be totally game breaking").
-- The rule every perk here follows: space, comfort, convenience and show. Never damage, defence, experience, loot,
-- skill speed, or a way out of a fight. Map: maps/manor.py. Commands and events: scripts/spirebound/manor.lua.
SpireManor = {
	HOUSE = "Spire Manor",
	TITLE = "Keeper of Spire Manor", -- kept for good, like every title (it follows the account into later seasons)
	MANNEQUINS = 10, -- an ordinary house has 3
	OPEN_HOUSE_TIME = 6 * 3600, -- an ordinary house: 2 hours
	OPEN_HOUSE_COOLDOWN = 12 * 3600, -- an ordinary house: 24 hours
	WAYSTONE_COOLDOWN = 30 * 60, -- one journey by the Waystone per character every half hour
	WAYSTONE_RADIUS = 3, -- how close to the stone you must stand
	FIXTURE_AID = 59900, -- the manor's own furniture (maps/manor.py): it can't be moved, taken or sold
}

function SpireManor.is(house)
	return house ~= nil and house:getName() == SpireManor.HOUSE
end

-- Pure: how many mannequins a house holds
function SpireManor.mannequinSlots(isManor, ordinary)
	return isManor and SpireManor.MANNEQUINS or ordinary
end

-- Pure: may this house open to the public again? Returns ok, hours to wait.
function SpireManor.openHouseAllowed(lastOpened, now)
	if lastOpened and now - lastOpened < SpireManor.OPEN_HOUSE_COOLDOWN then
		return false, math.ceil((SpireManor.OPEN_HOUSE_COOLDOWN - (now - lastOpened)) / 3600)
	end
	return true
end

local function cooled(lastUse, now)
	if lastUse and now - lastUse < SpireManor.WAYSTONE_COOLDOWN then
		return false, math.ceil((SpireManor.WAYSTONE_COOLDOWN - (now - lastUse)) / 60)
	end
	return true
end

-- Pure: the Waystone on the manor's roof sends whoever stands by it (the owner and invited guests: nobody else can
-- get up there) to the temple of any OPEN floor's town. a = { nearStone, floor, floorOpen, inFight, lastUse, now }
function SpireManor.waystoneOut(a)
	if not a.nearStone then
		return false, "Stand by the Waystone on Spire Manor's roof."
	end
	if not a.floor or a.floor < 1 then
		return false, "Which floor? Say !manor travel 2 (or any floor the tower has opened)."
	end
	if not a.floorOpen then
		return false, "Floor " .. a.floor .. " is still sealed. The Waystone only reaches floors the tower has opened."
	end
	if a.inFight then
		return false, "The Waystone stays dark while you are in a fight."
	end
	local ok, minutes = cooled(a.lastUse, a.now)
	if not ok then
		return false, "The Waystone is still gathering light: " .. minutes .. " more minutes."
	end
	return true
end

-- Pure: the owner alone can be called home to the manor, and only from inside a town (a safe zone), so it is never
-- an escape. a = { isOwner, inTown, inFight, lastUse, now }
function SpireManor.recall(a)
	if not a.isOwner then
		return false, "Only the Keeper of Spire Manor can be called home by its Waystone."
	end
	if not a.inTown then
		return false, "The Waystone can only call you home from inside a town."
	end
	if a.inFight then
		return false, "The Waystone stays dark while you are in a fight."
	end
	local ok, minutes = cooled(a.lastUse, a.now)
	if not ok then
		return false, "The Waystone is still gathering light: " .. minutes .. " more minutes."
	end
	return true
end

-- What the manor offers, for the !manor window and the shop page
function SpireManor.lines()
	return {
		"SPIRE MANOR, Hearthgate. One owner. Sold only in the Spire Shop; no rent.",
		"",
		"The house: four floors and nearly 900 tiles (an ordinary house has about 40).",
		"  1  Great hall with a fountain, dining hall, steward's office",
		"  2  Trophy and mannequin gallery, library, training hall",
		"  3  Master suite, lounge, two guest rooms",
		"  4  Roof garden with a fish pond, a telescope and the Waystone",
		"",
		"Only at the manor:",
		"- A private depot (two lockers) and mailbox in the steward's office.",
		"- Steward Aldous: your bank, at home. Housekeeper Mirelle: sells supplies and buys loot at the town's prices.",
		"- Three exercise dummies in the training hall (the same training as the town's).",
		"- " .. SpireManor.MANNEQUINS .. " mannequins for your outfits (other houses: 3).",
		"- A Fortune Hall license at no cost.",
		"- Open House for " .. (SpireManor.OPEN_HOUSE_TIME / 3600) .. " hours, twice a day (other houses: 2 hours, once a day).",
		"- The Waystone: !manor travel <floor> takes you and your guests from the roof to any open floor's town;",
		"  !manor home calls the owner back from inside any town. Once every " .. (SpireManor.WAYSTONE_COOLDOWN / 60) .. " minutes, never in a fight.",
		"- The title \"" .. SpireManor.TITLE .. "\", yours for good.",
		"",
		"Everything a house can do works here too: !portal, !summon, !trophies, !pond, !mannequin, !openhouse.",
		"No experience, damage, defence or loot is sold with it.",
	}
end
