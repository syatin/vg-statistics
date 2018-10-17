# 3v3 EA パッチ通してのランク別、ポジション別 ビルド勝率
SELECT `m`.`ja` AS `ヒーロー（EA, 3v3）`,
       `s`.`rank` AS `ランク`,
       `s`.`role` AS `ロール`,
       `s`.`build_type` AS `ビルド`,
       SUM(`s`.`games`) AS `試合数`,
       CONCAT(FORMAT((SUM(`s`.`wins`) / SUM(`s`.`games`) * 100), 2), ' %') as `勝率`
  FROM `stat_heros` `s`
  JOIN `m_heros` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '3.7'
   AND `s`.`gameMode` = 'ranked'
   AND `s`.`shardId` = 'ea'
   AND `s`.`rank` >= 7
 GROUP BY `s`.`hero_id`, `s`.`rank`, `s`.`role`, `s`.`build_type`
HAVING `試合数` > 100
 ORDER BY `s`.`rank` DESC, `勝率` DESC
;

# 味方との相性
SELECT `s`.`patchVersion`, `s`.`gameMode`, 
       `h1`.`ja`, `s`.`role_1`,
       `h2`.`ja`, `s`.`role_2`,
       `s`.`is_enemy`,
       `s`.`games`, `s`.`win_rate`, `s`.`synergy`
  FROM `stat_synergy` `s`
  JOIN `m_heros` `h1`
    ON `h1`.`id` = `s`.`hero_id_1`
  JOIN `m_heros` `h2`
    ON `h2`.`id` = `s`.`hero_id_2`
 WHERE `s`.`gameMode` = 'ranked'
   AND `s`.`patchVersion` = '3.7'
   AND `s`.`games` > 100
   AND `s`.`is_enemy` = 0
 ORDER BY `s`.`synergy` DESC
;

# 試合時間別の勝率
SELECT `sd`.`patchVersion`,
       `sd`.`shardId`,
       `sd`.`gameMode`,
       `h`.`ja` AS `ヒーロー`,
       `sd`.`role` AS `ロール`,
       `sd`.`build_type` AS `ビルド`,
       `sd`.`duration_type` AS `試合時間（分）`,
       `sd`.`games` AS `試合数`,
       `sd`.`win_rate` AS `勝率`
  FROM `stat_heros_duration` `sd`
  JOIN `m_heros` `h`
    ON `sd`.`hero_id` = `h`.`id`
  LEFT OUTER JOIN `stat_heros` `s`
    ON `s`.`patchVersion` = `sd`.`patchVersion`
   AND `s`.`shardId` = `sd`.`shardId`
   AND `s`.`gameMode` = `sd`.`gameMode`
   AND `s`.`hero_id` = `sd`.`hero_id`
   AND `s`.`role` = `sd`.`role`
   AND `s`.`build_type` = `sd`.`build_type`
   AND `s`.`rank` = 9
   AND `s`.`week` = '2018-09-17'
   AND `s`.`games` > 100
 WHERE `s`.`id` IS NOT NULL
   AND `s`.`gameMode` = 'ranked'
   AND `s`.`patchVersion` = '3.7'
 ORDER BY `sd`.`gameMode`, `sd`.`shardId`, `sd`.`hero_id`, `sd`.`role`, `sd`.`build_type`, `sd`.`duration_type`
;

########################################
# 生データからの直接集計
########################################

# 3v3 CPビルド勝率
SELECT `h`.`ja` AS `CPビルド(3v3, EA)`,
        SUM(`p`.`winner`) as `勝利数`,
        COUNT(`p`.`id`) AS `試合数`,
        CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`gamemode` = 'ranked' # ranked / 5v5_pvp_ranked
   AND `m`.`shardId` = 'ea'
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'CP'
 GROUP BY `h`.`ja`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;

# 3v3 WPビルド勝率
SELECT `h`.`ja` AS `WPビルド(3v3, EA)`,
        SUM(`p`.`winner`) as `勝利数`,
        COUNT(`p`.`id`) AS `試合数`,
        CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`gamemode` = 'ranked' # ranked, 5v5_pvp_ranked
   AND `m`.`shardId` = 'ea'
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'WP'
 GROUP BY `h`.`ja`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;

# 3v3 実用／サポートビルド勝率
SELECT `h`.`ja` AS `サポートビルド(3v3, EA)`,
        SUM(`p`.`winner`) as `勝利数`,
        COUNT(`p`.`id`) AS `試合数`,
        CONCAT(FORMAT((SUM(`p`.`winner`) / COUNT(`p`.`id`) * 100), 2), ' %') as `勝率`
  FROM `participants` `p`
  JOIN `matches` `m`
    ON `p`.`match_id` = `m`.`id`
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`gamemode` = 'ranked' # ranked / 5v5_pvp_ranked
   AND `m`.`shardId` = 'ea'
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'UTILITY'
 GROUP BY `h`.`ja`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;