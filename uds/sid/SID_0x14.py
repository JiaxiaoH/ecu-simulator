# sid_0x14.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
SID = 0x14
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
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F)
            if cls.check_length(request, expected_length=4) is False:
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_groupOfDtc_supported(request):
                 return cls.NegativeResponse(ecu, 0x31)        
            if cls.is_car_moving(ecu):
                 return cls.NegativeResponse(ecu, 0x22)
            ecu.dtc_clear()
            if cls.is_memory_error(ecu):
                 return cls.NegativeResponse(ecu, 0x72)
            return cls.PositiveResponse(ecu, [0x54])      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X14 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_groupOfDtc_supported(request):
        return request.data == bytes([0x14, 0xff, 0xff, 0xff])

register_sid(SID, SID_0x14)