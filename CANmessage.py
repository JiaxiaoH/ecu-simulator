from abc import ABC, abstractmethod
from queue import Queue
import threading
import time
from queue import Empty

request_queue=Queue()
response_queue=Queue()

class RequestMessage:
    def __init__(self, SID=0x00, subfunction=0x00, dataID=None, data=None):
        self.SID = SID
        self.subfunction = subfunction
        self.dataID = dataID
        self.data = data
    def to_bytearray(self):
        byte_data = bytearray()
        byte_data.append(self.SID)
        if(self.subfunction): byte_data.append(self.subfunction)
        if(self.dataID): byte_data.append(self.dataID)  
        if(self.data): byte_data.append(self.data)
        return byte_data
    def __str__(self) -> str:
        SID_str = f"0x{self.SID:02X}" if self.SID is not None else "None"
        subfunction_str = f"0x{self.subfunction:02X}" if self.subfunction is not None else "None"
        dataID_str = f"0x{self.dataID:02X}" if self.dataID is not None else "None"
        data_str = f"0x{self.data:02X}" if self.data is not None else "None"
        return (f"PositiveResponseMessage(SID={SID_str}, subfunction={subfunction_str}, dataID={dataID_str}, data={data_str})")
    
class ResponseMessage(ABC):
    @abstractmethod
    def is_positive(self) -> bool:
        pass
    @abstractmethod
    def __str__(self) -> str:
        pass

class PositiveResponseMessage(ResponseMessage):
    def __init__(self, SID=0x00, subfunction=0x00, dataID=0x00, data=0x00):
        self.SID = SID
        self.subfunction = subfunction
        self.dataID = dataID
        self.data = data
    def is_positive(self) -> bool:
        return True
    def __str__(self) -> str:
        SID_str = f"0x{self.SID:02X}" if self.SID is not None else "None"
        subfunction_str = f"0x{self.subfunction:02X}" if self.subfunction is not None else "None"
        dataID_str = f"0x{self.dataID:02X}" if self.dataID is not None else "None"
        data_str = f"0x{self.data:02X}" if self.data is not None else "None"
        return (f"PositiveResponseMessage(SID={SID_str}, subfunction={subfunction_str}, dataID={dataID_str}, data={data_str})")

class NegativeResponseMessage(ResponseMessage):
    def __init__(self, SID=0x7F, SIDRQ=0x00, NRC=0x00):
        self.SID = SID
        self.SIDRQ = SIDRQ
        self.NRC = NRC
    def is_positive(self) -> bool:
        return False
    def __str__(self) -> str:
        SID_str = f"0x{self.SID:02X}" if self.SID is not None else "None"
        SIDRQ_str = f"0x{self.SIDRQ:02X}" if self.SIDRQ is not None else "None"
        NRC_str = f"0x{self.NRC:02X}" if self.NRC is not None else "None"
        return (f"NegativeResponseMessage(SID={SID_str}, SIDRQ={SIDRQ_str}, NRC={NRC_str})")
    

# class MessageListener:
#     def __init__(self, request_queue, response_queue, handler_map, period=1/60):
#         """
#         request_queue: 队列，接收请求消息
#         response_queue: 队列，放入响应消息
#         handler_map: dict，SID到处理函数的映射，格式 {SID: function(req, listener)}
#         period: 循环周期，秒
#         """
#         self.request_queue = request_queue
#         self.response_queue = response_queue
#         self.handler_map = handler_map
#         self.period = period
#         self.running = False

#     def start(self):
#         self.running = True
#         threading.Thread(target=self._loop, daemon=True).start()

#     def stop(self):
#         self.running = False

#     def _loop(self):
#         while self.running:
#             start_time = time.time()
#             processing_request = False
#             try:
#                 req = self.request_queue.get_nowait()
#                 print(f"[Listener] Received {req}")
#                 processing_request = True

#                 def handle_request():
#                     handler = self.handler_map.get(req.SID)
#                     if handler:
#                         resp = handler(req, self)
#                         self.response_queue.put(resp)
#                         print(f"[Listener] Sent {resp}")
#                     else:
#                         print(f"[Listener] No handler for SID {req.SID}")

#                 handler_thread = threading.Thread(target=handle_request)
#                 handler_thread.start()
#                 handler_thread.join(timeout=self.period)  # 以周期时间作为超时
#                 if handler_thread.is_alive():
#                     print("[Listener] Handler timeout!")
#                     # 这里示例放入一个通用超时响应
#                     resp = NegativeResponseMessage(SIDRQ=req.SID, NRC=0x78)
#                     self.response_queue.put(resp)
#                 else:
#                     processing_request = False

#             except Empty:
#                 # 没有请求，正常等待周期
#                 pass

#             # 周期控制，避免CPU空转
#             elapsed = time.time() - start_time
#             sleep_time = self.period - elapsed
#             if sleep_time > 0 and not processing_request:
#                 time.sleep(sleep_time)