# uds.filter.py
import can

class ResponseFilter:
    """
    Performs UDS response filtering:
    - functional addressing NRC filtering
    - SPRMIB filtering
    """

    def __call__(self, msg: can.Message | None, ecu) -> can.Message | None:
        if msg is None:
            return None

        # -------- functional NRC filter --------
        if msg.data[0] == 0x7F and msg.data[2] in (0x11, 0x12, 0x31, 0x7E, 0x7F):
            return None

        # -------- SPRMIB filter --------
        if msg.data[0] != 0x7F and ecu.SPRMIB.get(bytes(msg.data[:2])):
            return None

        return msg


# Global instance
RESPONSE_FILTER = ResponseFilter()
