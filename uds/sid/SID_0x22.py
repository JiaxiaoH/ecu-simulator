# sid_0x22.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from did import DIDManager
SID = 0x22
class SID_0x22(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.is_request_message_less_than_3_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_request_message_even(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_request_message_3_byte(request):
                 return cls.NegativeResponse(ecu, 0x13)        
            if not cls.is_message_longer_than_available(request):
                 return cls.NegativeResponse(ecu, 0x13)
            res=None
            data=request.data[1:]
            for i in range(0, len(data, 2)):  
                did = []
                high = data[i]
                low = data[i + 1]
                value = (high << 8) + low
                did.append(value)
                if not cls.is_did_supported(ecu, did):
                    continue
                elif not cls.match_session(ecu, did):
                    continue
                elif not cls.check_did_security(ecu, did):
                    return cls.NegativeResponse(ecu, 0x33)
                elif not cls.check_did_driving(ecu, did):
                    return cls.NegativeResponse(ecu, 0x22)
                elif not cls.check_did_refused(ecu, did):
                    return cls.NegativeResponse(ecu, 0x10)
                res=res + [high, low] + ecu.finddataRecord(did)

            return cls.PositiveResponse(ecu, [0x62]+res)      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X28 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_message_longer_than_available(request):
        return len(request.data)>13

    @staticmethod
    def is_did_supported(did):
        return did

register_sid(SID, SID_0x22)