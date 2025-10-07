import threading
import time
from CANmessage import request_queue, response_queue, RequestMessage, PositiveResponseMessage, NegativeResponseMessage
from SID_0x10 import SID_0x10
from sessiontypes import SESSIONS
class ECU:
    def __init__(self, energy, request_queue, response_queue, frequency_hz=60):
        self.energy = energy
        self.DiagnosticSession = SESSIONS.DEFAULT_SESSION
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.frequency = frequency_hz
        self.period = 1.0 / frequency_hz
        self.running = False
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.timer_lock = threading.Lock()
        self.timer = 0
        self.clear_timer_event = threading.Event()
        self.lock = threading.Lock()
        self.security=False

    def on_power_status_changed(self, status):
        if status == "POWER_ON":
            print("[ECU] Received POWER_ON signal, starting ECU...")
            self.running = True
            self.start_event.set()
        elif status == "POWER_OFF":
            print("[ECU] Received POWER_OFF signal, stopping ECU...")
            self.running = False
            self.start_event.clear()

    def run(self):
        print("ECU is ready, waiting for power signal...")
        #last_status = None
        while not self.stop_event.is_set():
            # current_status = self.energy.status
            # if current_status != last_status:
            #     if current_status == "POWER_ON":
            #         print("[ECU] POWER_ON, ECU Start")
            #         self.start_event.set()
            #         self.running = True
            #     elif current_status == "POWER_OFF":
            #         print("[ECU] POWER_OFF, ECU Stop")
            #         self.start_event.clear()
            #         self.running = False
            #     last_status = current_status
            if self.running:
                preSession=self.DiagnosticSession
                start_time = time.time()
                # 这里放置ECU的循环处理逻辑
                if self.clear_timer_event.is_set():
                    with self.timer_lock:
                        self.timer = 0
                    print("[ECU] Timer cleared!")
                    self.clear_timer_event.clear()
                self.loop_task()
                #尝试通信
                try:
                    req = self.request_queue.get_nowait()  # 等待请求
                    print(f"[ECU] Received request SID: {req.SID}")
                    # 处理请求，构造响应
                    match req.SID:
                        case 16:
                            resp=SID_0x10.handle(req, self); 
                            self.response_queue.put(resp)                        
                    #resp = PositiveResponseMessage(SID=req.SID)
                    #self.response_queue.put(resp)
                except:
                   pass  # 超时无请求则继续循环
                if preSession != self.DiagnosticSession:
                    print(f"[ECU] session changed from {preSession} to {self.DiagnosticSession}")
                
                elapsed = time.time() - start_time
                sleep_time = self.period - elapsed
                if sleep_time >= 0:
                    time.sleep(sleep_time)
                #else:
                    #以后在想 

        print("[ECU] Stop event set, exiting...")

    def loop_task(self):
        # 模拟ECU每个周期要做的任务
        with self.timer_lock:
            self.timer += 1
            #print(f"[{self.timer}] ECU loop running at {time.time():.4f}")
    #下面是CAN通信相关
    #Request message
    # def process_requests(self):
    #     with self.lock:
    #         while self.request_queue:
    #             request = self.request_queue.pop(0)
    #             response = self.handle_request(request)
    #             self.response_queue.append(response)
    # #处理信息
    # def handle_request(self, request: RequestMessage):
    #     # 这里根据请求处理不同命令，模拟返回
    #     print(f"[ECU] Received request SID: {request.SID}")
    #     if request.SID == 0x10:  # 假设0x10代表读诊断会话
    #         return PositiveResponseMessage(SID=request.SID+0x40, subfunction=request.subfunction, dataID=request.dataID, data=self.DiagnosticSession)
    #     else:
    #         return NegativeResponseMessage(SID=0x7F, SIDRQ=request.SID, NRC=0x11)  # 11: Service not supported

    # def receive_request(self, request: RequestMessage):
    #     with self.lock:
    #         self.request_queue.append(request)

    # def get_response(self):
    #     with self.lock:
    #         if self.response_queue:
    #             return self.response_queue.pop(0)
    #         else:
    #             return None

    def clear_clock(self):
        self.clear_timer_event.set()

    def start(self):
        self.start_event.set()

    def stop(self):
        self.stop_event.set()