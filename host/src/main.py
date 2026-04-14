import os
import json
import sys

# 先加载环境变量
env_file = os.path.join(os.path.dirname(__file__), "..", "host.env")
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
    print("加载环境变量成功")
else:
    print("host.env文件不存在")

# 现在再导入其他模块
from config import config
from logger import logger
from memory import memory_manager
from llm_client import llm_client
from skill import execute_skills, SKILL_ALIASES

class XXBotHost:
    def __init__(self):
        logger.info("系统", "初始化XXBot Host")
    
    def initialize_environment(self):
        """初始化环境"""
        # 环境变量已经在导入模块之前加载
        logger.success("加载环境变量成功")
    
    def handle_message(self, user_input):
        """处理消息"""
        # 构建JSON（模拟设备发送的格式）
        message_json = {
            "object": "device",
            "time": "2026-04-14T10:00:00Z",
            "command": {
                "type": "talk",
                "data": {
                    "msg": user_input
                }
            }
        }
        
        logger.system(f"收到消息: {user_input}")
        
        # 解析命令
        command_type = message_json.get("command", {}).get("type", "")
        if command_type == "talk":
            self.handle_talk_command(message_json)
        else:
            logger.error(f"未知命令类型: {command_type}")
    
    def handle_talk_command(self, message_json):
        """处理talk命令"""
        # 提取消息内容
        msg = message_json.get("command", {}).get("data", {}).get("msg", "")
        
        # 读取记忆
        stm = memory_manager.get_stm()
        personality = memory_manager.get_personality()
        
        # 判断是否读取完整LTM
        full_ltm = memory_manager.should_read_full_ltm()
        ltm = memory_manager.get_ltm(full=full_ltm)
        
        # 构建messages
        messages = llm_client.build_messages(msg, stm, personality, ltm)
        
        # 调用LLM
        response_text = llm_client.call_llm(messages)
        
        if not response_text:
            logger.error("LLM没有返回响应")
            return
        
        # 解析响应
        reply, instructions = llm_client.parse_response(response_text)
        
        # 处理记忆指令
        if "memory" in instructions:
            memory_data = instructions["memory"]
            if "stm" in memory_data:
                memory_manager.add_to_stm("assistant", memory_data["stm"])
            if "ltm" in memory_data and memory_data["ltm"]:
                memory_manager.add_to_ltm(memory_data["ltm"])
        
        # 处理技能指令
        skill_results = []
        if "skills" in instructions:
            skill_results = execute_skills(instructions["skills"])
        
        # 处理esp_cmd指令（预留）
        esp_cmd = instructions.get("esp_cmd", {})
        
        # 处理esp_cmd中的技能别名
        if "skill" in esp_cmd:
            skill_name = esp_cmd["skill"]
            if skill_name in SKILL_ALIASES:
                original_skill = skill_name
                esp_cmd["skill"] = SKILL_ALIASES[skill_name]
                logger.system(f"ESP指令技能别名映射: {original_skill} -> {esp_cmd['skill']}")
        
        # 构建响应
        response = {
            "object": "host",
            "time": "2026-04-14T10:00:01Z",
            "command": {
                "type": "talk",
                "data": {
                    "msg": reply,
                    "skills": skill_results,
                    "esp_cmd": esp_cmd
                }
            }
        }
        
        # 输出结果
        logger.dialogue(f"回复: {reply}")
        
        if skill_results:
            for result in skill_results:
                logger.system(f"技能结果: {result}")
        
        if esp_cmd:
            logger.system(f"设备指令: {esp_cmd}")
        
        # 添加到STM
        memory_manager.add_to_stm("user", msg)
        memory_manager.add_to_stm("assistant", reply)
    
    def run(self):
        """运行主循环"""
        logger.info("系统", "XXBot Host启动成功")
        logger.info("系统", "输入'quit'退出")
        
        while True:
            try:
                user_input = input("你: ")
                if user_input.lower() == "quit":
                    logger.info("系统", "退出系统")
                    break
                self.handle_message(user_input)
            except KeyboardInterrupt:
                logger.info("系统", "用户中断")
                break
            except Exception as e:
                logger.error(f"处理消息时出错: {e}")

if __name__ == "__main__":
    host = XXBotHost()
    host.run()