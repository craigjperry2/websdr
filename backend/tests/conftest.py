import pytest

import os
import time
import signal
import platform
import subprocess
from rtlsdr import RtlSdr


@pytest.fixture(scope="session")
def dongles():
    if len(RtlSdr.get_device_serial_addresses()) != 1:
        return pytest.skip("Test requires 1 RTL SDR dongle to be present")


@pytest.fixture(scope="session")
def server(dongles):
    cmd_line = ["backend"]

    if platform.system() is "Windows":
        pro = subprocess.Popen(cmd_line, shell=True)
    else:
        pro = subprocess.Popen(cmd_line, shell=True, preexec_fn=os.setsid)

    yield pro

    if platform.system() is "Windows":
        os.kill(pro.pid, signal.CTRL_C_EVENT)
    else:
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

    time.sleep(5)  # plenty time to startup server, even on a RaspberryPi
