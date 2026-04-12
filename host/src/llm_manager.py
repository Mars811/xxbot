import logging
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from config import config


class LLMManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = config.LLM_BASE_URL
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
        self.timeout = config.LLM_TIMEOUT
        
        self.host_dir = Path(__file__).parent.parent
        self.system_prompt = self._load_file("host-llm/system_prompt.md")
        self.personality = self._load_file("memory-bank/personality.md")
        self.ltm = self._load_file("memory-bank/ltm.md")
    
    def _load_file(self, relative_path: str) -> str:
        file_path = self.host_dir / relative_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.logger.info(f"成功加载文件: {relative_path}")
                return content
        except FileNotFoundError:
            self.logger.warning(f"文件不存在: {relative_path}")
            return ""
        except Exception as e:
            self.logger.error(f"加载文件失败 {relative_path}: {e}")
            return ""
    
    def process_talk(self, user_message: str) -> Tuple[str, list, list]:
        messages = self._build_messages(user_message)
        
        response_text = self._call_api(messages)
        
        reply, esp_skills, host_skills = self._parse_response(response_text)
        
        return reply, esp_skills, host_skills
    
    def _build_messages(self, user_message: str) -> list:
        system_content = f"{self.system_prompt}\n\n"
        system_content += f"## 性格特征\n{self.personality}\n\n"
        system_content += f"## 长期记忆\n{self.ltm}\n\n"
        system_content += "## 响应格式\n"
        system_content += "请按以下格式回复：\n"
        system_content += "回复内容\n"
        system_content += "[ESP_SKILL: 技能名称 参数]\n"
        system_content += "[HOST_SKILL: 技能名称 参数]\n"
        system_content += "\n示例：\n"
        system_content += "你好！今天天气不错，阳光明媚。\n"
        system_content += "[ESP_SKILL: speak \"你好！今天天气不错，阳光明媚。\"]\n"
        system_content += "[HOST_SKILL: update_memory \"user_likes_weather\" \"sunny\"]\n"
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]
        
        return messages
    
    def _call_api(self, messages: list) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            self.logger.info(f"调用LLM API: {self.base_url}")
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                self.logger.info("LLM API调用成功")
                self.logger.debug(f"LLM响应: {content}")
                return content
            else:
                self.logger.error(f"LLM API调用失败: {response.status_code} - {response.text}")
                return "抱歉，我现在无法回应。"
        except requests.exceptions.Timeout:
            self.logger.error("LLM API调用超时")
            return "抱歉，响应超时了。"
        except Exception as e:
            self.logger.error(f"LLM API调用异常: {e}")
            return "抱歉，出现了错误。"
    
    def _parse_response(self, response_text: str) -> Tuple[str, list, list]:
        lines = response_text.strip().split('\n')
        
        reply_lines = []
        esp_skills = []
        host_skills = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('[ESP_SKILL:'):
                skill = self._parse_skill_line(line, 'ESP_SKILL')
                if skill:
                    esp_skills.append(skill)
            elif line.startswith('[HOST_SKILL:'):
                skill = self._parse_skill_line(line, 'HOST_SKILL')
                if skill:
                    host_skills.append(skill)
            else:
                reply_lines.append(line)
        
        reply = '\n'.join(reply_lines).strip()
        
        return reply, esp_skills, host_skills
    
    def _parse_skill_line(self, line: str, skill_type: str) -> Optional[Dict[str, Any]]:
        try:
            prefix = f'[{skill_type}: '
            if not line.startswith(prefix):
                return None
            
            content = line[len(prefix):-1]
            
            parts = content.split(None, 1)
            if not parts:
                return None
            
            skill_name = parts[0]
            params = {}
            
            if len(parts) > 1:
                params_str = parts[1]
                
                if params_str.startswith('"') and params_str.endswith('"'):
                    params["text"] = params_str[1:-1]
                elif params_str.startswith("'") and params_str.endswith("'"):
                    params["text"] = params_str[1:-1]
                else:
                    param_pairs = params_str.split()
                    for pair in param_pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            params[key] = value.strip('"\'')
            
            return {"skill": skill_name, "params": params}
        except Exception as e:
            self.logger.error(f"解析技能行失败: {line} - {e}")
            return None
