# sid_0x11.py
#import time
from sessiontypes import SESSIONS 
#import can
#import datetime
from uds_sid import BaseSID
class SID_0x11(BaseSID):
    SUPPORTED_SESSIONS={
        SESSIONS.PROGRAMMING_SESSION,
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
                return cls.NegativeResponse(ecu, 0x7F)
                #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7F], is_extended_id=False)
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
                #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False)          
            if not cls.is_resetType_supported(request):
                return cls.NegativeResponse(ecu, 0x12)
                 #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x12], is_extended_id=False)          
            if not cls.is_request_message_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
                 #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False)          
            if cls.is_car_moving(ecu):
                return cls.NegativeResponse(ecu, 0x22) 
                #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x22], is_extended_id=False)          
            ecu.hard_reset()
            return cls.PositiveResponse(ecu, [0x51, 0x01])
            #return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x51, 0x01], is_extended_id=False)          
            
        except Exception as e:
                    print(f"[ERROR] SID_0X11 error: {e}")
                    import traceback
                    traceback.print_exc()

    # def is_request_message_less_than_2_byte(request):
    #     return len(request.data) < 2    
      
    def is_resetType_supported(request):
        return request.data[1] == 0x01
    
    # def is_session_supported(session):
    #     return session!=SESSIONS.DEFAULT_SESSION

    # def is_request_message_2_byte(request):
    #     return len(request.data) == 2

    # def is_car_moving(ecu):
    #      return ecu.moving
    
    # def is_memory_error(ecu):
    #      return ecu.is_memory_error