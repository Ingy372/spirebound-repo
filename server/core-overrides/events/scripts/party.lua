function Party:onJoin(player)
	local playerUid = player:getGuid()
	addEvent(function(playerFuncUid)
		local playerEvent = Player(playerFuncUid)
		if not playerEvent then
			return
		end
		local party = playerEvent:getParty()
		if not party then
			return
		end
		party:refreshHazard()
	end, 100, playerUid)
	return true
end

function Party:onLeave(player)
	local playerUid = player:getGuid()
	local members = self:getMembers()
	table.insert(members, self:getLeader())
	local memberUids = {}
	for _, member in ipairs(members) do
		if member:getGuid() ~= playerUid then
			table.insert(memberUids, member:getGuid())
		end
	end

	addEvent(function(playerFuncUid, memberUidsTableEvent)
		local playerEvent = Player(playerFuncUid)
		if playerEvent then
			playerEvent:updateHazard()
		end

		for _, memberUid in ipairs(memberUidsTableEvent) do
			local member = Player(memberUid)
			if member then
				local party = member:getParty()
				if party then
					party:refreshHazard()
					return -- Only one player needs to refresh the hazard for the party
				end
			end
		end
	end, 100, playerUid, memberUids)
	return true
end

function Party:onDisband()
	local members = self:getMembers()
	table.insert(members, self:getLeader())
	local memberIds = {}
	for _, member in ipairs(members) do
		if member:getId() ~= playerId then
			table.insert(memberIds, member:getId())
		end
	end
	addEvent(function()
		for _, memberId in ipairs(memberIds) do
			local member = Player(memberId)
			if member then
				member:updateHazard()
			end
		end
	end, 100)
	return true
end

-- Spirebound party bonus (DESIGN.md 7.1): team hunting must beat solo.
-- Multiplier = 1 + 0.30 per extra member + 0.10 per extra vocation; the total is split evenly.
function SpirePartyShare(exp, partySize, uniqueVocations)
	local multiplier = 1 + 0.30 * (partySize - 1) + 0.10 * (math.max(uniqueVocations, 1) - 1)
	return math.ceil((exp * multiplier) / partySize)
end

function Party:onShareExperience(exp)
	return SpirePartyShare(exp, self:getMemberCount() + 1, self:getUniqueVocationsCount())
end
