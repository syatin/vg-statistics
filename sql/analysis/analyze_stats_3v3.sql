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
   AND `p`.`rank` >= 8
   AND `p`.`build_type` = 'UTILITY'
 GROUP BY `h`.`ja`
HAVING COUNT(`p`.`id`) >= 50
 ORDER BY `勝率` DESC
;