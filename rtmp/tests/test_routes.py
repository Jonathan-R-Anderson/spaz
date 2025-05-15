import sys
import os
import pytest
from unittest.mock import patch
from flask import Flask

# Ensure the app root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.routes import blueprint


@pytest.fixture
def client():
    with patch("api.routes.retrieve_magnet_urls") as mock_retrieve:
        mock_retrieve.return_value = {"message": "error"}  # default fallback

        app = Flask(__name__)
        app.register_blueprint(blueprint)
        app.config['TESTING'] = True

        with app.test_client() as client:
            yield client



@patch("api.routes.retrieve_magnet_urls")
def test_magnet_url_success(mock_retrieve, client):
    mock_retrieve.return_value = {
        "message": "success",
        "magnet_urls": ["magnet:?xt=test"]
    }
    response = client.get("/magnet_urls/0xtest")
    assert response.status_code == 200
    assert "magnet_urls" in response.json

@patch("api.routes.requests.post")
@patch("api.routes.retrieve_magnet_urls", return_value=None)
def test_magnet_url_monitoring(mock_retrieve, mock_post, client):
    # Ensure that both calls to /start_static_monitor and /start_hls_monitor succeed
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = "ok"

    response = client.get("/magnet_urls/0xtest")
    assert response.status_code == 404
    assert "error" in response.json


def test_seed_file_invalid_eth(client):
    response = client.post('/seed', data={})
    assert response.status_code == 400


def test_seed_file_missing_file(client):
    data = {'eth_address': '0xtest'}
    response = client.post('/seed', data=data)
    assert response.status_code == 400


@patch("utils.shared.requests.post")
@patch("utils.shared.requests.get")
def test_verify_secret_success(mock_get, mock_post, client):
    mock_post.return_value.status_code = 200
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'secret': 'abc123'}

    response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
    assert response.status_code == 204


@patch("utils.shared.requests.post")
def test_verify_secret_fail_store(mock_post, client):
    mock_post.return_value.status_code = 500
    response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
    assert response.status_code == 403


@patch("utils.shared.requests.post")
@patch("utils.shared.requests.get")
def test_verify_secret_fail_lookup(mock_get, mock_post, client):
    mock_post.return_value.status_code = 200
    mock_get.return_value.status_code = 403
    response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
    assert response.status_code == 403
