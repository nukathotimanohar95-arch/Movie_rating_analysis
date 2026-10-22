"""Movie Ratings Analysis and Basic Recommendation System (Flask).

Privacy rule: pages and APIs show aggregates (averages, counts) only. A person can see
their own ratings only after logging in; nobody can see another user's ratings.
"""
import secrets
from datetime import datetime

from flask import (Flask, Response, abort, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

import analysis as an
import charts
import recommender as rec
from config import GENRES, MIN_RATING_COUNT, MIN_USER_RATINGS, RATING_VALUES, SECRET_KEY
from db import create_tables, engine, movies, ratings, users

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
create_tables()


# ---------------------------------------------------------------- helpers
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    with engine.connect() as conn:
        row = conn.execute(select(users.c.user_id, users.c.display_name)
                           .where(users.c.user_id == uid)).first()
    if row is None:
        session.pop("user_id", None)
        return None
    return {"user_id": row.user_id, "display_name": row.display_name or f"User {row.user_id}"}


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warn")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def parse_rating(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if v in RATING_VALUES else None


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get("_csrf")
        if not token or token != request.form.get("_csrf"):
            abort(400, "Invalid or missing form token. Reload the page and try again.")


@app.context_processor
def inject_globals():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return {"csrf_token": session["_csrf"], "me": current_user(),
            "MIN_RATING_COUNT": MIN_RATING_COUNT, "RATING_VALUES": RATING_VALUES,
            "GENRES": GENRES, "MIN_USER_RATINGS": MIN_USER_RATINGS}


@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(err):
    return render_template("error.html", err=err), err.code


# ---------------------------------------------------------------- pages
@app.route("/")
def index():
    m, r, u = an.load_data()
    stats = an.movie_stats(m, r)
    totals = {"movies": len(m), "users": len(u), "ratings": len(r),
              "avg": round(float(r["rating"].mean()), 2) if len(r) else None}
    return render_template("index.html", totals=totals,
                           top=an.records(an.top_rated(stats, 5)),
                           genres=an.records(an.genre_analysis(m, r, stats).head(4)))


@app.route("/movies")
def movie_list():
    m, r, _ = an.load_data()
    df = an.movie_stats(m, r)
    genre, q, sort = request.args.get("genre", ""), request.args.get("q", "").strip(), request.args.get("sort", "title")
    if genre in GENRES:
        df = df[df["genre"] == genre]
    if q:
        df = df[df["title"].str.contains(q, case=False, regex=False)]
    order = {"title": ("title", True), "rating": ("avg_rating", False),
             "count": ("rating_count", False), "year": ("release_year", False)}
    col, asc = order.get(sort, order["title"])
    df = df.sort_values(col, ascending=asc)
    return render_template("movies.html", movies=an.records(df), genre=genre, q=q, sort=sort)


@app.route("/movies/new", methods=["GET", "POST"])
@login_required
def movie_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "")
        try:
            year = int(request.form.get("release_year", ""))
        except ValueError:
            year = 0
        if not title or len(title) > 200 or genre not in GENRES or not 1888 <= year <= datetime.now().year + 2:
            flash("Enter a title, a valid year and a genre.", "error")
        else:
            try:
                with engine.begin() as conn:
                    res = conn.execute(insert(movies).values(title=title, release_year=year, genre=genre))
                flash("Movie added.", "ok")
                return redirect(url_for("movie_detail", movie_id=res.inserted_primary_key[0]))
            except IntegrityError:
                flash("That movie (same title and year) already exists.", "error")
    return render_template("movie_form.html")


@app.route("/movies/<int:movie_id>")
def movie_detail(movie_id):
    m, r, _ = an.load_data()
    stats = an.movie_stats(m, r)
    row = stats[stats["movie_id"] == movie_id]
    if row.empty:
        abort(404)
    dist = an.distribution(r[r["movie_id"] == movie_id])
    peak = max(int(dist["count"].max()), 1)
    bars = [{"rating": f"{x.rating:g}", "count": int(x.count), "pct": round(100 * x.count / peak)}
            for x in dist.itertuples()]
    my_rating = None
    if session.get("user_id"):
        mine = r[(r["user_id"] == session["user_id"]) & (r["movie_id"] == movie_id)]
        if not mine.empty:
            my_rating = float(mine.iloc[0]["rating"])
    return render_template("movie.html", movie=an.records(row)[0], bars=bars, my_rating=my_rating,
                           similar=rec.similar_movies(r, stats, movie_id, 5))


@app.route("/movies/<int:movie_id>/rate", methods=["POST"])
@login_required
def rate(movie_id):
    value = parse_rating(request.form.get("rating"))
    if value is None:
        flash("Choose a rating from 0.5 to 5.", "error")
        return redirect(url_for("movie_detail", movie_id=movie_id))
    uid = session["user_id"]
    with engine.begin() as conn:
        if conn.execute(select(movies.c.movie_id).where(movies.c.movie_id == movie_id)).first() is None:
            abort(404)
        existing = conn.execute(select(ratings.c.rating_id).where(
            (ratings.c.user_id == uid) & (ratings.c.movie_id == movie_id))).first()
        if existing:
            conn.execute(update(ratings).where(ratings.c.rating_id == existing.rating_id)
                         .values(rating=value, rated_at=datetime.utcnow()))
        else:
            conn.execute(insert(ratings).values(user_id=uid, movie_id=movie_id, rating=value,
                                                rated_at=datetime.utcnow()))
    flash("Your rating was saved.", "ok")
    return redirect(url_for("movie_detail", movie_id=movie_id))


