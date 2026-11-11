-- Test registration helpers. Lives in lib/ so it always loads before any test script,
-- whatever order the filesystem lists the script folders in.
SpireTest = SpireTest or { tests = {} }

function SpireTest.add(name, fn)
	table.insert(SpireTest.tests, { name = name, fn = fn })
end

function SpireTest.eq(actual, expected, what)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", what or "value", tostring(expected), tostring(actual)), 2)
	end
end
