#ecu.py
import threading
import time
import can
from SID_0x10 import SID_0x10
from SID_0x14 import SID_0x14
from sessiontypes import SESSIONS
from uds_utils import handle_request_with_timeout
import random
class ECU(can.Listener):
    def __init__(self, energy, bus: can.Bus, frequency_hz=60):
        self.energy = energy
        self.DiagnosticSession = SESSIONS.DEFAULT_SESSION
        self.arbitration_id = 0x002
        self.bus = bus
        self.frequency = frequency_hz
        self.period = 1.0 / frequency_hz
        self.P2_time = 5
        self.running = False
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.security=False
        self.received_request=False
        self.moving=False
        self.dtc=None
        self.is_memory_error=False

    def on_power_status_changed(self, status):
        if status == "POWER_ON":
            print("[ECU] Received POWER_ON signal, starting ECU...")
            self.running = True
            self.start_event.set()
        elif status == "POWER_OFF":
            print("[ECU] Received POWER_OFF signal, stopping ECU...")
            self.running = False
            self.start_event.clear()

    def on_message_received(self, msg):
        if not self.running:
            return
        try:
            if not msg.arbitration_id == self.arbitration_id:
                msg.is_rx=True
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
                print(f"[ECU] Sent response after extended processing: {resp}")
            except can.CanError as e:
                print(f"[ERROR] CAN send failed (extende processing)")

    def handle_request(self, req):
        try:
            if req.data[0]==0x10:#SID
                resp=SID_0x10.handle(req, self) 
                return resp
            if req.data[0]==0x14:
                resp=SID_0x14.handle(req,self)
                return resp
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