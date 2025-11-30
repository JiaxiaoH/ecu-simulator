# sid_0x11.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID

SID = 0x11
class SID_0x11(BaseSID):
    SUPPORTED_SESSIONS={
        SESSIONS.PROGRAMMING_SESSION,
        #SESSIONS.EXTENDED_SESSION,
        #SESSIONS.ENGINEERING_SESSION,
        #SESSIONS.FOTAACTIVE_SESSION,
        #SESSIONS.FOTAINSTALL_SESSION,
        #SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F)
            if cls.check_length(request, min_length=2) is False:
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_resetType_supported(request):
                return cls.NegativeResponse(ecu, 0x12)
            if cls.check_length(request, expected_length=2) is False:
                return cls.NegativeResponse(ecu, 0x13)
            if cls.is_car_moving(ecu):
                return cls.NegativeResponse(ecu, 0x22) 
            ecu.hard_reset()
            return cls.PositiveResponse(ecu, [0x51, 0x01])
        except Exception as e:
                    print(f"[ERROR] SID_0x11 error: {e}")
                    import traceback
                    traceback.print_exc()
    @staticmethod
    def is_resetType_supported(request):
        return request.data[1] == 0x01
    
register_sid(SID, SID_0x11)