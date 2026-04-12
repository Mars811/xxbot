import logging
from typing import Callable, Optional
import paho.mqtt.client as mqtt
from config import config


class MQTTClient:
    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)
        self.client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.on_message_callback = on_message_callback
        self.connected = False
        self.logger = logging.getLogger(__name__)
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("MQTT连接成功")
            self.connected = True
            self.client.subscribe(config.MQTT_GET_TOPIC, qos=config.MQTT_QOS)
            self.logger.info(f"订阅主题: {config.MQTT_GET_TOPIC}")
        else:
            self.logger.error(f"MQTT连接失败，返回码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            self.logger.warning(f"MQTT意外断开，返回码: {rc}，尝试重连...")
            self._reconnect()
        else:
            self.logger.info("MQTT正常断开")
    
    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            self.logger.info(f"收到MQTT消息 - 主题: {topic}")
            self.logger.debug(f"消息内容: {payload}")
            
            if self.on_message_callback:
                self.on_message_callback(topic, payload)
        except Exception as e:
            self.logger.error(f"处理MQTT消息时出错: {e}")
    
    def _reconnect(self):
        try:
            self.logger.info("尝试重新连接MQTT...")
            self.client.reconnect()
        except Exception as e:
            self.logger.error(f"重连失败: {e}")
    
    def connect(self):
        try:
            self.logger.info(f"连接到MQTT服务器: {config.MQTT_URL}:{config.MQTT_PORT}")
            self.client.connect(
                config.MQTT_URL,
                config.MQTT_PORT,
                config.MQTT_KEEPALIVE
            )
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"MQTT连接失败: {e}")
            raise
    
    def disconnect(self):
        self.logger.info("断开MQTT连接")
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic: str, message: str, qos: Optional[int] = None):
        if not self.connected:
            self.logger.warning("MQTT未连接，无法发送消息")
            return False
        
        try:
            qos = qos or config.MQTT_QOS
            result = self.client.publish(topic, message, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"消息发送成功 - 主题: {topic}")
                return True
            else:
                self.logger.error(f"消息发送失败 - 返回码: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"发送消息时出错: {e}")
            return False
    

