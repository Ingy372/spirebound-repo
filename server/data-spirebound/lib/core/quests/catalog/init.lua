local questModules = {
	"q1_1",
	"q1_2",
	"q1_3",
}

local catalog = dofile(CORE_DIRECTORY .. "/lib/core/quests/catalog.lua")

return catalog.build(DATA_DIRECTORY .. ".lib.core.quests.catalog", questModules)
