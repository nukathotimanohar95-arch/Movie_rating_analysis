# Movie Ratings Analysis and Basic Recommendation System

Flask + MySQL + Pandas/NumPy/Matplotlib project that analyzes movie ratings and
genre preferences and produces simple, explainable recommendations.

> Recommendations are educational suggestions based on available ratings, not
> claims of guaranteed preference.

## Documented rules
- **Minimum rating count:** a movie appears in top-rated lists and popularity
  recommendations only if it has at least `MIN_RATING_COUNT` ratings
  (default **3**, set in `.env`).
- **Privacy:** public endpoints return aggregates only. Users never see other
  users' individual ratings. `display_name` is optional; no email or real name is stored.
- **Explainability:** every recommendation includes a `reason` field.

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit DB credentials
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
flask --app app run --debug
```

## Database schema
| Table | Columns |
|---|---|
| movies | movie_id, title, release_year, genre |
| users | user_id, display_name (optional) |
| ratings | rating_id, user_id, movie_id, rating (0.5-5.0), rated_at; unique (user_id, movie_id) |
| genres / movie_genres | optional multi-genre support for similarity |
| movie_stats (view) | per-movie rating_count and avg_rating, no user data |

## Flask URLs
| Method | URL | Purpose |
|---|---|---|
| GET | `/` | Home page |
| GET | `/movies` | All movies with avg rating and count |
| POST | `/movies` | Add a movie |
| GET | `/movies/<id>` | Movie aggregate stats |
| POST | `/users` | Create user (display name optional) |
| POST | `/ratings` | Add or update a rating |
| GET | `/users/<id>/ratings` | A user's own ratings (needs auth, TODO) |
| GET | `/analysis/top-rated?limit=&min_count=` | Top-rated with minimum-count rule |
| GET | `/analysis/genres` | Genre comparison |
| GET | `/analysis/distribution` | Rating distribution |
| GET | `/analysis/stats` | NumPy/Pandas statistics |
| GET | `/charts/genres.png` | Genre chart (TODO) |
| GET | `/charts/distribution.png` | Distribution chart (TODO) |
| GET | `/recommendations/popular` | Popularity-based recommendations |
| GET | `/recommendations/user/<id>` | Similarity-based, optional (TODO) |
| GET | `/recommendations/similar/<movie_id>` | Similar movies, optional (TODO) |

## Roadmap
1. Schema + seed data (done)
2. Core routes and aggregation (done)
3. Matplotlib charts
4. Simple authentication for per-user data
5. Similarity recommender (scikit-learn cosine similarity)
6. Tests
