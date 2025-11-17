#uds_sid.py
import can
import datetime
import secrets
from Crypto.Cipher import AES
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
    def is_request_message_less_than_4_byte(request):
        return len(request.data) < 4
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
    def is_did_supported(cls, ecu, did):
        sid=cls.get_sid_name()
        return ecu.did.is_supported(sid, did)
    @staticmethod
    def random_hex_list(x: int) -> list[int]:
        random_bytes = secrets.token_bytes(x)
        return [b for b in random_bytes]
    @staticmethod
    def aes128_encrypt(hex_list: list[int], key_list: list[int]) -> list[int]:
        if len(hex_list) != 16 or len(key_list) != 16:
            raise ValueError("Error: data is not 16 bytes!")
        data_bytes = bytes(hex_list)
        key_bytes = bytes(key_list)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        encrypted = cipher.encrypt(data_bytes)
        return list(encrypted)
    @classmethod
    def get_sid_name(cls):
        try:
            return int(cls.__name__[len("SID_"):], 16)
        except ValueError as e:
            print(f"[Error]: invalid SID class name '{cls.__name__}', must be SID_<hex>-{e}")
            return None
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