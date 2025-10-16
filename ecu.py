#ecu.py
import threading
import time
import can
from SID_0x10 import SID_0x10
from SID_0x11 import SID_0x11
from SID_0x14 import SID_0x14
from SID_0x28 import SID_0x28
from SID_0x3E import SID_0x3E
from sessiontypes import SESSIONS
from uds_utils import handle_request_with_timeout
import random
class ECU(can.Listener):
    SID_HANDLERS = {
        0x10: SID_0x10,
        0x11: SID_0x11,
        0x14: SID_0x14,
        0x28: SID_0x28,
        0x3E: SID_0x3E
    }
    def __init__(self, energy, bus: can.Bus, frequency_hz=60):
        self.energy = energy
        self.arbitration_id = 0x7E8
        self.bus = bus
        self.frequency = frequency_hz
        self.period = 1.0 / frequency_hz
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.allowed_diag_ids = [0x7E0, 0x7E8] 
        self.reset_state()
    
    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if value!=self._session:
            self._session=value
            self._start_reset_timer(self._delay)

    def _start_reset_timer(self, delay=3):
        if self._reset_timer and self._reset_timer.is_alive():
            self._reset_timer.cancel()
        self._delay = delay
        self._start_time = time.time()
        self._reset_timer = threading.Timer(delay, self._reset_session)
        self._reset_timer.start()

    def _reset_session(self):
        self._session = SESSIONS.DEFAULT_SESSION
        self._start_time = None
        self._reset_timer = None
        print(f"[ECU] Session transitioned back to defaultSession")

    def extend_delay(self, new_delay=30):
        self._start_reset_timer(new_delay)

    def communication_control(self, enable_restrict=True):
        self._disableRxAndTx = enable_restrict

    def reset_state(self):
        self._session = SESSIONS.DEFAULT_SESSION
        self.P2_time = 5
        self.running = False
        self.security = False
        self.received_request = False
        self.moving = False
        self.dtc = None
        self.is_memory_error = False
        self._delay = 3
        self._reset_timer = None
        self._start_time = None
        self._disableRxAndTx = False

    def hard_reset(self):
        print("[ECU] Performing hard reset...")
        self.on_power_status_changed("POWER_OFF")
        time.sleep(0.1)#a simmulation for hard reset
        self.on_power_status_changed("POWER_ON")
        print("[ECU] Hard reboot complete.")

    def on_power_status_changed(self, status):
        if status == "POWER_ON":
            print("[ECU] Received POWER_ON signal, starting ECU...")
            self.running = True
            self.start_event.set()
        elif status == "POWER_OFF":
            print("[ECU] Received POWER_OFF signal, stopping ECU...")
            self.running = False
            self.start_event.clear()
            self.reset_state()

    def on_message_received(self, msg):
        if not self.running:
            return
        if self._disableRxAndTx:
            if msg.arbitration_id not in self.allowed_diag_ids:
                return 
        try:
            #msg.is_rx = (msg.arbitration_id != self.arbitration_id)
            if msg.arbitration_id == self.arbitration_id:
                return
            print(f"[ECU] Received {msg}")
            self.received_request=True
            response = handle_request_with_timeout(
                request=msg,
                handler_func=self.handle_request,
                timeout=self.P2_time,
                on_timeout=self.on_timeout,
                on_finish=self.on_finish
            )
            if response:
                self.bus.send(response)
                self.received_request=False
        except Exception as e:        
            print(f"[ECU] Error processing message: {e}")
        
    def run(self):
        print("ECU is ready, waiting for power signal...")
        print(f"bus.channel_info = {self.bus.channel_info}")
        #last_status = None
        while not self.stop_event.is_set():
            if self.running:
                start_time = time.time()
                if not self.received_request:
                    elapsed = time.time() - start_time
                    sleep_time = self.period - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        print("[ECU] Stop event set, exiting...")

    def start(self):
        self.start_event.set()

    def stop(self):
        self.stop_event.set()

    def on_timeout(self, req):
        print("[ECU] P2 timeout!")
        try:
            data_bytes=bytearray([0x7F, req.data[0], 0x78])
            msg = can.Message(arbitration_id=self.arbitration_id, data=data_bytes, is_extended_id=False)
            self.bus.send(msg)
            print(f"[ECU] Sent NegativeResponse (timeout): {msg}")
        except can.CanError as e:
            print(f"[ERROR] CAN send failed (timeout response): {e}")
    
    def on_finish(self, resp):
        if resp is not None:
            try:
                self.bus.send(resp)
                print(f"[ECU] Sent response: {resp}")
            except can.CanError as e:
                print(f"[ERROR] CAN send failed")

    def handle_request(self, req):
        try:
            sid = req.data[0]
            handler_cls = self.SID_HANDLERS.get(sid)
            if handler_cls:
                return handler_cls.handle(req, self)
            else:
                print(f"[ECU] Unsupported SID: {sid}")
        except Exception as e:
            print(f"[ECU] Error processing message: {e}")
    
    def dtc_clear(self):
        try:
            self.timeout_set(self.random_set())
            self.dtc=None
            print("Success: DTC reset!")
        except Exception as e:
            self.is_memory_error=True
            print("Failed: DTC reset!")
    
    def random_set(self, rn=0.2):
        if random.random() < rn:  
            return True
        else:
            return False
    
    def timeout_set(self, flag):
        if flag:
            time.sleep(self.P2_time+1)