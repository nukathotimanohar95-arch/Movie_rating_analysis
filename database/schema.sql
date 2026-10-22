-- MySQL 8 schema. Matches db.py. (python init_db.py creates the same tables automatically.)
CREATE DATABASE IF NOT EXISTS movie_ratings CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movie_ratings;

CREATE TABLE movies (
  movie_id      INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(200) NOT NULL,
  release_year  SMALLINT NOT NULL,
  genre         VARCHAR(50) NOT NULL,
  UNIQUE KEY uq_title_year (title, release_year),
  CONSTRAINT chk_year CHECK (release_year BETWEEN 1888 AND 2100),
  INDEX idx_movies_genre (genre)
);

-- display_name is optional in the model; password_hash lets people see only their own ratings.
CREATE TABLE users (
  user_id        INT AUTO_INCREMENT PRIMARY KEY,
  display_name   VARCHAR(50) NULL UNIQUE,
  password_hash  VARCHAR(255) NULL,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ratings (
  rating_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  movie_id   INT NOT NULL,
  rating     FLOAT NOT NULL,
  rated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_movie (user_id, movie_id),          -- one rating per user per movie
  CONSTRAINT chk_rating CHECK (rating >= 0.5 AND rating <= 5.0),
  FOREIGN KEY (user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
  INDEX idx_ratings_movie (movie_id)
);
