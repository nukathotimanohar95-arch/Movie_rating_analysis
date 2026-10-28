
"""Central settings for the Movie Rating Analysis System."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent

# Connect to the existing MySQL database.
# Configure DATABASE_URL in your .env file.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'movie_ratings.db'}",
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

# A movie must have at least this many ratings to qualify for ranking.
MIN_RATING_COUNT = int(os.getenv("MIN_RATING_COUNT", "3"))

# Minimum personal ratings needed for personalised recommendations.
MIN_USER_RATINGS = 3

# Minimum number of common raters for movie similarity.
MIN_OVERLAP = 2

# Allowed ratings: 0.5, 1.0, 1.5, ..., 5.0.
RATING_VALUES = [i / 2 for i in range(1, 11)]

# The application will load actual genre names from MySQL.
# This list is retained temporarily for compatibility with existing pages.
GENRES = [
    "Action",
    "Animation",
    "Comedy",
    "Drama",
    "Horror",
    "Romance",
    "Sci-Fi",
    "Thriller",
]
