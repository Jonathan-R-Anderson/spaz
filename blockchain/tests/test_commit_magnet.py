import pytest
import logging
from flask import Flask
from api.views.update_site import update_site_routes
from system.logging import setup_logger

# Set up test logger
logger = setup_logger("test_update_site")

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(update_site_routes)
    app.config["TESTING"] = True
    logger.debug("[FIXTURE] Flask app created and blueprint registered")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_commit_magnet_success(mocker, client):
    logger.info("[TEST] test_commit_magnet_success started")

    mock_contract = mocker.MagicMock()
    mock_tx = {"tx": "data"}

    logger.debug("[MOCK] Patching magnet_contract and w3.eth.get_transaction_count")
    mocker.patch("api.views.update_site.magnet_contract", mock_contract)
    mocker.patch("api.views.update_site.w3.eth.get_transaction_count", return_value=1)
    mock_contract.functions.updateThemeMagnet.return_value.build_transaction.return_value = mock_tx

    test_data = {
        "eth_address": "0x0000000000000000000000000000000000000001",
        "magnet_url": "magnet:?xt=urn:btih:abc123"
    }
    logger.debug(f"[REQUEST] Sending POST /commit_magnet with data: {test_data}")
    response = client.post("/commit_magnet", json=test_data)

    logger.debug(f"[RESPONSE] Status Code: {response.status_code}, JSON: {response.json}")
    assert response.status_code == 200
    assert "Magnet committed" in response.json["message"]
    logger.info("[TEST] test_commit_magnet_success passed")

def test_commit_magnet_missing_fields(client):
    logger.info("[TEST] test_commit_magnet_missing_fields started")

    incomplete_data = {
        "magnet_url": "magnet:?xt=urn:btih:abc123"
        # eth_address missing
    }
    logger.debug(f"[REQUEST] Sending POST /commit_magnet with incomplete data: {incomplete_data}")
    response = client.post("/commit_magnet", json=incomplete_data)

    logger.debug(f"[RESPONSE] Status Code: {response.status_code}, JSON: {response.json}")
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]
    logger.info("[TEST] test_commit_magnet_missing_fields passed")
