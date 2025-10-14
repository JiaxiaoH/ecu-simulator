# sid_0x10.py
import time
#from ecu import ECU
from sessiontypes import SESSIONS 
import can
import datetime
class SID_0x10:
    AvailableSubFuncs={
        SESSIONS.DEFAULT_SESSION,
        SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    SESSION_SUPPORTED_SUBFUNCS = {
        SESSIONS.DEFAULT_SESSION: {SESSIONS.DEFAULT_SESSION, SESSIONS.EXTENDED_SESSION},
        SESSIONS.PROGRAMMING_SESSION: {SESSIONS.PROGRAMMING_SESSION},
        SESSIONS.EXTENDED_SESSION: {SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION,SESSIONS.FOTAACTIVE_SESSION,SESSIONS.FOTAINSTALL_SESSION,SESSIONS.FOTAINSTALLACTIVE_SESSION},
        SESSIONS.ENGINEERING_SESSION:{SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION},
        SESSIONS.FOTAINSTALLACTIVE_SESSION: {SESSIONS.FOTAINSTALLACTIVE_SESSION},
        SESSIONS.FOTAINSTALL_SESSION: {SESSIONS.DEFAULT_SESSION, SESSIONS.FOTAINSTALL_SESSION},
        SESSIONS.FOTAACTIVE_SESSION: {SESSIONS.FOTAACTIVE_SESSION}
    }

    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.is_request_message_less_than_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False)
            if not cls.is_subfuncs_supported(request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x12], is_extended_id=False)
        except Exception as e:
                    print(f"[ERROR] SID_0X10 error: {e}")
                    import traceback
                    traceback.print_exc()
        if request.data[1] == SESSIONS.DEFAULT_SESSION: 
            try:
                if not cls.is_session_supported(ecu.DiagnosticSession, request):
                    return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            except Exception as e:
                print(f"Error test: {e}")
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.PROGRAMMING_SESSION:
                #TODO: add sth...
                #
                #
            return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.EXTENDED_SESSION:
            if not cls.is_session_supported(ecu.DiagnosticSession, request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.ENGINEERING_SESSION:
            if not cls.is_session_supported(ecu.DiagnosticSession, request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            if (not ecu.security) and request.data[1]==0x4F:
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x33], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAINSTALL_SESSION:
                #TODO...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAACTIVE_SESSION:
                #TODO...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAINSTALLACTIVE_SESSION:
                #...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        else:
            print("Error: cannot match the subfunction")
            return None
    # @staticmethod
    # def PositiveResponse(can_bus, SID, subfunction, DID=[0x00, 0x32], data=[0x01, 0xF4]):
    #     sid_resp = SID + 0x40
    #     data_bytes = bytearray([sid_resp])
    #     if subfunction is not None:
    #         data_bytes.append(subfunction)

    #     # DID 和 data 直接拼接，假设是 list/tuple/bytes 或 None
    #     if DID:
    #         data_bytes.extend(DID)
    #     if data:
    #         data_bytes.extend(data)
    #     msg = can.Message(arbitration_id=0x7E8, data=data_bytes, is_extended_id=False)
    #     try:
    #         can_bus.send(msg)
    #         print(f"[ECU] Sent PositiveResponse: {msg}")
    #     except can.CanError as e:
    #         print(f"[ERROR] CAN send failed: {e}")
    # @staticmethod
    # def NegativeResponse(can_bus, SIDRQ, NRC):
    #     sid_resp = 0x7F  # UDS协议负响应SID固定为0x7F
    #     data_bytes = bytearray([sid_resp, SIDRQ, NRC])
    #     msg = can.Message(arbitration_id=0x7E8, data=data_bytes, is_extended_id=False)
    #     try:
    #         can_bus.send(msg)
    #         print(f"[ECU] Sent NegativeResponse: {msg}")
    #     except can.CanError as e:
    #         print(f"[ERROR] CAN send failed: {e}")
    #查找request message是否小于2byte
    def is_request_message_less_than_2_byte(request):
        return len(request.data) < 2

    #查找subfunction是否被支持
    def is_subfuncs_supported(request):
        return request.data[1] in SID_0x10.AvailableSubFuncs
    
    #查找session是否被支持
    def is_session_supported(session, request):
        supported_subfuncs = SID_0x10.SESSION_SUPPORTED_SUBFUNCS.get(session, set())
        return request.data[1] in supported_subfuncs
    
    #查找request message是否为2byte
    def is_request_message_2_byte(request):
        return len(request.data) == 2
