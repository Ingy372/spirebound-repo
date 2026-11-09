-- Local test accounts (roadmap 1.6). Safe to run any number of times.
-- LOCAL TESTING ONLY: the password below is public. Never run this on a public server.
-- Account: jay / spirebound  ->  characters "Jay" (gamemaster/god) and "Climber" (fresh, picks a vocation at the Registrar)

-- Canary's schema adds sample characters; Spirebound doesn't use them (one is a Monk, which we removed).
DELETE FROM `players` WHERE `name` IN ('Rook Sample','Sorcerer Sample','Druid Sample','Paladin Sample','Knight Sample','Monk Sample');

INSERT INTO `accounts` (`name`, `email`, `password`, `type`, `creation`)
VALUES ('jay', 'jay@localhost', '581b7c21c14889b414d7c1cb77e8deb69f7292b6', 6, UNIX_TIMESTAMP())
ON DUPLICATE KEY UPDATE `password` = VALUES(`password`), `type` = 6;

SET @acc = (SELECT `id` FROM `accounts` WHERE `name` = 'jay');
-- town 1 = Hearthgate
SET @town = 1;

INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`)
VALUES ('Jay', 6, @acc, 2, 0, 155, 155, 100, 113, 115, 95, 39, 75, 60, 60, @town, '', 410, 1)
ON DUPLICATE KEY UPDATE `group_id` = 6, `account_id` = @acc, `town_id` = @town, `posx` = 0, `posy` = 0, `posz` = 0;

INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`)
VALUES ('Climber', 1, @acc, 1, 0, 150, 150, 0, 68, 76, 78, 58, 128, 55, 55, @town, '', 400, 1)
ON DUPLICATE KEY UPDATE `account_id` = @acc, `town_id` = @town, `posx` = 0, `posy` = 0, `posz` = 0;
