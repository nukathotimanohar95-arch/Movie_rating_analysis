USE movie_ratings;

INSERT INTO genres (name) VALUES
 ('Action'),('Comedy'),('Drama'),('Sci-Fi'),('Thriller'),('Animation'),('Romance'),('Horror');

INSERT INTO movies (title, release_year, genre) VALUES
 ('The Shawshank Redemption', 1994, 'Drama'),
 ('Inception', 2010, 'Sci-Fi'),
 ('The Dark Knight', 2008, 'Action'),
 ('Interstellar', 2014, 'Sci-Fi'),
 ('Spirited Away', 2001, 'Animation'),
 ('Parasite', 2019, 'Thriller'),
 ('3 Idiots', 2009, 'Comedy'),
 ('Titanic', 1997, 'Romance'),
 ('Get Out', 2017, 'Horror'),
 ('Mad Max: Fury Road', 2015, 'Action'),
 ('Toy Story', 1995, 'Animation'),
 ('The Notebook', 2004, 'Romance');

INSERT INTO movie_genres (movie_id, genre_id) VALUES
 (1,3),(2,4),(2,5),(3,1),(3,5),(4,4),(4,3),(5,6),(6,5),(6,3),
 (7,2),(7,3),(8,7),(8,3),(9,8),(9,5),(10,1),(10,4),(11,6),(11,2),(12,7);

INSERT INTO users (display_name) VALUES
 ('user_a'),('user_b'),('user_c'),('user_d'),('user_e'),(NULL);

INSERT INTO ratings (user_id, movie_id, rating) VALUES
 (1,1,5.0),(1,2,4.5),(1,3,4.0),(1,4,4.5),(1,7,4.0),
 (2,1,4.5),(2,2,4.0),(2,3,4.5),(2,6,5.0),(2,10,4.0),
 (3,1,5.0),(3,5,4.5),(3,7,5.0),(3,8,3.5),(3,11,4.0),
 (4,2,5.0),(4,4,5.0),(4,6,4.5),(4,9,3.5),(4,10,4.5),
 (5,3,4.0),(5,5,5.0),(5,8,4.0),(5,11,4.5),(5,12,3.0),
 (6,1,4.0),(6,3,5.0),(6,6,4.0),(6,7,4.5),(6,9,3.0);
