CREATE TABLE `stat_ban_heroes` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `patchVersion` decimal(10,1) DEFAULT NULL,
  `shardId` varchar(3) DEFAULT NULL,
  `gameMode` varchar(32) DEFAULT NULL,
  `rank` tinyint(4) DEFAULT NULL,
  `side` enum('left/blue','right/red') DEFAULT NULL,


  `ban_hero_id_1` int(11) unsigned DEFAULT NULL,
  `ban_hero_id_2` int(11) unsigned DEFAULT NULL,
  `pick_hero_id` int(11) unsigned DEFAULT NULL,


  `role` enum('LANE','JUNGLE','CAPTAIN','MID','TOP','BOT') DEFAULT NULL,
  `build_type` enum('WP','CP','HYBRID','UTILITY') DEFAULT NULL,
  `games` int(11) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL,
  `win_rate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hero_id` (`patchVersion`,`gameMode`,`shardId`,`rank`,`side`),
  KEY `ban_hero_id_1` (`ban_hero_id_1`),
  KEY `ban_hero_id_2` (`ban_hero_id_2`),
  KEY `pick_hero_id` (`pick_hero_id`),
  CONSTRAINT `stat_ban_heroes_ibfk_1` FOREIGN KEY (`ban_hero_id_1`) REFERENCES `m_heros` (`id`),
  CONSTRAINT `stat_ban_heroes_ibfk_2` FOREIGN KEY (`ban_hero_id_2`) REFERENCES `m_heros` (`id`),
  CONSTRAINT `stat_ban_heroes_ibfk_3` FOREIGN KEY (`pick_hero_id`) REFERENCES `m_heros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




これじゃ自分たちのバンしたヒーローが分からない。ダメだ
JSONで出来るけどヴァーチャルカラムどうしよう

ヒーローのBAN率
どのヒーローがBANされた時、どのヒーローの勝率が高くなるのか