
"""
Create database tables and load synthetic sample data.

Run:
    python init_db.py          Create tables and seed if movies is empty.
    python init_db.py --reset  Drop tables and recreate sample data.
"""

import sys
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import insert, select, func

from db import (
    create_tables,
    engine,
    metadata,
    genres,
    movies,
    ratings,
    users,
)


# Sample movie data: (title, release year, genre name)
MOVIES = [
    ("The Shawshank Redemption", 1994, "Drama"),
    ("Forrest Gump", 1994, "Drama"),
    ("The Godfather", 1972, "Drama"),
    ("Schindler's List", 1993, "Drama"),
    ("Moonlight", 2016, "Drama"),
    ("12 Years a Slave", 2013, "Drama"),
    ("Inception", 2010, "Sci-Fi"),
    ("Interstellar", 2014, "Sci-Fi"),
    ("The Matrix", 1999, "Sci-Fi"),
    ("Blade Runner 2049", 2017, "Sci-Fi"),
    ("Arrival", 2016, "Sci-Fi"),
    ("Ex Machina", 2014, "Sci-Fi"),
    ("The Dark Knight", 2008, "Action"),
    ("Mad Max: Fury Road", 2015, "Action"),
    ("Gladiator", 2000, "Action"),
    ("John Wick", 2014, "Action"),
    ("Die Hard", 1988, "Action"),
    ("Mission: Impossible - Fallout", 2018, "Action"),
    ("3 Idiots", 2009, "Comedy"),
    ("The Grand Budapest Hotel", 2014, "Comedy"),
    ("Superbad", 2007, "Comedy"),
    ("Bridesmaids", 2011, "Comedy"),
    ("Knives Out", 2019, "Comedy"),
    ("Groundhog Day", 1993, "Comedy"),
    ("Spirited Away", 2001, "Animation"),
    ("Toy Story", 1995, "Animation"),
    ("Inside Out", 2015, "Animation"),
    ("Spider-Man: Into the Spider-Verse", 2018, "Animation"),
    ("Coco", 2017, "Animation"),
    ("Your Name", 2016, "Animation"),
    ("Parasite", 2019, "Thriller"),
    ("Se7en", 1995, "Thriller"),
    ("Gone Girl", 2014, "Thriller"),
    ("Prisoners", 2013, "Thriller"),
    ("Shutter Island", 2010, "Thriller"),
    ("Nightcrawler", 2014, "Thriller"),
    ("Get Out", 2017, "Horror"),
    ("Hereditary", 2018, "Horror"),
    ("The Conjuring", 2013, "Horror"),
    ("A Quiet Place", 2018, "Horror"),
    ("Titanic", 1997, "Romance"),
    ("The Notebook", 2004, "Romance"),
    ("La La Land", 2016, "Romance"),
    ("Pride & Prejudice", 2005, "Romance"),
    ("Before Sunrise", 1995, "Romance"),
]


def seed():
    """Insert genres, movies, users, and synthetic ratings."""

    rng = np.random.default_rng(42)

    with engine.begin() as conn:

        # 1. Insert all unique genres.
        genre_names = sorted(
            {genre_name for _, _, genre_name in MOVIES}
        )

        conn.execute(
            insert(genres),
            [
                {"genre_name": genre_name}
                for genre_name in genre_names
            ],
        )

        # 2. Create a mapping from genre name to genre ID.
        genre_rows = conn.execute(
            select(genres.c.genre_id, genres.c.genre_name)
        ).all()

        genre_ids = {
            genre_name: genre_id
            for genre_id, genre_name in genre_rows
        }

        # 3. Insert movies with their corresponding genre IDs.
        conn.execute(
            insert(movies),
            [
                {
                    "title": title,
                    "release_year": release_year,
                    "genre_id": genre_ids[genre_name],
                }
                for title, release_year, genre_name in MOVIES
            ],
        )

        # Read the inserted movie IDs and genre IDs.
        movie_rows = conn.execute(
            select(
                movies.c.movie_id,
                movies.c.genre_id,
            ).order_by(movies.c.movie_id)
        ).all()

        # 4. Insert 40 sample users.
        number_of_users = 40

        conn.execute(
            insert(users),
            [
                {
                    "display_name": f"viewer{i:02d}",
                    "password_hash": None,
                }
                for i in range(1, number_of_users + 1)
            ],
        )

        user_ids = [
            row[0]
            for row in conn.execute(
                select(users.c.user_id).order_by(users.c.user_id)
            )
        ]

        # Prepare movie information for rating generation.
        movie_ids = np.array(
            [row[0] for row in movie_rows]
        )

        movie_genres = {
            movie_id: genre_id
            for movie_id, genre_id in movie_rows
        }

        # Assign a synthetic quality score to each movie.
        movie_quality = {
            movie_id: rng.normal(3.7, 0.45)
            for movie_id in movie_ids
        }

        # Make some movies more popular than others.
        popularity = rng.lognormal(
            mean=0,
            sigma=1.7,
            size=len(movie_ids),
        )
        popularity /= popularity.sum()

        # 5. Generate synthetic ratings.
        output_ratings = []
        current_time = datetime.utcnow()

        for user_id in user_ids:

            # Different users have different tastes by genre.
            user_taste = {
                genre_id: rng.normal(0, 0.7)
                for genre_id in genre_ids.values()
            }

            number_to_rate = int(
                rng.integers(10, 22)
            )

            chosen_movies = rng.choice(
                movie_ids,
                size=number_to_rate,
                replace=False,
                p=popularity,
            )

            for movie_id in chosen_movies:

                raw_rating = (
                    movie_quality[movie_id]
                    + user_taste[movie_genres[movie_id]]
                    + rng.normal(0, 0.4)
                )

                # Ratings range from 0.5 to 5.0 in half-star steps.
                rating_value = float(
                    np.clip(
                        round(raw_rating * 2) / 2,
                        0.5,
                        5.0,
                    )
                )

                output_ratings.append(
                    {
                        "user_id": user_id,
                        "movie_id": int(movie_id),
                        "rating": rating_value,
                        "rated_at": current_time
                        - timedelta(
                            days=int(rng.integers(0, 365))
                        ),
                    }
                )

        # 6. Save the ratings.
        conn.execute(
            insert(ratings),
            output_ratings,
        )

    print(
        f"Seeded {len(MOVIES)} movies, "
        f"{number_of_users} sample users, "
        f"{len(output_ratings)} sample ratings."
    )


if __name__ == "__main__":

    # WARNING: --reset permanently deletes existing tables and data.
    if "--reset" in sys.argv:
        confirm = input(
            "This will delete existing database tables and data. "
            "Type RESET to continue: "
        )

        if confirm != "RESET":
            print("Reset cancelled. Existing data was not deleted.")
            sys.exit(0)

        metadata.drop_all(engine)

    # Create any missing tables.
    create_tables()

    # Seed only when the movies table is empty.
    with engine.connect() as conn:
        movie_count = conn.execute(
            select(func.count()).select_from(movies)
        ).scalar_one()

    if movie_count == 0:
        seed()
    else:
        print(
            "Tables already contain movies. "
            "No sample data was inserted."
        )
