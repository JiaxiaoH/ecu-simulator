# sid_0x29.py
from ..sid_registry import register_sid
from sessiontypes import SESSIONS 
from .uds_sid import BaseSID
from keys import ALGORITHMINDICATOR
import json
from pathlib import Path
SID = 0x29

authentication_tasks = {}
tasks_loaded = False

def register_auth_task(sub_func, name, length, sessions, handler):
    """register authentication tasks"""
    authentication_tasks[sub_func] = {
        "name": name,
        "length": length,
        "supported_sessions": set(sessions),
        "handler": handler,
    }

class SID_0x29(BaseSID):
    @classmethod    
    def handle(cls, request, ecu):
        ensure_tasks_loaded()
        try: 
            if cls.is_request_message_less_than_2_byte(request):
                return cls.NegativeResponse(ecu, 0x13)
            task=authentication_tasks.get(request.data[1])
            try:
                res=task["handler"](request.data, ecu)
            except TypeError as e:
                res=0x12
            if isinstance(res, int):
                return cls.NegativeResponse(ecu, res)
            elif isinstance(res, (list, bytes)):
                #res = bytes(res) if isinstance(res, list) else res
                return cls.PositiveResponse(ecu, [0x69]+res) 
            else:
                raise TypeError
            
        except Exception as e:
                    print(f"[ERROR] SID_0x29 error: {e}")
                    import traceback
                    traceback.print_exc()
    
    @staticmethod
    def handle_deauthenticate(reqdata: bytes, ecu) -> int|list[int]:
        if ecu.session not in [SESSIONS.DEFAULT_SESSION, SESSIONS.EXTENDED_SESSION, SESSIONS.ENGINEERING_SESSION]:
            return 0x7E
        if len(reqdata)!=2:
            return 0x13
        ecu.auth=False
        return [0x00, 0x10]
    
    @classmethod
    def handle_request_challenge(cls, reqdata: bytes, ecu) -> int|list[int]:
        if ecu.session not in [SESSIONS.EXTENDED_SESSION, SESSIONS.ENGINEERING_SESSION]:
            return 0x7E
        if len(reqdata)!=19:
            return 0x13
        if ecu.auth_failed>0:
            return 0x22
        if reqdata[2]!=0x00:
            return 0x5C
        if reqdata[3:]!=bytes(ALGORITHMINDICATOR):
            return 0x5C
        #if ecu.HSM
        #    res=0x22
        if ecu.ssk is None:
            return 0x22
        challengeServer=cls.random_hex_list(16)
        ecu.authenticator=cls.aes128_encrypt(challengeServer, list(ecu.ssk))
        ecu.ssk=None
        print(f"Authenticator = "+ ' '.join(f"{b:02X}" for b in ecu.authenticator))
        print(f"Answer = 29 06 "+ ' '.join(f"{b:02X}" for b in ALGORITHMINDICATOR)+ " 00 10 "+''.join(f"{b:02X} " for b in ecu.authenticator)+" 00 00 00 00")
        res=[0x05, 0x00] + ALGORITHMINDICATOR + [0x00, 0x10] + challengeServer + [0x00, 0x00]
        return res

    @staticmethod
    def handle_verify_proof(reqdata: bytes, ecu) -> int|list[int]:
        if ecu.session not in [SESSIONS.EXTENDED_SESSION, SESSIONS.ENGINEERING_SESSION]:
            return 0x7E
        if ecu.authenticator is None:
            return 0x24
        if len(reqdata)!=40:
            return 0x13
        if ecu.auth_failed>0:
            return 0x22
        if reqdata[2:18]!=bytes(ALGORITHMINDICATOR):
            print(f"reqdata = "+ ''.join(f"{b:02X} " for b in reqdata[2:18]))
            return 0x5C
        if reqdata[20:36]!=bytes(ecu.authenticator):
            ecu.auth_failed=ecu.auth_failed+1
            return 0x58
        ecu.auth=True
        ecu.authenticator=None
        return [0x06 ,0x12]+ALGORITHMINDICATOR+[0x00, 0x00]

    @staticmethod
    def handle_auth_config(reqdata: bytes, ecu) -> int|list[int]:
        if ecu.session not in [SESSIONS.DEFAULT_SESSION, SESSIONS.EXTENDED_SESSION, SESSIONS.ENGINEERING_SESSION]:
            return 0x7E
        if len(reqdata)!=2:
            return 0x13
        return [0x08, 0x04]

def load_auth_tasks_from_json(config_path: str):
    """load from json files"""
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sid_cls = SID_0x29 
    for sub_func_hex, cfg in data.items():
        sub_func = int(sub_func_hex, 16)
        func_name = cfg["handler"]
        handler = getattr(sid_cls, func_name)
        register_auth_task(
            sub_func=sub_func,
            name=cfg["name"],
            length=cfg["length"],
            sessions=cfg["sessions"],
            handler=handler,
        )

def ensure_tasks_loaded():
    global tasks_loaded
    if not tasks_loaded:
        load_auth_tasks_from_json(str(CONFIG_PATH))
        tasks_loaded = True

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default_auth.json"
register_sid(SID, SID_0x29)