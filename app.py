"""Flask app for Movie Ratings Analysis and Basic Recommendation System.

URL map (this is the starting skeleton; handlers marked TODO come next).
"""
import os
from flask import Flask, jsonify, request, render_template, abort
import pymysql
import pandas as pd

MIN_RATING_COUNT = int(os.getenv("MIN_RATING_COUNT", 3))  # documented rule

app = Flask(__name__)


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "movie_ratings"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def query(sql, params=None):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


# ---------- Pages ----------
@app.route("/")
def index():
    return render_template("index.html", min_count=MIN_RATING_COUNT)


# ---------- Movies ----------
@app.route("/movies", methods=["GET"])
def list_movies():
    return jsonify(query("SELECT * FROM movie_stats ORDER BY title"))


@app.route("/movies", methods=["POST"])
def add_movie():
    d = request.get_json(force=True)
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO movies (title, release_year, genre) VALUES (%s,%s,%s)",
                (d["title"], d["release_year"], d["genre"]))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"status": "created"}), 201


@app.route("/movies/<int:movie_id>")
def movie_detail(movie_id):
    rows = query("SELECT * FROM movie_stats WHERE movie_id=%s", (movie_id,))
    if not rows:
        abort(404)
    return jsonify(rows[0])  # aggregate only, no per-user data


# ---------- Users & ratings ----------
@app.route("/users", methods=["POST"])
def add_user():
    d = request.get_json(silent=True) or {}
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (display_name) VALUES (%s)",
                        (d.get("display_name"),))
            uid = cur.lastrowid
        conn.commit()
    finally:
        conn.close()
    return jsonify({"user_id": uid}), 201


@app.route("/ratings", methods=["POST"])
def add_rating():
    d = request.get_json(force=True)
    rating = float(d["rating"])
    if not 0.5 <= rating <= 5.0:
        abort(400, "rating must be between 0.5 and 5.0")
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s,%s,%s)
                   ON DUPLICATE KEY UPDATE rating=VALUES(rating), rated_at=NOW()""",
                (d["user_id"], d["movie_id"], rating))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"status": "saved"}), 201


@app.route("/users/<int:user_id>/ratings")
def my_ratings(user_id):
    # TODO: require authentication so a user only sees their OWN ratings
    return jsonify(query(
        """SELECT m.title, r.rating, r.rated_at FROM ratings r
           JOIN movies m ON m.movie_id=r.movie_id WHERE r.user_id=%s""", (user_id,)))


# ---------- Analysis ----------
@app.route("/analysis/top-rated")
def top_rated():
    limit = request.args.get("limit", 10, type=int)
    min_count = request.args.get("min_count", MIN_RATING_COUNT, type=int)
    return jsonify(query(
        """SELECT title, genre, rating_count, avg_rating FROM movie_stats
           WHERE rating_count >= %s ORDER BY avg_rating DESC, rating_count DESC LIMIT %s""",
        (min_count, limit)))


@app.route("/analysis/genres")
def genre_analysis():
    return jsonify(query(
        """SELECT genre, COUNT(DISTINCT movie_id) AS movies,
                  SUM(rating_count) AS total_ratings,
                  ROUND(SUM(avg_rating*rating_count)/NULLIF(SUM(rating_count),0),2) AS avg_rating
           FROM movie_stats GROUP BY genre ORDER BY avg_rating DESC"""))


@app.route("/analysis/distribution")
def rating_distribution():
    return jsonify(query(
        "SELECT rating, COUNT(*) AS count FROM ratings GROUP BY rating ORDER BY rating"))


@app.route("/analysis/stats")
def rating_stats():
    df = pd.DataFrame(query("SELECT rating FROM ratings"))
    s = df["rating"].astype(float)
    return jsonify({"count": int(s.count()), "mean": round(s.mean(), 2),
                    "median": float(s.median()), "std": round(s.std(), 2)})


# ---------- Charts (Matplotlib PNGs) ----------
@app.route("/charts/genres.png")
def chart_genres():
    # TODO: render bar chart of avg rating by genre with matplotlib
    abort(501)


@app.route("/charts/distribution.png")
def chart_distribution():
    # TODO: render rating histogram with matplotlib
    abort(501)


# ---------- Recommendations ----------
@app.route("/recommendations/popular")
def recommend_popular():
    """Popularity-based: highest avg rating with >= MIN_RATING_COUNT ratings."""
    rows = query(
        """SELECT title, genre, avg_rating, rating_count FROM movie_stats
           WHERE rating_count >= %s ORDER BY avg_rating DESC, rating_count DESC LIMIT 5""",
        (MIN_RATING_COUNT,))
    for r in rows:
        r["reason"] = (f"Average {r['avg_rating']} from {r['rating_count']} ratings "
                       f"(minimum {MIN_RATING_COUNT} required).")
    return jsonify(rows)


@app.route("/recommendations/user/<int:user_id>")
def recommend_for_user(user_id):
    """Optional similarity-based: TODO item-item cosine similarity.
    Each result must include a human-readable 'reason'."""
    abort(501)


@app.route("/recommendations/similar/<int:movie_id>")
def similar_movies(movie_id):
    """Optional: movies similar to this one (genre + co-rating similarity)."""
    abort(501)


if __name__ == "__main__":
    app.run(debug=True)
