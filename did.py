import os
import json
import yaml
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any

@dataclass
class DID:
    id: int
    name: str
    category: str
    length: int
    get_func: Optional[Callable[[], bytes]] = None
    value: Optional[bytes] = None


class DIDManager:
    """
    YAML and JSON are both supported
    Give priority to using JSON
    """
    def __init__(self, yaml_path: str, json_path: str):
        self.yaml_path = yaml_path
        self.json_path = json_path
        self.supported_dids: Dict[int, DID] = {}
        self.func_registry: Dict[str, Callable[[int], bytes]] = {
            "get_sensor_data": self.get_sensor_data
        }

        self._load_config()

    # ========= 示例动态函数 =========
    def get_data(self, index: int) -> bytes:
        # 模拟某个传感器值
        value = index
        return value.to_bytes(2, "big") + b"\x00\x00"

    # ========= Config loading logic =========
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

        #did from range
        for data, ranges in cfg.get("ranges", {}).items():
            for r in ranges:
                for did in range(r["start"], r["end"] + 1):
                    self.supported_dids[did] = DID(
                        id=did,
                        name=f"{data}_DID_{hex(did)[2:].upper()}",
                        category=data,
                        length=r["default_length"],
                        value=bytes.fromhex(r["default_value"]),
                    )

        #did from templates
        for tpl in cfg.get("templates", []):
            start = tpl["start_id"]
            func = self.func_registry[tpl["func_name"]]
            for i in range(tpl["count"]):
                did = start + i
                name = tpl["pattern"].format(index=i + 1)
                self.supported_dids[did] = DID(
                    id=did,
                    name=name,
                    category=tpl["category"],
                    length=tpl["length"],
                    get_func=lambda idx=i: func(idx),
                )

        #special did
        for s in cfg.get("specific", []):
            did = int(s["id"], 16) if isinstance(s["id"], str) else s["id"]
            if s["type"] == "static":
                value = bytes.fromhex(s["value"])
                self.supported_dids[did] = DID(
                    id=did, name=s["name"], category="Specific",
                    length=s["length"], value=value
                )
            elif s["type"] == "function":
                func = self.func_registry[s["func_name"]]
                self.supported_dids[did] = DID(
                    id=did, name=s["name"], category="Specific",
                    length=s["length"], get_func=func
                )

    # ========= public api =========
    def is_supported(self, did: int) -> bool:
        return did in self.supported_dids

    def read_did(self, did: int) -> Optional[bytes]:
        entry = self.supported_dids.get(did)
        if not entry:
            return None

        if entry.get_func:
            data = entry.get_func()
        else:
            data = entry.value

        if data is None or len(data) != entry.length:
            raise ValueError(f"DID {hex(did)} length error: Definition is {entry.length}, now it is{len(data) if data else 0}")
        return data

    def refresh_cache(self):
        """Force refresh cache"""
        if os.path.exists(self.yaml_path):
            data = self._load_yaml(self.yaml_path)
            self._save_json_cache(data, self.json_path)
            self._build_did_table(data)

    def test(self):
        self.refresh_cache()