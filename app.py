
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from sqlalchemy import select, insert, update, delete, func

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from config import (
    MIN_RATING_COUNT,
    MIN_USER_RATINGS,
    RATING_VALUES,
    SECRET_KEY,
)

from db import engine, genres, movies, ratings, users

from analysis import get_movie_analysis, get_genre_analysis
from recommender import get_recommendations


app = Flask(__name__)
app.secret_key = SECRET_KEY


# -------------------------
# Login protection
# -------------------------

def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# -------------------------
# Home page with movie search
# -------------------------

@app.route("/")
@app.route("/home")
def home():
    search_text = request.args.get("q", "").strip()

    query = (
        select(
            movies.c.movie_id,
            movies.c.title,
            movies.c.release_year,
            genres.c.genre_name.label("genre"),
            func.round(
                func.avg(ratings.c.rating), 2
            ).label("overall_rating"),
            func.count(
                ratings.c.rating_id
            ).label("total_ratings"),
        )
        .select_from(
            movies.join(
                genres,
                movies.c.genre_id == genres.c.genre_id,
            ).outerjoin(
                ratings,
                movies.c.movie_id == ratings.c.movie_id,
            )
        )
    )

    if search_text:
        query = query.where(
            movies.c.title.ilike(f"%{search_text}%")
        )

    query = (
        query.group_by(
            movies.c.movie_id,
            movies.c.title,
            movies.c.release_year,
            genres.c.genre_name,
        )
        .order_by(movies.c.title)
    )

    with engine.connect() as connection:
        movie_list = [
            dict(row)
            for row in connection.execute(
                query
            ).mappings().all()
        ]

    # Use the template file you provided: home.html
    return render_template(
        "index.html",
        movies=movie_list,
        search_text=search_text,
    )


# -------------------------
# Movie details page
# -------------------------

@app.route("/movies/<int:movie_id>")
def movie_detail(movie_id):
    query = (
        select(
            movies.c.movie_id,
            movies.c.title,
            movies.c.release_year,
            genres.c.genre_name.label("genre"),
            func.round(
                func.avg(ratings.c.rating), 2
            ).label("overall_rating"),
            func.count(
                ratings.c.rating_id
            ).label("total_ratings"),
        )
        .select_from(
            movies.join(
                genres,
                movies.c.genre_id == genres.c.genre_id,
            ).outerjoin(
                ratings,
                movies.c.movie_id == ratings.c.movie_id,
            )
        )
        .where(movies.c.movie_id == movie_id)
        .group_by(
            movies.c.movie_id,
            movies.c.title,
            movies.c.release_year,
            genres.c.genre_name,
        )
    )

    with engine.connect() as connection:
        movie = connection.execute(
            query
        ).mappings().first()

    if not movie:
        flash("Movie not found.", "error")
        return redirect(url_for("home"))

    return render_template(
        "movie_detail.html",
        movie=movie,
    )


# -------------------------
# Register
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        display_name = request.form.get(
            "display_name", ""
        ).strip()

        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not display_name or not password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error",
            )
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        try:
            with engine.begin() as connection:
                existing_user = connection.execute(
                    select(users.c.user_id).where(
                        users.c.display_name == display_name
                    )
                ).first()

                if existing_user:
                    flash(
                        "That display name is already registered.",
                        "error",
                    )
                    return render_template("register.html")

                result = connection.execute(
                    insert(users).values(
                        display_name=display_name,
                        password_hash=generate_password_hash(password),
                    )
                )

                user_id = result.inserted_primary_key[0]

            session["user_id"] = user_id
            session["display_name"] = display_name

            flash("Registration successful!", "success")
            return redirect(url_for("home"))

        except Exception:
            app.logger.exception("Registration failed")
            flash(
                "Registration failed. Please check the application and database.",
                "error",
            )

    return render_template("register.html")


# -------------------------
# Login
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        display_name = request.form.get(
            "display_name", ""
        ).strip()

        password = request.form.get("password", "")

        with engine.connect() as connection:
            user = connection.execute(
                select(users).where(
                    users.c.display_name == display_name
                )
            ).mappings().first()

        if (
            user
            and user["password_hash"]
            and check_password_hash(
                user["password_hash"], password
            )
        ):
            session.clear()
            session["user_id"] = user["user_id"]
            session["display_name"] = user["display_name"]

            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid display name or password.", "error")

    return render_template("login.html")


# -------------------------
# Logout
# -------------------------

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("home"))


# -------------------------
# Add a movie
# -------------------------

@app.route("/movies/new", methods=["GET", "POST"])
@login_required
def add_movie():
    if request.method == "POST":
        title = request.form.get("title", "").strip()

        release_year_text = request.form.get(
            "release_year", ""
        ).strip()

        genre_id_text = request.form.get(
            "genre_id", ""
        ).strip()

        if not title or not genre_id_text:
            flash(
                "Movie title and genre are required.",
                "error",
            )
        else:
            try:
                release_year = (
                    int(release_year_text)
                    if release_year_text
                    else None
                )

                genre_id = int(genre_id_text)

                with engine.begin() as connection:
                    genre_exists = connection.execute(
                        select(genres.c.genre_id).where(
                            genres.c.genre_id == genre_id
                        )
                    ).first()

                    if not genre_exists:
                        flash(
                            "Please select a valid genre.",
                            "error",
                        )
                        return redirect(url_for("add_movie"))

                    connection.execute(
                        insert(movies).values(
                            title=title,
                            release_year=release_year,
                            genre_id=genre_id,
                        )
                    )

                flash("Movie added successfully!", "success")
                return redirect(url_for("home"))

            except ValueError:
                flash(
                    "Release year and genre must be valid numbers.",
                    "error",
                )

            except Exception:
                app.logger.exception("Adding movie failed")
                flash("Could not add the movie.", "error")

    with engine.connect() as connection:
        genre_list = connection.execute(
            select(genres).order_by(genres.c.genre_name)
        ).mappings().all()

    return render_template(
        "movie_form.html",
        genres=genre_list,
    )


