import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from config import config
from mqtt_client import MQTTClient
from json_parser import JSONParser, ParsedCommand
from llm_manager import LLMManager
from ui_manager import ui_manager


class XXBotHost:
    def __init__(self):
        self._setup_logging()
        
        self.mqtt_client: Optional[MQTTClient] = None
        self.llm_manager: Optional[LLMManager] = None
        self.running = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / Path(config.LOG_FILE).name
        
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"接收到信号 {signum}，准备退出...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        try:
            ui_manager.show_welcome()
            ui_manager.show_status("正在初始化系统...")
            
            self.llm_manager = LLMManager()
            ui_manager.show_status("LLM管理器初始化成功")
            
            self.mqtt_client = MQTTClient(on_message_callback=self._handle_mqtt_message)
            self.mqtt_client.connect()
            ui_manager.show_status("MQTT客户端连接成功")
            
            self.running = True
            ui_manager.show_status("系统启动成功，开始监听消息...")
            ui_manager.show_separator()
            
            while self.running:
                import time
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"系统启动失败: {e}")
            ui_manager.show_error(f"系统启动失败: {e}")
            self.stop()
    
    def stop(self):
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            ui_manager.show_status("MQTT客户端已断开")
        
        ui_manager.show_statistics()
        ui_manager.show_status("系统已停止")
    
    def _handle_mqtt_message(self, topic: str, payload: str):
        try:
            ui_manager.show_mqtt_message(topic, payload, "接收")
            
            parsed_command = JSONParser.parse(payload)
            ui_manager.show_parsed_command(parsed_command)
            
            if parsed_command.is_device_talk():
                self._handle_device_talk(parsed_command)
            elif parsed_command.is_host_talk():
                self._handle_host_talk(parsed_command, topic)
            else:
                ui_manager.show_status(f"未处理的命令类型: {parsed_command.command_type}")
                
        except ValueError as e:
            ui_manager.show_error(f"JSON解析失败: {e}")
        except Exception as e:
            ui_manager.show_error(f"处理消息时出错: {e}")
        
        ui_manager.show_separator()
    
    def _handle_device_talk(self, parsed_command: ParsedCommand):
        try:
            user_message = parsed_command.data.get("msg", "")
            
            if not user_message:
                ui_manager.show_error("talk命令缺少msg字段")
                return
            
            ui_manager.show_status(f"处理用户消息: {user_message}")
            
            reply, esp_skills, host_skills = self.llm_manager.process_talk(user_message)
            
            ui_manager.show_api_response(reply)
            ui_manager.show_skills(esp_skills, host_skills)
            
            response_json = JSONParser.build_response(reply, esp_skills, host_skills)
            
            self._process_response_json(response_json)
            
        except Exception as e:
            ui_manager.show_error(f"处理设备对话失败: {e}")
    
    def _handle_host_talk(self, parsed_command: ParsedCommand, topic: str):
        try:
            msg = parsed_command.data.get("msg", "")
            esp_skills = parsed_command.data.get("esp_skills", [])
            host_skills = parsed_command.data.get("host_skills", [])
            
            ui_manager.show_status(f"转发消息到设备: {msg}")
            ui_manager.show_skills(esp_skills, host_skills)
            
            device_id = self._extract_device_id(topic)
            
            if device_id:
                success = self.mqtt_client.publish_to_device(device_id, str(parsed_command.raw_json))
                
                if success:
                    ui_manager.show_mqtt_message(
                        config.get_mqtt_topic_host_to_device(device_id),
                        str(parsed_command.raw_json),
                        "发送"
                    )
                else:
                    ui_manager.show_error("发送消息到设备失败")
            else:
                ui_manager.show_error("无法从主题中提取设备ID")
                
        except Exception as e:
            ui_manager.show_error(f"处理主机对话失败: {e}")
    
    def _process_response_json(self, response_json: str):
        try:
            parsed_response = JSONParser.parse(response_json)
            
            if parsed_response.is_host_talk():
                ui_manager.show_status("检测到host talk命令，准备转发")
                
                self._handle_host_talk(parsed_response, "local")
            else:
                ui_manager.show_status(f"未知的响应类型: {parsed_response.command_type}")
                
        except Exception as e:
            ui_manager.show_error(f"处理响应JSON失败: {e}")
    
    def _extract_device_id(self, topic: str) -> Optional[str]:
        parts = topic.split('/')
        
        for i, part in enumerate(parts):
            if part == "device" and i + 1 < len(parts):
                return parts[i + 1]
        
        return "default"


def main():
    host = XXBotHost()
    host.start()


if __name__ == "__main__":
    main()
