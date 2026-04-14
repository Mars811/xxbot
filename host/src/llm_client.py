import requests
import json
from config import config
from logger import logger

class LLMClient:
    def __init__(self):
        self.base_url = config.LLM_BASE_URL
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
    
    def call_llm(self, messages):
        """调用LLM API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": config.LLM_TEMPERATURE,
            "max_tokens": config.LLM_MAX_TOKENS
        }
        
        try:
            logger.system(f"调用LLM API: {self.base_url}")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            logger.success("LLM API调用成功")
            return content
        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            return ""
    
    def parse_response(self, response_text):
        """解析LLM响应"""
        try:
            # 分离回复和指令
            if "```json" in response_text:
                parts = response_text.split("```json")
                reply = parts[0].strip()
                json_part = parts[1].split("```")[0].strip()
                
                # 解析JSON
                instructions = json.loads(json_part)
                return reply, instructions
            else:
                # 如果没有JSON部分，返回纯文本
                return response_text, {}
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            return response_text, {}
    
    def build_messages(self, user_input, stm, personality, ltm):
        """构建messages数组"""
        messages = []
        
        # 系统提示词
        system_prompt = self._get_system_prompt()
        messages.append({"role": "system", "content": system_prompt})
        
        # 性格和长期记忆
        if personality:
            messages.append({"role": "system", "content": f"# 性格特征\n{personality}"})
        
        if ltm:
            messages.append({"role": "system", "content": f"# 长期记忆\n{ltm}"})
        
        # 短期记忆（历史对话）
        for msg in stm:
            messages.append(msg)
        
        # 当前用户消息
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _get_system_prompt(self):
        """获取系统提示词"""
        prompt_file = "host-llm/system_prompt.md"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            # 默认提示词
            return '''你是xxbot，你的任务是准确扮演personality.md中描述的性格特征，并且根据ltm.md中的长期记忆，进行智能决策，回答用户问题。请在回复中包含以下格式：

用户回复内容

```json
{
  "memory": {
    "stm": "需要写入短期记忆的内容",
    "ltm": "需要写入长期记忆的内容"
  },
  "skills": [
    {"name": "技能名称", "params": {"参数1": "值1"}}
  ],
  "esp_cmd": {
    "skill": "技能名称",
    "params": {"参数1": "值1"}
  }
}
```'''

llm_client = LLMClient()