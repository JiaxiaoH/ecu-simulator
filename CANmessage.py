from abc import ABC, abstractmethod
from queue import Queue

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