# 5v5 EA 週別、ランク別、ポジション別 ビルド勝率
SELECT `s`.`week`, `m`.`ja`, `s`.`rank`, `s`.`role`, `s`.`build_type`, `s`.`games`, `s`.`win_rate`
  FROM `stat_heroes` `s`
  JOIN `m_heroes` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '4.1'
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`shardId` = 'ea'
   AND `s`.`games` > 50
 ORDER BY `s`.`week`, `s`.`rank`, `s`.`win_rate`
;

# 5v5 全地域、週別のヒーロー x ポジション x ビルド勝率
SELECT `m`.`ja` AS `ヒーロー（5v5）`,
       `s`.`week`,
       `s`.`role` AS `ロール`,
       `s`.`build_type` AS `ビルド`,
       SUM(`s`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`s`.`wins`) / SUM(`s`.`games`) * 100), 2), ' %') as `勝率`
  FROM `stat_heroes` `s`
  JOIN `m_heroes` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '4.1'
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`rank` >= 9
 GROUP BY `s`.`hero_id`, `s`.`week`, `s`.`role`, `s`.`build_type`
HAVING `試合数` > 50
 ORDER BY `s`.`week`, `勝率` DESC, `s`.`hero_id`, `s`.`role`, `s`.`build_type`
;

# 5v5 全地域 パッチ通しての、ランク9以上のポジション別 ビルド勝率
SELECT `m`.`ja` AS `ヒーロー（全地域, 5v5）`,
       `s`.`role` AS `ロール`,
       `s`.`build_type` AS `ビルド`,
       SUM(`s`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`s`.`wins`) / SUM(`s`.`games`) * 100), 2), ' %') as `勝率`
  FROM `stat_heroes` `s`
  JOIN `m_heroes` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '4.1'
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`rank` >= 9
 GROUP BY `s`.`hero_id`, `s`.`role`, `s`.`build_type`
HAVING `試合数` >100
 ORDER BY `勝率` DESC
;

# 5v5 EA パッチ通してのランク別、ポジション別 ビルド勝率
SELECT `m`.`ja` AS `ヒーロー（EA, 5v5）`,
       `s`.`rank` AS `ランク`,
       `s`.`role` AS `ロール`,
       `s`.`build_type` AS `ビルド`,
       SUM(`s`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`s`.`wins`) / SUM(`s`.`games`) * 100), 2), ' %') as `勝率`
  FROM `stat_heroes` `s`
  JOIN `m_heroes` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '4.1'
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`shardId` = 'ea'
   AND `s`.`rank` >= 7
 GROUP BY `s`.`hero_id`, `s`.`rank`, `s`.`role`, `s`.`build_type`
HAVING `試合数` > 100
 ORDER BY `s`.`rank` DESC, `勝率` DESC
;

# 敵との相性（パッチ指定）
SELECT `s`.`patchVersion`, `s`.`gameMode`,
       `h1`.`ja`, `s`.`role_1`, `s`.`build_type_1`,
       `h2`.`ja`, `s`.`role_2`, `s`.`build_type_2`,
       `s`.`is_enemy`,
       `s`.`games`, `s`.`win_rate`, `s`.`synergy`
  FROM `stat_synergy` `s`
  JOIN `m_heroes` `h1`
    ON `h1`.`id` = `s`.`hero_id_1`
  JOIN `m_heroes` `h2`
    ON `h2`.`id` = `s`.`hero_id_2`
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '4.1'
   AND `s`.`games` > 100
   AND `s`.`is_enemy` = 1
 ORDER BY `s`.`synergy` DESC
;

