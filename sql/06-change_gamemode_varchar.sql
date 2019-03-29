ALTER TABLE `matches` CHANGE COLUMN `gameMode` `gameMode` varchar(32) DEFAULT NULL;
ALTER TABLE `stat_heroes` CHANGE COLUMN `gameMode` `gameMode` varchar(32) DEFAULT NULL;
ALTER TABLE `stat_heroes_duration` CHANGE COLUMN `gameMode` `gameMode` varchar(32) DEFAULT NULL;
ALTER TABLE `stat_synergy` CHANGE COLUMN `gameMode` `gameMode` varchar(32) DEFAULT NULL;