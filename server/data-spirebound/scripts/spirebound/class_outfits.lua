-- Class outfits (roadmap 6.5): the four approved Blender-pipeline outfits, each with a look number of its own
-- (tools/make_creature_sheets.py NEW_LOOKS, put in the client by tools/install_effects.py, listed in outfits.xml by
-- tools/build_server.py). A class owns its outfit: a player gets it when they pick the class at the Registrar, and
-- wears it once automatically. Older characters get it at their next login.
-- (Claude's call, Jay can veto: only your own class's outfit, so a glance tells the classes apart in PvP.)
-- There is no colour-mask layer yet, so the outfit colour choices do nothing on these four.
-- Each sex has its own body (Jay, 2026-11-26: "Approve all"); PLAYERSEX_FEMALE = 0, PLAYERSEX_MALE = 1.
ClassOutfits = {
	-- base vocation: Arcanist, Mystic, Ranger, Vanguard
	LOOKS = {
		[0] = { [1] = 2003, [2] = 2004, [3] = 2006, [4] = 2005 },
		[1] = { [1] = 2007, [2] = 2008, [3] = 2002, [4] = 2001 },
	},
}

-- the other sex's version of each class outfit (characters made before the split wore one body for both sexes)
local OTHER = {}
for sex = 0, 1 do
	for voc, look in pairs(ClassOutfits.LOOKS[sex]) do
		OTHER[ClassOutfits.LOOKS[1 - sex][voc]] = look
	end
end

local function store(player)
	return player:kv():scoped("spirebound-class-outfit")
end

-- give the player their class outfit; wear = put it on now (only once per character unless forced)
function ClassOutfits.give(player, wear)
	local voc = player:getVocation()
	local looks = ClassOutfits.LOOKS[player:getSex()] or ClassOutfits.LOOKS[1]
	local look = voc and looks[voc:getBaseId()]
	if not look then
		return false
	end
	if not player:hasOutfit(look) then
		player:addOutfit(look)
	end
	local o = player:getOutfit()
	if OTHER[o.lookType] == look then
		-- wearing the other sex's body of this class outfit: swap to their own, keeping the addons
		o.lookType = look
		player:setOutfit(o)
		store(player):set("worn", look)
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
