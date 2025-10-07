import threading
import time
from CANmessage import request_queue, response_queue, RequestMessage
from ecu import ECU
class Tester:
    def __init__(self, request_queue, response_queue):
        super().__init__()
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.running = False
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def run(self):
        # 简单模拟给ECU发送请求并读取响应
        while self.running:
            req = RequestMessage(SID=0x10, subfunction = 0x03)  # 诊断会话请求
            print(f"[Tester] Sending request to ECU, SID=0x{req.SID:02X}, subfunction=0x{req.subfunction:02X}")
            self.request_queue.put(req)

            # 等待响应
            # time.sleep(0.1)
            # resp = self.ecu.get_response()
            # if resp:
            #     if resp.is_positive():
            #         print(f"[Tester] Positive response received with data: {resp.data}")
            #     else:
            #         print("[Tester] Negative response received")
            # else:
            #     print("[Tester] No response yet")

            time.sleep(1)  # 等待1秒再发请求

