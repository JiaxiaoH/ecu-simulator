# sid_0x27.py
from sessiontypes import SESSIONS 
from uds_sid import BaseSID
class SID_0x27(BaseSID):
    SUPPORTED_SESSIONS={
        #SESSIONS.DEFAULT_SESSION,
        #SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    SECURITYACCESSTYPE = {
        "requestSeed": {
            "TypeV": 0x07, 
            "TypeX": 0x31, 
            #"TypeIV": 0x41
            },
        "sendKey": {
            "TypeV": 0x08, 
            "TypeX": 0x32, 
            #"TypeIV": 0x42
            }
    }

    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F) 
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            
            securityType=SID_0x27.get_security_access_type(request)
            category, type_name=securityType
            if securityType is None:
                return cls.NegativeResponse(ecu, 0x12)
            elif category == "requestSeed":
                if not cls.is_request_message_2_byte(request):
                     return cls.NegativeResponse(ecu, 0x13)
                if ecu.illegal_access>0:
                     return cls.NegativeResponse(ecu, 0x37)
                if ecu.dt_igon<10 and type_name=="TypeV":
                     return cls.NegativeResponse(ecu, 0x37)
                if ecu.security is not None:
                    # if type_name=="TypeIV":
                    #     return cls.PositiveResponse(ecu, [0x67, 0x41, 0x00, 0x00, 0x00, 0x00, 0x00])
                    if type_name=="TypeV":
                        return cls.PositiveResponse(ecu, [0x67, 0x07, 0x00, 0x00, 0x00, 0x00])
                    if type_name=="TypeX":
                        return cls.PositiveResponse(ecu, [0x67, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                else:
                    # if type_name=="TypeIV":
                    #     RN4=[0x00, 0x00, 0x00, 0x00] 
                    #     SC=[0x00]
                    #     return cls.PositiveResponse(ecu, [0x67, 0x41]+RN4+SC)
                    if type_name=="TypeV":
                        RN2=[0x00, 0x00]
                        SC2=[0x00, 0x00]
                        return cls.PositiveResponse(ecu, [0x67, 0x07]+RN2+SC2)
                    if type_name=="TypeX":
                        securitySeed=[0x00, 0x00]
                        securityCode=[0x00, 0x00]
                        return cls.PositiveResponse(ecu, [0x67, 0x31]+securitySeed+securityCode)
            if not cls.is_request_message_3_byte(request):
                 return cls.NegativeResponse(ecu, 0x13)        
            if not cls.is_communicationType_supported(request):
                 return cls.NegativeResponse(ecu, 0x31)
            
            ecu.communication_control()

            return cls.PositiveResponse(ecu, [0x68, 0x03])      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X27 error: {e}")
                    import traceback
                    traceback.print_exc()
    
    @staticmethod
    def get_security_access_type(request):
        for category, type_dict in SID_0x27.SECURITYACCESSTYPE.items():
            for type_name, type_value in type_dict.items():
                if type_value == request.data[1]:
                    return category, type_name
        return None         

    @staticmethod
    def is_communicationType_supported(request):
        return request.data[2] == 0x03