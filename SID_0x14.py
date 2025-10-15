# sid_0x14.py
import time
from sessiontypes import SESSIONS 
import can
import datetime
class SID_0x14:

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
            if cls.is_memory_error(ecu):
                 return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x72], is_extended_id=False)          
            ecu.dtc_clear()
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x54], is_extended_id=False)          
            
        except Exception as e:
                    print(f"[ERROR] SID_0X14 error: {e}")
                    import traceback
                    traceback.print_exc()
            

    #查找groupOfDtc是否被支持
    def is_groupOfDtc_supported(request):
        return request.data == bytes([0x14, 0xff, 0xff, 0xff])
    
    #查找session是否被支持
    def is_session_supported(session):
        return session!=SESSIONS.PROGRAMMING_SESSION
    
    #查找request message是否为4byte
    def is_request_message_4_byte(request):
        return len(request.data) == 4

    #检查车辆运行条件
    def is_car_moving(ecu):
         return ecu.moving
    
    def is_memory_error(ecu):
         return ecu.is_memory_error