from CANmessage import request_queue, response_queue, RequestMessage, PositiveResponseMessage, NegativeResponseMessage


def len2dlc(length: int) -> int:
    """Calculate the DLC from data length.
    :param length: Length in number of bytes (0-64)
    :returns: DLC (0-15)
    """
    CAN_FD_DLC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64] 
    if length <= 8:
        return length
    for dlc, nof_bytes in enumerate(CAN_FD_DLC):
        if nof_bytes >= length:
            return dlc
    return 15

def is_request_message_2_byte(request):
        length=len(request.to_bytearray())
        if len2dlc(length)==2:
            return True
        else:
            return False

req = RequestMessage(SID=0x10, subfunction = 0x01) 

#hex_length = len(hex(req.SID)) - 2 
#length=2 #len(req.SID)+len(req.subfunction)
#res = len2dlc(len(byte_array))
res=is_request_message_2_byte(req)
print(res)

    