@app.route("/top-rated")
def top_rated_page():
    m, r, _ = an.load_data()
    stats = an.movie_stats(m, r)
    genre = request.args.get("genre", "")
    top = an.top_rated(stats, 15, genre if genre in GENRES else None)
    below = stats[~stats["qualifies"]].sort_values("rating_count", ascending=False)
    return render_template("top.html", top=an.records(top), genre=genre,
                           below=len(below), total=len(stats))


@app.route("/genres")
def genres_page():
    m, r, _ = an.load_data()
    stats = an.movie_stats(m, r)
    return render_template("genres.html", genres=an.records(an.genre_analysis(m, r, stats)))


@app.route("/distribution")
def distribution_page():
    _, r, _ = an.load_data()
    d = an.distribution(r)
    return render_template("distribution.html", stats=an.rating_stats(r), dist=an.records(d))


@app.route("/recommendations")
def recommendations():
    m, r, _ = an.load_data()
    stats = an.movie_stats(m, r)
    uid = session.get("user_id")
    personal, note = ([], None)
    if uid:
        personal, note = rec.recommend_for_user(r, stats, uid, 5)
        already = set(r[r["user_id"] == uid]["movie_id"])
    else:
        already = set()
    return render_template("recommendations.html", personal=personal, note=note,
                           popular=rec.popular(stats, 5, already))


@app.route("/my-ratings")
@login_required
def my_ratings():
    uid = session["user_id"]  # only ever the logged-in user's own rows
    with engine.connect() as conn:
        rows = conn.execute(
            select(movies.c.movie_id, movies.c.title, movies.c.genre, ratings.c.rating, ratings.c.rated_at)
            .join(ratings, ratings.c.movie_id == movies.c.movie_id)
            .where(ratings.c.user_id == uid).order_by(ratings.c.rated_at.desc())).all()
    return render_template("my_ratings.html", rows=rows)


@app.route("/my-ratings/<int:movie_id>/delete", methods=["POST"])
@login_required
def delete_rating(movie_id):
    with engine.begin() as conn:
        conn.execute(delete(ratings).where((ratings.c.user_id == session["user_id"])
                                           & (ratings.c.movie_id == movie_id)))
    flash("Rating removed.", "ok")
    return redirect(url_for("my_ratings"))


@app.route("/about")
def about():
    return render_template("about.html")


# ---------------------------------------------------------------- accounts
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("display_name", "").strip()
        pw = request.form.get("password", "")
        if not (2 <= len(name) <= 50) or len(pw) < 6:
            flash("Name must be 2-50 characters and password at least 6.", "error")
        else:
            try:
                with engine.begin() as conn:
                    res = conn.execute(insert(users).values(
                        display_name=name, password_hash=generate_password_hash(pw)))
                session.clear()
                session["user_id"] = res.inserted_primary_key[0]
                flash("Account created. You are logged in.", "ok")
                return redirect(url_for("index"))
            except IntegrityError:
                flash("That display name is taken.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("display_name", "").strip()
        pw = request.form.get("password", "")
        with engine.connect() as conn:
            row = conn.execute(select(users).where(users.c.display_name == name)).first()
        if row is None or not row.password_hash or not check_password_hash(row.password_hash, pw):
            flash("Wrong name or password.", "error")
        else:
            session.clear()
            session["user_id"] = row.user_id
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("index"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.", "ok")
    return redirect(url_for("index"))


# ---------------------------------------------------------------- charts
def _png(data: bytes) -> Response:
    return Response(data, mimetype="image/png", headers={"Cache-Control": "no-cache"})


@app.route("/charts/genres.png")
def chart_genres():
    m, r, _ = an.load_data()
    return _png(charts.genre_chart(an.genre_analysis(m, r, an.movie_stats(m, r))))


@app.route("/charts/distribution.png")
def chart_distribution():
    _, r, _ = an.load_data()
    return _png(charts.distribution_chart(an.distribution(r)))


@app.route("/charts/top-rated.png")
def chart_top():
    m, r, _ = an.load_data()
    return _png(charts.top_chart(an.top_rated(an.movie_stats(m, r), 10)))


# ---------------------------------------------------------------- JSON API (aggregates only)
@app.route("/api/top-rated")
def api_top():
    m, r, _ = an.load_data()
    limit = min(request.args.get("limit", 10, type=int), 100)
    cols = ["movie_id", "title", "genre", "release_year", "avg_rating", "rating_count"]
    return jsonify({"min_rating_count": MIN_RATING_COUNT,
                    "movies": an.records(an.top_rated(an.movie_stats(m, r), limit)[cols])})


@app.route("/api/genres")
def api_genres():
    m, r, _ = an.load_data()
    return jsonify(an.records(an.genre_analysis(m, r, an.movie_stats(m, r))))


@app.route("/api/distribution")
def api_distribution():
    _, r, _ = an.load_data()
    return jsonify({"distribution": an.records(an.distribution(r)), "summary": an.rating_stats(r)})


@app.route("/api/recommendations/popular")
def api_popular():
    m, r, _ = an.load_data()
    return jsonify(rec.popular(an.movie_stats(m, r), 5))


@app.route("/api/movies/<int:movie_id>/similar")
def api_similar(movie_id):
    m, r, _ = an.load_data()
    return jsonify(rec.similar_movies(r, an.movie_stats(m, r), movie_id, 5))


if __name__ == "__main__":
    app.run(debug=True)
