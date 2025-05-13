import pytest
from driver import create_app
from extensions import db as _db
from models.user import Users
from models.magnet import MagnetURL

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://admin:admin@localhost:5432/rtmp_db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()



@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def test_generate_secret(client):
    data = {"eth_address": "0xTEST", "ip_address": "127.0.0.1"}
    response = client.post("/generate_secret", json=data)
    assert response.status_code == 200
    assert "secret" in response.get_json()


def test_get_secret(client):
    data = {"eth_address": "0xSECRET", "ip_address": "127.0.0.1"}
    client.post("/generate_secret", json=data)

    response = client.get("/get_secret/0xSECRET")
    assert response.status_code == 200
    assert response.get_json()["eth_address"] == "0xSECRET"


def test_get_rtmp_url(client):
    data = {"eth_address": "0xRTMP", "ip_address": "127.0.0.1"}
    res = client.post("/generate_secret", json=data)
    secret = res.get_json()["secret"]

    response = client.get("/get_rtmp_url/0xRTMP")
    assert response.status_code == 200
    assert secret in response.get_json()["rtmp_url"]


def test_store_and_get_magnet_url(client):
    client.post("/generate_secret", json={"eth_address": "0xMAG", "ip_address": "127.0.0.1"})

    magnet_data = {
        "eth_address": "0xMAG",
        "magnet_url": "magnet:?xt=urn:btih:123",
        "snapshot_index": 0
    }
    store_res = client.post("/store_magnet_url", json=magnet_data)
    assert store_res.status_code == 200

    get_res = client.get("/get_magnet_urls/0xMAG")
    assert get_res.status_code == 200
    assert len(get_res.get_json()["magnet_urls"]) == 1


def test_clear_magnet_urls(client):
    eth = "0xCLEAR"
    client.post("/generate_secret", json={"eth_address": eth, "ip_address": "127.0.0.1"})
    client.post("/store_magnet_url", json={
        "eth_address": eth,
        "magnet_url": "magnet:?xt=urn:btih:clear",
        "snapshot_index": 1
    })

    res = client.delete(f"/clear_magnet_urls/{eth}")
    assert res.status_code == 200


def test_verify_secret_success(client):
    eth = "0xVERIFY"
    ip = "127.0.0.1"
    secret = client.post("/generate_secret", json={"eth_address": eth, "ip_address": ip}).get_json()["secret"]

    verify_res = client.post("/verify_secret", json={"eth_address": eth, "secret": secret})
    assert verify_res.status_code == 204


def test_verify_secret_failure(client):
    eth = "0xFAIL"
    client.post("/generate_secret", json={"eth_address": eth, "ip_address": "127.0.0.1"})

    verify_res = client.post("/verify_secret", json={"eth_address": eth, "secret": "wrongsecret"})
    assert verify_res.status_code == 403
