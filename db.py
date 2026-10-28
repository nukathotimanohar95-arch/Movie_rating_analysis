
"""Database tables using SQLAlchemy Core.
Matches the existing movie_rating MySQL database.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    TIMESTAMP,
    MetaData,
    Table,
    create_engine,
    text,
)

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()


# 1. Genres table
genres = Table(
    "genres",
    metadata,
    Column("genre_id", Integer, primary_key=True, autoincrement=True),
    Column("genre_name", String(100), nullable=False, unique=True),
)


# 2. Movies table
movies = Table(
    "movies",
    metadata,
    Column("movie_id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(150), nullable=False),
    Column("release_year", Integer, nullable=True),
    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.genre_id"),
        nullable=False,
    ),
)


# 3. Users table
users = Table(
    "users",
    metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("display_name", String(100), nullable=True),
    Column("password_hash", String(255), nullable=True),
)


# 4. Ratings table
ratings = Table(
    "ratings",
    metadata,
    Column("rating_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    ),
    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.movie_id"),
        nullable=False,
    ),
    Column("rating", Numeric(2, 1), nullable=False),
    Column(
        "rated_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=True,
    ),
)


def create_tables():
    """Create any missing tables; do not alter existing tables."""
    metadata.create_all(engine)

