-- Forget per-player memory at logout (roadmap R20, REVIEW 3.12): every script that keeps a table keyed by a
-- player registers a function here; scripts/spirebound/cleanup.lua calls them all when a player logs out.
SpireCleanup = SpireCleanup or { fns = {} }

function SpireCleanup.add(fn)
	table.insert(SpireCleanup.fns, fn)
end

function SpireCleanup.run(playerId, guid)
	for _, fn in ipairs(SpireCleanup.fns) do
		pcall(fn, playerId, guid)
	end
	return #SpireCleanup.fns
end
