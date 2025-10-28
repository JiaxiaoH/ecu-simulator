# sid_0x27.py
# skip TypeIV
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from security import SecurityType
import secrets
from Crypto.Cipher import AES
from keys import AES_KEY
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
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            
            securityType=SID_0x27.get_security_access_type(request)
            if securityType is None:
                return cls.NegativeResponse(ecu, 0x12)
            else:
                category, type_name=securityType
                if category == "requestSeed":
                    if not cls.is_request_message_2_byte(request):
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
                            print(f"key="+ ''.join(f"{b:02X}' '" for b in kc2))
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
                        #     return cls.PositiveResponse(ecu, [0x67, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00])
                        if type_name == SecurityType.TYPE_V:
                            return cls.PositiveResponse(ecu, [0x67, 0x08, 0x00, 0x00, 0x00, 0x00])
                        if type_name == SecurityType.TYPE_X:
                            return cls.PositiveResponse(ecu, [0x67, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])                              
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
                        #   return cls.PositiveResponse(ecu, [0x67, 0x08]+kc2+sc2)
                        if type_name == SecurityType.TYPE_V:
                            ecu.security=SecurityType.TYPE_V
                            return cls.PositiveResponse(ecu, [0x67, 0x08] + ecu.key + sc2)
                        if type_name == SecurityType.TYPE_X:
                            ecu.security=SecurityType.TYPE_X
                            return cls.PositiveResponse(ecu, [0x67, 0x32] + ecu.key)                    
                
        except Exception as e:
                    print(f"[ERROR] SID_0X27 error: {e}")
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
    def random_hex_list(x: int) -> list[int]:
        random_bytes = secrets.token_bytes(x)
        return [b for b in random_bytes]
    
    @staticmethod
    def calc_kc2(rn2: list[int]) -> list[int]:
        xor_mask = [0xA0, 0xB0]
        if len(rn2) != 2:
            raise ValueError("RN2 must be length 2")
        kc2 = [b ^ m for b, m in zip(rn2, xor_mask)]
        return kc2
    
    @staticmethod
    def aes128_encrypt(hex_list: list[int], key_list: list[int]) -> list[int]:
        if len(hex_list) != 16 or len(key_list) != 16:
            raise ValueError("Error: data is not 16 bytes!")
        data_bytes = bytes(hex_list)
        key_bytes = bytes(key_list)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        encrypted = cipher.encrypt(data_bytes)
        return list(encrypted)
    
register_sid(SID, SID_0x27)