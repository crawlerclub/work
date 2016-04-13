-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: onlinedb
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `show_pattern`
--

DROP TABLE IF EXISTS `show_pattern`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `show_pattern` (
  `source` varchar(32) DEFAULT 'NULL',
  `show_id` int(11) NOT NULL AUTO_INCREMENT,
  `key_words` varchar(64) DEFAULT 'NULL',
  `type` varchar(64) DEFAULT 'NULL',
  `pattern` varchar(128) DEFAULT 'NULL',
  PRIMARY KEY (`show_id`)
) ENGINE=MyISAM AUTO_INCREMENT=78 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `show_pattern`
--

LOCK TABLES `show_pattern` WRITE;
/*!40000 ALTER TABLE `show_pattern` DISABLE KEYS */;
INSERT INTO `show_pattern` VALUES ('booking',1,'out_time_charge','out_time_charge','如果info_date取消或更改预订，info_price。'),('booking',2,'noshow_free','noshow_free','请注意，如果未如期入住，您无需支付任何费用。'),('elong',3,'不可退','不可退','如果取消预订，您需要支付info_price。'),('elong',4,'不可改','不可改','如果更改预订，您需要支付info_price。'),('elong',5,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('elong',6,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('elong',7,'收费退','收费退','如果info_date取消预订，您需要支付info_price。'),('elong',8,'收费改','收费改','如果info_date更改预订，您需要支付info_price。'),('elong',9,'noshow','noshow','如果未入住或提早退房，您需要支付info_price。'),('elong',10,'预付','预付','预订后，您需要支付info_price。'),('hotels',11,'不可退','不可退','此特价房不可退款，如果取消预订，您需要支付info_price。'),('hotels',12,'不可改','不可改','此特价房不可退款，如果更改预订，您需要支付info_price。'),('hotels',13,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('hotels',14,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('hotels',15,'收费退','收费退','如果info_date取消预订，您可能需要支付一定费用，具体金额以原网站为准。'),('hotels',16,'收费改','收费改','如果info_date更改预订，您可能需要支付一定费用，具体金额以原网站为准。'),('hotels',17,'noshow','noshow','如果未入住或提早退房，您需要支付info_price。'),('hotels',18,'预付','预付','预订后，您需要支付info_price。'),('booking',19,'noshow','noshow','如果未入住，您需要支付info_price。'),('booking',20,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('booking',21,'收费改','收费改','如果info_date更改预订，您需要支付info_price。'),('booking',22,'不可改','不可改','请注意，如果info_date更改预订，您需要支付info_price。'),('booking',23,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('booking',24,'收费退','收费退','如果info_date取消预订，您需要支付info_price。'),('booking',25,'不可退','不可退','请注意，如果info_date取消预订，您需要支付info_price。'),('booking',26,'others','预付','预订后,您需要支付info_price。'),('booking',27,'入住日当天','预付','入住日当天，您需要支付info_price。'),('booking',28,'N天之前','预付','info_date，您需要支付info_price。'),('booking',29,'现付','现付','免费预订，入住时付款。'),('elong',30,'out_time_charge','out_time_charge','如果info_date取消或更改预订，info_price。'),('hotels',31,'out_time_charge','out_time_charge','如果超出时限，您可能需要支付一定费用，具体金额以原网站为准。'),('elong',32,'不可取消或更改','不可取消或更改','如果取消或更改预订，您需要支付info_price。'),('elong',33,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('elong',34,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您需要支付info_price。'),('hotels',35,'不可取消或更改','不可取消或更改','此特价房不可退款，如果取消或更改预订，您需要支付info_price。'),('hotels',36,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('hotels',37,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您可能需要支付一定费用，具体金额以原网站为准。'),('booking',38,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('booking',39,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您需要支付info_price。'),('booking',40,'不可取消或更改','不可取消或更改','请注意，如果info_date取消或更改预订，您需要支付info_price。'),('venere',41,'不可退','不可退','此特价房不可退款，如果取消预订，您需要支付info_price。'),('venere',42,'不可改','不可改','此特价房不可退款，如果更改预订，您需要支付info_price。'),('venere',43,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('venere',44,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('venere',45,'收费退','收费退','如果info_date取消预订，您可能需要支付一定费用，具体金额以原网站为准。'),('venere',46,'收费改','收费改','如果info_date更改预订，您可能需要支付一定费用，具体金额以原网站为准。'),('venere',47,'noshow','noshow','如果未入住或提早退房，您需要支付info_price。'),('venere',48,'预付','预付','预订后，您需要支付info_price。'),('venere',49,'out_time_charge','out_time_charge','如果超出时限，您可能需要支付一定费用，具体金额以原网站为准。'),('venere',50,'不可取消或更改','不可取消或更改','此特价房不可退款，如果取消或更改预订，您需要支付info_price。'),('venere',51,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('venere',52,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您可能需要支付一定费用，具体金额以原网站为准。'),('ctrip',57,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('ctrip',58,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您需要支付info_price。'),('ctrip',56,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('ctrip',55,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('ctrip',54,'预付','预付','预订后，您需要支付info_price。'),('ctrip',53,'现付','现付','免费预订，入住时付款。'),('ctrip',59,'收费退','收费退','如果info_date取消预订，您需要支付info_price。'),('ctrip',60,'收费改','收费改','如果info_date更改预订，您需要支付info_price。'),('ctrip',61,'不可取消或更改','不可取消或更改','请注意，如果info_date取消或更改预订，您需要支付info_price。'),('ctrip',62,'不可退','不可退','请注意，如果info_date取消预订，您需要支付info_price。'),('ctrip',63,'不可改','不可改','请注意，如果info_date更改预订，您需要支付info_price。'),('ctrip',64,'noshow','noshow','如果未如期入住，您需要支付info_price。'),('ctrip',65,'预付1','预付1','预订后，您需要以info_price。'),('expedia',66,'免费改','免费改','如果info_date更改预订，您无需支付任何费用。'),('expedia',67,'免费退','免费退','如果info_date取消预订，您无需支付任何费用。'),('expedia',68,'免费取消或更改','免费取消或更改','如果info_date取消或更改预订，您无需支付任何费用。'),('expedia',69,'预付','预付','预订后，您需要支付info_price。'),('expedia',70,'现付','现付','免费预订，入住时付款。'),('expedia',71,'收费退','收费退','如果info_date取消预订，您需要支付info_price。'),('expedia',72,'收费改','收费改','如果info_date更改预订，您需要支付info_price。'),('expedia',73,'收费取消或更改','收费取消或更改','如果info_date取消或更改预订，您需要支付info_price。'),('expedia',74,'不可取消或更改','不可取消或更改','请注意，如果info_date取消或更改预订，您将不会获得任何退款'),('expedia',75,'不可退','不可退','请注意，如果info_date取消预订，您将不会获得任何退款。'),('expedia',76,'不可改','不可改','请注意，如果info_date更改预订，您将不会获得任何退款。'),('expedia',77,'noshow','noshow','如果未如期入住，您需要支付info_price。');
/*!40000 ALTER TABLE `show_pattern` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-10 14:30:47
