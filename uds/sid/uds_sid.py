#uds_sid.py
import can
import datetime
from uds.utils.crypto import (
    random_hex_list as _crypto_random_hex_list,
    aes128_encrypt_hex_list as _crypto_aes128_encrypt_hex_list,
)
class BaseSID:
    SUPPORTED_SESSIONS = set()  
    # @classmethod
    # def sid(cls):
    #     if not hasattr(cls, "_sid_cache"):
    #         cls._sid_cache = int(cls.__name__[4:], 16)
    #     return cls._sid_cache
    @staticmethod
    def check_length(request, min_length:int=None, max_length:int=None, expected_length:int=None) -> bool:
        '''
        Check if the request message length is valid.
        request: can.Message
        min_length: minimum valid length 
        max_length: maximum valid length 
        expected_length: exact valid length
        Returns: True if valid, False otherwise.
        '''
        length = len(request.data)
        if expected_length is not None:
            return length == expected_length
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
    
    @classmethod
    def is_session_supported(cls, session):
        return session in cls.SUPPORTED_SESSIONS
    @staticmethod
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
        return _crypto_random_hex_list(x)
    @staticmethod
    def aes128_encrypt(hex_list: list[int], key_list: list[int]) -> list[int]:
        return _crypto_aes128_encrypt_hex_list(hex_list, key_list)
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
            #timestamp=datetime.datetime.now().timestamp(),
            arbitration_id=ecu.arbitration_id,
            data=data,
            is_extended_id=False
        )
    
    @classmethod
    def handle_functional(cls, request:can.Message, ecu) -> can.Message|None:
        response = cls.handle(request, ecu)  
        return cls.filter_functional_response(response)
    
    @classmethod
    def filter_functional_response(cls, response:can.Message) -> can.Message|None:
        return None if (response.data[0]==0x7F and response.data[2] in [0x11, 0x12, 0x31, 0x7E, 0x7F]) else response
    
    @classmethod
    def filter_SPRMIB_response(cls, response, ecu) -> can.Message|None:
        if response is None:
            return None
        key=(response.data[0]-0x40, response.data[1])
        return None if (response.data[0]!=0x7F and ecu.SPRMIB.get(key)) else response
    
    @classmethod
    def set_SPRMIB_response(cls, req, ecu) ->None:
        key = (req.data[0], req.data[1]) if req.data[1]<0x80 else (req.data[0], req.data[1]-0x80)
        flag = ecu.SPRMIB.get(key)
        if flag is None:
            ecu.SPRMIB[key]=True
        else:
            ecu.SPRMIB[key]=not flag
        return None

    # @classmethod
    # def SPRMIB_response(cls, msg: can.Message, ecu):
    #     if msg.data[1]>0x7F:
    #         cls.set_SPRMIB_response(msg, ecu)
    #     else:
    #         cls.filter_SPRMIB_response(msg, ecu)