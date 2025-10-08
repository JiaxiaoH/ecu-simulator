import threading
import time
from CANmessage import request_queue, response_queue, RequestMessage, PositiveResponseMessage, NegativeResponseMessage
from SID_0x10 import SID_0x10
from sessiontypes import SESSIONS
class ECU:
    def __init__(self, energy, request_queue, response_queue, tree, frequency_hz=60):
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
        self.tree = tree
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
        P2_time = 5
        print("ECU is ready, waiting for power signal...")
        #last_status = None
        while not self.stop_event.is_set():
            if self.running:
                preSession=self.DiagnosticSession
                start_time = time.time()
                # 这里放置ECU的循环处理逻辑
                if self.clear_timer_event.is_set():
                    with self.timer_lock:
                        self.timer = 0
                    print("[ECU] Timer cleared!")
                    self.clear_timer_event.clear()
                #尝试通信
                processing_request=False
                try:
                    req = self.request_queue.get_nowait()  # 等待请求
                    print(f"[ECU] Received {req}")
                    # 收到请求，启动处理逻辑
                    processing_request=True
                    def handle_request():
                        # 处理请求，构造响应
                        match req.SID:
                            case 16: #16=0x10
                                resp=SID_0x10.handle(req, self); 
                                self.response_queue.put(resp)
                                resp.log_to_treeview(self.tree)
                                print(f"[ECU] Sended {resp}")                     
                        if preSession != self.DiagnosticSession:
                            print(f"[ECU] Session changed from {preSession} to {self.DiagnosticSession}")
                    # 启动请求处理线程
                    handler_thread = threading.Thread(target=handle_request())
                    handler_thread.start()
                    handler_thread.join(timeout=P2_time)
                    if handler_thread.is_alive():
                        print("[ECU][SID$10] P2 timeout!")
                        resp=NegativeResponseMessage(SIDRQ=req.SID, NRC=0x78)
                        self.response_queue.put(resp)  
                        req.log_to_treeview(self.tree)
                    else :
                        processing_request=False
                except:
                   pass  # 超时无请求则继续循环
                # 频率控制（60Hz，周期1/60秒），
                # 如果当前没有处理request，就要sleep保证周期
                if not processing_request:
                    self.loop_task()
                    elapsed = time.time() - start_time
                    sleep_time = self.period - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        print("[ECU] Stop event set, exiting...")

    def loop_task(self):
        # 模拟ECU每个周期要做的任务
        with self.timer_lock:
            self.timer += 1
            #print(f"[{self.timer}] ECU loop running at {time.time():.4f}")
    def clear_clock(self):
        self.clear_timer_event.set()

    def start(self):
        self.start_event.set()

    def stop(self):
        self.stop_event.set()