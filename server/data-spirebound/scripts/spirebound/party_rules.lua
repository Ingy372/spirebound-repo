-- Party size cap (DESIGN.md 7.1): up to 6 members including the leader.
SPIRE_PARTY_MAX = 6

local join = EventCallback("SpirePartyCap")
function join.partyOnJoin(party, player)
	if party:getMemberCount() + 1 >= SPIRE_PARTY_MAX then
		player:sendCancelMessage("That party is full (" .. SPIRE_PARTY_MAX .. " players).")
		return false
	end
	return true
end
join:register()
