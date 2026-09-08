import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True

    database = tmp_path / "test.db"

    import app as application
    application.DATABASE = str(database)

    init_db()

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Tool Sharing Platform" in response.data


def test_add_tool(client):
    response = client.post(
        "/add",
        data={
            "name": "Δοκιμαστικό Τρυπάνι",
            "description": "Τρυπάνι για testing"
        }
    )

    assert response.status_code == 200
    assert "Δοκιμαστικό Τρυπάνι".encode("utf-8") in response.data


def test_request_tool(client):
    response = client.post(
        "/request/1",
        data={
            "borrower": "Πάνος",
            "days": "3"
        }
    )

    assert response.status_code == 200
    assert "Το αίτημα υποβλήθηκε".encode("utf-8") in response.data