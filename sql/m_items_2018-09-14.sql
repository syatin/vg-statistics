# ************************************************************
# Sequel Pro SQL dump
# バージョン 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# ホスト: 127.0.0.1 (MySQL 5.7.22)
# データベース: vainglory
# 作成時刻: 2018-09-13 18:03:09 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# テーブルのダンプ m_items
# ------------------------------------------------------------

DROP TABLE IF EXISTS `m_items`;

CREATE TABLE `m_items` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  `item_id` varchar(32) DEFAULT NULL,
  `type` varchar(16) DEFAULT NULL,
  `tier` int(11) DEFAULT NULL,
  `build_type` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `item_id` (`item_id`),
  KEY `type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `m_items` WRITE;
/*!40000 ALTER TABLE `m_items` DISABLE KEYS */;

INSERT INTO `m_items` (`id`, `name`, `item_id`, `type`, `tier`, `build_type`)
VALUES
	(1,'Weapon Blade','*Item_WeaponBlade*','weapon',1,'wp'),
	(2,'Book Of Eulogies','*Item_BookOfEulogies*','weapon',1,'wp'),
	(3,'Swift Shooter','*Item_SwiftShooter*','weapon',1,'wp'),
	(4,'Minions Foot','*Item_MinionsFoot*','weapon',1,'wp'),
	(5,'Heavy Steel','*Item_HeavySteel*','weapon',2,'wp'),
	(6,'Six Sins','*Item_SixSins*','weapon',2,'wp'),
	(7,'Barbed Needle','*Item_BarbedNeedle*','weapon',2,'wp'),
	(8,'Piercing Spear','*Item_PiercingSpear*','weapon',2,'wp'),
	(9,'Blazing Salvo','*Item_BlazingSalvo*','weapon',2,'wp'),
	(10,'Lucky Strike','*Item_LuckyStrike*','weapon',2,'wp'),
	(11,'Sorrowblade','*Item_Sorrowblade*','weapon',3,'wp'),
	(12,'Serpent Mask','*Item_SerpentMask*','weapon',3,'wp'),
	(13,'Spellsword','*Item_Spellsword*','weapon',3,'wp'),
	(14,'Poisoned Shiv','*Item_PoisonedShiv*','weapon',3,'wp'),
	(15,'Breaking Point','*Item_BreakingPoint*','weapon',3,'wp'),
	(16,'Tension Bow','*Item_TensionBow*','weapon',3,'wp'),
	(17,'Bonesaw','*Item_Bonesaw*','weapon',3,'wp'),
	(18,'Tornado Trigger','*Item_TornadoTrigger*','weapon',3,'wp'),
	(19,'Tyrants Monocle','*Item_TyrantsMonocle*','weapon',3,'wp'),
	(20,'Crystal Bit','*Item_CrystalBit*','ability',1,'cp'),
	(21,'Hourglass','*Item_Hourglass*','ability',1,'cp'),
	(22,'Energy Battery','*Item_EnergyBattery*','ability',1,'cp'),
	(23,'Heavy Prism','*Item_HeavyPrism*','ability',2,'cp'),
	(24,'Eclipse Prism','*Item_EclipsePrism*','ability',2,'cp'),
	(25,'Chronograph','*Item_Chronograph*','ability',2,'cp'),
	(26,'Void Battery','*Item_VoidBattery*','ability',2,'cp'),
	(27,'Piercing Shard','*Item_PiercingShard*','ability',2,'cp'),
	(28,'Shatterglass','*Item_Shatterglass*','ability',3,'cp'),
	(29,'Spellfire','*Item_Spellfire*','ability',3,'cp'),
	(30,'Frostburn','*Item_Frostburn*','ability',3,'cp'),
	(31,'Dragon\'s Eye','*Item_DragonsEye*','ability',3,'cp'),
	(32,'Clockwork','*Item_Clockwork*','ability',3,'cp'),
	(33,'Broken Myth','*Item_BrokenMyth*','ability',3,'cp'),
	(34,'Eve Of Harvest','*Item_EveOfHarvest*','ability',3,'cp'),
	(35,'Aftershock','*Item_Aftershock*','ability',2,'cp'),
	(36,'Alternating Current','*Item_AlternatingCurrent*','ability',3,'cp'),
	(37,'Oakheart','*Item_Oakheart*','defense',1,NULL),
	(38,'Light Shield','*Item_LightShield*','defense',1,NULL),
	(39,'Light Armor','*Item_LightArmor*','defense',1,NULL),
	(40,'Dragonheart','*Item_Dragonheart*','defense',2,NULL),
	(41,'Lifespring','*Item_Lifespring*','defense',2,'support'),
	(42,'Reflex Block','*Item_ReflexBlock*','defense',2,NULL),
	(43,'Kinetic Shield','*Item_KineticShield*','defense',2,NULL),
	(44,'Coat Of Plates','*Item_CoatOfPlates*','defense',2,NULL),
	(45,'Pulseweave','*Item_Pulseweave*','defense',3,'support'),
	(46,'Crucible','*Item_Crucible*','defense',3,'support'),
	(47,'Capacitor Plate','*Item_CapacitorPlate*','defense',3,'support'),
	(48,'Rook\'s Decree','*Item_RooksDecree*','defense',3,'support'),
	(49,'Fountain of Renewal','*Item_FountainOfRenewal*','defense',3,'support'),
	(50,'Aegis','*Item_Aegis*','defense',3,NULL),
	(51,'Slumbering Husk','*Item_SlumberingHusk*','defense',3,NULL),
	(52,'Metal Jacket','*Item_MetalJacket*','defense',3,NULL),
	(53,'Atlas Pauldron','*Item_AtlasPauldron*','defense',3,'support'),
	(54,'Sprint Boots','*Item_SprintBoots*','utility',1,NULL),
	(55,'Travel Boots','*Item_TravelBoots*','utility',2,NULL),
	(56,'Stormguard Banner','*Item_StormguardBanner*','utility',2,'support'),
	(57,'Teleport Boots','*Item_TeleportBoots*','utility',3,NULL),
	(58,'Journey Boots','*Item_JourneyBoots*','utility',3,NULL),
	(59,'War Treads','*Item_WarTreads*','utility',3,'support'),
	(60,'Halcyon Chargers','*Item_HalcyonChargers*','utility',3,NULL),
	(61,'Stormcrown','*Item_Stormcrown*','utility',3,'support'),
	(62,'Nullwave Gauntlet','*Item_NullwaveGauntlet*','utility',3,'support'),
	(63,'Shiversteel','*Item_Shiversteel*','utility',3,'support'),
	(64,'Healing Flask','*Item_HealingFlask*','other',1,NULL),
	(65,'Vision Totem','*Item_VisionTotem*','other',1,'support'),
	(66,'FlareLoader','*Item_FlareLoader*','other',1,'support'),
	(67,'Minion Candy','*Item_MinionCandy*','other',1,NULL),
	(68,'ScoutPak','*Item_ScoutPak*','other',2,'support'),
	(69,'ScoutTuff','*Item_ScoutTuff*','other',2,'support'),
	(70,'Ironguard Contract','*Item_IronguardContract*','other',1,'support'),
	(71,'Protector Contract','*Item_ProtectorContract*','other',1,'support'),
	(72,'Dragonblood Contract','*Item_DragonbloodContract*','other',1,'support'),
	(73,'SuperScout 2000','*Item_SuperScout2000*','other',3,'support'),
	(74,'Crystal Infusion','*Item_CrystalInfusion*','other',1,NULL),
	(75,'Weapon Infusion','*Item_WeaponInfusion*','other',1,NULL),
	(76,'Flare','*Item_Flare*','other',1,'support'),
	(77,'Scout Trap','*Item_ScoutTrap*','other',1,'support'),
	(78,'Flaregun','*Item_Flaregun*','other',2,'support'),
	(79,'Contraption','*Item_Contraption*','other',3,'support'),
	(80,'ScoutTrap','*Item_ScoutTrap*','other',1,'support');

/*!40000 ALTER TABLE `m_items` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
