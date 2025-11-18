# sid_0x2E.py
from ..sid_registry import register_sid
from .uds_sid import BaseSID
SID = 0x2E
class SID_0x2E(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        try:
            
            if cls.is_request_message_less_than_4_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            high = request.data[1]
            low = request.data[2]
            did_value = (high << 8) + low
            data_record=list(request.data[3:])
            if not cls.is_did_session_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x31)      
            if not cls.is_did_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x31)
            if len(data_record)!=ecu.did.get_data_record_length(did_value):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_did_security_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x33)
            if not cls.is_did_driving_supported(ecu, did_value):
                return cls.NegativeResponse(ecu, 0x22)
            if not cls.is_data_record_supported(ecu, did_value, data_record):
                return cls.NegativeResponse(ecu, 0x31)
            if ecu.is_memory_error:
                return cls.NegativeResponse(ecu, 0x72)

            ecu.did.write_data_record(did_value, data_record)
            return cls.PositiveResponse(ecu, [0x6E, request.data[1], request.data[2]])    
            
        except Exception as e:
                    print(f"[ERROR] SID_0X2E error: {e}")
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
            not entry.supported_security_0x2E
            or entry.supported_security_0x2E == "all"
            or ecu.security in entry.supported_security_0x2E
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
    def is_data_record_supported(ecu, did, data_record):
        data=ecu.did.read_did(did)
        if did==0x48F5:
            return (data_record[1:]==data[1:] and data_record[0]==0x01 and not all(x == 0x30 for x in data_record[0x01:0x05]))
        elif did==0xA19D:
            return True
        else:
            return False

register_sid(SID, SID_0x2E)