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
SELECT `m`.`gamemode` AS `ゲームモード`,
       `m`.`shardId` AS `地域`,
       `r`.`averageRank` AS `ランク`,
       CONCAT(FORMAT(AVG(`m`.`duration`) / 60, 2), ' 分') AS `試合時間`,
       COUNT(`m`.`id`) AS `試合数`
  FROM `matches` `m`
  JOIN `rosters` `r`
    ON `m`.`id` = `r`.`match_id`
 WHERE `m`.`gameMode` = '5v5_pvp_ranked' # 5v5_pvp_ranked / ranked
   AND `m`.`patchVersion` = '3.8'
   AND `r`.`averageRank` > 4
 GROUP BY `m`.`gamemode`, `m`.`shardId`, `r`.`averageRank`
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

# 時間帯別の試合数
SELECT DATE_FORMAT(`createdAt` - INTERVAL 9 HOUR , '%H:00:00') AS time,
       (COUNT(*) / 14) AS count 
  FROM `matches`
 WHERE `shardId` = 'na'
   AND `gameMode` = 'ranked'
   AND `createdAt` > DATE('2018-09-19 00:00:00')
   AND `createdAt` <  (DATE('2018-09-19 00:00:00') + INTERVAL 14 DAY)
 GROUP BY DATE_FORMAT(`createdAt`, '%H')
;

# 1日毎の試合数
SELECT DATE_FORMAT(`createdAt` + INTERVAL 9 HOUR , '%Y-%m-%d') AS time,
       (
         CASE dayofweek(`createdAt` - INTERVAL 9 HOUR)
           WHEN 1 THEN '日曜日'
           WHEN 2 THEN '月曜日'
           WHEN 3 THEN '火曜日'
           WHEN 4 THEN '水曜日'
           WHEN 5 THEN '木曜日'
           WHEN 6 THEN '金曜日'
           WHEN 7 THEN '土曜日'
         END
       ) AS week,
       COUNT(*) AS count 
  FROM `matches`
 WHERE `shardId` = 'ea'
   AND `gameMode` = 'ranked'
   AND `createdAt` > DATE('2018-09-20 00:00:00')
   AND `createdAt` <  (DATE('2018-09-20 00:00:00') + INTERVAL 15 DAY)
 GROUP BY DATE_FORMAT(`createdAt`, '%Y%m%d')
;

# 地域別ゲームモード別のプレイ回数
SELECT DATE_FORMAT(`createdAt` + INTERVAL 9 HOUR , '%Y-%m-%d') AS time,
       (
         CASE dayofweek(`createdAt` - INTERVAL 9 HOUR)
           WHEN 1 THEN '日曜日'
           WHEN 2 THEN '月曜日'
           WHEN 3 THEN '火曜日'
           WHEN 4 THEN '水曜日'
           WHEN 5 THEN '木曜日'
           WHEN 6 THEN '金曜日'
           WHEN 7 THEN '土曜日'
         END
       ) AS week,
       `shardId`,
       `gameMode`,
       COUNT(*) AS count
  FROM `matches`
 WHERE `createdAt` > DATE('2018-09-23 00:00:00')
   AND `createdAt` <  (DATE('2018-09-23 00:00:00') + INTERVAL 7 DAY)
 GROUP BY DATE_FORMAT(`createdAt`, '%Y%m%d'), `shardId`, `gameMode`
;
