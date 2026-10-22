"""Database tables (SQLAlchemy Core). Works with MySQL and SQLite."""
from datetime import datetime

from sqlalchemy import (CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer,
                        MetaData, SmallInteger, String, Table, UniqueConstraint, create_engine)

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

movies = Table(
    "movies", metadata,
    Column("movie_id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(200), nullable=False),
    Column("release_year", SmallInteger, nullable=False),
    Column("genre", String(50), nullable=False),
    UniqueConstraint("title", "release_year", name="uq_title_year"),
    CheckConstraint("release_year BETWEEN 1888 AND 2100", name="chk_year"),
    Index("idx_movies_genre", "genre"),
)

# display_name is optional in the data model; password_hash lets a person see only their own ratings.
users = Table(
    "users", metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("display_name", String(50), nullable=True, unique=True),
    Column("password_hash", String(255), nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

ratings = Table(
    "ratings", metadata,
    Column("rating_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("movie_id", Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False),
    Column("rating", Float, nullable=False),
    Column("rated_at", DateTime, default=datetime.utcnow, nullable=False),
    UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),  # one rating per user per movie
    CheckConstraint("rating >= 0.5 AND rating <= 5.0", name="chk_rating"),
    Index("idx_ratings_movie", "movie_id"),
)


def create_tables():
    metadata.create_all(engine)
