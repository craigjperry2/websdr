import logging
LOGGER = logging.getLogger()

from pathlib import Path

from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from .broadcaster import sdr_websocket_broadcaster as sdr


app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent.absolute() / "templates"))


@app.on_event("startup")
def init_sdr():
    LOGGER.info("Startup event")
    sdr.start()


@app.on_event("shutdown")
async def close_sdr():
    LOGGER.debug("Shutdown event")
    await sdr.stop()
    LOGGER.info("Shutdown complete")


@app.get("/")
async def page(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})


@app.websocket("/iqstream")
async def iq_stream(websocket: WebSocket):
    await websocket.accept()
    await sdr.register(websocket)
    clients = await sdr.client_count()
    LOGGER.info(f"Added client: {clients}")
    try:
        ping = await websocket.receive_text()
    except WebSocketDisconnect:
        clients = await sdr.client_count()
        LOGGER.debug(f"Client disconnected, there are {clients} clients left")
