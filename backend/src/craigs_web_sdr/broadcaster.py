import logging
LOGGER = logging.getLogger()

import asyncio

from rtlsdr import RtlSdrAio

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from websockets.exceptions import ConnectionClosedError


class _SdrWebsocketBroadcaster:

    def __init__(self):
        self._sdr = None
        self._clients = []  # TODO: Provide typing? e.g. List(WebSocket)
        self._clients_lock = asyncio.Lock()
    
    def start(self, sample_size=128 * 1024, throttle_delay_secs=1):
        if not self._sdr:
            LOGGER.info("Starting SDR Sampler")
            self._sdr = RtlSdrAio()
            self._sdr.sample_rate = 1.2e6  # 1.2 MHz
            self._sdr.center_freq = 102e6  # 102 MHz (FM broadcast band)
            self._sdr.gain = 'auto'
            asyncio.create_task(
                self._stream_samples_from_sdr(sample_size, throttle_delay_secs)
            )
    
    async def stop(self,):
        await self._sdr.stop()
        self._sdr.close()

    async def register(self, websocket: WebSocket):
        async with self._clients_lock:
            self._clients.append(websocket)

    async def client_count(self):
        async with self._clients_lock:
            return len(self._clients)

    async def _stream_samples_from_sdr(self, sample_size, delay):
        async for samples in self._sdr.stream(num_samples_or_bytes=sample_size):
            LOGGER.debug(f"Collected {len(samples)} samples, now broadcasting")
            await self._broadcast(samples)
            await asyncio.sleep(delay)

    async def _broadcast(self, samples):
        async with self._clients_lock:
            for websocket in self._clients:
                LOGGER.debug(f"Broadcasting to next of {len(self._clients)} websockets")
                
                if websocket.client_state == WebSocketState.CONNECTED:
                    try:
                        await websocket.send_text(str(samples))
                    except (WebSocketDisconnect, ConnectionClosedError):
                        LOGGER.debug("Websocket dropped during send")
                
                if websocket.client_state != WebSocketState.CONNECTED:
                    LOGGER.debug("Reaping closed socket")
                    self._clients.remove(websocket)


sdr_websocket_broadcaster = _SdrWebsocketBroadcaster()
