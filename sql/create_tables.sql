-- Create syntax for TABLE 'matches'
CREATE TABLE `matches` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uuid` varchar(40) DEFAULT NULL,
  `shardId` varchar(4) DEFAULT NULL,
  `gameMode` varchar(16) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `endGameReason` varchar(16) DEFAULT NULL,
  `patchVersion` decimal(10,1) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `uuid` (`uuid`),
  KEY `gameMode` (`gameMode`,`shardId`,`patchVersion`),
  KEY `shardId` (`shardId`,`gameMode`,`createdAt`),
  KEY `gameMode_2` (`gameMode`,`createdAt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'participants'
CREATE TABLE `participants` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `match_id` int(11) unsigned DEFAULT NULL,
  `roster_id` int(11) unsigned DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  `player_name` varchar(64) DEFAULT NULL,
  `rankPoint` smallint(6) DEFAULT NULL,
  `rank` tinyint(4) DEFAULT NULL,
  `hero_id` int(11) unsigned DEFAULT NULL,
  `actor` varchar(32) DEFAULT NULL,
  `skinKey` varchar(64) DEFAULT NULL,
  `role` enum('LANE','JUNGLE','CAPTAIN') DEFAULT NULL,
  `kills` int(11) DEFAULT NULL,
  `assists` int(11) DEFAULT NULL,
  `deaths` int(11) DEFAULT NULL,
  `gold` int(11) DEFAULT NULL,
  `minionKills` int(11) DEFAULT NULL,
  `jungleKills` int(11) DEFAULT NULL,
  `nonJungleMinionKills` int(11) DEFAULT NULL,
  `items` json DEFAULT NULL,
  `itemUses` json DEFAULT NULL,
  `is_wp_build` tinyint(1) DEFAULT NULL,
  `is_cp_build` tinyint(1) DEFAULT NULL,
  `is_hybrid_build` tinyint(1) DEFAULT NULL,
  `is_utility_build` tinyint(1) DEFAULT NULL,
  `wentAfk` tinyint(1) DEFAULT NULL,
  `winner` tinyint(1) DEFAULT NULL,
  `build_type` enum('WP','CP','HYBRID','UTILITY') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `roster_id` (`roster_id`),
  KEY `build_type` (`build_type`,`rank`),
  KEY `hero_id` (`hero_id`),
  KEY `match_id` (`match_id`,`player_id`),
  CONSTRAINT `participants_ibfk_1` FOREIGN KEY (`roster_id`) REFERENCES `rosters` (`id`),
  CONSTRAINT `participants_ibfk_3` FOREIGN KEY (`hero_id`) REFERENCES `m_heros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'players'
CREATE TABLE `players` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `playerId` varchar(64) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `shardId` varchar(3) DEFAULT NULL,
  `gamesPlayed` json DEFAULT NULL,
  `guildTag` varchar(32) DEFAULT NULL,
  `karmaLevel` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `rankPoints` json DEFAULT NULL,
  `updatedAt` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `playerId` (`playerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'rosters'
CREATE TABLE `rosters` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `match_id` int(11) unsigned DEFAULT NULL,
  `acesEarned` int(11) DEFAULT NULL,
  `gold` int(11) DEFAULT NULL,
  `heroKills` int(11) DEFAULT NULL,
  `krakenCaptures` int(11) DEFAULT NULL,
  `side` varchar(16) DEFAULT NULL,
  `turretKills` int(11) DEFAULT NULL,
  `turretsRemaining` int(11) DEFAULT NULL,
  `won` tinyint(1) DEFAULT NULL,
  `averageRankedPoint` int(11) DEFAULT NULL,
  `averageRank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `match_id` (`match_id`),
  CONSTRAINT `rosters_ibfk_1` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `stat_heros` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `patchVersion` decimal(10,1) DEFAULT NULL,
  `shardId` varchar(3) DEFAULT NULL,
  `gameMode` varchar(16) DEFAULT NULL,
  `week` date DEFAULT NULL,
  `hero_id` int(11) unsigned DEFAULT NULL,
  `rank` tinyint(4) DEFAULT NULL,
  `role` enum('LANE','JUNGLE','CAPTAIN') DEFAULT NULL,
  `build_type` enum('WP','CP','HYBRID','UTILITY') DEFAULT NULL,
  `duration_type` tinyint(4) DEFAULT NULL COMMENT '10, 15, 20, 25, 30, 35..',
  `games` int(11) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL,
  `win_rate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hero_id` (`hero_id`,`patchVersion`,`gameMode`,`shardId`,`week`),
  KEY `hero_id_2` (`hero_id`,`patchVersion`,`gameMode`,`week`),
  CONSTRAINT `stat_heros_ibfk_1` FOREIGN KEY (`hero_id`) REFERENCES `m_heros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `stat_synergy` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `patchVersion` decimal(10,1) DEFAULT NULL,
  `gameMode` varchar(16) DEFAULT NULL,
  `hero_id_1` int(11) unsigned DEFAULT NULL,
  `role_1` enum('LANE','JUNGLE','CAPTAIN') DEFAULT NULL,
  `hero_id_2` int(11) unsigned DEFAULT NULL,
  `role_2` enum('LANE','JUNGLE','CAPTAIN') DEFAULT NULL,
  `is_enemy` tinyint(1) DEFAULT NULL,
  `games` int(11) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL,
  `win_rate` decimal(5,2) DEFAULT NULL,
  `synergy` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patchVersion` (`patchVersion`,`gameMode`,`hero_id_1`,`role_1`,`is_enemy`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'vgpro_leaderboard'
CREATE TABLE `vgpro_leaderboard` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gamemode` varchar(16) NOT NULL DEFAULT '',
  `playerId` varchar(64) NOT NULL DEFAULT '',
  `name` varchar(64) NOT NULL DEFAULT '',
  `region` varchar(2) NOT NULL DEFAULT '',
  `tier` int(11) DEFAULT NULL,
  `position` int(11) NOT NULL,
  `points` float DEFAULT NULL,
  `kda` decimal(10,2) DEFAULT NULL,
  `winRate` decimal(10,2) DEFAULT NULL,
  `kp` decimal(10,2) DEFAULT NULL,
  `games` int(11) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL,
  `request_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `gamemode` (`gamemode`,`region`,`position`),
  KEY `playerId` (`playerId`,`gamemode`),
  KEY `name` (`name`,`gamemode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;