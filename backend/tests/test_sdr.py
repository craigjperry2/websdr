import pytest
from asynctest import CoroutineMock

import asyncio
from pathlib import Path

from rtlsdr import RtlSdr
import numpy as np

from craigs_web_sdr.sdr import _AsyncSdrSampler


def _has_rtl_sdr():
    """Convenience for marking tests to run if an RTL SDR is present"""
    return len(RtlSdr.get_device_serial_addresses()) == 1


def _sample_fixture():
    """Convenience for marking tests to when a dump file of samples data is present"""
    fixture = Path(__file__).parent / "fixtures" / "sample.dat"
    print(fixture)
    if fixture.exists():
        return fixture
    return None


@pytest.fixture
async def mocked_callback():
    """Setup and teardown an _AsyncSdrSampler with a mock callback"""
    m = CoroutineMock(return_value=False)
    sdr = _AsyncSdrSampler()
    sdr.start(m)
    await asyncio.sleep(5)  # HACK: wait for pyrtlsdr bg thread to init
    yield m
    await sdr.stop()


@pytest.mark.skipif(not _has_rtl_sdr(), reason="This test requires an RTL SDR dongle")
@pytest.mark.asyncio
async def test_callback_is_provided_with_samples_data(mocked_callback):
    mocked_callback.assert_awaited()
    mocked_callback.assert_called()

    latest_callback_param = mocked_callback.call_args[0][0]
    assert type(latest_callback_param) is np.ndarray
    assert len(latest_callback_param) > 0

    sample_data_element = latest_callback_param[0]
    assert type(sample_data_element) is np.complex128
    assert sample_data_element != np.complex()  # i.e. default 0j value


@pytest.mark.skipif(not _sample_fixture(), reason="This test requires a sample data fixture file")
@pytest.mark.asyncio
async def test_callback_is_provided_with_samples_data_without_sdr_dongle():
    mocked_callback = CoroutineMock(return_value=False)
    sdr = _FakeAsyncSdrSampler()
    sdr.start(mocked_callback)
    await asyncio.sleep(0)

    mocked_callback.assert_awaited()
    mocked_callback.assert_called()

    latest_callback_param = mocked_callback.call_args[0][0]
    assert type(latest_callback_param) is np.ndarray
    assert len(latest_callback_param) > 0

    sample_data_element = latest_callback_param[0]
    assert type(sample_data_element) is np.complex128
    assert sample_data_element != np.complex()  # i.e. default 0j value

    await sdr.stop()


class _FakeAsyncSdrSampler(_AsyncSdrSampler):
    
    def start(self, samples_callback, delay=1):
        self._callback = samples_callback
        self._task = asyncio.create_task(self._stream_samples_from_sdr())
    
    async def stop(self):
        self._task.cancel()

    async def _stream_samples_from_sdr(self):
        dump_file = _sample_fixture()
        samples = np.fromfile(dump_file, dtype=np.complex128)
        while True:
            if not await self._callback(samples):
                return
            await asyncio.sleep(self._delay)
