#uds_sid.py
import can
import datetime
class BaseSID:
    SUPPORTED_SESSIONS = set()  
    @classmethod
    def is_session_supported(cls, session):
        return session in cls.SUPPORTED_SESSIONS
    @staticmethod
    def is_request_message_less_than_2_byte(request):
        return len(request.data) < 2  
    @staticmethod
    def is_request_message_less_than_3_byte(request):
        return len(request.data) < 3  
    @staticmethod
    def is_request_message_2_byte(request):
        return len(request.data) == 2
    @staticmethod
    def is_request_message_3_byte(request):
        return len(request.data) == 3
    @staticmethod
    def is_request_message_4_byte(request):
        return len(request.data) == 4
    staticmethod
    def is_request_message_even(request):
        return len(request.data) % 2 == 0
    @staticmethod
    def is_car_moving(ecu):
         return ecu.moving
    @staticmethod
    def is_memory_error(ecu):
         return ecu.is_memory_error
    @classmethod
    def NegativeResponse(cls, ecu, nrc):
        sidrq_str = cls.__name__.replace('SID_', '')
        sidrq = int(sidrq_str, 16) 
        return can.Message(
            timestamp=datetime.datetime.now().timestamp(),
            arbitration_id=ecu.arbitration_id,
            data=[0x7F, sidrq, nrc],
            is_extended_id=False
        )
    @staticmethod
    def PositiveResponse(ecu, data):
        return can.Message(
            timestamp=datetime.datetime.now().timestamp(),
            arbitration_id=ecu.arbitration_id,
            data=data,
            is_extended_id=False
        )