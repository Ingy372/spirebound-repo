-- Spirebound: a bookmark in vBot's load order (client/modules/game_spirebound/bot/spirebound_pvp_guard.lua). The installer loads this file
-- right before and right after the scripts that may keep running in a fight with a player (healing and eating), and
-- once more right before spirebound_report. Each load writes down how many helper jobs (macros) exist so far, so the
-- guard knows which jobs belong to which scripts.
SpireMarks = SpireMarks or {}
table.insert(SpireMarks, #_macros)
