-- Every player:method() our scripts call must exist in this engine (Canary 3.6.1). Found 2026-11-23: the Weaponsmith's
-- wallet called player:getTotalMoney(), which this Canary doesn't have; the unit tests used a fake wallet, so only
-- talking to Garrick in the real client showed it (the NPC went silent).
local ALLOWED = {} -- names that are fields of our own fake players in pure functions, if any ever need it

SpireTest.add("engine: every player:method() in our scripts exists on Player", function()
	local p = io.popen("ls data-spirebound/lib/spirebound/*.lua data-spirebound/scripts/spirebound/*.lua data-spirebound/npc/*.lua 2>/dev/null")
	local files = {}
	for line in p:lines() do
		table.insert(files, line)
	end
	p:close()
	SpireTest.eq(#files > 50, true, "found our script files (" .. #files .. ")")
	local missing = {}
	for _, path in ipairs(files) do
		local f = io.open(path, "r")
		if f then
			local n = 0
			for line in f:lines() do
				n = n + 1
				if not line:match("^%s*%-%-") then
					for name in line:gmatch("[^%w_]player:([%a_][%w_]*)%(") do
						if Player[name] == nil and not ALLOWED[name] then
							table.insert(missing, path:match("[^/]+$") .. ":" .. n .. " player:" .. name)
						end
					end
				end
			end
			f:close()
		end
	end
	SpireTest.eq(table.concat(missing, ", "), "", "methods this engine does not have")
end)
