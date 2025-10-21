# sid_0x85.py
from sessiontypes import SESSIONS 
from uds_sid import BaseSID
class SID_0x85(BaseSID):
    SUPPORTED_SESSIONS={
        #SESSIONS.DEFAULT_SESSION,
        #SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        #SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        #SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F)
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_DTCSettingType_supported(request):
                 return cls.NegativeResponse(ecu, 0x12)        
            if not cls.is_request_message_2_byte(request):
                 return cls.NegativeResponse(ecu, 0x13)
            
            ecu.dtc_setting()

            return cls.PositiveResponse(ecu, [0xC5, 0x02])      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X14 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_DTCSettingType_supported(request):
        return request.data[1] == 0x02