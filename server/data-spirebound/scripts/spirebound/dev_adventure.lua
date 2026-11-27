-- Test-only commands for the adventure layer (AD1-AD3, AD6, AD7), for the autopilot's Pilot characters.
--   /adv firsts on|off        Pilots count for season firsts (they never do on a real server); off puts it back
--   /adv resetfirst cat id    forget one season first (e.g. "/adv resetfirst secret s12")
--   /adv forget s12           this character forgets a secret: found, its gold, its keepsakes (to test it again)
--   /adv rumourreset          this character may hear a rumour again now
--   /adv bottle               open a message bottle as if fished (the catch itself is a 1-in-100 roll)
--   /adv rare on|off          the next elite this character kills drops a rare weapon
if os.getenv("SPIRE_DEV") ~= "1" and os.getenv("SPIRE_TESTS") ~= "1" and os.getenv("SPIRE_LOADTEST") ~= "1" then
	logger.info("[Spirebound] {} not loaded: this is not a dev or test server", "the /adv test commands")
	return
end

local adv = TalkAction("/adv")
function adv.onSay(player, words, param)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	if not email or not email:match("^autopilot%d*@localhost$") then
		return false
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	local say = function(t) player:sendTextMessage(MESSAGE_STATUS, "adv: " .. t) end
	if cmd == "firsts" then
		if rest == "on" then
			SpireFinds.testerOverride = function() return false end
		else
			SpireFinds.testerOverride = nil
		end
		say("Pilots count for firsts: " .. tostring(SpireFinds.testerOverride ~= nil))
	elseif cmd == "resetfirst" then
		local cat, id = rest:match("^(%S+)%s+(%S+)$")
		if cat then
			SpireFinds.resetFirst(cat, id)
		end
		say("first reset: " .. tostring(cat) .. " " .. tostring(id))
	elseif cmd == "forget" then
		local id = rest:match("^(%S+)")
		local s = id and SpireSecrets.get(id)
		if s then
			SpireSecrets.forget(player, id)
			kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-secretgold"):remove(id)
			local keeps = player:kv():scoped("spirebound-secret-keeps")
			for _, k in ipairs({ "title", "title_r", "aura", "keepsake", "gear" }) do
				keeps:remove(id .. ":" .. k)
			end
			local r = type(s.reward) == "table" and s.reward or {}
			if r.aura then SpireAuras.take(player, r.aura) end
			if r.keepsake then SpireKeepsakes.forget(player, r.keepsake) end
			if r.gear then player:kv():scoped("spirebound-secret-gear"):remove(r.gear) end
			say("forgot " .. id)
		end
	elseif cmd == "rumourreset" then
		player:kv():scoped("spirebound"):remove("rumour_at")
		say("rumour ready")
	elseif cmd == "bottle" then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You fished up a message in a bottle. " .. SpireRumours.openBottle(player))
	elseif cmd == "rare" then
		SpireGear.forceRare = SpireGear.forceRare or {}
		SpireGear.forceRare[player:getId()] = rest == "on" or nil
		say("next elite drops a rare weapon: " .. tostring(rest == "on"))
	else
		say("firsts on|off, resetfirst cat id, forget sN, rumourreset, bottle, rare on|off")
	end
	return true
end
adv:separator(" ")
adv:groupType("normal")
adv:register()