# -------------------------
# Rate a movie
# -------------------------

@app.route(
    "/movies/<int:movie_id>/rate",
    methods=["GET", "POST"],
)
@login_required
def rate_movie(movie_id):
    with engine.connect() as connection:
        movie = connection.execute(
            select(
                movies.c.movie_id,
                movies.c.title,
            ).where(movies.c.movie_id == movie_id)
        ).mappings().first()

    if not movie:
        flash("Movie not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        try:
            rating_value = float(
                request.form.get("rating", "")
            )

            if rating_value not in RATING_VALUES:
                flash(
                    "Choose a rating from 0.5 to 5.0 in 0.5 steps.",
                    "error",
                )
                return render_template(
                    "rate_movie.html",
                    movie=movie,
                )

            user_id = session["user_id"]

            with engine.begin() as connection:
                existing_rating = connection.execute(
                    select(ratings.c.rating_id).where(
                        ratings.c.user_id == user_id,
                        ratings.c.movie_id == movie_id,
                    )
                ).first()

                if existing_rating:
                    connection.execute(
                        update(ratings)
                        .where(
                            ratings.c.rating_id == existing_rating[0]
                        )
                        .values(rating=rating_value)
                    )

                    flash(
                        "Your rating has been updated.",
                        "success",
                    )

                else:
                    connection.execute(
                        insert(ratings).values(
                            user_id=user_id,
                            movie_id=movie_id,
                            rating=rating_value,
                        )
                    )

                    flash(
                        "Your rating has been saved.",
                        "success",
                    )

            return redirect(
                url_for("movie_detail", movie_id=movie_id)
            )

        except ValueError:
            flash("Please enter a valid rating.", "error")

        except Exception:
            app.logger.exception("Saving rating failed")
            flash("Could not save your rating.", "error")

    return render_template(
        "rate_movie.html",
        movie=movie,
    )


# -------------------------
# My ratings
# -------------------------

@app.route("/my-ratings")
@login_required
def my_ratings():
    query = (
        select(
            ratings.c.rating_id,
            ratings.c.rating,
            ratings.c.rated_at,
            movies.c.movie_id,
            movies.c.title,
            genres.c.genre_name.label("genre"),
        )
        .select_from(
            ratings.join(
                movies,
                ratings.c.movie_id == movies.c.movie_id,
            ).join(
                genres,
                movies.c.genre_id == genres.c.genre_id,
            )
        )
        .where(
            ratings.c.user_id == session["user_id"]
        )
        .order_by(movies.c.title)
    )

    with engine.connect() as connection:
        rating_list = [
            dict(row)
            for row in connection.execute(
                query
            ).mappings().all()
        ]

    return render_template(
        "my_ratings.html",
        ratings=rating_list,
        rows=rating_list,
    )


# -------------------------
# Delete one of my ratings
# -------------------------

@app.route(
    "/ratings/<int:rating_id>/delete",
    methods=["POST"],
)
@login_required
def delete_rating(rating_id):
    with engine.begin() as connection:
        connection.execute(
            delete(ratings).where(
                ratings.c.rating_id == rating_id,
                ratings.c.user_id == session["user_id"],
            )
        )

    flash(
        "Your rating has been deleted if it belonged to your account.",
        "success",
    )

    return redirect(url_for("my_ratings"))


# -------------------------
# Movie and genre analysis
# -------------------------

@app.route("/analysis")
def analysis_page():
    movie_analysis = get_movie_analysis()
    genre_analysis = get_genre_analysis()

    return render_template(
        "analysis.html",
        movie_analysis=movie_analysis,
        genre_analysis=genre_analysis,
        minimum_ratings=MIN_RATING_COUNT,
    )


# -------------------------
# Recommendations
# Public access for all visitors
# -------------------------

@app.route("/recommendations")
def recommendations_page():
    # Logged-in users receive personalized recommendations.
    if session.get("user_id"):
        recommendations = get_recommendations(session["user_id"])

    # Visitors who are not logged in see popular movies.
    else:
        query = (
            select(
                movies.c.movie_id,
                movies.c.title,
                movies.c.release_year,
                genres.c.genre_name.label("genre"),
                func.round(
                    func.avg(ratings.c.rating), 2
                ).label("overall_rating"),
                func.count(
                    ratings.c.rating_id
                ).label("total_ratings"),
            )
            .select_from(
                movies.join(
                    genres,
                    movies.c.genre_id == genres.c.genre_id,
                ).outerjoin(
                    ratings,
                    movies.c.movie_id == ratings.c.movie_id,
                )
            )
            .group_by(
                movies.c.movie_id,
                movies.c.title,
                movies.c.release_year,
                genres.c.genre_name,
            )
            .having(
                func.count(ratings.c.rating_id) >= MIN_RATING_COUNT
            )
            .order_by(
                func.avg(ratings.c.rating).desc(),
                func.count(ratings.c.rating_id).desc(),
                movies.c.title,
            )
            .limit(12)
        )

        with engine.connect() as connection:
            recommendations = [
                dict(row)
                for row in connection.execute(
                    query
                ).mappings().all()
            ]

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        minimum_ratings=MIN_RATING_COUNT,
        minimum_user_ratings=MIN_USER_RATINGS,
    )


# -------------------------
# Run the Flask application
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
