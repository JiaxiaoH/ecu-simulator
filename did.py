#did.py
import os
import json
import yaml
import random
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any
from sessiontypes import SESSIONS
@dataclass
class DID:
    id: int
    name: str
    category: str
    get_func: Optional[Callable[[], bytes]] = None
    value: Optional[bytes] = None
    supported_services: Optional[list[int]] = None   
    supported_sessions: Optional[list[int]] = None
    supported_security_levels: Optional[list[Any]] = None
    supported_driving: Optional[list[Any]] = None
    refusal: Optional[list[Any]] = None
    # boot_support: Optional[Dict[str, bool]] = None
    # support_conditions: Optional[list[Dict[str, Any]]] = None

class DIDManager:
    """
    YAML and JSON are both supported
    Give priority to using JSON
    """
    def __init__(self, did_yaml_name: str, did_json_name: str, ecu_yaml_name: str, ecu=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(base_dir, "config")

        self.yaml_path = os.path.join(config_dir, did_yaml_name)
        self.json_path = os.path.join(config_dir, did_json_name)
        self.ecu_config_path = os.path.join(config_dir, ecu_yaml_name)
        self.supported_dids: Dict[int, DID] = {}
        self.func_registry: Dict[str, Callable[[int], bytes]] = {
            "get_did_0xA19D": self.get_did_0xA19D,
        }
        self.ecu=ecu
        self.ecu_static_data: Dict[int, bytes] = self._load_ecu_config()
        self.ecu_dataRecord=self.ecu_static_data
        self._load_config()

    # ========= Config Loading Logic =========
    def _load_config(self):
        yaml_exists = os.path.exists(self.yaml_path)
        json_exists = os.path.exists(self.json_path)
        #check if we need to update the .json
        if yaml_exists:
            yaml_mtime = os.path.getmtime(self.yaml_path)
            json_mtime = os.path.getmtime(self.json_path) if json_exists else 0
            if not json_exists or yaml_mtime > json_mtime:
                data = self._load_yaml(self.yaml_path)
                self._save_json_cache(data, self.json_path)
            else:
                data = self._load_json(self.json_path)
        elif json_exists:
            data = self._load_json(self.json_path)
        else:
            raise FileNotFoundError("Cannot find DID config")
        #create did table
        self._build_did_table(data)

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_json(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_json_cache(self, data: Dict[str, Any], path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ========= DID creating logic =========
    def _build_did_table(self, cfg: Dict[str, Any]):
        self.supported_dids.clear()
        # ==== Ranges ====
        for category, ranges in cfg.get("ranges", {}).items():
            for r in ranges:
                sessions=r.get("supported_sessions", [1])
                for did in range(r["start"], r["end"] + 1):
                    self.supported_dids[did] = DID(
                        id=did,
                        name=f"{category}_DID_{hex(did)[2:].upper()}",
                        category=category,
                        supported_sessions=sessions,
                        # supported_services=r.get("supported_services"),
                        supported_security_levels=r.get("supported_security_levels"),
                        supported_driving=r.get("supported_driving"),
                        # boot_support=r.get("boot_support"),
                        # support_conditions=r.get("support_conditions"),
                        value=bytes.fromhex(r["default_value"]) if r.get("default_value") else None,
                    )
        # ==== Templates ====
        for tpl in cfg.get("templates", []):
            start = tpl["start_id"]
            func_name=tpl.get("func_name")
            func = self.func_registry.get(func_name)
            for i in range(tpl["count"]):
                did = start + i
                name = tpl["pattern"].format(index=i + 1)
                def make_func(f, idx=i):
                    if not f:
                        return None
                    return lambda: f(idx)
                self.supported_dids[did] = DID(
                    id=did,
                    name=name,
                    category=tpl["category"],
                    get_func=make_func(func),
                    supported_sessions=tpl.get("supported_sessions"),
                    # supported_services=tpl.get("supported_services"),
                    supported_security_levels=tpl.get("supported_security_levels"),
                    supported_driving=tpl.get("supported_driving"),
                    # boot_support=tpl.get("boot_support"),
                    # support_conditions=tpl.get("support_conditions"),
                )
        # ==== Special DID ====
        for s in cfg.get("specific", []):
            did = int(s["id"], 16) if isinstance(s["id"], str) else s["id"]
            if s["type"] == "static":
                value = None
                v = s["value"]
                if isinstance(v, str):
                    v = v.removeprefix("0x").replace(" ", "")
                    value = bytes.fromhex(v)
                elif isinstance(v, int):
                    value = v.to_bytes((v.bit_length() + 7) // 8 or 1, "big")
                elif isinstance(v, list):
                    value = bytes(v)
                self.supported_dids[did] = DID(
                    id=did, 
                    name=s["name"], 
                    category="Specific",
                    value=value,
                    supported_sessions=s.get("supported_sessions"),
                    # supported_services=s.get("supported_services"),
                    supported_security_levels=s.get("supported_security_levels"),
                    supported_driving=s.get("supported_driving"),
                    # boot_support=s.get("boot_support"),
                    # support_conditions=s.get("support_conditions"),
                )
            elif s["type"] == "function":
                func_name=s.get("func_name")
                func=self.func_registry.get(func_name)
                self.supported_dids[did] = DID(
                    id=did, 
                    name=s["name"], 
                    category="Specific",
                    get_func=func,
                    supported_sessions=s.get("supported_sessions"),
                    # supported_services=s.get("supported_services"),
                    supported_security_levels=s.get("supported_security_levels"),
                    supported_driving=s.get("supported_driving"),
                    # boot_support=s.get("boot_support"),
                    # support_conditions=s.get("support_conditions"),
                )
            elif s["type"] == "composite":
                def make_composite_func(structure, obj):
                    def get_func(did=None):
                        length=max(int(f['range'].split('-')[1],16) for f in structure) + 1
                        result=[0x00]*length
                        for sd in structure:
                            start, end = map(lambda x: int(x,16), sd['range'].split('-'))
                            if sd['type'] == 'static':
                                result[start:end+1]=sd['value']
                            if sd['type']=='dynamic':
                                if hasattr(obj, sd['source']):
                                    func = getattr(obj, sd['source'])
                                    val = func()
                                else:
                                    val = 0x00
                                length = end+1-start
                                if isinstance(val, list):
                                    result[start:end+1] = (val + [0x00]*length)[:length]
                                else:
                                    result[start:end+1] = [val]*length                                    
                        return result
                    return get_func
                get_func = make_composite_func(s['structure'], self)
                self.supported_dids[did] = DID(
                    id=did,
                    name=s["name"],
                    category="Specific",
                    # length=length,
                    get_func=get_func,
                    supported_sessions=s.get("supported_sessions"),
                    supported_security_levels=s.get("supported_security_levels"),
                    supported_driving=s.get("supported_driving"),
                )

    # ========= Public API =========
    def set_session(self, session: int):
        self.current_session = session

    def is_supported(self, did: int) -> bool:
        return did in self.supported_dids

    def read_did(self, did: int) -> list[int]:
        entry = self.supported_dids.get(did)
        if not entry:
            return []
        if entry.get_func:
            data = entry.get_func()
        elif entry.value is not None:
            data = entry.value
        else:
            data = b""
        if isinstance(data, bytes):
            return list(data)
        elif isinstance(data, list):
            return data
        elif isinstance(data, str):
            return [ord(c) for c in data]
        else:
            return []        

    def refresh_cache(self):
        """Force refresh cache"""
        if os.path.exists(self.yaml_path):
            data = self._load_yaml(self.yaml_path)
            self._save_json_cache(data, self.json_path)
            self._build_did_table(data)

    def test(self):
        self.refresh_cache()

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

    def read_VC_Status(self):
        variant_code=self.ecu_static_data.get("variant_code", "")
        if variant_code is None or variant_code=="00000":
            return 0x00
        else:
            return 0x01
    
    def read_VC_Code(self):
        variant_code=self.ecu_static_data.get("variant_code", "")
        if variant_code is None:
            return [0x00, 0x00, 0x00, 0x00, 0x00]
        else:
            return [ord(vc_code) for vc_code in variant_code]

    def read_VPN_Length(self):
        variant_code=self.ecu_static_data.get("variant_code", "")
        if variant_code is None or variant_code=="00000":
            return 0x00
        else:
            return 0x0C
     
    def read_VPN_Id(self):
        variant_parts_number=self.ecu_static_data.get("variant_parts_number", "")
        if variant_parts_number is None:
            return [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00]
        else:
            return [ord(vpn_id) for vpn_id in variant_parts_number]

    def read_METER_ODO_DATA(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        n = random.randint(0, 0xFFFFFF)
        b = n.to_bytes(3, "big")
        return [byte for byte in b]
    
    def read_IG_ON_COUNTER(self):
        n = max(0, min(int(self.ecu.dt_igon), 0xFFFFFF))
        b = n.to_bytes(3, "big")
        return [byte for byte in b]
    
    def read_IG_VOLTAGE(self):
        res = max(0, min(int(self.ecu.energy.voltage), 0xFF))
        return res
    
    def read_FL_WHEEL_SPEED(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)
    
    def read_FR_WHEEL_SPEED(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)    
    
    def read_RL_WHEEL_SPEED(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  

    def read_RR_WHEEL_SPEED(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  

    def read_TM_SPEED(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  
    
    def read_LATERAL_G(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  
    
    def read_LONGITUDINAL_G(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  
    
    def read_YAW(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  
    
    def read_STR_ANGLE(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        return random.randint(0, 0xFF)  
    
    def read_SHIFT_POS(self):
        """
        Need to be made after developing the module for reading .blf files. 
        For now, random numbers will be used as a substitute.
        """
        shift_positions = {
            0x00: "N",
            0x01: "D",
            0x02: "B",
            0x03: "L",
            0x04: "S",
            0x05: "P",
            0x08: "R",
            0xFF: "Invalid"
        }
        return random.choice(list(shift_positions.keys()))  
    
    def read_SCS_CODE(self):
        return 0x00
    
    def read_SAE_CODE(self):
        return [0x00, 0x00, 0x00]
    
    def get_did_0xA19D(self):
        """
        Need to be made after developing SID$2E
        For now, [0x00, 0x00, ...] will be used as a substitute.
        """
        return [0x00]*56