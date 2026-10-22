"""Create the tables and load realistic SAMPLE data (synthetic ratings, fixed random seed).

    python init_db.py            create tables, seed only if the movies table is empty
    python init_db.py --reset    drop everything and re-seed
"""
import sys
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import insert, select, func

from config import GENRES
from db import create_tables, engine, metadata, movies, ratings, users

MOVIES = [
    ("The Shawshank Redemption", 1994, "Drama"), ("Forrest Gump", 1994, "Drama"),
    ("The Godfather", 1972, "Drama"), ("Schindler's List", 1993, "Drama"),
    ("Moonlight", 2016, "Drama"), ("12 Years a Slave", 2013, "Drama"),
    ("Inception", 2010, "Sci-Fi"), ("Interstellar", 2014, "Sci-Fi"),
    ("The Matrix", 1999, "Sci-Fi"), ("Blade Runner 2049", 2017, "Sci-Fi"),
    ("Arrival", 2016, "Sci-Fi"), ("Ex Machina", 2014, "Sci-Fi"),
    ("The Dark Knight", 2008, "Action"), ("Mad Max: Fury Road", 2015, "Action"),
    ("Gladiator", 2000, "Action"), ("John Wick", 2014, "Action"),
    ("Die Hard", 1988, "Action"), ("Mission: Impossible - Fallout", 2018, "Action"),
    ("3 Idiots", 2009, "Comedy"), ("The Grand Budapest Hotel", 2014, "Comedy"),
    ("Superbad", 2007, "Comedy"), ("Bridesmaids", 2011, "Comedy"),
    ("Knives Out", 2019, "Comedy"), ("Groundhog Day", 1993, "Comedy"),
    ("Spirited Away", 2001, "Animation"), ("Toy Story", 1995, "Animation"),
    ("Inside Out", 2015, "Animation"), ("Spider-Man: Into the Spider-Verse", 2018, "Animation"),
    ("Coco", 2017, "Animation"), ("Your Name", 2016, "Animation"),
    ("Parasite", 2019, "Thriller"), ("Se7en", 1995, "Thriller"),
    ("Gone Girl", 2014, "Thriller"), ("Prisoners", 2013, "Thriller"),
    ("Shutter Island", 2010, "Thriller"), ("Nightcrawler", 2014, "Thriller"),
    ("Get Out", 2017, "Horror"), ("Hereditary", 2018, "Horror"),
    ("The Conjuring", 2013, "Horror"), ("A Quiet Place", 2018, "Horror"),
    ("Titanic", 1997, "Romance"), ("The Notebook", 2004, "Romance"),
    ("La La Land", 2016, "Romance"), ("Pride & Prejudice", 2005, "Romance"),
    ("Before Sunrise", 1995, "Romance"),
]


def seed():
    rng = np.random.default_rng(42)
    with engine.begin() as conn:
        conn.execute(insert(movies), [{"title": t, "release_year": y, "genre": g} for t, y, g in MOVIES])
        movie_rows = conn.execute(select(movies.c.movie_id, movies.c.genre).order_by(movies.c.movie_id)).all()
        n_users = 40
        conn.execute(insert(users), [{"display_name": f"viewer{i:02d}", "password_hash": None}
                                     for i in range(1, n_users + 1)])
        user_ids = [r[0] for r in conn.execute(select(users.c.user_id).order_by(users.c.user_id))]

        ids = np.array([r[0] for r in movie_rows])
        genre_of = {r[0]: r[1] for r in movie_rows}
        quality = {i: rng.normal(3.7, 0.45) for i in ids}
        popularity = rng.lognormal(0, 1.7, size=len(ids))  # skewed: a few movies get few ratings
        popularity /= popularity.sum()

        out = []
        now = datetime.utcnow()
        for uid in user_ids:
            taste = {g: rng.normal(0, 0.7) for g in GENRES}
            n = int(rng.integers(10, 22))
            for mid in rng.choice(ids, size=n, replace=False, p=popularity):
                raw = quality[mid] + taste[genre_of[mid]] + rng.normal(0, 0.4)
                value = float(np.clip(round(raw * 2) / 2, 0.5, 5.0))
                out.append({"user_id": uid, "movie_id": int(mid), "rating": value,
                            "rated_at": now - timedelta(days=int(rng.integers(0, 365)))})
        conn.execute(insert(ratings), out)
    print(f"Seeded {len(MOVIES)} movies, {n_users} sample users, {len(out)} sample ratings.")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        metadata.drop_all(engine)
    create_tables()
    with engine.connect() as conn:
        empty = conn.execute(select(func.count()).select_from(movies)).scalar() == 0
    if empty:
        seed()
    else:
        print("Tables already contain data. Use --reset to start over.")
