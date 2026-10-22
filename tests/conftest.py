import os
import tempfile

# Must be set before the app modules are imported.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["MIN_RATING_COUNT"] = "3"
os.environ["SECRET_KEY"] = "test"

import pytest  # noqa: E402

import init_db  # noqa: E402
from db import create_tables  # noqa: E402

create_tables()
init_db.seed()

from app import app as flask_app  # noqa: E402


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def post(client, url, data=None, follow=True):
    """POST with the CSRF token the site expects."""
    client.get("/about")  # makes sure a token exists in the session
    with client.session_transaction() as s:
        token = s["_csrf"]
    return client.post(url, data={**(data or {}), "_csrf": token}, follow_redirects=follow)
