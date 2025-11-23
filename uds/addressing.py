#addressing.py
def is_functional(arbitration_id: int, is_extended_id: bool) -> bool:
    """
    Determine if the message from tester is "Functional Address"
    supporting 11-bit and 29-bit CAN ID
    """
    # ========= 11bit CAN =========
    if not is_extended_id:
        return arbitration_id == 0x7DF
    # ========= 29bit CAN (J1939) =========
    # PF=0xDB → functional 
    # PF=0xDA → physical
    pf = (arbitration_id >> 16) & 0xFF
    return pf == 0xDB