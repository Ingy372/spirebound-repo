#!/usr/bin/env python3
"""Writes Hearthgate's townsfolk (roadmap P3, Jay's playtest 2026-11-23: "Hearthgate feels dead"): people who walk
about Hearth Plaza, chat to themselves now and then, and give a useful tip when greeted. The town crier also calls
out the tower's news. They are spawned at start-up by scripts/spirebound/townlife.lua (no map change).
Usage: python tools/gen_townsfolk.py"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "server" / "data-spirebound" / "npc"

# name, file, look (type, head, body, legs, feet, addons), where (a world point or [x, y, z]), walk radius,
# what they say to themselves, what they tell a climber who greets them (one picked each time)
FOLK = [
    dict(file="town_crier", name="Crier Halsey", desc="the town crier of Hearthgate", look=(128, 78, 94, 114, 95, 1),
         near=(1233, 1275, 7), radius=3, crier=True,
         chatter=["Hear ye! The tower stands sealed! Who will climb?", "News of the Spire, every hour on the hour!",
                  "Lost a friend in the wilds? The Priest in the Climbers' Temple heals for free below level 50!"],
         tips=["Say !hunt and the tower will tell you where to fight at your level.",
               "Every hour one lucky climber gets gold in the bank. Be online and be lucky!",
               "Climbers who read the old stones in the wilds sell the story to Vesper. Ask her for a quest."]),
    dict(file="town_lamplighter", name="Lamplighter Odo", desc="the lamplighter", look=(128, 58, 79, 76, 115, 0),
         near=(1218, 1286, 7), radius=6,
         chatter=["Lamps lit, lamps lit...", "One more round the plaza, then my supper.", "Mind the ladder!"],
         tips=["The wilds are calm near their gates and grow fierce the deeper you go. Turn back while you can.",
               "At night the lamps of Hearthgate guide you home. Follow the road and you can't get lost.",
               "A '!' on your minimap marks someone with work for you."]),
    dict(file="town_baker", name="Baker Wenna", desc="the baker's wife", look=(136, 78, 39, 76, 115, 0),
         near=(1228, 1297, 7), radius=4,
         chatter=["Fresh bread! Well, yesterday's bread.", "Miller Agna's flour is the best on the floor.",
                  "Who keeps stealing my cheese? Rats, I tell you."],
         tips=["Miller Agna in Millcross always needs a hand, and her flour pays well if it reaches the guards.",
               "Field rats will snatch coins right out of your pack. Kill the thief and you get them back.",
               "Hungry? Food brings your health and mana back faster while you rest."]),
    dict(file="town_elder", name="Old Teodric", desc="an old man who has seen everything", look=(128, 0, 57, 57, 76, 0),
         near=(1232, 1268, 7), radius=2,
         chatter=["In my day the Pass was a cart road.", "*coughs* The fountain was dry for forty years, you know.",
                  "Blue light at the top of the Spire... never trusted it."],
         tips=["They say the builders carved their story on six stones in the wilds. I read three, once.",
               "The Gate Hound guards the Pass. Never go alone: take two friends, at least.",
               "The Axe-Lord's hall opens only for those who hold the Stair Key. Ask your quest log what it needs."]),
    dict(file="town_child", name="Little Bix", desc="a child who never stops running", look=(2028, 0, 0, 0, 0, 0),
         near=(1238, 1282, 7), radius=7,
         chatter=["Can't catch me!", "I'm going to climb the whole tower when I'm big!", "Tag, you're it!"],
         tips=["There's a sluice in the marsh with three levers! I pulled them all and nothing happened...",
               "My brother saw a GLOWING boar in the meadow! It was huge!",
               "Hunter Brannoch is scary but he pays good gold."]),
    dict(file="town_guard", name="Guard Ressa", desc="a guard of Hearthgate", look=(2023, 0, 0, 0, 0, 0),
         near=(1247, 1285, 7), radius=4,
         chatter=["Keep the peace in town.", "Captain Dorrow wants more climbers on the north road.",
                  "No fighting in town. Take it outside the walls."],
         tips=["Inside Hearthgate nobody can attack you. Out in the Guarded lands, only players of 50 and up fight each other.",
               "Captain Dorrow at the north gate hands out a real weapon to climbers who reach level 10.",
               "Bandits on the east road hit hard. Don't go there before level 19."]),
    dict(file="town_porter", name="Porter Gimble", desc="a porter who carries climbers' crates to the lockers",
         look=(128, 95, 58, 58, 76, 0), near=(1226, 1286, 7), radius=4,
         chatter=["Mind your backs! Crate coming through!", "Twenty lockers and every one of them full of junk...",
                  "Who packs a whole boar in a backpack? Climbers, that's who."],
         tips=["Your depot lockers are shared: whatever you leave here is waiting at every depot in the tower.",
               "Coins you loot go straight to the bank. Banker Tolliver at the west counter will tell you your balance.",
               "Sell your loot to Trader Osric at the west counter, or put it on the market from any locker."]),
    dict(file="town_florist", name="Lysa the Florist", desc="a girl selling flowers she never seems to sell",
         look=(136, 79, 86, 86, 95, 0), near=(1226, 1270, 7), radius=3,
         chatter=["Flowers! Fresh flowers for the brave!", "The temple garden grows the best roses on the floor.",
                  "A flower for your sweetheart before you climb?"],
         tips=["Priest Odran in the Climbers' Temple can heal and bless you. The temple is just north of the Hearth.",
               "The Trading Gallery upstairs in the temple is where climbers haggle face to face.",
               "Hearthgate Green has a pond with lilies. The fishermen say something big lives in it."]),
    dict(file="town_minstrel", name="Corwin the Minstrel", desc="a minstrel who sings of climbers past",
         look=(128, 114, 94, 79, 76, 1), near=(1240, 1295, 7), radius=2,
         chatter=["*strums* Oh the tower stands so tall and grey...", "A copper for a song? No? A song anyway!",
                  "*hums a tune about the Gate Hound*"],
         tips=["The Floor Beacon by the Hearth: light a fire bowl and everyone on the floor hunts better for an hour.",
               "The Monument by the Hearth carries the names of those who opened each floor. Be the next!",
               "Every arena event crowns a champion. Their statue stands right here by the fountain."]),
]

TEMPLATE = '''-- GENERATED by tools/gen_townsfolk.py. Hearthgate townsfolk (roadmap P3): walks about, talks to itself, gives a tip.
local npcName = "{name}"
local npcType = Game.createNpcType(npcName)
local npcConfig = {{}}
npcConfig.name = npcName
npcConfig.description = "{desc}"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 2000
npcConfig.walkRadius = {radius}
npcConfig.outfit = {{ lookType = {l0}, lookHead = {l1}, lookBody = {l2}, lookLegs = {l3}, lookFeet = {l4}, lookAddons = {l5} }}
npcConfig.flags = {{ floorchange = false }}
-- G12 (Grok session 3): six townsfolk at one line per ~57 s each filled the square's chat; now about one every 3 minutes each
npcConfig.voices = {{
	interval = 45000,
	chance = 25,
{voices}
}}

local TIPS = {{
{tips}
}}

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval)
	npcHandler:onThink(npc, interval){crier_think}
end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local function greet(npc, player)
	npcHandler:say(TIPS[math.random(#TIPS)], npc, player)
	return true
end

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	if SpireHunt and MsgContains(msg, "hunt") then
		npcHandler:say(SpireHunt.advice(player:getLevel()), npc, player)
		return true
	end
	return greet(npc, player)
end

npcHandler:setMessage(MESSAGE_GREET, "Oh, hello |PLAYERNAME|! Want a {{tip}}? Or ask me where to {{hunt}}.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Off you go, then!")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
'''

CRIER = '''
	-- the crier calls out the tower's news every few minutes
	SpireCrier = SpireCrier or {{ last = 0 }}
	if os.time() - SpireCrier.last >= 180 and Floors and Floors.raceLine then
		SpireCrier.last = os.time()
		local top = Floors.highestOpen()
		npc:say("Hear ye! " .. Floors.raceLine(top, Floors.get(top)):gsub("^The tower: ", ""), TALKTYPE_SAY)
	end'''


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    for f in FOLK:
        look = list(f["look"]) + [0] * (6 - len(f["look"]))
        text = TEMPLATE.format(
            name=f["name"], desc=f["desc"], radius=f["radius"], l0=look[0], l1=look[1], l2=look[2], l3=look[3],
            l4=look[4], l5=look[5],
            voices="\n".join(f"\t{{ text = {lua_str(v)} }}," for v in f["chatter"]),
            tips="\n".join(f"\t{lua_str(t)}," for t in f["tips"]),
            crier_think=CRIER.format() if f.get("crier") else "")
        (OUT / f"{f['file']}.lua").write_text(text, encoding="utf-8", newline="\n")
    lua = ["-- GENERATED by tools/gen_townsfolk.py: where each townsperson starts (scripts/spirebound/townlife.lua)",
           "SpireTownsfolk = {"]
    for f in FOLK:
        x, y, z = f["near"]
        lua.append(f"\t{{ name = {lua_str(f['name'])}, near = Position({x}, {y}, {z}) }},")
    lua.append("}")
    (OUT.parent / "lib" / "spirebound" / "townsfolk.lua").write_text("\n".join(lua) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(FOLK)} townsfolk")


if __name__ == "__main__":
    main()
