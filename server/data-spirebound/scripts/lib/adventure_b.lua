-- The adventure layer's Session B rules (roadmap AD4, AD5): rare roamers, treasure maps, addon hunts, hidden places.
-- Loaded here (scripts/lib loads before every other script, after lib/lib.lua) so lib/lib.lua stays one session's file.
dofile(DATA_DIRECTORY .. "/lib/spirebound/adventure_data.lua")
dofile(DATA_DIRECTORY .. "/lib/spirebound/roamers.lua")
dofile(DATA_DIRECTORY .. "/lib/spirebound/treasure_maps.lua")
