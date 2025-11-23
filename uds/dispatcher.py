#dispatcher.py
import copy
from uds.addressing import is_functional
import can
from uds.sid_registry import SID_HANDLERS
SUPPORTED_FUNCTIONAL_SID = {
    0x10,  # Diagnostic Session Control
    0x11,  # ECU Reset
    0x19,  # Read DTC Information
    0x27,  # Security Access
    0x28,  # Communication Control
    0x29,  # Authentication
    0x31,  # Routine Control
    0x3E,  # Tester Present
    0x85,  # Control DTC Setting
}

def dispatch_request(request, ecu) -> can.Message:
    sid = request.data[0]
    handler = SID_HANDLERS.get(sid)
    def handle(request, ecu)->can.Message:
        # Distinguish between physical address / functional address
        if is_functional(request.arbitration_id, request.is_extended_id):
            # is functional address
            if sid not in SUPPORTED_FUNCTIONAL_SID:
                #was NRC0x11. no response
                return None
            # sid is supported → handle request (functional addresss)
            return handler.filter_SPRMIB_response(handler.handle_functional(request, ecu), ecu)
        else:
            # physical address → normal handler
            if handler:
                #return handler.handle(request, ecu)
                return handler.filter_SPRMIB_response(handler.handle(request, ecu), ecu)
            else:
                print(f"[ECU] Unsupported SID: {sid}")
                data_bytes = bytearray([0x7F, sid, 0x11])
                return can.Message(arbitration_id=ecu.arbitration_id,data=data_bytes,is_extended_id=True)
    #set SPRMIB
    if len(request.data)>1: 
        if request.data[1]>0x7F and request.data[0] in SUPPORTED_FUNCTIONAL_SID:
            req=copy.copy(request)
            req.data = bytearray(request.data)  
            req.data[1] = request.data[1] - 0x80
            res=handle(req, ecu)
            if res is not None and res.data[0]==0x7F:
                return res
            else:
                handler.set_SPRMIB_response(req, ecu)
                return None
    return handle(request, ecu)


