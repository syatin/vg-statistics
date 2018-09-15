# 5v5 ポジション別 CPビルド勝率
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
 WHERE `m`.`gamemode` = '5v5_pvp_ranked' # ranked / 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`is_cp_build` = 1
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
 WHERE `m`.`gamemode` = '5v5_pvp_ranked' # ranked, 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`is_wp_build` = 1
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
 WHERE `m`.`gamemode` = '5v5_pvp_ranked' # ranked / 5v5_pvp_ranked
   AND `p`.`rank` >= 8
   AND `p`.`is_utility_build` = 1
 GROUP BY `h`.`ja`, `p`.`role`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;