#rid.py
import os
import yaml
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any
from sessiontypes import SESSIONS
from ecdsa import gen_ecdhe_keypair, gen_ssk, bytes2Ecckey, verify_signature
@dataclass
class RID:
    id: int
    name: str
    supported_services: Optional[list[int]] = None   
    supported_sessions: Optional[list[int]] = None
    supported_security_levels: Optional[list[Any]] = None
    supported_driving: Optional[list[Any]] = None
    aiming_mode_setting: Optional[list[Any]] = None
    routine_status: Optional[dict] = None
    error_status: Optional[dict] = None
    req_length: Optional[list[int]] = None
    rep_length: Optional[list[int]] = None
    routine_control_types: Optional[dict] = None

class RIDManager:
    def __init__(self, rid_yaml_name: str, ecu_yaml_name: str, ecu=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(base_dir, "config")

        self.yaml_path = os.path.join(config_dir, rid_yaml_name)
        self.ecu_config_path = os.path.join(config_dir, ecu_yaml_name)
        self.supported_rids: Dict[int, RID] = {}
        self.rid_sid_table: Dict[int, Dict[int, RID]] = {}
        self.func_registry: Dict[str, Callable[[int], bytes]] = {
        
        }
        self.ecu=ecu
        self.ecu_static_data: Dict[int, bytes] = self._load_ecu_config()
        self.ecu_dataRecord=self.ecu_static_data
        self._load_config()

    # ========= Config Loading Logic =========
    def _load_config(self):
        yaml_exists = os.path.exists(self.yaml_path)      
        if yaml_exists:
            data = self._load_yaml(self.yaml_path)
            #create rid table
            self._build_rid_table(data)

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_yaml_cache(self, data:Dict[str, Any], path: str):
        with open(path, "w", encoding="utf-8")as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    # ========= RID creating logic =========
    def _update_sid_table(self, rid:RID):
        sids=rid.supported_services
        if sids is not None:
            for sid in sids:
                if sid not in self.rid_sid_table:
                    self.rid_sid_table[sid]={}
                self.rid_sid_table[sid][rid.id]=rid

    def _build_rid_table(self, cfg: Dict[str, Any]):
        self.supported_rids.clear()
        for s in cfg.get("rid", []):
            rid_id = int(s["id"], 16) if isinstance(s["id"], str) else s["id"]
            routine_control = s.get("routine_control_types", {})
            for ctrl_type, ctrl_data in routine_control.items():
                if "variants" in ctrl_data:
                    ctrl_data["variants"] = [dict(v) for v in ctrl_data["variants"]]
            self.supported_rids[rid_id] = RID(
                id=rid_id,
                name=s["name"],
                supported_services=s.get("supported_services"),
                supported_sessions=s.get("supported_sessions"),
                supported_security_levels=s.get("supported_security_levels"),
                supported_driving=s.get("supported_driving"),
                req_length=s.get("req_length"),
                rep_length=s.get("rep_length"),
                aiming_mode_setting=s.get("aiming_mode_setting"),
                routine_status=s.get("routine_status"),
                error_status=s.get("error_status"),
                routine_control_types=routine_control                
            )
            self._update_sid_table(self.supported_rids[rid_id])
            
    def _load_ecu_config(self) :
        """read ecu_config.yaml"""
        if not os.path.exists(self.ecu_config_path):
            return {}
        with open(self.ecu_config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        static_data = cfg.get("ecu_static_data", {})
        result = {}
        for key, val in static_data.items():
            try:
                if isinstance(key, str) and (key.startswith("0x") or key.isdigit()):
                    i = int(key, 16)if key.startswith("0x") else int (key)
                else:
                    i = key
                result[i] = val          
            except Exception as e:
                print(f"[ERROR]ecu_config error: {e}")
                import traceback
                traceback.print_exc()
        return result

    def _update_config(self, name: str, data_dict: Dict[str, Any]):
        from ruamel.yaml import YAML
        yaml = YAML()
        yaml.preserve_quotes = True  
        yaml.indent(mapping=2, sequence=4, offset=2)
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
        def recursive_update(obj):
            if isinstance(obj, dict):
                if obj.get("name")==name:
                    for dk, dv in data_dict.items():
                        obj[dk] = dv
                for v in obj.values():
                    recursive_update(v)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_update(item)
        recursive_update(data)

        with open(self.yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    # ========= Public API =========
    def func(self, rid:int, routine_type:int=0x01, routine_record: list|None=None) -> list[int]:
        func_name = self.read_rid_func(rid, routine_type)
        if func_name:
            func = getattr(self, func_name)
        if routine_record is not None:
            return func(self.read_rid_obj(rid), routine_record)
        return func(self.read_rid_obj(rid))
    
    def is_supported(self,sid: int, rid: int) -> bool:
        return rid in self.rid_sid_table.get(sid, {})

    def read_rid_obj(self, rid: int) -> Optional[RID]:
        return self.supported_rids.get(rid)
    
    def read_rid_func(self, rid: int, routine_type: int):
        return self.get_routine_info(rid, routine_type)[0]
    
    def refresh_cache(self):
        """Force refresh cache"""
        if os.path.exists(self.yaml_path):
            data = self._load_yaml(self.yaml_path)
            self._build_rid_table(data)

    def test(self):
        self.refresh_cache()

    def get_req_length(self, rid:int, routine_type:int=None):
        rid_obj = self.supported_rids.get(rid)
        if routine_type and rid_obj.routine_control_types:
            ctrl_entry = rid_obj.routine_control_types.get(routine_type)
            if ctrl_entry:
                if "variants" in ctrl_entry:
                    lengths = [v.get("req_length") for v in ctrl_entry["variants"] if "req_length" in v]
                    return lengths if lengths else None
                if "req_length" in ctrl_entry:
                    return ctrl_entry.get("req_length")
        return rid_obj.req_length
    
    def get_routine_info(self, rid:int, ctrl_type:int, req_len:int=None):
        """
        return handler_func、req_length、rep_length
        ctrl_type: routine_control_types key (int)
        req_len: choose the right variant if there is variant
        """
        rid_obj = self.supported_rids.get(rid)
        if not rid_obj or not rid_obj.routine_control_types:
            return None
        ctrl_type_hex = ctrl_type if isinstance(ctrl_type, int) else int(ctrl_type, 16)
        ctrl_entry = rid_obj.routine_control_types.get(ctrl_type_hex)
        if not ctrl_entry:
            return None
        variants = ctrl_entry.get("variants")
        if variants:
            if req_len:
                for v in variants:
                    if v.get("req_length") == req_len:
                        return v.get("handler_func"), v.get("req_length"), v.get("rep_length")
                return None  
            else:
                v = variants[0]
                return v.get("handler_func"), v.get("req_length"), v.get("rep_length")
        else:
            return ctrl_entry.get("handler_func"), ctrl_entry.get("req_length"), ctrl_entry.get("rep_length")

    def is_routine_order_allowed(self, rid_value: int, routine_type: int) -> bool:
        rid = self.read_rid_obj(rid_value)
        if rid.routine_status is None or rid.routine_status==[]:
            return True
        if rid.routine_status['current_value']!=0x7F and routine_type!=0x01:
            return False
        return True

    def do_rid_0xA1A3_0x01(self, rid:RID) -> list[int]:
        #something about startRoutine
        #...
        rid.routine_status['current_value']=0x7F
        return [rid.routine_status.get("current_value", 0), rid.error_status.get("current_value", 0), 0xff, 0xff, 0x00, 0x00]
    
    def do_rid_0xA1A3_0x02(self, rid:RID) -> list[int]:
        #something about stopRoutine
        #...
        rid.routine_status['current_value']=0x00
        return [rid.routine_status.get("current_value", 0), rid.error_status.get("current_value", 0), 0xff, 0xff, 0x00, 0x00]
    
    def do_rid_0xA1A3_0x03(self, rid:RID) -> list[int]:
        #something about requestRoutineResult
        #...
        return [rid.routine_status.get("current_value", 0), rid.error_status.get("current_value", 0), 0xff, 0xff, 0x00, 0x00]
    
    def do_rid_0xFF00_len4(self, rid:RID) -> list[int]:
        #something about len(msg)==4
        # if ...:
        #     return 0x72
        # elif ...:
        #     return 0x10
        return []
    
    def do_rid_0xFF00_len12(self, rid:RID) -> list[int]:
        #something about len(msg)==12
        # if ...:
        #     return 0x31
        # elif ...:
        #     return 0x10
        return []

    def do_rid_0xD111(self, rid:RID, routine_record:list) -> list[int]:
        '''
        some logicts about rid0xD111
        '''
        raw_pk=bytes(routine_record[:64])
        kx_pk1 = bytes2Ecckey(raw_pk)
        signature=routine_record[64:128]
        if self.ecu.auth_public_key is None:
            rid.routien_status=0x80
            rid.error_status=0x01
            return [rid.routine_status, rid.error_status] + [0x00]*64                
        if verify_signature(self.ecu.auth_public_key, raw_pk, bytes(signature)):
            print("[ECU] verify ok")
        else:
            rid.routine_status=0x80
            rid.error_status=0x02
            return [rid.routine_status, rid.error_status] + [0x00]*64
            
        kx_sk2, kx_pk2=gen_ecdhe_keypair()
        self.ecu.ssk=gen_ssk(kx_sk2, kx_pk1)
        qx = int(kx_pk2.pointQ.x).to_bytes(32, "big")
        qy = int(kx_pk2.pointQ.y).to_bytes(32, "big")
        kxpk2_bytes = qx + qy

        print("[ECU] kx_pk2 =", kxpk2_bytes.hex())
        return [0x00, 0x00]+list(kxpk2_bytes)


