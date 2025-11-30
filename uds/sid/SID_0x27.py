# sid_0x27.py
# skip TypeIV
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from security import SecurityType
# import secrets
# from Crypto.Cipher import AES
from keys import AES_KEY, XOR_MASK
SID = 0x27
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
            SecurityType.TYPE_V: [0x07, 4, 10], 
            SecurityType.TYPE_X: [0x31, 18, 0], 
            #SecurityType.TYPE_IV: [0x41, 5, 0]
            },
        "sendKey": {
            SecurityType.TYPE_V: [0x08, 4, 0], 
            SecurityType.TYPE_X: [0x32, 18, 0], 
            #SecurityType.TYPE_IV: [0x42, 5, 0]
            }
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            sc2=[0x00, 0x00]
            securityCode=[0x00, 0x00]
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F) 
            if cls.check_length(request, min_length=2) is False:
                return cls.NegativeResponse(ecu, 0x13)
            
            securityType=SID_0x27.get_security_access_type(request)
            if securityType is None:
                return cls.NegativeResponse(ecu, 0x12)
            else:
                category, type_name=securityType
                if category == "requestSeed":
                    if cls.check_length(request, expected_length=2) is False:
                        return cls.NegativeResponse(ecu, 0x13)
                    if ecu.illegal_access>0:
                        return cls.NegativeResponse(ecu, 0x37)
                    if ecu.dt_igon<SID_0x27.SECURITYACCESSTYPE[category][type_name][2]:
                        return cls.NegativeResponse(ecu, 0x37)
                    if ecu.security != SecurityType.FALSE:
                        # if type_name=="TypeIV":
                        #     return cls.PositiveResponse(ecu, [0x67, 0x41, 0x00, 0x00, 0x00, 0x00, 0x00])
                        if type_name == SecurityType.TYPE_V:
                            return cls.PositiveResponse(ecu, [0x67, 0x07, 0x00, 0x00, 0x00, 0x00])
                        if type_name == SecurityType.TYPE_X:
                            return cls.PositiveResponse(ecu, [0x67, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                    else:
                        # if type_name==SecurityType.TYPE_IV:
                        #     RN4=[0x00, 0x00, 0x00, 0x00] 
                        #     SC=[0x00]
                        #     return cls.PositiveResponse(ecu, [0x67, 0x41]+RN4+SC)
                        if type_name==SecurityType.TYPE_V:
                            rn2=cls.random_hex_list(2)
                            kc2=cls.calc_kc2(rn2)
                            ecu.key=kc2
                            print(f"key="+ ''.join(f"{b:02X} " for b in kc2))
                            return cls.PositiveResponse(ecu, [0x67, 0x07] + rn2 + sc2)
                        if type_name==SecurityType.TYPE_X:
                            securitySeed=cls.random_hex_list(16)
                            securityAccessDataRecord=cls.aes128_encrypt(securitySeed,AES_KEY)
                            ecu.key=securityAccessDataRecord
                            print(f"key="+ ''.join(f"{b:02X} " for b in securityAccessDataRecord))
                            return cls.PositiveResponse(ecu, [0x67, 0x31] + securitySeed + securityCode)
                elif category == "sendKey":
                    if ecu.security != SecurityType.FALSE:
                        # if type_name==SecurityType.Type_IV:
                        #     return cls.PositiveResponse(ecu, [0x67, 0x42])
                        if type_name == SecurityType.TYPE_V:
                            return cls.PositiveResponse(ecu, [0x67, 0x08])
                        if type_name == SecurityType.TYPE_X:
                            return cls.PositiveResponse(ecu, [0x67, 0x32])                              
                    else:
                        if ecu.key is None:
                            return cls.NegativeResponse(ecu, 0x24)
                        if len(request.data) != SID_0x27.SECURITYACCESSTYPE[category][type_name][1]:  
                            return cls.NegativeResponse(ecu, 0x13)
                        if not request.data[2:] == bytearray(ecu.key):
                            ecu.key=None
                            ecu.illegal_access+=1
                            return cls.NegativeResponse(ecu, 0x36)
                        # if type_name == SecurityType.TYPE_IV:
                        #   return cls.PositiveResponse(ecu, [0x67, 0x08])
                        if type_name == SecurityType.TYPE_V:
                            ecu.security=SecurityType.TYPE_V
                            return cls.PositiveResponse(ecu, [0x67, 0x08] )
                        if type_name == SecurityType.TYPE_X:
                            ecu.security=SecurityType.TYPE_X
                            return cls.PositiveResponse(ecu, [0x67, 0x32] )                    
                
        except Exception as e:
                    print(f"[ERROR] SID_0x27 error: {e}")
                    import traceback
                    traceback.print_exc()
    
    @staticmethod
    def get_security_access_type(request):
        for category, type_dict in SID_0x27.SECURITYACCESSTYPE.items():
            for type_name, type_value in type_dict.items():
                if isinstance(type_value, list) and type_value[0] == request.data[1]:
                    return category, type_name
        return None         

    @staticmethod
    def is_communicationType_supported(request):
        return request.data[2] == 0x03
    
    @staticmethod
    def calc_kc2(rn2: list[int]) -> list[int]:
        if len(rn2) != 2:
            raise ValueError("RN2 must be length 2")
        kc2 = [b ^ m for b, m in zip(rn2, XOR_MASK)]
        return kc2
    
register_sid(SID, SID_0x27)