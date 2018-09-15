# サイド別勝率
SELECT `r`.`side` AS `サイド`,
       SUM(`r`.`won`) AS `勝利数`,
       COUNT(`r`.`id`) AS `試合数`,
       CONCAT(FORMAT((SUM(`r`.`won`) / COUNT(`r`.`id`) * 100), 2), ' %') as `勝率`,
       AVG(`r`.`averageRankedPoint`) AS `平均ランクポイント`
  FROM `rosters` `r`
  JOIN `matches` `m`
    ON `r`.`match_id` = `m`.`id`
 WHERE `m`.`gamemode` = 'ranked' # ranked / 5v5_pvp_ranked
   AND `r`.`averageRank` >= 8
 GROUP BY `r`.`side`
;

# 平均試合時間
SELECT `m`.`gamemode` AS `ゲームモード`, AVG(`m`.`duration`) / 60 AS `試合時間`, COUNT(`m`.`id`) AS `試合数`
  FROM `matches` `m`
  JOIN `rosters` `r`
    ON `m`.`id` = `r`.`match_id`
 WHERE `r`.`averageRank` >= 8
 GROUP BY `m`.`gamemode`
;