# 敵との相性（パッチ毎のシナジーを試合数で加重平均）
SELECT `s`.`gameMode`,
       `h1`.`ja`, `s`.`role_1`, `s`.`build_type_1`,
       `h2`.`ja`, `s`.`role_2`, `s`.`build_type_2`,
       `s`.`is_enemy`,
       SUM(`s`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`s`.`wins`) / SUM(`s`.`games`) * 100), 2), ' %') AS `勝率`,
       FORMAT(SUM((`s`.`synergy` * `s`.`games`)) / SUM(`s`.`games`), 2) AS `シナジー`
  FROM `stat_synergy` `s`
  JOIN `m_heroes` `h1`
    ON `h1`.`id` = `s`.`hero_id_1`
  JOIN `m_heroes` `h2`
    ON `h2`.`id` = `s`.`hero_id_2`
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`is_enemy` = 1
   AND `h1`.`ja` = 'レザ'
   AND `s`.`role_2` = 'CAPTAIN'
 GROUP BY `h1`.`ja`, `s`.`role_1`, `s`.`build_type_1`, `h2`.`ja`, `s`.`role_2`, `s`.`build_type_2`
 HAVING `試合数` > 500
 ORDER BY `シナジー` DESC
;

# 味方との相性
SELECT `s`.`patchVersion`, `s`.`gameMode`,
       `h1`.`ja`, `s`.`role_1`, `s`.`build_type_1`,
       `h2`.`ja`, `s`.`role_2`, `s`.`build_type_2`,
       `s`.`is_enemy`,
       `s`.`games`, `s`.`win_rate`, `s`.`synergy`
  FROM `stat_synergy` `s`
  JOIN `m_heroes` `h1`
    ON `h1`.`id` = `s`.`hero_id_1`
  JOIN `m_heroes` `h2`
    ON `h2`.`id` = `s`.`hero_id_2`
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '4.1'
   AND `s`.`games` > 100
   AND `s`.`is_enemy` = 0
 ORDER BY `s`.`synergy` DESC
;

# カスタマイズ例：キャプテンローレライと味方の相性
SELECT `s`.`patchVersion` AS 'パッチ',
       `s`.`gameMode` AS 'ゲームモード',
       `h1`.`ja` AS 'ヒーロー1', `s`.`role_1` AS 'ロール1',
       `h2`.`ja` AS 'ヒーロー2', `s`.`role_2` AS 'ロール2',
       `s`.`games` AS '試合数', `s`.`win_rate` AS '勝率', `s`.`synergy` AS 'シナジー'
  FROM `stat_synergy` `s`
  JOIN `m_heroes` `h1`
    ON `h1`.`id` = `s`.`hero_id_1`
  JOIN `m_heroes` `h2`
    ON `h2`.`id` = `s`.`hero_id_2`
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '4.1'
   AND `s`.`games` > 150
   AND `s`.`is_enemy` = 0
   AND `h1`.`ja` = 'ローレライ'
   AND `s`.`role_1` = 'CAPTAIN'
 ORDER BY `s`.`synergy` DESC
;

# 地域別、試合時間別の勝率
SELECT `sd`.`patchVersion`,
       `sd`.`shardId`,
       `sd`.`gameMode`,
       `h`.`ja` AS `ヒーロー`,
       `sd`.`role` AS `ロール`,
       `sd`.`build_type` AS `ビルド`,
       `sd`.`duration_type` AS `試合時間（分）`,
       `sd`.`games` AS `試合数`,
       `sd`.`win_rate` AS `勝率`
  FROM `stat_heroes_duration` `sd`
  JOIN `m_heroes` `h`
    ON `sd`.`hero_id` = `h`.`id`
  LEFT OUTER JOIN `stat_heroes` `s`
    ON `s`.`patchVersion` = `sd`.`patchVersion`
   AND `s`.`shardId` = `sd`.`shardId`
   AND `s`.`gameMode` = `sd`.`gameMode`
   AND `s`.`hero_id` = `sd`.`hero_id`
   AND `s`.`role` = `sd`.`role`
   AND `s`.`build_type` = `sd`.`build_type`
   AND `s`.`rank` = 9
   AND `s`.`week` = '2019-03-18' # patch 4.1 first week
   AND `s`.`games` > 100
 WHERE `s`.`id` IS NOT NULL
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '4.1'
 ORDER BY `sd`.`gameMode`, `sd`.`shardId`, `sd`.`hero_id`, `sd`.`role`, `sd`.`build_type`, `sd`.`duration_type`
