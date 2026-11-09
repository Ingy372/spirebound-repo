-- Roadmap 1.20: messages for the Spirebound client.
SpireTest.add("client link: JSON encoding and floor lookup", function()
	SpireTest.eq(SpireClient.encode({ t = "floor", n = 1, name = "Hearthgate Plains" }), '{"n":1,"name":"Hearthgate Plains","t":"floor"}', "floor message")
	SpireTest.eq(SpireClient.encode({ 1, 2 }), "[1,2]", "list")
	SpireTest.eq(SpireClient.encode('say "hi"'), '"say \\u0022hi\\u0022"', "quotes escaped")
	SpireTest.eq(Floors.at(WorldPoints.temple_hearthgate), 1, "temple is on floor 1")
	SpireTest.eq(Floors.at(WorldPoints.floor2_landing), 2, "landing is on floor 2")
	SpireTest.eq(Floors.at(Position(100, 100, 7)), 0, "outside the tower")
end)
