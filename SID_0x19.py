# sid_0x19.py
from sessiontypes import SESSIONS 
from uds_sid import BaseSID
class SID_0x19(BaseSID):
    AvailableSubFuncs={
        0x01,
        0x02,
        0x0A
    }
    SUPPORTED_SESSIONS={
        SESSIONS.DEFAULT_SESSION,
        #SESSIONS.PROGRAMMING_SESSION,
        SESSIONS.EXTENDED_SESSION,
        SESSIONS.ENGINEERING_SESSION,
        SESSIONS.FOTAACTIVE_SESSION,
        SESSIONS.FOTAINSTALL_SESSION,
        SESSIONS.FOTAINSTALLACTIVE_SESSION
    }
    @classmethod    
    def handle(cls, request, ecu):
        try:
            if not cls.is_session_supported(ecu.session):
                return cls.NegativeResponse(ecu, 0x7F) 
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            if not cls.is_subfuncs_supported(request):
                 return cls.NegativeResponse(ecu, 0x12)
            if cls.is_request_message_3_byte(request):
                if request.data[1]==0x01:
                    DTCCount=cls.reportNumberOfDTCByStatusMask(ecu, request)
                    res=[0x59, 0x01, ecu.DTCStatusAvailabilityMask]+DTCCount
                    return cls.PositiveResponse(ecu, res)
                elif request.data[1]==0x02:
                    DTCAndStatusRecord=cls.reportDTCByStatusMask(ecu, request)
                    res=[0x59, 0x02, ecu.DTCStatusAvailabilityMask]+DTCAndStatusRecord
                    return cls.PositiveResponse(ecu, res)
                else:
                     return cls.NegativeResponse(ecu, 0x13)
            elif cls.is_request_message_2_byte(request):
                if request.data[1]==0x0A:#reportSupportedDTC
                    DTCAndStatusRecord=cls.reportSupportedDTC(ecu)
                    res=[0x59, 0x0A, ecu.DTCStatusAvailabilityMask]+DTCAndStatusRecord
                    return cls.PositiveResponse(ecu, res)
                else:  
                    return cls.NegativeResponse(ecu, 0x13)
            else:
                 return cls.NegativeResponse(ecu, 0x13)  
            
        except Exception as e:
                    print(f"[ERROR] SID_0X19 error: {e}")
                    import traceback
                    traceback.print_exc()
            
    @staticmethod
    def reportNumberOfDTCByStatusMask(ecu, request):
        return ecu.dtc.report_number(request.data[2])
    
    @staticmethod
    def reportDTCByStatusMask(ecu, request):
         return ecu.dtc.report_dtc(request.data[2])
    
    @staticmethod
    def reportSupportedDTC(ecu):
         return ecu.dtc.report_dtc(0xFF)
    
    @staticmethod
    def is_subfuncs_supported(request):
        return request.data[1] in SID_0x19.AvailableSubFuncs