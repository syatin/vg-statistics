ALTER TABLE `participants`
CHANGE COLUMN `role` `role` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL;