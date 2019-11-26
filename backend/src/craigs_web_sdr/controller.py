"""Provide web interfaces and orchestrate the SDR / SDE components

Co-ordinate the overall application flow. Serve the HTTP & Websocket
interfaces and orchestrate communication with the SDR / SDE components.

Notes
-----
This is an ASGI application, it is designed to be hosted in an ASGI server
like uvicorn.

Examples
--------
The following example:

    [user@host]$ backend  # see setup.py entry_points configuration
    INFO:     Started server process [26900]
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     Waiting for application startup.
    INFO:     Startup event
    INFO:     Starting SDR Sampler
    Found Rafael Micro R820T tuner
    [R82XX] PLL not locked!
    INFO:     Application startup complete.

Is equivalent to:

    [user@host]$ uvicorn craigs_web_sdr.controller:app
    INFO:     Started server process [26901]
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     Waiting for application startup.
    INFO:     Startup event
    INFO:     Starting SDR Sampler
    Found Rafael Micro R820T tuner
    [R82XX] PLL not locked!
    INFO:     Application startup complete.

"""


import logging

LOGGER = logging.getLogger()

import asyncio
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from websockets.exceptions import ConnectionClosedError

from craigs_web_sdr.sdr import sdr


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.absolute() / "templates")
)

_WEBSOCKET_CLIENTS = []
_WEBSOCKET_CLIENTS_LOCK = asyncio.Lock()


@app.on_event("startup")
def init_sdr():
    """Start the SDR component; begin receiving SDR sample data
    
    SDR samples will be delivered asynchronously to the callback.
    
    """

    LOGGER.info("Performing SDR initialisation on application startup")
    sdr.start(samples_callback=broadcast)


@app.on_event("shutdown")
async def close_sdr():
    """Relinquish use of the SDR device. Shutdown bg thread in pyrtlsdr

    """

    LOGGER.debug("Shutdown event triggered")
    await sdr.stop()
    LOGGER.info("SDR shutdown complete, hardware device relinquished")


@app.get("/")
async def page(request: Request):
    """Serve requests for the single-page application.

    Provides a hook into the SPA startup process. If this is not useful,
    this endpoint could be serviced by the "/static" mount instead.

    """

    return templates.TemplateResponse("page.html", {"request": request})


@app.websocket("/sde")
async def sde(websocket: WebSocket):
    """Serve websocket requests for SDE measurements

    Awaits pings from the client in an infinite loop. Sample data is sent
    asynchronously over the websocket from the broadcast() callback.
    
    This function is responsible for adding clients to _WEBSOCKET_CLIENTS
    but never modifies or removes them afterward.

    """

    await websocket.accept()
    async with _WEBSOCKET_CLIENTS_LOCK:
        _WEBSOCKET_CLIENTS.append(websocket)
        clients = len(_WEBSOCKET_CLIENTS)
    LOGGER.info(f"Added client, there are {clients} connected")

    try:
        while True:
            ping = await websocket.receive_text()
    except WebSocketDisconnect:
        async with _WEBSOCKET_CLIENTS_LOCK:
            clients = len(_WEBSOCKET_CLIENTS)
        LOGGER.debug(f"Client disconnected, there are {clients} clients left")


async def broadcast(samples):
    """Callback handler, broadcasts samples to all connected websocket clients

    Sockets that have disconnected are reaped here. Relies on FastAPI's ujson
    middleware to convert the underlying numpy ndarray to JSON.

    """

    async with _WEBSOCKET_CLIENTS_LOCK:
        for websocket in _WEBSOCKET_CLIENTS:
            LOGGER.debug(
                f"Broadcasting to next of {len(_WEBSOCKET_CLIENTS)} websockets"
            )

            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(samples.tolist())
                except (WebSocketDisconnect, ConnectionClosedError):
                    LOGGER.debug("Websocket dropped, will be reaped")

            if websocket.client_state != WebSocketState.CONNECTED:
                LOGGER.debug("Reaping closed socket")
                _WEBSOCKET_CLIENTS.remove(websocket)

    return True  # receive more sample callbacks


def main(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port)
