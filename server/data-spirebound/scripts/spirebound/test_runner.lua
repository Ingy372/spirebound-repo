-- Spirebound in-game test runner.
-- Tests register with SpireTest.add(name, fn). On startup every test runs
-- once; each prints "[SPIRETEST] PASS <name>" or "[SPIRETEST] FAIL <name>: why".
-- tools/test_boot.sh fails the build on any FAIL.
SpireTest = SpireTest or { tests = {} }

function SpireTest.add(name, fn)
	table.insert(SpireTest.tests, { name = name, fn = fn })
end

function SpireTest.eq(actual, expected, what)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", what or "value", tostring(expected), tostring(actual)), 2)
	end
end

local runner = GlobalEvent("SpireTestRunner")
function runner.onStartup()
	-- Only on test boots (tools/test_boot.sh sets SPIRE_TESTS=1); never on a server people play on.
	if os.getenv("SPIRE_TESTS") ~= "1" then
		return true
	end
	addEvent(function()
		local pass, fail = 0, 0
		for _, t in ipairs(SpireTest.tests) do
			local ok, err = pcall(t.fn)
			if ok then
				pass = pass + 1
				logger.info("[SPIRETEST] PASS {}", t.name)
			else
				fail = fail + 1
				logger.info("[SPIRETEST] FAIL {}: {}", t.name, tostring(err))
			end
		end
		logger.info("[SPIRETEST] done: {} passed, {} failed", pass, fail)
	end, 1000)
end
runner:register()
