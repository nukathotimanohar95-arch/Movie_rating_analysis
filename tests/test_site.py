import pytest

from conftest import post

PAGES = ["/", "/movies", "/movies/1", "/top-rated", "/genres", "/distribution",
         "/recommendations", "/about", "/login", "/register",
         "/charts/genres.png", "/charts/distribution.png", "/charts/top-rated.png",
         "/api/top-rated", "/api/genres", "/api/distribution",
         "/api/recommendations/popular", "/api/movies/1/similar"]


@pytest.mark.parametrize("url", PAGES)
def test_pages_load(client, url):
    assert client.get(url).status_code == 200


def test_minimum_rating_count_rule(client):
    data = client.get("/api/top-rated?limit=100").get_json()
    assert data["min_rating_count"] == 3
    assert data["movies"], "seed data should produce ranked movies"
    assert all(m["rating_count"] >= 3 for m in data["movies"])


def test_public_api_has_no_user_level_data(client):
    for url in ["/api/top-rated", "/api/genres", "/api/distribution", "/api/recommendations/popular"]:
        text = client.get(url).get_data(as_text=True)
        assert "user_id" not in text and "viewer" not in text


def test_my_ratings_requires_login(client):
    resp = client.get("/my-ratings")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_cannot_log_in_as_seed_user(client):
    resp = post(client, "/login", {"display_name": "viewer01", "password": "anything"})
    assert b"Wrong name or password" in resp.data


def test_users_only_see_their_own_ratings(client):
    from app import app
    alice, bob = app.test_client(), app.test_client()
    post(alice, "/register", {"display_name": "alice", "password": "secret1"})
    post(bob, "/register", {"display_name": "bob", "password": "secret2"})
    post(alice, "/movies/1/rate", {"rating": "1.5"})
    post(bob, "/movies/2/rate", {"rating": "4.5"})
    alice_page = alice.get("/my-ratings").get_data(as_text=True)
    bob_page = bob.get("/my-ratings").get_data(as_text=True)
    assert "The Shawshank Redemption" in alice_page and "Forrest Gump" not in alice_page
    assert "Forrest Gump" in bob_page and "The Shawshank Redemption" not in bob_page


def test_post_without_csrf_token_is_rejected(client):
    assert client.post("/logout").status_code == 400


def test_recommendations_are_explained(client):
    from app import app
    c = app.test_client()
    post(c, "/register", {"display_name": "carol", "password": "secret3"})
    for movie_id, value in [(1, "5"), (7, "4.5"), (13, "4"), (25, "5")]:
        post(c, f"/movies/{movie_id}/rate", {"rating": value})
    html = c.get("/recommendations").get_data(as_text=True)
    assert "For you" in html and 'class="why"' in html
    from analysis import load_data, movie_stats
    import recommender
    m, r, _ = load_data()
    uid = r[r["user_id"] == r["user_id"].max()]["user_id"].iloc[0]
    recs, _ = recommender.recommend_for_user(r, movie_stats(m, r), int(uid), 5)
    assert recs and all(x["reason"] for x in recs)
    assert all(x["rating_count"] >= 3 for x in recs)


def test_invalid_rating_rejected(client):
    from app import app
    c = app.test_client()
    post(c, "/register", {"display_name": "dave", "password": "secret4"})
    resp = post(c, "/movies/1/rate", {"rating": "9"})
    assert b"Choose a rating" in resp.data
