#ecu.py
import threading
import time
import can
from SID_0x10 import SID_0x10
from sessiontypes import SESSIONS
from uds_utils import handle_request_with_timeout
from can import Notifier
class ECU(can.Listener):
    def __init__(self, energy, bus: can.Bus, tree=None, frequency_hz=60):
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
        #self.timer_lock = threading.Lock()
        #self.timer = 0
        self.lock = threading.Lock()
        self.security=False
        self.tree = tree
        self.received_request=False
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
                on_timeout=self.on_timeout
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
                # 这里放置ECU的循环处理逻辑
                #尝试通信
                # 收到请求，启动处理逻辑 -> 移动到on_message_received
                # 超时无请求则继续循环
                # 频率控制（60Hz，周期1/60秒），
                # 如果当前没有处理request，就要sleep保证周期
                if not self.received_request:
                    #self.loop_task()
                    elapsed = time.time() - start_time
                    sleep_time = self.period - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        print("[ECU] Stop event set, exiting...")

    # def loop_task(self):
    #     # 模拟ECU每个周期要做的任务
    #     with self.timer_lock:
    #         self.timer += 1
    #         #print(f"[{self.timer}] ECU loop running at {time.time():.4f}")

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
    
    def handle_request(self, req):
        try:
            if req.data[0]==0x10:#SID
                resp=SID_0x10.handle(req, self) 
                return resp
        except Exception as e:
            print(f"[ECU] Error processing message: {e}")