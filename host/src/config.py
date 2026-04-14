import os

class Config:
    def __init__(self):
        self.LLM_BASE_URL = os.getenv("LLM_BASE_URL")
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")
        self.LLM_MODEL = os.getenv("LLM_MODEL")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        self.STM_MAX_MESSAGES = int(os.getenv("STM_MAX_MESSAGES", "10"))
        self.LTM_MAX_SIZE = int(os.getenv("LTM_MAX_SIZE", "10240"))
        self.LTM_CORE_SIZE = int(os.getenv("LTM_CORE_SIZE", "1000"))
        self.LTM_FULL_READ_INTERVAL = int(os.getenv("LTM_FULL_READ_INTERVAL", "10"))
        
        self.MQTT_GET_TOPIC = os.getenv("MQTT_GET_TOPIC")
        self.MQTT_UPDATE_TOPIC = os.getenv("MQTT_UPDATE_TOPIC")

config = Config()