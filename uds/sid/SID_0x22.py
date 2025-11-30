# sid_0x22.py
from ..sid_registry import register_sid
from .uds_sid import BaseSID
SID = 0x22
class SID_0x22(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.check_length(request, min_length=3) is False:
                return cls.NegativeResponse(ecu, 0x13)
            if cls.is_request_message_even(request):
                return cls.NegativeResponse(ecu, 0x13)      
            if cls.check_length(request, max_length=13) is False:
                 return cls.NegativeResponse(ecu, 0x13)
            res=[]
            data=request.data[1:]
            for i in range(0, len(data), 2):  
                high = data[i]
                low = data[i + 1]
                did_value = (high << 8) + low
                
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
                    print(f"[ERROR] SID_0x22 error: {e}")
                    import traceback
                    traceback.print_exc()

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

register_sid(SID, SID_0x22)