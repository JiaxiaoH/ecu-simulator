#dtc.py
import re
import math

class DTC:
    def __init__(self, data=[0x00, 0x00, 0x00, 0x00]):
        if not isinstance(data, (bytes, bytearray, list, tuple)):
            raise TypeError("data must be bytes, bytearray, list, or tuple")
        if len(data) != 4:
            raise ValueError("data must be exactly 4 bytes long")
        for b in data:
            if not (0 <= b <= 0xFF):
                raise ValueError("each byte must be 0-255")
        self._data = list(data)
    
    def _set_byte(self, index, value):
        if not (0 <= value <= 0xFF):
            raise ValueError(f"byte at index {index} must be 0-255")
        self._data[index] = value

    @property
    def high(self):
        return self._data[0]
    
    @high.setter
    def high(self, value):
        self._set_byte(0, value)

    @property
    def mid(self):
        return self._data[1]
    
    @mid.setter
    def mid(self, value):
        self._set_byte(1, value)

    @property
    def low(self):
        return self._data[2]
    
    @low.setter
    def low(self, value):
        self._set_byte(2, value)

    @property
    def status(self):
        return self._data[3]

    @status.setter
    def status(self, value):
        self._set_byte(3, value)

    def to_bytes(self):
        return bytes(self._data)

    def to_list(self):
        return self._data.copy()

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._set_byte(index, value)

    def __repr__(self):
        return " ".join(f"{b:02X}" for b in self._data)
        
    def _get_status_bit(self, bit):
        return (self.status >> bit) & 1

    def _set_status_bit(self, bit, val):
        if val:
            self.status = self.status | (1 << bit)
        else:
            self.status = self.status & ~(1 << bit)

    @property
    def testFailed(self):
        return bool(self._get_status_bit(0))

    @testFailed.setter
    def testFailed(self, val):
        self._set_status_bit(0, val)

    @property
    def testFailedThisMonitoringCycle(self):
        return bool(self._get_status_bit(1))

    @testFailedThisMonitoringCycle.setter
    def testFailedThisMonitoringCycle(self, val):
        self._set_status_bit(1, val)

    @property
    def pendingDTC(self):
        return bool(self._get_status_bit(2))

    @pendingDTC.setter
    def pendingDTC(self, val):
        self._set_status_bit(2, val)

    @property
    def confirmedDTC(self):
        return bool(self._get_status_bit(3))

    @confirmedDTC.setter
    def confirmedDTC(self, val):
        self._set_status_bit(3, val)

    @property
    def testNotCompletedSinceLastClear(self):
        return bool(self._get_status_bit(4))

    @testNotCompletedSinceLastClear.setter
    def testNotCompletedSinceLastClear(self, val):
        self._set_status_bit(4, val)

    @property
    def testFailedSinceLastClear(self):
        return bool(self._get_status_bit(5))

    @testFailedSinceLastClear.setter
    def testFailedSinceLastClear(self, val):
        self._set_status_bit(5, val)

    @property
    def testNotCompletedThisMonitoringCycle(self):
        return bool(self._get_status_bit(6))

    @testNotCompletedThisMonitoringCycle.setter
    def testNotCompletedThisMonitoringCycle(self, val):
        self._set_status_bit(6, val)

    @property
    def warningIndicatorRequested(self):
        return bool(self._get_status_bit(7))

    @warningIndicatorRequested.setter
    def warningIndicatorRequested(self, val):
        self._set_status_bit(7, val)

    @staticmethod
    def _dtc_string_to_hex(dtc: str) -> str:
        dtc = dtc.strip().upper().replace('-', '')
        pattern = r'^[PCBU][0-9A-F]+$'
        if not re.fullmatch(pattern, dtc):
            raise ValueError("Invalid DTC format.")
        map_first = {'P': 0b00, 'C': 0b01, 'B': 0b10, 'U': 0b11}
        first_val = map_first[dtc[0]]
        second_val = int(dtc[1])
        third_val = int(dtc[2], 16)
        combined=(first_val<<6) | (second_val <<4) | third_val
        hex_val = combined
        if len(dtc)==5:
            remaining_val = int(dtc[3:], 16)
            hex_val = (hex_val << 8) | remaining_val
        if len(dtc)==7:
            remaining_val = int(dtc[3:], 16)
            hex_val = (hex_val << 16) | remaining_val
        return hex(hex_val)[2:].upper()
    
    @classmethod
    def from_dtc_string(cls, dtc_str: str, status_byte: int = None):
        obj=cls()
        hex_value = obj._dtc_string_to_hex(dtc_str)
        bytes_data = bytes.fromhex(hex_value)
        for i in range(3):
            if i < len(bytes_data):
                obj._data[i] = bytes_data[i]
            else:
                obj._data[i] = 0x00
        if status_byte is not None:
            obj._data[3] = status_byte
        # else:
        #     self._data[3] = 0x00
        return obj

def check_dtc_setting(method):
    def wrapper(self, *args, **kwargs):
        if not self._dtc_setting:
            if method.__name__ == "__iadd__":
                return self
            elif method.__name__ == "__add__":
                return self
            else:
                # 
                return None
        return method(self, *args, **kwargs)
    return wrapper

class DTCManager:
    def __init__(self, dtc_list=None):
        self._dtc_list = dtc_list if dtc_list is not None else []
        self._dtc_setting = True 

    @check_dtc_setting
    def __iadd__(self, dtc_code: DTC):
        if dtc_code not in self._dtc_list:
            self._dtc_list.append(dtc_code)
        return self

    @check_dtc_setting
    def __add__(self, dtc_code: DTC):
        new_list = self._dtc_list.copy()
        if dtc_code not in new_list:
            new_list.append(dtc_code)
        return DTCManager(new_list)

    def clear_dtc(self):
        self._dtc_list.clear()

    def get_dtcs(self):
        return self._dtc_list.copy()

    @property
    def dtc_list(self):
        return self._dtc_list.copy()    
    
    @property
    def dtc_setting(self):
        return self._dtc_setting
    
    @dtc_setting.setter
    def dtc_setting(self, value):
        self._dtc_setting=value

    def report_number(self, mask: int) -> int:
        count = 0
        for dtc in self._dtc_list:
            if (dtc.status & mask) != 0:
                count += 1
        high_byte = (count>>8) & 0xFF
        low_byte = count & 0xFF
        return [high_byte, low_byte]
    
    def report_dtc(self, mask: int) -> list[DTC]:
        result = []
        for dtc in self._dtc_list:
            if (dtc.status & mask) != 0:
                result+=dtc
        return result