;

# 全地域総合、試合時間別の勝率
SELECT `sd`.`patchVersion`,
       `sd`.`gameMode`,
       `h`.`ja` AS `ヒーロー`,
       `sd`.`role` AS `ロール`,
       `sd`.`build_type` AS `ビルド`,
       `sd`.`duration_type` AS `試合時間（分）`,
       SUM(`sd`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`sd`.`wins`) / SUM(`sd`.`games`) * 100), 2), ' %') AS `勝率`
  FROM `stat_heroes_duration` `sd`
  JOIN `m_heroes` `h`
    ON `sd`.`hero_id` = `h`.`id`
  LEFT OUTER JOIN `stat_heroes` `s`
    ON `s`.`patchVersion` = `sd`.`patchVersion`
   AND `s`.`shardId` = `sd`.`shardId`
   AND `s`.`gameMode` = `sd`.`gameMode`
   AND `s`.`hero_id` = `sd`.`hero_id`
   AND `s`.`role` = `sd`.`role`
   AND `s`.`build_type` = `sd`.`build_type`
   AND `s`.`rank` >= 9
   AND `s`.`week` = '2019-03-18' # patch 4.1 first week
   AND `s`.`games` > 50
 WHERE `s`.`id` IS NOT NULL
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '4.1'
   AND `sd`.`rank` >= 9
 GROUP BY `sd`.`gameMode`, `sd`.`hero_id`, `sd`.`role`, `sd`.`build_type`, `sd`.`duration_type`
 ORDER BY `sd`.`gameMode`, `sd`.`hero_id`, `sd`.`role`, `sd`.`build_type`, `sd`.`duration_type`
;

########################################
# 生データからの直接集計
########################################

# 5v5 EA ポジション別 CPビルド勝率
SELECT `h`.`ja` AS `CPビルド(5v5, EA)`,
       `p`.`role` AS `ロール`,
        SUM(`p`.`winner`) as `勝利数`,
        COUNT(`p`.`id`) AS `試合数`,
        CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heroes` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`patchVersion` = '4.1'
   AND `m`.`shardId` = 'ea'
   AND `m`.`gamemode` = '5v5_pvp_ranked' # ranked / 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'CP'
 GROUP BY `h`.`ja`, `p`.`role`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;

# 5v5 ポジション別 WPビルド勝率
SELECT `h`.`ja` AS `WPビルド(5v5, EA)`,
       `p`.`role` AS `ロール`,
        SUM(`p`.`winner`) as `勝利数`,
        COUNT(`p`.`id`) AS `試合数`,
        CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heroes` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`patchVersion` = '4.1'
   AND `m`.`shardId` = 'ea'
   AND `m`.`gamemode` = '5v5_pvp_ranked' # ranked, 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'WP'
 GROUP BY `h`.`ja`, `p`.`role`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;

# 5v5 ポジション別 実用／サポートビルド勝率
SELECT `h`.`ja` AS `サポートビルド(5v5, EA)`,
       `p`.`role` AS `ロール`,
       SUM(`p`.`winner`) as `勝利数`,
       COUNT(`p`.`id`) AS `試合数`,
       CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heroes` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`patchVersion` = '4.1'
   AND `m`.`shardId` = 'ea'
   AND `m`.`gamemode` = '5v5_pvp_ranked' # ranked / 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'UTILITY'
 GROUP BY `h`.`ja`, `p`.`role`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;

# 平均CSを出すSQL
# 生集計のため時間が掛かります
SELECT AVG(`p`.`minionKills` / (`m`.`duration` / 60))
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
 WHERE `p`.`rankPoint` >= 2600
   AND `p`.`rankPoint` < 2800
   AND `p`.`rank` = 10
   AND `p`.`role` = 'BOT'
   AND `m`.`patchVersion` = '4.1'