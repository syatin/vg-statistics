ALTER TABLE `participants`
CHANGE COLUMN `role` `role` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL;

ALTER TABLE `stat_heroes`
CHANGE COLUMN `role` `role` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL;

ALTER TABLE `stat_heroes_duration`
CHANGE COLUMN `role` `role` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL;

ALTER TABLE `stat_synergy`
CHANGE COLUMN `role_1` `role_1` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL,
CHANGE COLUMN `role_2` `role_2` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL;
