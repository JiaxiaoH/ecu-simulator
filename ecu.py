#ecu.py
import threading
import time
import can
import uds.sid
from uds.sid_registry import get_handler, SID_HANDLERS
from sessiontypes import SESSIONS
from security import SecurityType
from dtc import DTCManager, DTC
from uds_utils import handle_request_with_timeout
import random

class ECU(can.Listener):
    def __init__(self, energy, bus: can.Bus, frequency_hz=60):
        self.SID_HANDLERS=SID_HANDLERS
        self.energy = energy
        self.arbitration_id = 0x7E8
        self.bus = bus
        self.frequency = frequency_hz
        self.period = 1.0 / frequency_hz
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.allowed_diag_ids = [0x7E0, 0x7E8] 
        self.dtc = DTCManager()

        self._timer_lock=threading.Lock()

        self._DTCStatusAvailabilityMask=0x0E
        self._DTCFormatIdentifier=0x00
        self._dtcstr=["B2B10-A3", "U0146-00", "C0037-62"]
        dtc1=DTC.from_dtc_string("B2B10-A3", self.DTCStatusAvailabilityMask)
        dtc2=DTC.from_dtc_string("U0146-00", self.DTCStatusAvailabilityMask)
        dtc3=DTC.from_dtc_string("C0037-62", self.DTCStatusAvailabilityMask)
        self._dtc_available_list=[]
        self._dtc_available_list.extend([dtc1, dtc2, dtc3])
        self.key=None
        self._reset_timer = None
        self._start_time = None
        self.reset_state()

    @property
    def DTCStatusAvailabilityMask(self):
        return self._DTCStatusAvailabilityMask
    
    @property
    def DTCFormatIdentifier(self):
        return self._DTCFormatIdentifier

    @property
    def dtcstr(self):
        return self._dtcstr
        
    @property
    def dtc_available_list(self):
        return self._dtc_available_list
    
    def reset_state(self):
        self._session = SESSIONS.DEFAULT_SESSION
        self.P2_time = 5
        self.running = False
        self.security = SecurityType.FALSE
        self.received_request = False
        self.moving = False
        self.is_memory_error = False
        self._delay = 3
        self._disableRxAndTx = False
        self.illegal_access=0
        self.power_on_time = None
        self.dt_igon = 0.0  

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if value!=self._session:
            self._session=value
            self._start_reset_timer(self._delay)
        if (value == SESSIONS.DEFAULT_SESSION) and self._disableRxAndTx:
            self.communication_control(False)
        if (value == SESSIONS.DEFAULT_SESSION):
            self.dtc.dtc_setting=True
            self.security=SecurityType.FALSE

    def _start_reset_timer(self, delay=3):
        with self._timer_lock:
            if self._reset_timer and self._reset_timer.is_alive():
                self._reset_timer.cancel()
            self._delay = delay
            self._start_time = time.time()
            self._reset_timer = threading.Timer(delay, self._reset_session_safe)
            self._reset_timer.name="ECU_Reset_Timer"
            self._reset_timer.daemon=True
            self._reset_timer.start()

    def _reset_session_safe(self):
        #with self._timer_lock:
        if self._reset_timer and threading.current_thread() is self._reset_timer:
            self._reset_session()

    def _reset_session(self):
        self.session = SESSIONS.DEFAULT_SESSION
        self._start_time = None
        self._reset_timer = None
        print(f"[ECU] Session transitioned back to defaultSession")

    def extend_delay(self, new_delay=60):
        self._start_reset_timer(new_delay)

    def communication_control(self, enable_restrict=True):
        self._disableRxAndTx = enable_restrict

    def dtc_setting(self):
        self.dtc._dtc_setting = False

    def hard_reset(self):
        print("[ECU] Performing hard reset...")
        self.on_power_status_changed("POWER_OFF")
        time.sleep(1)#a time simmulation for hard reset
        self.on_power_status_changed("POWER_ON")
        print("[ECU] Hard reboot complete.")

    def on_power_status_changed(self, status):
        if status == "POWER_ON":
            print("[ECU] Received POWER_ON signal, starting ECU...")
            self.running = True
            self.start_event.set()
            self.stop_event.clear() 
            self.power_on_time = time.time()
            self.dt_igon = 0.0
            self.start_thread() 
        elif status == "POWER_OFF":
            print("[ECU] Received POWER_OFF signal, stopping ECU...")
            self.running = False
            self.start_event.clear()
            self.stop_event.set()
            self.reset_state()
            with self._timer_lock:
                if self._reset_timer:
                    self._reset_timer.cancel()
                    try:
                        self._reset_timer.join(timeout=1)
                    except RuntimeError:
                        pass
                    self._reset_timer = None

    def on_message_received(self, msg):
        if self._disableRxAndTx:
            if msg.arbitration_id not in self.allowed_diag_ids:
                return 
        try:
            if msg.arbitration_id == self.arbitration_id:
                return
            print(f"[ECU] Received {msg}")
            self.received_request=True
            if len(msg.data) >= 2 and msg.data[0] == 0x27 and msg.data[1] in (0x07, 0x31, 0x41):
                timeout = 0.1
            else:
                timeout = self.P2_time
            response = handle_request_with_timeout(
                request=msg,
                handler_func=self.handle_request,
                timeout=timeout,
                on_timeout=self.on_timeout,
                on_finish=self.on_finish
            )
            if response is not None:
                self.bus.send(response)
                self.received_request=False
        except Exception as e:        
            print(f"[ECU] Error processing message: {e}")
        
    def run(self):
        print("ECU is ready, waiting for power signal...")
        print(f"bus.channel_info = {self.bus.channel_info}")
        while not self.stop_event.is_set():
            if self.running:
                self.igon_timer()
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

    def start_thread(self):
        if not hasattr(self, '_thread') or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True, name="ECU_Thread")
            self._thread.start()

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
            #self.timeout_set(self.random_set())
            self.dtc.clear_dtc()
            print("Success: DTC reset!")
        except Exception as e:
            self.is_memory_error=True
            print("Failed: DTC reset!")
    
    def random_set(self, rn=0.2):
         return random.random() < rn
    
    def timeout_set(self, flag):
        if flag:
            time.sleep(self.P2_time+1)
    
    def igon_timer(self):
        if self.power_on_time is None:
            return
        try:
            self.dt_igon = time.time() - self.power_on_time
        except TypeError as e:
            self.dt_igon = 0.0
            print(f"[ECU]Error: {e}")