# sid_registry.py
SID_HANDLERS = {}
"""
callable, Handler function, accept data bytes
"""

def register_sid(sid, func):
    """
    register SID handler function
    sid: int,UDS SID
    func: callable, Handler function, accept data bytes
    """
    if sid in SID_HANDLERS:
        print(f"Warning: SID 0x{sid:X} is covered")
    SID_HANDLERS[sid] = func

def get_handler(sid):
    """
    get the handler function of sid
    """
    return SID_HANDLERS.get(sid, None)