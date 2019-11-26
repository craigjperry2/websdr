"""Filter raw spectrum samples into spectral density estimates

Consumes raw IQ sample data from an SDR and perform's an SDE using Welch's
method.

Notes
-----
Due to the underlying implementation of Welch's method, the returned data
layout is unexpected, to me at least:

    [0:n/2] : frequency bins 0 -> Fhi
    [n/2:n-1] : frequency bins Flo -> 0

I will probably come back and change this like e.g. https://github.com/matplotlib/matplotlib/blob/d41775327c1101b3fefc6fcf0fdf12a1a0254d3f/lib/matplotlib/mlab.py#L571

"""

import numpy as np
from scipy import signal


def spectrum_density_estimator(callback, fs=1.2e6*2, window="flattop", nperseg=1024):

    async def sde_filter(samples):
        f, psd = signal.welch(samples, fs, window, nperseg, scaling='density', return_onesided=False)
        return await callback({ "Pxx": np.absolute(psd.round(decimals=9)).tolist(), "f": f.tolist() })

    return sde_filter
