-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: movie_rating
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `genres`
--

DROP TABLE IF EXISTS `genres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genres` (
  `genre_id` int NOT NULL AUTO_INCREMENT,
  `genre_name` varchar(100) NOT NULL,
  PRIMARY KEY (`genre_id`),
  UNIQUE KEY `genre_name` (`genre_name`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genres`
--

LOCK TABLES `genres` WRITE;
/*!40000 ALTER TABLE `genres` DISABLE KEYS */;
INSERT INTO `genres` VALUES (1,'Action'),(2,'Adventure'),(3,'Animation'),(4,'Comedy'),(5,'Crime'),(12,'Documentary'),(6,'Drama'),(7,'Fantasy'),(8,'Horror'),(9,'Romance'),(10,'Sci-Fi'),(11,'Thriller');
/*!40000 ALTER TABLE `genres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies` (
  `movie_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `release_year` int DEFAULT NULL,
  `genre_id` int NOT NULL,
  PRIMARY KEY (`movie_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `movies_ibfk_1` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES (1,'Inception',2010,10),(2,'Interstellar',2014,10),(3,'The Dark Knight',2008,1),(4,'Titanic',1997,9),(5,'Avatar',2009,10),(6,'The Avengers',2012,1),(7,'3 Idiots',2009,4),(8,'Dangal',2016,6),(9,'Joker',2019,6),(10,'Toy Story',1995,3),(11,'The Matrix',1999,10),(12,'Finding Nemo',2003,3),(13,'The Hangover',2009,4),(14,'Gladiator',2000,1),(15,'Coco',2017,3);
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ratings` (
  `rating_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `movie_id` int NOT NULL,
  `rating` decimal(2,1) NOT NULL,
  `rated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rating_id`),
  KEY `user_id` (`user_id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`),
  CONSTRAINT `ratings_chk_1` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings`
--

LOCK TABLES `ratings` WRITE;
/*!40000 ALTER TABLE `ratings` DISABLE KEYS */;
INSERT INTO `ratings` VALUES (1,1,1,5.0,'2026-10-25 09:11:32'),(2,2,1,4.5,'2026-10-25 09:11:32'),(3,3,1,4.0,'2026-10-25 09:11:32'),(4,4,1,5.0,'2026-10-25 09:11:32'),(5,5,1,4.5,'2026-10-25 09:11:32'),(6,6,1,4.0,'2026-10-25 09:11:32'),(7,1,2,5.0,'2026-10-25 09:11:32'),(8,2,2,4.5,'2026-10-25 09:11:32'),(9,3,2,5.0,'2026-10-25 09:11:32'),(10,4,2,4.0,'2026-10-25 09:11:32'),(11,5,2,4.5,'2026-10-25 09:11:32'),(12,1,3,4.5,'2026-10-25 09:11:32'),(13,2,3,5.0,'2026-10-25 09:11:32'),(14,3,3,4.5,'2026-10-25 09:11:32'),(15,4,3,4.0,'2026-10-25 09:11:32'),(16,5,3,5.0,'2026-10-25 09:11:32'),(17,6,3,4.5,'2026-10-25 09:11:32'),(18,1,4,4.0,'2026-10-25 09:11:32'),(19,2,4,4.5,'2026-10-25 09:11:32'),(20,3,4,3.5,'2026-10-25 09:11:32'),(21,4,4,4.0,'2026-10-25 09:11:32'),(22,1,5,4.5,'2026-10-25 09:11:32'),(23,2,5,5.0,'2026-10-25 09:11:32'),(24,3,5,4.0,'2026-10-25 09:11:32'),(25,4,5,4.5,'2026-10-25 09:11:32'),(26,5,5,4.0,'2026-10-25 09:11:32'),(27,1,6,4.0,'2026-10-25 09:11:32'),(28,2,6,4.5,'2026-10-25 09:11:32'),(29,3,6,4.0,'2026-10-25 09:11:32'),(30,4,6,4.5,'2026-10-25 09:11:32'),(31,1,7,5.0,'2026-10-25 09:11:32'),(32,2,7,4.5,'2026-10-25 09:11:32'),(33,3,7,4.0,'2026-10-25 09:11:32'),(34,4,7,5.0,'2026-10-25 09:11:32'),(35,5,7,4.5,'2026-10-25 09:11:32'),(36,1,8,4.5,'2026-10-25 09:11:32'),(37,2,8,4.0,'2026-10-25 09:11:32'),(38,3,8,5.0,'2026-10-25 09:11:32'),(39,4,8,4.5,'2026-10-25 09:11:32'),(40,1,9,4.0,'2026-10-25 09:11:32'),(41,3,9,4.5,'2026-10-25 09:11:32'),(42,5,9,4.0,'2026-10-25 09:11:32'),(43,2,10,4.5,'2026-10-25 09:11:32'),(44,4,10,5.0,'2026-10-25 09:11:32'),(45,5,10,4.5,'2026-10-25 09:11:32'),(46,1,11,5.0,'2026-10-25 09:11:32'),(47,2,11,4.5,'2026-10-25 09:11:32'),(48,3,11,4.0,'2026-10-25 09:11:32'),(49,6,11,5.0,'2026-10-25 09:11:32'),(50,2,12,4.5,'2026-10-25 09:11:32'),(51,3,12,4.0,'2026-10-25 09:11:32'),(52,4,12,5.0,'2026-10-25 09:11:32'),(53,1,13,4.0,'2026-10-25 09:11:32'),(54,2,13,4.5,'2026-10-25 09:11:32'),(55,5,13,4.0,'2026-10-25 09:11:32'),(56,1,14,4.5,'2026-10-25 09:11:32'),(57,3,14,5.0,'2026-10-25 09:11:32'),(58,4,14,4.5,'2026-10-25 09:11:32'),(59,2,15,5.0,'2026-10-25 09:11:32'),(60,4,15,4.5,'2026-10-25 09:11:32'),(61,5,15,5.0,'2026-10-25 09:11:32'),(62,1,1,5.0,'2026-10-25 09:13:59'),(63,2,1,4.5,'2026-10-25 09:13:59'),(64,3,1,4.0,'2026-10-25 09:13:59'),(65,4,1,5.0,'2026-10-25 09:13:59'),(66,5,1,4.5,'2026-10-25 09:13:59'),(67,6,1,4.0,'2026-10-25 09:13:59'),(68,1,2,5.0,'2026-10-25 09:13:59'),(69,2,2,4.5,'2026-10-25 09:13:59'),(70,3,2,5.0,'2026-10-25 09:13:59'),(71,4,2,4.0,'2026-10-25 09:13:59'),(72,5,2,4.5,'2026-10-25 09:13:59'),(73,1,3,4.5,'2026-10-25 09:13:59'),(74,2,3,5.0,'2026-10-25 09:13:59'),(75,3,3,4.5,'2026-10-25 09:13:59'),(76,4,3,4.0,'2026-10-25 09:13:59'),(77,5,3,5.0,'2026-10-25 09:13:59'),(78,6,3,4.5,'2026-10-25 09:13:59'),(79,1,4,4.0,'2026-10-25 09:13:59'),(80,2,4,4.5,'2026-10-25 09:13:59'),(81,3,4,3.5,'2026-10-25 09:13:59'),(82,4,4,4.0,'2026-10-25 09:13:59'),(83,1,5,4.5,'2026-10-25 09:13:59'),(84,2,5,5.0,'2026-10-25 09:13:59'),(85,3,5,4.0,'2026-10-25 09:13:59'),(86,4,5,4.5,'2026-10-25 09:13:59'),(87,5,5,4.0,'2026-10-25 09:13:59'),(88,1,6,4.0,'2026-10-25 09:13:59'),(89,2,6,4.5,'2026-10-25 09:13:59'),(90,3,6,4.0,'2026-10-25 09:13:59'),(91,4,6,4.5,'2026-10-25 09:13:59'),(92,1,7,5.0,'2026-10-25 09:13:59'),(93,2,7,4.5,'2026-10-25 09:13:59'),(94,3,7,4.0,'2026-10-25 09:13:59'),(95,4,7,5.0,'2026-10-25 09:13:59'),(96,5,7,4.5,'2026-10-25 09:13:59'),(97,1,8,4.5,'2026-10-25 09:13:59'),(98,2,8,4.0,'2026-10-25 09:13:59'),(99,3,8,5.0,'2026-10-25 09:13:59'),(100,4,8,4.5,'2026-10-25 09:13:59'),(101,1,9,4.0,'2026-10-25 09:13:59'),(102,3,9,4.5,'2026-10-25 09:13:59'),(103,5,9,4.0,'2026-10-25 09:13:59'),(104,2,10,4.5,'2026-10-25 09:13:59'),(105,4,10,5.0,'2026-10-25 09:13:59'),(106,5,10,4.5,'2026-10-25 09:13:59'),(107,1,11,5.0,'2026-10-25 09:13:59'),(108,2,11,4.5,'2026-10-25 09:13:59'),(109,3,11,4.0,'2026-10-25 09:13:59'),(110,6,11,5.0,'2026-10-25 09:13:59'),(111,2,12,4.5,'2026-10-25 09:13:59'),(112,3,12,4.0,'2026-10-25 09:13:59'),(113,4,12,5.0,'2026-10-25 09:13:59'),(114,1,13,4.0,'2026-10-25 09:13:59'),(115,2,13,4.5,'2026-10-25 09:13:59'),(116,5,13,4.0,'2026-10-25 09:13:59'),(117,1,14,4.5,'2026-10-25 09:13:59'),(118,3,14,5.0,'2026-10-25 09:13:59'),(119,4,14,4.5,'2026-10-25 09:13:59'),(120,2,15,5.0,'2026-10-25 09:13:59'),(121,4,15,4.5,'2026-10-25 09:13:59'),(122,5,15,5.0,'2026-10-25 09:13:59');
/*!40000 ALTER TABLE `ratings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `display_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'User1'),(2,'User2'),(3,'User3'),(4,'User4'),(5,'User5'),(6,'User6'),(7,'User7'),(8,'User8');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 15:17:57
