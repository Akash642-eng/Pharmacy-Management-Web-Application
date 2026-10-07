import pytest


def test_app_starts(app):
    assert app is not None
    assert app.name == "app"


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/login-page",
        "/register-page",
    ],
)
def test_public_pages(client, url):
    response = client.get(url)

    assert response.status_code == 200


def test_admin_requires_authentication(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/login-page" in response.headers["Location"]


def test_database_is_available(app):
    from sqlalchemy import text

    from app.extensions import db

    with app.app_context():
        result = db.session.execute(text("SELECT 1")).scalar()

        assert result == 1
