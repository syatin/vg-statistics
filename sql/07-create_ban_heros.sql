CREATE TABLE `stat_ban_heroes` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `patchVersion` decimal(10,1) DEFAULT NULL,
  `shardId` varchar(3) DEFAULT NULL,
  `gameMode` varchar(32) DEFAULT NULL,
  `averageRank` tinyint(4) DEFAULT NULL,
  `side` enum('left/blue','right/red') DEFAULT NULL,
  `ban_order` int(11) unsigned DEFAULT NULL,
  `ban_hero_id` int(11) unsigned DEFAULT NULL,

  `games` int(11) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL,
  `win_rate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hero_id` (`patchVersion`,`gameMode`,`shardId`,`averageRank`,`side`),
  KEY `ban_hero_id_1` (`ban_hero_id`, `gameMode`, `patchVersion`),
  CONSTRAINT `stat_ban_heroes_ibfk_1` FOREIGN KEY (`ban_hero_id`) REFERENCES `m_heroes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
