# 5v5 EA 週別、ランク別、ポジション別 ビルド勝率
SELECT `s`.`week`, `m`.`ja`, `s`.`rank`, `s`.`role`, `s`.`build_type`, `s`.`games`, `s`.`win_rate`
  FROM `stat_heros` `s`
  JOIN `m_heros` `m`
    ON `s`.`hero_id` = `m`.`id`
 WHERE `s`.`patchVersion` = '3.7'
   AND `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`shardId` = 'ea'
   AND `s`.`games` > 50
ORDER BY `s`.`week`, `s`.`rank`, `s`.`win_rate`
;

# 敵との相性
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
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '3.7'
   AND `s`.`games` > 100
   AND `s`.`is_enemy` = 0
 ORDER BY `s`.`synergy` DESC
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
 WHERE `s`.`gameMode` = '5v5_pvp_ranked'
   AND `s`.`patchVersion` = '3.7'
   AND `s`.`games` > 100
   AND `s`.`is_enemy` = 0
 ORDER BY `s`.`synergy` DESC
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
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`shardId` = 'ea'
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
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`shardId` = 'ea'
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
  JOIN `m_heros` `h`
    ON `p`.`actor` = `h`.`actor`
 WHERE `m`.`shardId` = 'ea'
   AND `m`.`gamemode` = '5v5_pvp_ranked' # ranked / 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'UTILITY'
 GROUP BY `h`.`ja`, `p`.`role`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;