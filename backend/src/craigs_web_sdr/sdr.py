"""Manage a singleton RTL SDR dongle and stream samples asynch to a callback

Prepare an RTL SDR for sample measurements then begin streaming the data.
Deliver samples data to a caller-provided asynchronous callback. Throttle
the rate of samples delivered to the callback.

Notes
-----
sdr : _AsyncSdrSampler
    The singleton "sdr" is intended for consumption by clients rather than
    instantiating an ``_AsyncSdrSampler()`` in each client module. This
    will avoid contention of the underlying physical RTL SDR device.

Examples
--------
>>> from craigs_web_sdr.sdr import sdr
>>> type(sdr)
<class 'craigs_web_sdr.sdr._AsyncSdrSampler'>

>>> import asyncio
>>> async def dotter(_):
...     print('.', end='')
...
>>> async def main():
...     sdr.start(dotter)
...
>>> asyncio.ensure_future(main())
>>> asyncio.get_event_loop().run_forever()
.........

"""


import logging
LOGGER = logging.getLogger()

import asyncio

from rtlsdr import RtlSdrAio
import numpy as np


class _AsyncSdrSampler:
    """Configure an RTL SDR then begin streaming samples asynchronously

    Streaming of samples is done from a (Python, GIL-acquiring) thread in
    pyrtlsdr. The samples are collected asynchronously via a co-routine in
    this module.

    Notes
    -----
    _AsyncSdrSampler only supports 1 RTL SDR at a time and it is not
    possible to restart streaming after stopping. A new _AsyncSdrSampler()
    will be required in that case.

    See Also
    --------
    sdr module docstring contains usage examples of an _AsyncSdrSampler

    """

    def __init__(self):
        self._sdr = None
        self._callback = None

    def start(self, samples_callback, delay=1):
        """Begin buffering samples from the SDR
        
        Samples are enqueued in a small buffer, when sample consumption
        doesn't keep pace with samples being enqueued then new samples
        are dropped. Any delay > 0 guarantees drops, which is often ok.

        Parameters
        ----------
        samples_callback : callable
            callable expecting one parameter - a numpy ndarray of sample data
        
        delay : number
            int or float, throttling delay between callbacks in seconds

        Notes
        -----
        New samples are enqueued in real-time in a background thread
        managed by pyrtlsdr.

        """

        if not self._sdr:
            self._callback = samples_callback
            LOGGER.info("Starting Async SDR Sampler")
            self._sdr = RtlSdrAio()
            self._sdr.sample_rate = 1.2e6  # 1.2 MHz, bandwidth
            self._sdr.center_freq = 102e6  # 102 MHz (in FM broadcast band)
            self._sdr.gain = 'auto'
            self._sample_size = self._sdr.sample_rate * 2  # Nyquist freq
            self._delay = delay
            asyncio.create_task(self._stream_samples_from_sdr())
    
    async def stop(self):
        """Stop sample collection and relinquish the SDR device"""

        await self._sdr.stop()
        self._sdr.close()
    
    async def _stream_samples_from_sdr(self):
        """Throttle the rate of samples sent to the client's callback"""

        async for samples in self._sdr.stream(num_samples_or_bytes=self._sample_size):
            LOGGER.debug(f"Got {len(samples)} samples in a {type(samples)}")
            if not await self._callback(np.absolute(samples)):
                return
            await asyncio.sleep(self._delay)


sdr = _AsyncSdrSampler()
