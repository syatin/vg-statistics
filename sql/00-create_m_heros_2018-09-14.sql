# ************************************************************
# Sequel Pro SQL dump
# バージョン 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# ホスト: 127.0.0.1 (MySQL 5.7.22)
# データベース: vainglory
# 作成時刻: 2018-09-13 18:03:37 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# テーブルのダンプ m_heroes
# ------------------------------------------------------------

DROP TABLE IF EXISTS `m_heroes`;

CREATE TABLE `m_heroes` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `actor` varchar(32) DEFAULT NULL,
  `ja` varchar(32) DEFAULT NULL,
  `en` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `m_heroes` WRITE;
/*!40000 ALTER TABLE `m_heroes` DISABLE KEYS */;

INSERT INTO `m_heroes` (`id`, `actor`, `ja`, `en`)
VALUES
	(1,'*Adagio*','アダージオ','Adagio'),
	(2,'*Alpha*','アルファ','Alpha'),
	(3,'*Anka*','アンカ','Anka'),
	(4,'*Ardan*','アーダン','Ardan'),
	(5,'*Baptiste*','バティスト','Baptiste'),
	(6,'*Baron*','バロン','Baron'),
	(7,'*Blackfeather*','ブラックフェザー','Blackfeather'),
	(8,'*Catherine*','キャサリン','Catherine'),
	(9,'*Celeste*','セレス','Celeste'),
	(10,'*Churnwalker*','チャーンウォーカー','Churnwalker'),
	(11,'*Flicker*','フリッカー','Flicker'),
	(12,'*Fortress*','フォートレス','Fortress'),
	(13,'*Glaive*','グレイヴ','Glaive'),
	(14,'*Grace*','グレース','Grace'),
	(15,'*Grumpjaw*','グランプジョー','Grumpjaw'),
	(16,'*Gwen*','グウェン','Gwen'),
	(17,'*Idris*','イドリス','Idris'),
	(18,'*Joule*','ジュール','Joule'),
	(19,'*Kensei*','剣聖','Kensei'),
	(20,'*Kestrel*','ケストレル','Kestrel'),
	(21,'*Kinetic*','キネティック','Kinetic'),
	(22,'*Koshka*','コシュカ','Koshka'),
	(23,'*Krul*','クラル','Krul'),
	(24,'*Lance*','ランス','Lance'),
	(25,'*Lorelai*','ローレライ','Lorelai'),
	(26,'*Lyra*','ライラ','Lyra'),
	(27,'*Malene*','マレン','Malene'),
	(28,'*Ozo*','オゾ','Ozo'),
	(29,'*Petal*','ペタル','Petal'),
	(30,'*Phinn*','フィン','Phinn'),
	(31,'*Reim*','ライム','Reim'),
	(32,'*Reza*','レザ','Reza'),
	(33,'*Ringo*','リンゴ','Ringo'),
	(34,'*Rona*','ロナ','Rona'),
	(35,'*Samuel*','サムエル','Samuel'),
	(36,'*SAW*','ソー','SAW'),
	(37,'*Silvernail*','シルバーネイル','Silvernail'),
	(38,'*Skaarf*','スカーフ','Skaarf'),
	(39,'*Skye*','スカイ','Skye'),
	(40,'*Taka*','タカ','Taka'),
	(41,'*Tony*','トニー','Tony'),
	(42,'*Varya*','ヴァーリア','Varya'),
	(43,'*Vox*','ヴォックス','Vox'),
	(44,'*Yates*','イェーツ','Yates');

/*!40000 ALTER TABLE `m_heroes` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
