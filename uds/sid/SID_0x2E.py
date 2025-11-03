# sid_0x2E.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from did import DIDManager
SID = 0x2E
class SID_0x2E(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        try:
            did_value=request.data[1:2]
            dids = []
            for i in range(0, len(data), 2):  
                high = data[i]
                low = data[i + 1]
                did_value = (high << 8) + low
                dids.append(did_value)            
            if cls.is_request_message_less_than_4_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_did_session_supported(request):
                return cls.NegativeResponse(ecu, 0x31)      
            if not cls.is_did_supported(request):
                return cls.NegativeResponse(ecu, 0x31)
            if len(request.data)!=ecu.did.cal_length(request.data):
                return cls.Negativeresponse(ecu, 0x13)
            if not cls.is_did_security_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x33)
            if not cls.is_did_driving_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x22)
            if not cls.is_datarecord_ok(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x31)
            if ecu.is_memory_error(ecu):
                return cls.NegativeResponse(ecu, 0x72)

            do_0x2E()
            return cls.PositiveResponse(ecu, [request.data[1], request.data[2]])

            res=[]
            data=request.data[1:]
            dids = []
            for i in range(0, len(data), 2):  
                high = data[i]
                low = data[i + 1]
                did_value = (high << 8) + low
                dids.append(did_value)
                
                if not cls.is_did_supported(ecu, did_value):
                    continue
                elif not cls.is_did_session_supported(ecu, did_value):
                    continue
                elif not cls.is_did_security_supported(ecu, did_value):
                    return cls.NegativeResponse(ecu, 0x33)
                elif not cls.is_did_driving_supported(ecu, did_value):
                    return cls.NegativeResponse(ecu, 0x22)
                elif not cls.is_did_refused(ecu, did_value):
                    return cls.NegativeResponse(ecu, 0x10)
                res=res + [high, low] + ecu.find_dataRecord(did_value)
            if len(res)==0:
                return cls.NegativeResponse(ecu, 0x31)
            return cls.PositiveResponse(ecu, [0x62]+res)      
            
        except Exception as e:
                    print(f"[ERROR] SID_0X22 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def is_message_longer_than_available(request):
        return len(request.data)>13

    @staticmethod
    def is_did_supported(ecu, did):
        return ecu.did.is_supported(did)

    @staticmethod
    def is_did_session_supported(ecu, did):
        entry=ecu.did.supported_dids.get(did)
        if not entry:
            return False
        return ecu.session in entry.supported_sessions if entry.supported_sessions else True

    @staticmethod
    def is_did_security_supported(ecu, did):
        entry=ecu.did.supported_dids.get(did)
        if not entry:
            return False
        return (
            not entry.supported_security_levels
            or entry.supported_security_levels == "all"
            or ecu.security in entry.supported_security_levels
        )

    @staticmethod
    def is_did_driving_supported(ecu, did):
        entry=ecu.did.supported_dids.get(did)
        if not entry:
            return False
        return (
            not entry.supported_driving
            or entry.supported_driving == "all"
            or ecu.moving in entry.supported_driving
        )

    @staticmethod
    def is_did_refused(ecu, did):
        entry=ecu.did.supported_dids.get(did)
        if not entry:
            return False
        return (
            not entry.refusal
            or entry.refusal == "all"
            #or ecu.dtc in entry.refusal
        )

register_sid(SID, SID_0x2E)