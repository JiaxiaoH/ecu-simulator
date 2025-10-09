from abc import ABC, abstractmethod
from queue import Queue
import threading
import time
from queue import Empty
import datetime
request_queue=Queue()
response_queue=Queue()

class CanMessage(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def is_request(self) -> bool:
        return isinstance(self, RequestMessage)

    def is_response(self) -> bool:
        return isinstance(self, ResponseMessage)
    #about tree: something about tree or ecu maybe deleted after report...
    def log_to_treeview(self, tree, ecu):
        #Time
        now_str = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]  # ms
        msg_str = str(self)
        if self.is_request():
            direction = "Rx"
        elif self.is_response():
            direction = "Tx"
        else:
            direction = "Unknown"
        tree.insert('', 'end', values=[now_str, direction, msg_str, ecu.DiagnosticSession, ecu.security, ''])
        tree.see(tree.get_children()[-1])

    def to_bytearray(self):
        byte_data = bytearray()
        byte_data.append(self.SID)
        if self.subfunction is not None:
            byte_data.append(self.subfunction)
        # dataID 拆成高低字节
        if self.dataID is not None:
            byte_data.append((self.dataID >> 8) & 0xFF)
            byte_data.append(self.dataID & 0xFF)
        # data 拆成高低字节
        if self.data is not None:
            byte_data.append((self.data >> 8) & 0xFF)
            byte_data.append(self.data & 0xFF)
        return byte_data

class RequestMessage(CanMessage):
    def __init__(self, SID=0x00, subfunction=0x00, dataID=None, data=None):
        self.SID = SID
        self.subfunction = subfunction
        self.dataID = dataID
        self.data = data

    def __str__(self) -> str:
        # SID_str = f"{self.SID:02X}" if self.SID is not None else "  "
        # subfunction_str = f"{self.subfunction:02X}" if self.subfunction is not None else "  "
        # dataID_str = f"{self.dataID:02X}" if self.dataID is not None else "  "
        # data_str = f"{self.data:02X}" if self.data is not None else "  "
        # return (f"{SID_str} {subfunction_str} {dataID_str} {data_str}")
        SID_str = f"{self.SID:02X}" if self.SID is not None else "  "
        subfunction_str = f"{self.subfunction:02X}" if self.subfunction is not None else "  "
        if self.dataID is None:
            dataID_str = "  "
        elif isinstance(self.dataID, int):
            if self.dataID > 0xFF:
                dataID_str = f"{(self.dataID >> 8) & 0xFF:02X} {self.dataID & 0xFF:02X}"
            else:
                dataID_str = f"{self.dataID:02X}"
        elif isinstance(self.dataID, list):
            dataID_str = " ".join(f"{b:02X}" for b in self.dataID)
        else:
            dataID_str = str(self.dataID)
        # data部分以空格分隔的两位十六进制数列展示
        if self.data is not None:
            if isinstance(self.data, int):
                data_str = f"{self.data:02X}"
            else:
                data_str = " ".join(f"{b:02X}" for b in self.data)
        else:
            data_str = ""
        return f"{SID_str} {subfunction_str} {dataID_str} {data_str}".strip()
    def to_bytearray(self):
        byte_data = bytearray()
        byte_data.append(self.SID)
        
        if self.subfunction is not None:
            byte_data.append(self.subfunction)
        
        if self.dataID is not None:
            if isinstance(self.dataID, int):
                # 如果是整数（向后兼容）
                if self.dataID > 0xFF:
                    byte_data.append((self.dataID >> 8) & 0xFF)
                    byte_data.append(self.dataID & 0xFF)
                else:
                    byte_data.append(self.dataID & 0xFF)
            elif isinstance(self.dataID, list):
                byte_data.extend(self.dataID)
        
        if self.data:
            byte_data.extend(self.data)
        
        return byte_data

class ResponseMessage(CanMessage):
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
        SID_str = f"{self.SID:02X}" if self.SID is not None else "  "
        subfunction_str = f"{self.subfunction:02X}" if self.subfunction is not None else "  "
        if self.dataID is None:
            dataID_high_str = "  "
            dataID_low_str = "  "
        else:
            dataID_high = (self.dataID >> 8) & 0xFF
            dataID_low = self.dataID & 0xFF
            dataID_high_str = f"{dataID_high:02X}"
            dataID_low_str = f"{dataID_low:02X}"
        if self.data is None:
            data_high_str = "  "
            data_low_str = "  "
        else:
            data_high = (self.data >> 8) & 0xFF
            data_low = self.data & 0xFF
            data_high_str = f"{data_high:02X}"
            data_low_str = f"{data_low:02X}"
        return (f"{SID_str} {subfunction_str} "
                f"{dataID_high_str} {dataID_low_str} "
                f"{data_high_str} {data_low_str}")

class NegativeResponseMessage(ResponseMessage):
    def __init__(self, SID=0x7F, SIDRQ=0x00, NRC=0x00):
        self.SID = SID
        self.SIDRQ = SIDRQ
        self.NRC = NRC
    def is_positive(self) -> bool:
        return False
    def __str__(self) -> str:
        SID_str = f"{self.SID:02X}" if self.SID is not None else "  "
        SIDRQ_str = f"{self.SIDRQ:02X}" if self.SIDRQ is not None else "  "
        NRC_str = f"{self.NRC:02X}" if self.NRC is not None else "  "
        return (f"{SID_str} {SIDRQ_str} {NRC_str}")
    

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