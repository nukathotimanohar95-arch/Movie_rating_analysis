# CineStats: Movie Ratings Analysis and Basic Recommendation System

A Flask website that stores movie ratings, analyses them (Pandas, NumPy, Matplotlib) and
gives explainable recommendations. Uses MySQL (or SQLite for a zero-setup start).

> Recommendations are educational suggestions based on available ratings, not guarantees of preference.

## Run it (PyCharm or terminal)
```bash
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python init_db.py                # creates tables + sample data (SQLite by default)
python app.py                    # open http://127.0.0.1:5000
```
Run the tests with `python -m pytest`.

### Use MySQL instead of SQLite
1. In MySQL: `CREATE DATABASE movie_ratings CHARACTER SET utf8mb4;`
2. Copy `.env.example` to `.env` and set `DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/movie_ratings?charset=utf8mb4`
3. Run `python init_db.py` (use `--reset` to wipe and reseed), then `python app.py`.

(`database/schema.sql` is the same schema as plain SQL, if you prefer to run it yourself.)

## Documented rules (acceptance criteria)
- **Minimum rating count:** a movie is ranked or recommended by popularity only with at least
  `MIN_RATING_COUNT` ratings (default **3**, set in `.env`). Shown on the Top rated, About and footer.
- **Privacy:** pages and APIs show only averages and counts. A person sees their own ratings only after
  logging in (display name + password hash; no email or real name stored). Nobody can see another user's ratings.
  Sample users have no password, so nobody can log in as them.
- **Explainable recommendations:** every result has a plain-language reason. Personalised reasons cite
  only the viewer's own ratings plus aggregate similarity.

## Pages and URLs
| URL | Purpose |
|---|---|
| `/` | Dashboard: totals, top 5, best genres |
| `/movies`, `/movies/<id>`, `/movies/new` | Browse, detail (aggregate stats + similar movies), add a movie |
| `/movies/<id>/rate` (POST) | Rate a movie (login required) |
| `/top-rated` | Ranking with minimum-count rule, genre filter, chart |
| `/genres` | Genre comparison + chart |
| `/distribution` | Rating histogram + NumPy statistics |
| `/recommendations` | Personalised (similarity) and popularity-based suggestions |
| `/my-ratings` | Your own ratings only (login required) |
| `/register`, `/login`, `/logout` | Accounts |
| `/about` | Rules and method |
| `/charts/genres.png`, `/charts/distribution.png`, `/charts/top-rated.png` | Matplotlib charts |
| `/api/top-rated`, `/api/genres`, `/api/distribution`, `/api/recommendations/popular`, `/api/movies/<id>/similar` | JSON, aggregates only |

## How recommendations work
- **Popularity:** highest average rating among movies meeting the minimum count, excluding ones you rated.
- **Similarity (item-item):** movies are similar when people who rated both score them alike relative to their
  own average (adjusted cosine similarity in NumPy; at least 2 common raters). A movie is suggested because it is
  similar to movies you rated highly. You need 3 ratings of your own, otherwise you see popular movies.

## Project layout
`app.py` routes · `db.py` tables · `analysis.py` Pandas/NumPy · `recommender.py` · `charts.py` Matplotlib ·
`init_db.py` schema + sample data · `templates/` · `static/` · `tests/`

The starter data is synthetic (fixed random seed) for demonstration.
