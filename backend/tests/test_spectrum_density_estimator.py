import pytest
from asynctest import patch, Mock

import numpy as np

from tests.test_controller import ndarray_of_float

from craigs_web_sdr.spectrum_density_estimator import spectrum_density_estimator


@pytest.fixture
def callback(ndarray_of_float):
    """Substitute for the broadcast() func in controller"""

    async def awaitable():
        return True

    return Mock(return_value=awaitable())


@pytest.fixture
def ndarray_of_complex():
    """Simulate samples data from sdr component"""
    return np.ones(1, dtype="complex128")


@patch("craigs_web_sdr.spectrum_density_estimator.signal")
@pytest.mark.asyncio
async def test_callsback_with_parameter(signal_mock, callback, ndarray_of_float):
    signal_mock.welch.return_value = (ndarray_of_float, ndarray_of_float)
    sde = spectrum_density_estimator(callback)

    take_more = await sde(ndarray_of_complex)

    sde_data = callback.call_args[0][0]
    assert sde_data == {
        "Pxx": ndarray_of_float,
        "f": ndarray_of_float,
    }
    assert take_more is True
