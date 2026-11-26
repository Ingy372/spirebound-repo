-- Party size cap (DESIGN.md 7.1, 9.4): up to 8 members including the leader, so a large-group ground fits in one party.
SPIRE_PARTY_MAX = 8

local join = EventCallback("SpirePartyCap")
function join.partyOnJoin(party, player)
	if party:getMemberCount() + 1 >= SPIRE_PARTY_MAX then
		player:sendCancelMessage("That party is full (" .. SPIRE_PARTY_MAX .. " players).")
		return false
	end
	return true
end
join:register()
