-- Ending a season (roadmap 8.3): what is wiped. Run OFFLINE only (tools/season_wipe.sh, windows\Season-Reset.bat),
-- after /season end has archived every character and the server has shut down. Never touches accounts, account-level
-- rewards or the Hall of Seasons. lib/spirebound/season.lua reads this same file for its safety test.
DELETE FROM `players` WHERE `group_id` < 4;
UPDATE `houses` SET `owner` = 0, `new_owner` = -1, `paid` = 0, `warnings` = 0, `bidder` = 0, `bidder_name` = '', `highest_bid` = 0, `internal_bid` = 0, `bid_end_date` = 0, `state` = 0, `transfer_status` = 0;
-- house contents: the engine saves each house's tiles here and loads them over the map; empty = the map's own items
DELETE FROM `tile_store`;
DELETE FROM `house_lists`;
DELETE FROM `guild_wars`;
DELETE FROM `guilds`;
DELETE FROM `market_offers`;
DELETE FROM `market_history`;
DELETE FROM `kv_store` WHERE `key_name` LIKE 'player.%' OR `key_name` LIKE 'spirebound-floors%' OR `key_name` LIKE 'spirebound-secrets-public%' OR `key_name` LIKE 'spirebound-bounties%' OR `key_name` LIKE 'spirebound-headstart%' OR `key_name` LIKE 'spirebound-twinfang%' OR `key_name` LIKE 'spirebound-fortune%' OR `key_name` LIKE 'spirebound-recruit%' OR `key_name` LIKE 'spirebound-memorial%' OR `key_name` LIKE 'spirebound-openhouse%' OR `key_name` LIKE 'spirebound-houselist%' OR `key_name` LIKE 'spirebound-siege%';
