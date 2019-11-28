import pytest
import asyncio
import ujson
import websockets

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

import logging


@pytest.fixture
def websocket_data(scope="session"):
    data1 = data2 = None

    async def collect_stream():
        nonlocal data1, data2
        async with websockets.connect(
            "ws://localhost:8000/sde"
        ) as ws1, websockets.connect("ws://localhost:8000/sde") as ws2:
            await ws1.send("ping: not req'd but permitted so check it works")
            await ws1.recv()  # discard a packet due to send(), ws1 gets extra 1 frame before ws2
            data1 = await ws1.recv()
            data2 = await ws2.recv()
            await asyncio.sleep(0)

    asyncio.run(collect_stream())
    return {"ws1": ujson.loads(data1), "ws2": ujson.loads(data2)}


@scenario(
    "spectrum_measurements.feature", "Stream Welch's method spectral density estimates"
)
def test_stream_welchs_method_spectral_density_estimates():
    pass


@given("the SDR dongle is ready")
def sdr_present(dongles):
    pass  # extracted to shared fixture


@given("the websocket server is ready")
def pid(server):
    logging.info(f"Spawned server with pid {server.pid}")


@when("2 clients connect via websocket to sde")
def clients():
    pass  # body extracted to module fixture for speed


@then("the maps have <key> of <dtype> with values between <min> and <max>")
def the_maps_have_key_of_type_with_values_between_min_and_max(
    key, dtype, min, max, websocket_data
):
    value = websocket_data["ws1"][key]
    assert str(type(value)) == dtype
    assert len(value) >= int(min)
    assert len(value) <= int(max)


@then("they receive identical streams of json map objects")
def they_receive_identical_streams_of_json_map_objects(websocket_data):
    assert websocket_data["ws1"] == websocket_data["ws2"]
