import pytest
from flask import Flask
from driver import create_app
from extensions import db as _db
from models.user import Users
from models.magnet import MagnetURL
from services.auth import _generate_secret, _store_secret, _fetch_secret_from_api
from api.views import generate_rtmp_url, verify_secret
from flask import jsonify

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
def db_session(app):
    with app.app_context():
        yield _db.session
        _db.session.rollback()

# Helper function to simulate the /generate_secret logic
def manual_generate_secret(eth_address, ip_address):
    secret = _generate_secret()
    _store_secret(eth_address, secret, ip_address)
    return secret

def test_generate_secret(db_session):
    secret = manual_generate_secret("0xTEST", "127.0.0.1")
    assert isinstance(secret, str)
    assert len(secret) == 16

def test_get_secret(db_session):
    eth = "0xSECRET"
    ip = "127.0.0.1"
    secret = manual_generate_secret(eth, ip)

    user = Users.query.filter_by(eth_address=eth).first()
    assert user is not None
    assert user.rtmp_secret == secret

def test_get_rtmp_url(db_session):
    eth = "0xRTMP"
    ip = "127.0.0.1"
    secret = manual_generate_secret(eth, ip)

    rtmp_url = f"rtmp://stream.server/live/eth_address={eth}&secret={secret}"
    assert eth in rtmp_url
    assert secret in rtmp_url

def test_store_and_get_magnet_url(db_session):
    from models.magnet import MagnetURL

    eth = "0xMAG"
    manual_generate_secret(eth, "127.0.0.1")

    magnet_url = "magnet:?xt=urn:btih:123"
    entry = MagnetURL(eth_address=eth, magnet_url=magnet_url, snapshot_index=0)
    _db.session.add(entry)
    _db.session.commit()

    entries = MagnetURL.query.filter_by(eth_address=eth).all()
    assert len(entries) == 1
    assert entries[0].magnet_url == magnet_url

def test_clear_magnet_urls(db_session):
    from models.magnet import MagnetURL

    eth = "0xCLEAR"
    manual_generate_secret(eth, "127.0.0.1")

    entry = MagnetURL(eth_address=eth, magnet_url="magnet:?xt=urn:btih:clear", snapshot_index=1)
    _db.session.add(entry)
    _db.session.commit()

    MagnetURL.query.filter_by(eth_address=eth).delete()
    _db.session.commit()

    remaining = MagnetURL.query.filter_by(eth_address=eth).all()
    assert len(remaining) == 0

def test_verify_secret_success(db_session):
    eth = "0xVERIFY"
    ip = "127.0.0.1"
    secret = manual_generate_secret(eth, ip)

    fetched_secret = _fetch_secret_from_api(eth)
    assert fetched_secret == secret

def test_verify_secret_failure(db_session):
    eth = "0xFAIL"
    manual_generate_secret(eth, "127.0.0.1")

    fetched_secret = _fetch_secret_from_api(eth)
    assert fetched_secret != "wrongsecret"
