-- The Floor 1 checklist shown in the "Next upgrade" window (gear progression spec 4.5, 4.7).
-- Each step: key, text, where (one plain sentence part naming the place), done(player) -> bool.
SpireClimb = SpireClimb or {}

local function questDone(id)
	return function(player)
		local q = SpireQuests.get(id)
		return q ~= nil and SpireQuests.state(player, q) == 3
	end
end

local function bossDone(boss)
	return function(player)
		return player:kv():scoped("spirebound"):get("boss_credit_" .. boss) ~= nil
	end
end

SpireClimb.FLOOR1 = {
	{ key = "weapon", text = "Reach level 10 and get your weapon from Captain Dorrow",
		where = "see Captain Dorrow at Hearthgate's north gate and ask for a weapon",
		done = function(player) return SpireGear.earnedMain(player, 1) ~= nil end },
	{ key = "temper", text = "Tempered in the Field (Captain Dorrow)",
		where = "hunt Meadow Wolves in Wolf Copse (west of Hearthgate), then report to Captain Dorrow",
		done = questDone("q1_temper") },
	{ key = "iron1", text = "Iron for the Stair, part 1 (Hunter Brannoch)",
		where = "ask Hunter Brannoch in the Hunters' Hall, then hunt Burrow Moles in Burrow Hills (north-east)",
		done = questDone("q1_iron1") },
	{ key = "iron2", text = "Iron for the Stair, part 2: your Floor 1 armour (Hunter Brannoch)",
		where = "hunt Road Bandits on the Bandit Road (east of Hearthgate), then report to Hunter Brannoch",
		done = questDone("q1_iron2") },
	{ key = "gate_hound", text = "Defeat the Gate Hound",
		where = "fight the Gate Hound at the Pass, the way into the Floor 1 labyrinth",
		done = bossDone("Gate Hound") },
	{ key = "axe_lord", text = "Defeat the Axe-Lord of the Stair: your weapon awakens",
		where = "climb the Floor 1 labyrinth behind the Pass to the Axe-Lord's hall",
		done = bossDone("Axe-Lord of the Stair") },
}

-- The first step not done yet, or nil
function SpireClimb.next(player, steps)
	for _, s in ipairs(steps or SpireClimb.FLOOR1) do
		if not s.done(player) then
			return s
		end
	end
end
