-- N8: kills are counted through one death callback, not the deprecated onKill event.
SpireTest.add("N8: every kill counter is reached through SpireKills, and one failure doesn't stop the rest", function()
	for _, name in ipairs({ "SpireTaskKill", "SpirePathKill", "SpireChronicleKill", "SpireBotWatchKill", "SpireTutorialKill", "SpireProgressKill" }) do
		SpireTest.eq(type(SpireKills.handlers[name]), "function", name .. " counts kills through SpireKills")
	end
	local saved, savedOrder, savedReport = SpireKills.handlers, SpireKills.order, SpireKills.report
	local reported
	SpireKills.report = function(name) reported = name end -- keeps the boot log free of a test error
	local hits = {}
	SpireKills.handlers, SpireKills.order = {}, {}
	SpireKills.on("a", function(p, t) hits.a = t end)
	SpireKills.on("b", function() error("boom") end)
	SpireKills.on("c", function(p, t) hits.c = t end)
	local ok, n = pcall(SpireKills.fire, nil, "rat")
	SpireKills.handlers, SpireKills.order, SpireKills.report = saved, savedOrder, savedReport
	SpireTest.eq(reported, "b", "the failure is reported by name")
	SpireTest.eq(ok, true, "a failing counter is caught")
	SpireTest.eq(n, 2, "the other two still counted")
	SpireTest.eq(hits.a == "rat" and hits.c == "rat", true, "each counter gets the dead monster")
end)
