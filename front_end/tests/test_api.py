import pytest
import requests

# Only if you mock requests using requests-mock
pytest_plugins = ['requests_mock']

# If your tests rely on a test client fixture
from flask import Flask
from api import create_app

ef test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard(client):
    response = client.get('/dashboard/0xtest')
    assert response.status_code == 200

def test_user_profile_get(client):
    response = client.get('/users/0xtest')
    assert response.status_code == 200

def test_user_profile_post(client):
    response = client.post('/users/0xtest', json={'current_user_eth_address': '0xtest'})
    assert response.status_code == 200
    assert response.is_json
    assert response.json['is_owner'] is True

def test_get_rtmp_url(client, requests_mock):
    requests_mock.get("http://localhost:5001/get_rtmp_url/0xtest", json={"url": "test"}, status_code=200)
    response = client.get('/get_rtmp_url/0xtest')
    assert response.status_code == 200

def test_generate_rtmp_url_success(client, requests_mock):
    requests_mock.post("http://localhost:5001/generate_secret", json={"secret": "abc123"}, status_code=200)
    response = client.post('/generate_rtmp_url', json={"eth_address": "0xtest", "ip_address": "127.0.0.1"})
    assert response.status_code == 200
    assert "new_rtmp_url" in response.json

def test_magnet_url_success(client, requests_mock):
    requests_mock.get("http://localhost:8000/magnet_urls/0xtest", json={"magnet_urls": ["magnet:?xt=urn:btih:test"]})
    response = client.get("/magnet_urls/0xtest")
    assert response.status_code == 200
    assert response.json["magnet_urls"]

def test_start_session(client):
    response = client.post("/start_session", json={"eth_address": "0xtest"})
    assert response.status_code == 200
    assert "public_key" in response.json

def test_verify_hmac_missing_fields(client):
    response = client.post("/verify", json={"eth_address": "0xtest"})
    assert response.status_code == 400

def test_verify_secret_invalid(client):
    response = client.get("/verify_secret?name=invalidkey")
    assert response.status_code == 403
