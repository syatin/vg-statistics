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

# 階層別プレイ回数
SELECT `m`.`shardId`, `m`.`gamemode` AS `ゲームモード`, `r`.`averageRank`, COUNT(`m`.`id`) AS `試合数`
  FROM `matches` `m`
  JOIN `rosters` `r`
    ON `m`.`id` = `r`.`match_id`
 GROUP BY `m`.`shardId`, `m`.`gamemode`, `r`.`averageRank`
 ORDER BY `m`.`shardId`, `m`.`gamemode`, `r`.`averageRank`
;

# 特定のユーザーの試合履歴取得
 SELECT *
   FROM matches m
   JOIN participants p
     ON m.id = p.match_id
   JOIN players pl
     ON pl.id = p.player_id
  WHERE m.gameMode = '5v5_pvp_ranked'
    AND pl.name = 'Kootam'
    AND m.createdAt > (NOW() - INTERVAL 1 WEEK)
  ORDER BY m.createdAt DESC
  LIMIT 10
;