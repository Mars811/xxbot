import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedCommand:
    object: str
    time: str
    command_type: str
    data: Dict[str, Any]
    raw_json: Dict[str, Any]
    
    def is_device_talk(self) -> bool:
        return self.object == "device" and self.command_type == "talk"
    
    def is_host_talk(self) -> bool:
        return self.object == "host" and self.command_type == "talk"


class JSONParser:
    @staticmethod
    def parse(json_str: str) -> ParsedCommand:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}")
        
        JSONParser._validate_structure(data)
        
        return ParsedCommand(
            object=data["object"],
            time=data["time"],
            command_type=data["command"]["type"],
            data=data["command"]["data"],
            raw_json=data
        )
    
    @staticmethod
    def _validate_structure(data: Dict[str, Any]):
        required_fields = ["object", "time", "command"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")
        
        if "type" not in data["command"]:
            raise ValueError("command字段缺少type")
        
        if "data" not in data["command"]:
            raise ValueError("command字段缺少data")
        
        if data["object"] not in ["device", "host"]:
            raise ValueError(f"无效的object值: {data['object']}")
    
    @staticmethod
    def build_response(
        msg: str,
        esp_skills: Optional[list] = None,
        host_skills: Optional[list] = None
    ) -> str:
        response_data = {
            "msg": msg
        }
        
        if esp_skills:
            response_data["esp_skills"] = esp_skills
        
        if host_skills:
            response_data["host_skills"] = host_skills
        
        response = {
            "object": "host",
            "time": datetime.now().isoformat(),
            "command": {
                "type": "talk",
                "data": response_data
            }
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
    
    @staticmethod
    def build_error_response(error_msg: str) -> str:
        response = {
            "object": "host",
            "time": datetime.now().isoformat(),
            "command": {
                "type": "error",
                "data": {
                    "msg": error_msg
                }
            }
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
