import pytest
from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient

import numpy as np

from craigs_web_sdr.controller import (
    app,
    _WEBSOCKET_CLIENTS,
    _WEBSOCKET_CLIENTS_LOCK,
    broadcast,
)


client = TestClient(app)


@pytest.fixture
def ndarray_of_float():
    """The datatype ordinarily sent through broadcast() from SDR"""
    return np.ones(1, dtype="float64")


@pytest.fixture
async def cleanup_websockets(ndarray_of_float):
    """Without a background thread calling broadcast(), there's no reaping"""
    yield
    await broadcast(ndarray_of_float)
    await broadcast(ndarray_of_float)
    async with _WEBSOCKET_CLIENTS_LOCK:
        assert len(_WEBSOCKET_CLIENTS) == 0


def test_serves_page():
    response = client.get("/")
    assert response.status_code == 200
    print(response.text)
    assert "<title>Craig's Web SDR</title>" in response.text
    assert (
        '<link href="http://testserver/static/styles.css" rel="stylesheet">'
        in response.text
    )
    assert "</html>" in response.text


def test_serves_static_content():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "h1 {" in response.text


def test_unknown_requests_generate_404():
    response = client.get("/doesnt/exist")
    assert response.status_code == 404


@patch("craigs_web_sdr.controller.sdr")
def test_sdr_startup_and_shutdown_events_are_triggered(mock_sdr):
    stopped = False

    async def awaitable():
        nonlocal stopped
        stopped = True

    mock_sdr.stop.return_value = awaitable()

    with TestClient(app) as client:
        mock_sdr.start.assert_called()
    assert stopped == True


@patch("craigs_web_sdr.controller.sdr")
@pytest.mark.asyncio
async def test_consumes_infinite_pings_on_sde_websocket(
    mock_sdr, ndarray_of_float, cleanup_websockets
):
    with client.websocket_connect("/sde") as websocket:
        websocket.send_text("Ping...")
        websocket.send_text("Ping...")
        websocket.send_text("Ping...")


@pytest.mark.asyncio
async def test_broadcasts_samples_data_to_clients(ndarray_of_float, cleanup_websockets):
    with client.websocket_connect("/sde") as client1:
        with client.websocket_connect("/sde") as client2:

            await broadcast(ndarray_of_float.tolist())
            for c in [client1, client2]:
                r = c.receive_text()
                assert r == str(ndarray_of_float.tolist())
