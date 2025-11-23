# sid_0x10.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from security import SecurityType
from .uds_sid import BaseSID
SID = 0x10

class SID_0x10(BaseSID):
    handler_registry = {}

    @classmethod
    def register_handler(cls, subfunc, handler):
        cls.handler_registry[subfunc] = handler

    AvailableSubFuncs={
        SESSIONS.DEFAULT_SESSION,
        SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    SESSION_SUPPORTED_SUBFUNCS = {
        SESSIONS.DEFAULT_SESSION: {SESSIONS.DEFAULT_SESSION, SESSIONS.EXTENDED_SESSION},
        SESSIONS.PROGRAMMING_SESSION: {SESSIONS.PROGRAMMING_SESSION, SESSIONS.EXTENDED_SESSION, SESSIONS.ENGINEERING_SESSION},
        SESSIONS.EXTENDED_SESSION: {SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION,SESSIONS.FOTAACTIVE_SESSION,SESSIONS.FOTAINSTALL_SESSION,SESSIONS.FOTAINSTALLACTIVE_SESSION},
        SESSIONS.ENGINEERING_SESSION:{SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION},
        #SESSIONS.FOTAINSTALLACTIVE_SESSION: {SESSIONS.FOTAINSTALLACTIVE_SESSION},
        #SESSIONS.FOTAINSTALL_SESSION: {SESSIONS.DEFAULT_SESSION, SESSIONS.FOTAINSTALL_SESSION},
        #SESSIONS.FOTAACTIVE_SESSION: {SESSIONS.FOTAACTIVE_SESSION}
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.check_length(request, min_length=2) is False:
                return cls.NegativeResponse(ecu, 0x13)
            subfunc=request.data[1]
            if not cls.is_subfuncs_supported(subfunc):
                return cls.NegativeResponse(ecu, 0x12)
            # handler_map = {
            #     SESSIONS.DEFAULT_SESSION: cls.handle_default,
            #     SESSIONS.PROGRAMMING_SESSION: cls.handle_programming,
            #     SESSIONS.EXTENDED_SESSION: cls.handle_extended,
            #     SESSIONS.ENGINEERING_SESSION: cls.handle_engineering,
            # }
            #handler = handler_map.get(subfunc)
            handler = cls.handler_registry.get(subfunc)
            if handler is None:
                return cls.NegativeResponse(ecu, 0x12)    
            return handler(cls, request, ecu)
        except Exception as e:
                    print(f"[ERROR] SID_0X10 error: {e}")
                    import traceback
                    traceback.print_exc()

    @staticmethod
    def handle_default(cls, request, ecu):
        if not cls.is_session_supported(ecu.session, request):
            return cls.NegativeResponse(ecu, 0x7E)
        if cls.check_length(request, expected_length=2) is False:
            return cls.NegativeResponse(ecu, 0x13)
        ecu.session=SESSIONS.DEFAULT_SESSION
        return cls.PositiveResponse(ecu, [0x50, SESSIONS.DEFAULT_SESSION, 0x00, 0x32, 0x01, 0xF4])

    @staticmethod
    def handle_programming(cls, request, ecu):
        if not cls.is_session_supported(ecu.session, request):
            return cls.NegativeResponse(ecu, 0x7E)
        if ecu.security==SecurityType.FALSE or ecu.illegal_access>0:
            return cls.NegativeResponse(ecu, 0x33)
        if ecu.auth==False or ecu.auth_failed>0:
            return cls.NegativeResponse(ecu, 0x34)
        if cls.check_length(request, expected_length=2) is False:
            return cls.NegativeResponse(ecu, 0x13)
        ecu.session=SESSIONS.PROGRAMMING_SESSION
        return cls.PositiveResponse(ecu, [0x50, SESSIONS.PROGRAMMING_SESSION, 0x00, 0x32, 0x01, 0xF4])

    @staticmethod
    def handle_extended(cls, request, ecu):
        if not cls.is_session_supported(ecu.session, request):
            return cls.NegativeResponse(ecu, 0x7E)
        if cls.check_length(request, expected_length=2) is False:
            return cls.NegativeResponse(ecu, 0x13)
        ecu.session=SESSIONS.EXTENDED_SESSION
        return cls.PositiveResponse(ecu, [0x50, SESSIONS.EXTENDED_SESSION, 0x00, 0x32, 0x01, 0xF4])
    
    @staticmethod
    def handle_engineering(cls, request, ecu):
        if not cls.is_session_supported(ecu.session, request):
            return cls.NegativeResponse(ecu, 0x7E)
        if cls.check_length(request, expected_length=2) is False:
            return cls.NegativeResponse(ecu, 0x13)
        if (ecu.security == SecurityType.FALSE) and request.data[1]==SESSIONS.ENGINEERING_SESSION:
            return cls.NegativeResponse(ecu, 0x33)
        ecu.session=SESSIONS.ENGINEERING_SESSION
        return cls.PositiveResponse(ecu, [0x50, SESSIONS.ENGINEERING_SESSION, 0x00, 0x32, 0x01, 0xF4])
    
    @classmethod
    def is_subfuncs_supported(cls,subfunc:int) ->bool:
        return subfunc in cls.AvailableSubFuncs
    
    @classmethod
    def is_session_supported(cls, session, request):
        supported_subfuncs = cls.SESSION_SUPPORTED_SUBFUNCS.get(session, set())
        return request.data[1] in supported_subfuncs

SID_0x10.register_handler(SESSIONS.DEFAULT_SESSION, SID_0x10.handle_default)
SID_0x10.register_handler(SESSIONS.PROGRAMMING_SESSION, SID_0x10.handle_programming)
SID_0x10.register_handler(SESSIONS.EXTENDED_SESSION, SID_0x10.handle_extended)
SID_0x10.register_handler(SESSIONS.ENGINEERING_SESSION, SID_0x10.handle_engineering)

register_sid(SID, SID_0x10)