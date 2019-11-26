"""Stream 1x sample data frame from an SDR into a file.

Can be used to capture real fixture data instead of reading from an SDR
dongle each time. The default sample settings produce 1 sample frame of 37Mb.
It's binary data and quite chunky so not suitable for checkin to git.

"""

import logging

logging.basicConfig(level=logging.DEBUG)

import asyncio
from pathlib import Path

from craigs_web_sdr.sdr import sdr


_event = None


async def capture_sample_frame(samples):
    dump_file = Path(__file__).parents[1] / "tests" / "fixtures" / "samples.dat"
    samples.tofile(dump_file)
    global _event
    _event.set()
    return False


async def main():
    global _event
    _event = asyncio.Event()
    sdr.start(capture_sample_frame)
    logging.info("Awaiting sample to be produced...")
    await _event.wait()
    logging.info("Done, stopping SDR...")
    await sdr.stop()


if __name__ == "__main__":
    asyncio.run(main())
