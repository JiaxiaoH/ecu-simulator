# sid_0x28.py
from sessiontypes import SESSIONS 
from uds_sid import BaseSID
class SID_0x28(BaseSID):
    SUPPORTED_SESSIONS={
        #SESSIONS.DEFAULT_SESSION,
        #SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        #SESSIONS.FOTAACTIVE_SESSION,
        #SESSIONS.FOTAINSTALL_SESSION,
        #SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F) 
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_controlType_supported(request):
                return cls.NegativeResponse(ecu, 0x12)
            if not cls.is_request_message_3_byte(request):
                 return cls.NegativeResponse(ecu, 0x13)        
            if not cls.is_communicationType_supported(request):
                 return cls.NegativeResponse(ecu, 0x31)
            
            ecu.communication_control()

            return cls.PositiveResponse(ecu, [0x68, 0x03])      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X28 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_controlType_supported(request):
        return request.data[1] == 0x03

    @staticmethod
    def is_communicationType_supported(request):
        return request.data[2] == 0x03