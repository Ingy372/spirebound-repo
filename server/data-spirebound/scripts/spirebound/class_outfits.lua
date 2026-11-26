-- Class outfits (roadmap 6.5): the four approved Blender-pipeline outfits, each with a look number of its own
-- (tools/make_creature_sheets.py NEW_LOOKS, put in the client by tools/install_effects.py, listed in outfits.xml by
-- tools/build_server.py). A class owns its outfit: a player gets it when they pick the class at the Registrar, and
-- wears it once automatically. Older characters get it at their next login.
-- (Claude's call, Jay can veto: only your own class's outfit, so a glance tells the classes apart in PvP.)
-- There is no colour-mask layer yet, so the outfit colour choices do nothing on these four.
ClassOutfits = {
	LOOKS = { [1] = 2003, [2] = 2004, [3] = 2002, [4] = 2001 }, -- base vocation: Arcanist, Mystic, Ranger, Vanguard
}

local function store(player)
	return player:kv():scoped("spirebound-class-outfit")
end

-- give the player their class outfit; wear = put it on now (only once per character unless forced)
function ClassOutfits.give(player, wear)
	local voc = player:getVocation()
	local look = voc and ClassOutfits.LOOKS[voc:getBaseId()]
	if not look then
		return false
	end
	if not player:hasOutfit(look) then
		player:addOutfit(look)
	end
	if wear or not store(player):get("worn") then
		local o = player:getOutfit()
		o.lookType = look
		o.lookAddons = 0
		player:setOutfit(o)
		store(player):set("worn", look)
	end
	return true
end

local login = CreatureEvent("SpireClassOutfitLogin")
function login.onLogin(player)
	ClassOutfits.give(player, false)
	return true
end
login:register()
