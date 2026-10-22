"""Pandas / NumPy aggregation. Everything here returns aggregates only (no per-user rows)."""
import json

import numpy as np
import pandas as pd
from sqlalchemy import select

from config import MIN_RATING_COUNT, RATING_VALUES
from db import engine, movies, ratings, users


def records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> plain Python list of dicts (JSON/Jinja safe, NaN -> None)."""
    return json.loads(df.to_json(orient="records"))


def load_data():
    """Return (movies, ratings, users) DataFrames. Password hashes are never loaded."""
    with engine.connect() as conn:
        m = pd.read_sql(select(movies), conn)
        r = pd.read_sql(select(ratings.c.user_id, ratings.c.movie_id,
                               ratings.c.rating, ratings.c.rated_at), conn)
        u = pd.read_sql(select(users.c.user_id), conn)
    r["rating"] = r["rating"].astype(float)
    return m, r, u


def movie_stats(m: pd.DataFrame, r: pd.DataFrame) -> pd.DataFrame:
    """One row per movie: rating_count, avg_rating, and whether it meets the minimum-count rule."""
    agg = (r.groupby("movie_id")["rating"]
             .agg(rating_count="count", avg_rating="mean").reset_index())
    df = m.merge(agg, on="movie_id", how="left")
    df["rating_count"] = df["rating_count"].fillna(0).astype(int)
    df["avg_rating"] = df["avg_rating"].round(2)
    df["qualifies"] = df["rating_count"] >= MIN_RATING_COUNT
    return df


def top_rated(stats: pd.DataFrame, n: int = 10, genre: str | None = None) -> pd.DataFrame:
    df = stats[stats["qualifies"]]
    if genre:
        df = df[df["genre"] == genre]
    return (df.sort_values(["avg_rating", "rating_count"], ascending=False)
              .head(n).reset_index(drop=True))


def genre_analysis(m: pd.DataFrame, r: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    rm = r.merge(m[["movie_id", "genre"]], on="movie_id")
    per_rating = rm.groupby("genre")["rating"].agg(total_ratings="count", avg_rating="mean")
    per_movie = stats.groupby("genre").agg(movies=("movie_id", "count"),
                                           ranked_movies=("qualifies", "sum"))
    g = per_movie.join(per_rating, how="left")
    g["total_ratings"] = g["total_ratings"].fillna(0).astype(int)
    g["avg_rating"] = g["avg_rating"].fillna(0).round(2)
    g["ranked_movies"] = g["ranked_movies"].astype(int)
    return g.sort_values("avg_rating", ascending=False).reset_index()


def distribution(r: pd.DataFrame) -> pd.DataFrame:
    counts = r["rating"].value_counts().reindex(RATING_VALUES, fill_value=0)
    return pd.DataFrame({"rating": counts.index, "count": counts.values.astype(int)})


def rating_stats(r: pd.DataFrame) -> dict | None:
    """NumPy summary statistics for all ratings."""
    if r.empty:
        return None
    a = r["rating"].to_numpy(dtype=float)
    return {
        "count": int(a.size),
        "mean": round(float(np.mean(a)), 2),
        "median": float(np.median(a)),
        "std": round(float(np.std(a, ddof=1)), 2) if a.size > 1 else 0.0,
        "p25": float(np.percentile(a, 25)),
        "p75": float(np.percentile(a, 75)),
        "min": float(a.min()),
        "max": float(a.max()),
    }
