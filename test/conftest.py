#test/conftest.py
import pytest
import can
import sys, os
import time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ecu import ECU
from energy import Energy   
from tester import Tester
RESPONSE_ID=0x18DAF1BA
class TestMessageCollector(can.Listener):
    def __init__(self, response_id):
        super().__init__()
        self.response_id = response_id
        self.last_msg = None
    
    def on_message_received(self, msg):
        if msg.arbitration_id == self.response_id:
            self.last_msg = msg

@pytest.fixture(scope="module")
def bus():
    bus = can.interface.Bus(
        interface="virtual",
        channel="vcan0",
        bitrate=500000,
        receive_own_messages=True
    )
    return bus

@pytest.fixture(scope="module")
def collector():
    return TestMessageCollector(RESPONSE_ID)

@pytest.fixture
def energy():
    energy=Energy()
    return energy

@pytest.fixture
def runtime(bus, energy, collector):
    """
    A full runtime environment:
    - ECU
    - Tester
    - Notifier
    - Threads
    but WITHOUT attaching notifier into bus.
    """
    ecu = ECU(energy=energy, bus=bus)
    tester = Tester(bus=bus)
    notifier = can.Notifier(bus, [ecu, tester, collector])
    ecu.on_power_status_changed("POWER_ON")
    yield ecu, tester, notifier

    # teardown
    time.sleep(1)
    notifier.stop()
    ecu.on_power_status_changed("POWER_OFF")
    ecu.stop()


@pytest.fixture(scope="session")
def excel():
    from excel_io import ExcelTestCases
    excel = ExcelTestCases("testcases.xlsx")
    excel.load()
    yield excel
    excel.save() 