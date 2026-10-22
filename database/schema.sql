-- Movie Ratings Analysis and Basic Recommendation System
-- MySQL 8.x schema

CREATE DATABASE IF NOT EXISTS movie_ratings
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movie_ratings;

-- Genres kept in their own table so a movie can have several genres
CREATE TABLE genres (
  genre_id   INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE movies (
  movie_id      INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(200) NOT NULL,
  release_year  SMALLINT NOT NULL,
  genre         VARCHAR(50) NOT NULL,          -- primary genre (matches project spec)
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_title_year (title, release_year),
  CONSTRAINT chk_year CHECK (release_year BETWEEN 1888 AND 2100),
  INDEX idx_genre (genre)
);

-- Optional extra genres per movie (many-to-many); used for similarity
CREATE TABLE movie_genres (
  movie_id INT NOT NULL,
  genre_id INT NOT NULL,
  PRIMARY KEY (movie_id, genre_id),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE
);

-- display_name is optional; no email/real name stored (privacy requirement)
CREATE TABLE users (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  display_name  VARCHAR(50) NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ratings (
  rating_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  movie_id   INT NOT NULL,
  rating     DECIMAL(2,1) NOT NULL,            -- 0.5 to 5.0
  rated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_movie (user_id, movie_id), -- one rating per user per movie
  CONSTRAINT chk_rating CHECK (rating BETWEEN 0.5 AND 5.0),
  FOREIGN KEY (user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
  INDEX idx_movie (movie_id)
);

-- Aggregate-only view: safe to expose, contains no per-user data
CREATE VIEW movie_stats AS
SELECT m.movie_id, m.title, m.release_year, m.genre,
       COUNT(r.rating_id)        AS rating_count,
       ROUND(AVG(r.rating), 2)   AS avg_rating
FROM movies m
LEFT JOIN ratings r ON r.movie_id = m.movie_id
GROUP BY m.movie_id, m.title, m.release_year, m.genre;
