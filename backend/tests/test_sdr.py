import pytest
from asynctest import CoroutineMock

import asyncio

from rtlsdr import RtlSdr
import numpy as np

from craigs_web_sdr.sdr import _AsyncSdrSampler


def _has_rtl_sdr():
    """Convenience for marking tests to run if an RTL SDR is present"""
    return len(RtlSdr.get_device_serial_addresses()) == 1


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
async def test_callback_is_provided_with_samples_data(
    mocked_callback
):
    mocked_callback.assert_awaited()
    mocked_callback.assert_called()

    latest_callback_param = mocked_callback.call_args[0][0]
    assert type(latest_callback_param) is np.ndarray
    assert len(latest_callback_param) > 0

    sample_data_element = latest_callback_param[0]
    assert type(sample_data_element) is np.complex128
    assert sample_data_element != np.complex()  # i.e. default 0j value
