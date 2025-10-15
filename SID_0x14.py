# sid_0x14.py
import time
from sessiontypes import SESSIONS 
import can
import datetime
from uds_sid import BaseSID
class SID_0x14(BaseSID):
    SUPPORTED_SESSIONS={
        SESSIONS.DEFAULT_SESSION,
        #SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.DiagnosticSession):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7F], is_extended_id=False)
            if not cls.is_request_message_4_byte(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False)          
            if not cls.is_groupOfDtc_supported(request):
                 return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x31], is_extended_id=False)          
            if cls.is_car_moving(ecu):
                 return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x22], is_extended_id=False)          
            ecu.dtc_clear()
            if cls.is_memory_error(ecu):
                 return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x72], is_extended_id=False)          
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x54], is_extended_id=False)          
            
        except Exception as e:
                    print(f"[ERROR] SID_0X14 error: {e}")
                    import traceback
                    traceback.print_exc()
            

    #查找groupOfDtc是否被支持
    def is_groupOfDtc_supported(request):
        return request.data == bytes([0x14, 0xff, 0xff, 0xff])