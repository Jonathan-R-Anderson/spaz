import pytest
from flask import Flask
from api.views.update_site import update_site_routes

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(update_site_routes)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()


def test_commit_magnet_success(mocker, client):
    # Mock Web3 contract interaction
    mock_contract = mocker.MagicMock()
    mock_tx = {"tx": "data"}

    # Patch contract + web3 in view
    mocker.patch("api.views.update_site.magnet_contract", mock_contract)
    mocker.patch("api.views.update_site.w3.eth.get_transaction_count", return_value=1)
    mock_contract.functions.updateThemeMagnet.return_value.build_transaction.return_value = mock_tx

    response = client.post("/commit_magnet", json={
        "eth_address": "0x0000000000000000000000000000000000000001",
        "magnet_url": "magnet:?xt=urn:btih:abc123"
    })

    assert response.status_code == 200
    assert "Magnet committed" in response.json["message"]


def test_commit_magnet_missing_fields(client):
    response = client.post("/commit_magnet", json={
        "magnet_url": "magnet:?xt=urn:btih:abc123"
        # Missing eth_address
    })
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]
