import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    def __init__(self, env_file: Optional[str] = None):
        if env_file:
            env_path = Path(env_file)
        else:
            env_path = Path(__file__).parent.parent / "host.env"
        
        load_dotenv(env_path)
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        self.LLM_BASE_URL = os.getenv("LLM_BASE_URL")
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")
        self.LLM_MODEL = os.getenv("LLM_MODEL")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE")) if os.getenv("LLM_TEMPERATURE") else None
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None
        self.LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT")) if os.getenv("LLM_TIMEOUT") else None
        
        self.MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
        self.MQTT_USERNAME = os.getenv("MQTT_USERNAME")
        self.MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
        self.MQTT_URL = os.getenv("MQTT_URL")
        self.MQTT_PORT = int(os.getenv("MQTT_PORT")) if os.getenv("MQTT_PORT") else None
        self.MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE")) if os.getenv("MQTT_KEEPALIVE") else None
        self.MQTT_QOS = int(os.getenv("MQTT_QOS")) if os.getenv("MQTT_QOS") else None
        self.MQTT_UPDATE_TOPIC = os.getenv("MQTT_UPDATE_TOPIC")
        self.MQTT_GET_TOPIC = os.getenv("MQTT_GET_TOPIC")
        
        self.LOG_LEVEL = os.getenv("LOG_LEVEL")
        self.LOG_FILE = os.getenv("LOG_FILE")
    
    def _validate_config(self):
        required_configs = [
            ("LLM_BASE_URL", self.LLM_BASE_URL),
            ("LLM_API_KEY", self.LLM_API_KEY),
            ("LLM_MODEL", self.LLM_MODEL),
            ("MQTT_CLIENT_ID", self.MQTT_CLIENT_ID),
            ("MQTT_USERNAME", self.MQTT_USERNAME),
            ("MQTT_PASSWORD", self.MQTT_PASSWORD),
            ("MQTT_URL", self.MQTT_URL),
            ("MQTT_PORT", self.MQTT_PORT),
            ("MQTT_UPDATE_TOPIC", self.MQTT_UPDATE_TOPIC),
            ("MQTT_GET_TOPIC", self.MQTT_GET_TOPIC),
        ]
        
        missing_configs = []
        for name, value in required_configs:
            if value is None:
                missing_configs.append(name)
        
        if missing_configs:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing_configs)}")
    



config = Config()
