-- Test-only commands for the Floor 1 depth features (roadmap FD2, FD4, FD5), for the autopilot's Pilot characters.
--   /depth night on|off|auto   force the night (Toad Pond's lilies, the howl's bigger pack) or leave it to the clock
--   /depth tide low|high|auto  force Reedmarsh's tide
--   /depth vines               regrow Thornsnap Hollow's vine walls now
--   /depth wind                the chimes' wind blows now, and the order is told (as if heard)
--   /depth lieutenant          the Bandit Lieutenant comes out now; says where
--   /depth stash               says which of Smugglers' Ridge's stones holds the stash
--   /depth truffle             a truffle spot under you (as if a boar rooted there)
--   /depth seedling            a sproutling seedling under you (it grows in two minutes)
--   /depth forget              this character forgets its ground lore, Cookbook and cool-downs
--   /depth works               the Works state; "/depth works reset" starts the season's Works again (pieces stay till restart)
if os.getenv("SPIRE_DEV") ~= "1" and os.getenv("SPIRE_TESTS") ~= "1" and os.getenv("SPIRE_LOADTEST") ~= "1" then
	logger.info("[Spirebound] {} not loaded: this is not a dev or test server", "the /depth test commands")
	return
end

local depth = TalkAction("/depth")
function depth.onSay(player, words, param)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	if not email or not email:match("^autopilot%d*@localhost$") then
		return false
	end
	local F = SpireFeatures
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	local say = function(t) player:sendTextMessage(MESSAGE_STATUS, "depth: " .. t) end
	if cmd == "night" then
		if rest == "on" then
			F.forceNight = true
		elseif rest == "off" then
			F.forceNight = false
		else
			F.forceNight = nil
		end
		F.liliesUp(F.forceNight == nil and F.isNight() or F.forceNight)
		say("night " .. tostring(F.forceNight))
	elseif cmd == "tide" then
		if rest == "low" then
			F.forceTide = true
		elseif rest == "high" then
			F.forceTide = false
		else
			F.forceTide = nil
		end
		F.tideSet(F.forceTide == nil and false or F.forceTide)
		local where = {}
		for _, rec in ipairs(F.state.tide.items or {}) do
			table.insert(where, rec.id .. "@" .. rec.pos.x .. "," .. rec.pos.y)
		end
		say("tide low " .. tostring(F.forceTide) .. " " .. table.concat(where, " "))
	elseif cmd == "vines" then
		say(F.vineWalls() .. " vine tiles stand")
	elseif cmd == "wind" then
		F.wind()
		say("the wind plays " .. table.concat(F.state.chimes.order, " "))
	elseif cmd == "lieutenant" then
		F.state.lieutenant = nil
		F.lieutenantOut()
		local L = F.state.lieutenant
		local m = L and Monster(L.id)
		say(m and ("out on loop " .. L.loop .. " at " .. m:getPosition():toString()) or "no lieutenant")
	elseif cmd == "stash" then
		if not F.state.stash.idx then
			F.stashPick()
		end
		local p = WorldPoints["feat_stash_" .. F.state.stash.idx]
		say("the stash is under stone " .. F.state.stash.idx .. (p and (" at " .. p.x .. "," .. p.y) or ""))
	elseif cmd == "truffle" then
		F.truffleSpot(player:getPosition())
		say("truffle spot made")
	elseif cmd == "seedling" then
		say(F.plantSeedling(player:getPosition()) and "seedling made (it grows in two minutes)" or "no room for a seedling")
	elseif cmd == "forget" then
		for _, f in ipairs(SpireDepthData.features) do
			SpireDiscoveries.unmark(player, "groundlore", f.id)
		end
		for _, d in ipairs(SpireDepthData.cooking.dishes) do
			player:kv():scoped("spirebound-cookbook"):remove(d.id)
			SpireDiscoveries.unmark(player, "cookbook", d.id)
		end
		for k in pairs(F.cool) do
			if k:find("^" .. player:getGuid() .. ":") then
				F.cool[k] = nil
			end
		end
		say("forgotten")
	elseif cmd == "probe" then
		local x, y, z = rest:match("(%d+)%D+(%d+)%D+(%d+)")
		local t = x and Tile(Position(tonumber(x), tonumber(y), tonumber(z)))
		local out = {}
		for _, it in ipairs(t and t:getItems() or {}) do
			table.insert(out, it:getId() .. "/" .. it:getActionId())
		end
		say("tile " .. tostring(rest) .. ": ground " .. tostring(t and t:getGround() and t:getGround():getId()) .. ", items " .. table.concat(out, " "))
	elseif cmd == "works" then
		if rest == "reset" then
			kv.scoped("spirebound-works"):remove("state")
		elseif rest == "nocap" then
			SpireWorks.noCap = true
		end
		local s = SpireWorks.state()
		say(string.format("project %d, %d of %s given", s.current, s.given, tostring(s.size)))
	else
		say("night|tide|vines|wind|lieutenant|stash|truffle|seedling|forget|works")
	end
	return true
end
depth:separator(" ")
depth:groupType("normal")
depth:register()
