-- MySQL dump 10.13  Distrib 8.0.21, for Win64 (x86_64)
--
-- Host: localhost    Database: arways
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bro_info`
--

DROP TABLE IF EXISTS `bro_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bro_info` (
  `b_id` int NOT NULL AUTO_INCREMENT,
  `_id` int DEFAULT NULL,
  `title` varchar(40) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `status` int DEFAULT NULL,
  PRIMARY KEY (`b_id`),
  KEY `_id` (`_id`),
  CONSTRAINT `bro_info_ibfk_1` FOREIGN KEY (`_id`) REFERENCES `user_info` (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bro_info`
--

LOCK TABLES `bro_info` WRITE;
/*!40000 ALTER TABLE `bro_info` DISABLE KEYS */;
INSERT INTO `bro_info` VALUES (1,1,'hello','2021-10-11 18:22:44','2021-10-11 21:42:14',0),(2,1,'bye','2021-10-11 21:17:17',NULL,1);
/*!40000 ALTER TABLE `bro_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bro_join`
--

DROP TABLE IF EXISTS `bro_join`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bro_join` (
  `b_id` int DEFAULT NULL,
  `_id` int DEFAULT NULL,
  KEY `b_id` (`b_id`),
  KEY `_id` (`_id`),
  CONSTRAINT `bro_join_ibfk_1` FOREIGN KEY (`b_id`) REFERENCES `bro_info` (`b_id`),
  CONSTRAINT `bro_join_ibfk_2` FOREIGN KEY (`_id`) REFERENCES `user_info` (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bro_join`
--

LOCK TABLES `bro_join` WRITE;
/*!40000 ALTER TABLE `bro_join` DISABLE KEYS */;
/*!40000 ALTER TABLE `bro_join` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `_id` int NOT NULL AUTO_INCREMENT,
  `id` varchar(40) NOT NULL,
  `pasword` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_info`
--

LOCK TABLES `user_info` WRITE;
/*!40000 ALTER TABLE `user_info` DISABLE KEYS */;
INSERT INTO `user_info` VALUES (1,'test','1234'),(2,'undefined','9a996f77282f7c0ea64a733676485162f5f6933e43199fec8c6f8adf20b6f260295c290b3f67702fc2c64c4b41ddfb614cc7a0545932191477d2a1cf7cf56446'),(3,'lhk','84f7b42cb00004078d8858decf3dff5a36817a8aa09e4134f9a1929afd3501d39f282116f468b9ae271754c614fbee4b478576c2f6808243da42aa2e8cd37c60'),(4,'lhk2','84f7b42cb00004078d8858decf3dff5a36817a8aa09e4134f9a1929afd3501d39f282116f468b9ae271754c614fbee4b478576c2f6808243da42aa2e8cd37c60');
/*!40000 ALTER TABLE `user_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-11 21:56:42
