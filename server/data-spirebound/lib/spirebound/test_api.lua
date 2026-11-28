-- Test registration helpers. Lives in lib/ so it always loads before any test script,
-- whatever order the filesystem lists the script folders in.
SpireTest = SpireTest or { tests = {} }

function SpireTest.add(name, fn)
	table.insert(SpireTest.tests, { name = name, fn = fn })
end

-- total gold value of the coins in a container (for tests of rewards paid into the backpack)
function SpireTest.coinValue(container)
	local n = 0
	for _, it in ipairs(container:getItems(true) or {}) do
		local v = ({ [3031] = 1, [3035] = 100, [3043] = 10000 })[it:getId()]
		if v then
			n = n + v * it:getCount()
		end
	end
	return n
end

function SpireTest.eq(actual, expected, what)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", what or "value", tostring(expected), tostring(actual)), 2)
	end
end
