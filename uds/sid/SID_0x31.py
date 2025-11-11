# sid_0x31.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from did import DIDManager
SID = 0x31
class SID_0x31(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.is_request_message_less_than_4_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            routine_type=request.data[1]
            high = request.data[2]
            low = request.data[3]
            rid_value = (high << 8) + low
            routine_record=list(request.data[4:]) if len(request.data)>4 else None
            if not cls.is_rid_session_supported(ecu, rid_value):
                return cls.NegativeResponse(ecu, 0x31)      
            if not cls.is_rid_security_supported(ecu, rid_value):
                return cls.NegativeResponse(ecu, 0x33)
            if not cls.is_routine_type_supported(routine_type):
                return cls.NegativeResponse(ecu, 0x12)
            if not cls.is_req_length_supported(ecu, request.data, rid_value):
                return cls.NegativeResponse(ecu, 0x13)   
            if not cls.is_routine_record_supported(ecu, routine_type, rid_value, routine_record):
                return cls.NegativeResponse(ecu, 0x31)                                        
            if not cls.is_rid_driving_supported(ecu, rid_value):
                return cls.NegativeResponse(ecu, 0x22)
            if not cls.is_routine_order_supported(ecu, rid_value, routine_type):
                return cls.NegativeResponse(ecu, 0x24)
            if ecu.is_memory_error:
                return cls.NegativeResponse(ecu, 0x72)

            res=ecu.rid.func(rid_value, routine_type)
            if isinstance(res, list):
                return cls.PositiveResponse(ecu, [0x71]+[routine_type, high, low]+res)   
            else:
                return cls.NegativeResponse(ecu, res) 
            
        except Exception as e:
                    print(f"[ERROR] SID_0X31 error: {e}")
                    import traceback
                    traceback.print_exc()

    @staticmethod
    def is_rid_session_supported(ecu, rid):
        entry=ecu.rid.supported_rids.get(rid)
        if not entry:
            return False
        return ecu.session in entry.supported_sessions if entry.supported_sessions else True

    @staticmethod
    def is_rid_security_supported(ecu, rid):
        entry=ecu.rid.supported_rids.get(rid)
        if not entry:
            return False
        return (
            not entry.supported_security_levels
            or entry.supported_security_levels == "all"
            or ecu.security in entry.supported_security_levels
        )   

    @staticmethod
    def is_routine_type_supported(routine_type):
        return routine_type in [0x01, 0x02, 0x03]
        
    @staticmethod
    def is_rid_driving_supported(ecu, rid):
        entry=ecu.rid.supported_rids.get(rid)
        if not entry:
            return False
        return (
            not entry.supported_driving
            or entry.supported_driving == "all"
            or ecu.moving in entry.supported_driving
        )

    @staticmethod
    def is_routine_record_supported(ecu, routine_type, rid, routine_record):
        data=ecu.rid.read_rid_obj(rid)
        if rid==0xA1A3:
            if routine_type==0x01:
                return False if routine_record is None else routine_record[0] in data.aiming_mode_setting
            else:
                return True if routine_record is None else False
        elif rid==0xD111:
            return routine_type==0x01
        elif rid==0xFF00:
            return routine_type==0x01
        else:
            return False

    @staticmethod
    def is_routine_order_supported(ecu, rid_value, routine_type):
        return ecu.rid.is_routine_order_allowed(rid_value, routine_type)

    @staticmethod
    def is_req_length_supported(ecu, msg:list[int], rid:int):
        req_length=ecu.rid.get_req_length(rid, msg[1])
        if isinstance(req_length, int):
            return len(msg) == req_length
        elif isinstance(req_length, (list, tuple)):
            return len(msg) in req_length
        else:
            return False

register_sid(SID, SID_0x31)