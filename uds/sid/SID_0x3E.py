# sid_0x3E.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
SID = 0x3E
class SID_0x3E(BaseSID):
    SUPPORTED_SESSIONS={
        SESSIONS.DEFAULT_SESSION,
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
            if cls.check_length(request, min_length=2) is False:
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_zeroSubFunction_supported(request):
                return cls.NegativeResponse(ecu, 0x12)
            if cls.check_length(request, expected_length=2) is False:
                 return cls.NegativeResponse(ecu, 0x13)        
            
            ecu.extend_delay()

            return cls.PositiveResponse(ecu, [0x7E, 0x00])      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X3E error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_zeroSubFunction_supported(request):
        return request.data[1] == 0x00

register_sid(SID, SID_0x3E)