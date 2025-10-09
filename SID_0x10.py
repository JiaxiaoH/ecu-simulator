# sid_0x10.py
import time
from CANmessage import request_queue, response_queue, RequestMessage, PositiveResponseMessage, NegativeResponseMessage
#from ecu import ECU
from sessiontypes import SESSIONS 

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
    def handle(self, request, ecu):
        try:
            if SID_0x10.is_request_message_less_than_2_byte(request):
                return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x13)
            if not SID_0x10.is_subfuncs_supported(request.subfunction):
                 return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x12)
        except Exception as e:
                    print(f"[ERROR] SID_0X10 error: {e}")
                    import traceback
                    traceback.print_exc()
        match request.subfunction:
            case SESSIONS.DEFAULT_SESSION:
                if not SID_0x10.is_session_supported(ecu.DiagnosticSession, request.subfunction):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x7E)
                if not SID_0x10.is_request_message_2_byte(request):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x13)
                ecu.DiagnosticSession=request.subfunction
                return PositiveResponseMessage(SID=request.SID+0x40, subfunction=request.subfunction, dataID=0x0032, data=0x01F4)
            case SESSIONS.PROGRAMMING_SESSION:
                #...
                #
                #
                return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x00)
            case SESSIONS.EXTENDED_SESSION:
                if not SID_0x10.is_session_supported(ecu.DiagnosticSession, request.subfunction):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x7E)
                if not SID_0x10.is_request_message_2_byte(request):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x13)
                ecu.DiagnosticSession=request.subfunction
                return PositiveResponseMessage(SID=request.SID+0x40, subfunction=request.subfunction, dataID=0x0032, data=0x01F4)
            case SESSIONS.ENGINEERING_SESSION:
                if not SID_0x10.is_session_supported(ecu.DiagnosticSession, request.subfunction):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x7E)
                if not SID_0x10.is_request_message_2_byte(request):
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x13)
                if (not ecu.security) and request.subfunction==0x4F:
                    return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x33)
                ecu.DiagnosticSession=request.subfunction
                return PositiveResponseMessage(SID=request.SID+0x40, subfunction=request.subfunction, dataID=0x0032, data=0x01F4)
            case SESSIONS.FOTAINSTALL_SESSION:
                #...
                #
                #
                return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x00)
            case SESSIONS.FOTAACTIVE_SESSION:
                #...
                #
                #
                return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x00)
            case SESSIONS.FOTAINSTALLACTIVE_SESSION:
                #...
                #
                #
                return NegativeResponseMessage(SIDRQ=request.SID, NRC=0x00)

    #查找request message是否小于2byte
    def is_request_message_less_than_2_byte(request):
        length=len(request.to_bytearray())
        if len2dlc(length)<2:
            return True
        else:
            return False

    #查找subfunction是否被支持
    def is_subfuncs_supported(subfunction):
        return subfunction in SID_0x10.AvailableSubFuncs
    
    #查找session是否被支持
    def is_session_supported(session, subfunction):
        supported_subfuncs = SID_0x10.SESSION_SUPPORTED_SUBFUNCS.get(session, set())
        return subfunction in supported_subfuncs
    
    #查找request message是否为2byte
    def is_request_message_2_byte(request):
        length=len(request.to_bytearray())
        if len2dlc(length)==2:
            return True
        else:
            return False

def len2dlc(length: int) -> int:
    """Calculate the DLC from data length.
    :param length: Length in number of bytes (0-64)
    :returns: DLC (0-15)
    """
    # List of valid data lengths for a CAN FD message 从Python-CAN抄的
    CAN_FD_DLC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
    if length <= 8:
        return length
    for dlc, nof_bytes in enumerate(CAN_FD_DLC):
        if nof_bytes >= length:
            return dlc
    return 15