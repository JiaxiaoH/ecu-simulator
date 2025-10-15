# sid_0x10.py
import time
from sessiontypes import SESSIONS 
import can
import datetime
class SID_0x10:
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
        SESSIONS.PROGRAMMING_SESSION: {SESSIONS.PROGRAMMING_SESSION},
        SESSIONS.EXTENDED_SESSION: {SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION,SESSIONS.FOTAACTIVE_SESSION,SESSIONS.FOTAINSTALL_SESSION,SESSIONS.FOTAINSTALLACTIVE_SESSION},
        SESSIONS.ENGINEERING_SESSION:{SESSIONS.DEFAULT_SESSION,SESSIONS.PROGRAMMING_SESSION,SESSIONS.EXTENDED_SESSION,SESSIONS.ENGINEERING_SESSION},
        SESSIONS.FOTAINSTALLACTIVE_SESSION: {SESSIONS.FOTAINSTALLACTIVE_SESSION},
        SESSIONS.FOTAINSTALL_SESSION: {SESSIONS.DEFAULT_SESSION, SESSIONS.FOTAINSTALL_SESSION},
        SESSIONS.FOTAACTIVE_SESSION: {SESSIONS.FOTAACTIVE_SESSION}
    }

    @classmethod    
    def handle(cls, request, ecu):
        try:
            if cls.is_request_message_less_than_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False)
            if not cls.is_subfuncs_supported(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x12], is_extended_id=False)
        except Exception as e:
                    print(f"[ERROR] SID_0X10 error: {e}")
                    import traceback
                    traceback.print_exc()
        if request.data[1] == SESSIONS.DEFAULT_SESSION: 
            try:
                if not cls.is_session_supported(ecu.DiagnosticSession, request):
                    return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            except Exception as e:
                print(f"Error test: {e}")
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.PROGRAMMING_SESSION:
                #TODO: add sth...
                #
                #
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.EXTENDED_SESSION:
            if not cls.is_session_supported(ecu.DiagnosticSession, request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.ENGINEERING_SESSION:
            if not cls.is_session_supported(ecu.DiagnosticSession, request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x7E], is_extended_id=False, is_rx=True)
            if not cls.is_request_message_2_byte(request):
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x13], is_extended_id=False, is_rx=True)
            if (not ecu.security) and request.data[1]==0x4F:
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x33], is_extended_id=False, is_rx=True)
            ecu.DiagnosticSession=request.data[1]
            return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x50, request.data[1], 0x00, 0x32, 0x01, 0xF4], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAINSTALL_SESSION:
                #TODO...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAACTIVE_SESSION:
                #TODO...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        elif request.data[1] == SESSIONS.FOTAINSTALLACTIVE_SESSION:
                #...
                #
                #
                return can.Message(timestamp=datetime.datetime.now().timestamp(), arbitration_id=ecu.arbitration_id, data=[0x7F, 0x10, 0x00], is_extended_id=False, is_rx=True)
        else:
            print("Error: cannot match the subfunction")
            return None
    #查找request message是否小于2byte
    def is_request_message_less_than_2_byte(request):
        return len(request.data) < 2

    #查找subfunction是否被支持
    def is_subfuncs_supported(request):
        return request.data[1] in SID_0x10.AvailableSubFuncs
    
    #查找session是否被支持
    def is_session_supported(session, request):
        supported_subfuncs = SID_0x10.SESSION_SUPPORTED_SUBFUNCS.get(session, set())
        return request.data[1] in supported_subfuncs
    
    #查找request message是否为2byte
    def is_request_message_2_byte(request):
        return len(request.data) == 2
