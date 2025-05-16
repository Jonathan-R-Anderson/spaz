import io
import pytest
from unittest.mock import patch
from api import create_app
from api.services.monitor import seed_processes
from config import Config



@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_start_static_monitor(client):
    with patch('api.routes.Process') as mock_process:
        response = client.post('/start_static_monitor', json={"eth_address": "0xabc123"})
        assert response.status_code in [200, 400]


def test_start_hls_monitor(client):
    with patch('api.routes.Process') as mock_process:
        response = client.post('/start_hls_monitor', json={"eth_address": "0xabc123"})
        assert response.status_code in [200, 400]


def test_convert_to_mp4_missing_fields(client):
    response = client.post('/convert_to_mp4', json={"eth_address": "0xabc123"})
    assert response.status_code == 400
    assert b"eth_address and filename are required" in response.data


def test_peer_count_missing_url(client):
    response = client.post('/peer_count', json={})
    assert response.status_code == 400
    assert b"magnet_url is required" in response.data


def test_magnet_url_endpoint(client):
    with patch('api.routes.retrieve_magnet_urls') as mock_retrieve:
        mock_retrieve.return_value = {"message": "success", "magnet_urls": ["magnet:?xt=urn:btih:123"]}
        response = client.get('/magnet_urls/0xabc123')
        assert response.status_code == 200
        assert b"magnet_urls" in response.data


def test_magnet_url_trigger_monitor(client):
    with patch('api.routes.retrieve_magnet_urls') as mock_retrieve, \
         patch('api.routes.Process') as mock_process:
        mock_retrieve.return_value = {"message": "error"}
        response = client.get('/magnet_urls/0xabc123')
        assert response.status_code == 404


def test_seed_file_missing_file(client):
    response = client.post('/seed', data={"eth_address": "0xabc123"})
    assert response.status_code == 400
    assert b"File is required" in response.data


def test_seed_file_invalid_eth(client):
    dummy_file = (io.BytesIO(b"dummy content"), "video.mp4")
    response = client.post('/seed', data={
        "eth_address": "not_an_eth_address",
        "file": dummy_file
    }, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Valid eth_address is required" in response.data


def test_seed_file_success(client):
    dummy_file = (io.BytesIO(b"dummy content"), "video.mp4")
    with patch('api.routes.subprocess.Popen') as mock_popen, \
        patch('api.routes.stream_output') as mock_stream_output:

        mock_stream_output.return_value = "magnet:?xt=urn:btih:123"
        process_mock = mock_popen.return_value
        process_mock.stdout = io.StringIO("output")
        process_mock.stderr = io.StringIO("")

        response = client.post('/seed', data={
            "eth_address": "0xabc123abc123abc123abc123abc123abc123abc1",
            "file": dummy_file
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        assert b"magnet_url" in response.data


def test_stop_seeding_missing_eth(client):
    response = client.post('/stop_seeding', json={})
    assert response.status_code == 400


def test_stop_seeding_no_process(client):
    Config.seed_processes.clear()
    response = client.post('/stop_seeding', json={"eth_address": "0xabc123"})
    assert response.status_code == 404
