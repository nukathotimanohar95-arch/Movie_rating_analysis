"""Central settings. Values come from environment variables or a .env file."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:  # python-dotenv is optional
    pass

BASE_DIR = Path(__file__).resolve().parent

# MySQL example: mysql+pymysql://root:password@localhost/movie_ratings?charset=utf8mb4
# Default is a local SQLite file so the site runs with no database server.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'movie_ratings.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

# Documented rule: a movie is ranked / recommended only with at least this many ratings.
MIN_RATING_COUNT = int(os.getenv("MIN_RATING_COUNT", "3"))
# A user needs at least this many own ratings before personalised recommendations.
MIN_USER_RATINGS = 3
# Two movies need at least this many common raters to be called "similar".
MIN_OVERLAP = 2

RATING_VALUES = [i / 2 for i in range(1, 11)]  # 0.5 ... 5.0
GENRES = ["Action", "Animation", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller"]
