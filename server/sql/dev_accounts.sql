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

-- One test character per vocation (level 30) plus a Hardcore one, all on account jay.
-- On first login scripts/spirebound/dev_seed.lua sets their difficulty and gives a starter kit.
-- vocation ids: 1 arcanist, 2 mystic, 3 ranger, 4 vanguard. Experience 368300 = level 30.
INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`)
VALUES
 ('Test Vanguard', 1, @acc, 30, 4, 560, 560, 368300, 68, 76, 78, 58, 128, 150, 150, @town, '', 700, 1),
 ('Test Ranger', 1, @acc, 30, 3, 440, 440, 368300, 68, 76, 78, 58, 129, 250, 250, @town, '', 650, 1),
 ('Test Arcanist', 1, @acc, 30, 1, 320, 320, 368300, 68, 76, 78, 58, 130, 600, 600, @town, '', 550, 1),
 ('Test Mystic', 1, @acc, 30, 2, 320, 320, 368300, 68, 76, 78, 58, 131, 600, 600, @town, '', 550, 1),
 ('Test Hardcore', 1, @acc, 30, 4, 560, 560, 368300, 113, 115, 95, 39, 128, 150, 150, @town, '', 700, 1)
ON DUPLICATE KEY UPDATE `account_id` = @acc, `town_id` = @town;

-- The test autopilot's characters (tools/autopilot.py): level 2, a new player in the Ratwarren (made for levels 1-4).
-- Experience 100 = level 2. Running this file again puts them back to a fresh level 2 with starting skills (a test must
-- not get easier as the test characters train). Their own NORMAL account (type 1), like a real player's.
-- /pilot only works for the account whose e-mail is autopilot@localhost; the sign-up page never accepts an e-mail
-- without a real domain, so no player can make that account.
INSERT INTO `accounts` (`name`, `email`, `password`, `type`, `creation`)
VALUES ('autopilot', 'autopilot@localhost', '581b7c21c14889b414d7c1cb77e8deb69f7292b6', 1, UNIX_TIMESTAMP())
ON DUPLICATE KEY UPDATE `password` = VALUES(`password`), `type` = 1;
SET @pilot = (SELECT `id` FROM `accounts` WHERE `name` = 'autopilot');
INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`)
VALUES
 ('Pilot Vanguard', 1, @pilot, 2, 4, 165, 165, 100, 68, 76, 78, 58, 128, 60, 60, @town, '', 425, 1),
 ('Pilot Ranger', 1, @pilot, 2, 3, 160, 160, 100, 68, 76, 78, 58, 129, 70, 70, @town, '', 420, 1)
ON DUPLICATE KEY UPDATE `account_id` = @pilot, `town_id` = @town, `level` = VALUES(`level`), `experience` = VALUES(`experience`),
 `health` = VALUES(`healthmax`), `healthmax` = VALUES(`healthmax`), `mana` = VALUES(`manamax`), `manamax` = VALUES(`manamax`),
 `skill_fist` = 10, `skill_fist_tries` = 0, `skill_club` = 10, `skill_club_tries` = 0, `skill_sword` = 10, `skill_sword_tries` = 0,
 `skill_axe` = 10, `skill_axe_tries` = 0, `skill_dist` = 10, `skill_dist_tries` = 0, `skill_shielding` = 10, `skill_shielding_tries` = 0,
 `posx` = 0, `posy` = 0, `posz` = 0;

-- A middle-level autopilot character for the level 11-16 grounds (Burrow Hills, task H5): a level 14 vanguard with the
-- skills a level 14 vanguard would have. Reset to exactly this on every run of this file, like the two above.
-- Experience 29900 = level 14.
INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`)
VALUES
 ('Pilot Warden', 1, @pilot, 14, 4, 335, 335, 29900, 68, 76, 78, 58, 128, 100, 100, @town, '', 530, 1)
ON DUPLICATE KEY UPDATE `account_id` = @pilot, `town_id` = @town, `level` = VALUES(`level`), `experience` = VALUES(`experience`),
 `health` = VALUES(`healthmax`), `healthmax` = VALUES(`healthmax`), `mana` = VALUES(`manamax`), `manamax` = VALUES(`manamax`),
 `skill_fist` = 20, `skill_fist_tries` = 0, `skill_club` = 45, `skill_club_tries` = 0, `skill_sword` = 45, `skill_sword_tries` = 0,
 `skill_axe` = 45, `skill_axe_tries` = 0, `skill_dist` = 15, `skill_dist_tries` = 0, `skill_shielding` = 40, `skill_shielding_tries` = 0,
 `posx` = 0, `posy` = 0, `posz` = 0;

-- Spell testers for the autopilot (tools/spell_routes.py, task J13b): one level 300 character per vocation with the
-- skills of a well-trained player, so every spell up to the level 300 capstones can be cast in the real client.
-- Experience 441084800 = level 300. Reset to exactly this on every run of this file.
INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`, `maglevel`, `skill_sword`, `skill_axe`, `skill_club`, `skill_dist`, `skill_shielding`)
VALUES
 ('Spell Arcanist', 1, @pilot, 300, 1, 1655, 1655, 441084800, 68, 76, 78, 58, 130, 8835, 8835, @town, '', 3000, 1, 90, 20, 20, 20, 20, 30),
 ('Spell Mystic', 1, @pilot, 300, 2, 1655, 1655, 441084800, 68, 76, 78, 58, 131, 8835, 8835, @town, '', 3000, 1, 90, 20, 20, 20, 20, 30),
 ('Spell Ranger', 1, @pilot, 300, 3, 3135, 3135, 441084800, 68, 76, 78, 58, 129, 4395, 4395, @town, '', 6000, 1, 30, 30, 30, 30, 110, 80),
 ('Spell Vanguard', 1, @pilot, 300, 4, 4615, 4615, 441084800, 68, 76, 78, 58, 128, 1495, 1495, @town, '', 7500, 1, 12, 110, 110, 110, 30, 105)
ON DUPLICATE KEY UPDATE `account_id` = @pilot, `town_id` = @town, `level` = VALUES(`level`), `experience` = VALUES(`experience`),
 `health` = VALUES(`healthmax`), `healthmax` = VALUES(`healthmax`), `mana` = VALUES(`manamax`), `manamax` = VALUES(`manamax`),
 `maglevel` = VALUES(`maglevel`), `skill_sword` = VALUES(`skill_sword`), `skill_axe` = VALUES(`skill_axe`), `skill_club` = VALUES(`skill_club`),
 `skill_dist` = VALUES(`skill_dist`), `skill_shielding` = VALUES(`skill_shielding`), `posx` = 0, `posy` = 0, `posz` = 0;
