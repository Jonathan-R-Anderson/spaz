import sys
import os
import pytest
from unittest.mock import patch, Mock
from flask import Flask

# Allow importing 'api' from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.routes import blueprint


from unittest.mock import patch


@patch("utils.shared.retrieve_magnet_urls", return_value=None)
@patch("utils.shared.requests.post")
def test_magnet_url_monitoring(mock_post, mock_retrieve, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = "ok"

    response = client.get("/magnet_urls/0xtest")
    assert response.status_code == 404



@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_magnet_url_success(client):
    with patch("utils.shared.retrieve_magnet_urls") as mock_retrieve:
        mock_retrieve.return_value = {"message": "success", "magnet_urls": ["magnet:?xt=test"]}
        response = client.get('/magnet_urls/0xtest')
        assert response.status_code == 200
        assert "magnet_urls" in response.json

def test_magnet_url_monitoring(client):
    with patch("utils.shared.retrieve_magnet_urls", return_value={"message": "fail"}), \
         patch("utils.shared.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "started"
        response = client.get('/magnet_urls/0xtest')
        assert response.status_code == 404
        assert "error" in response.json

def test_seed_file_invalid_eth(client):
    response = client.post('/seed', data={})
    assert response.status_code == 400

def test_seed_file_missing_file(client):
    data = {'eth_address': '0xtest'}
    response = client.post('/seed', data=data)
    assert response.status_code == 400

def test_verify_secret_success(client):
    with patch("utils.shared.requests.post") as mock_post, \
         patch("utils.shared.requests.get") as mock_get:
        mock_post.return_value.status_code = 200
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'secret': 'abc123'}

        response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
        assert response.status_code == 204

def test_verify_secret_fail_store(client):
    with patch("utils.shared.requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
        assert response.status_code == 403

def test_verify_secret_fail_lookup(client):
    with patch("utils.shared.requests.post") as mock_post, \
         patch("utils.shared.requests.get") as mock_get:
        mock_post.return_value.status_code = 200
        mock_get.return_value.status_code = 403
        response = client.post('/verify_secret', json={"eth_address": "0xtest", "secret": "abc123"})
        assert response.status_code == 403
