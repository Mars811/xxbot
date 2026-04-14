import os
from config import config
from logger import logger

class MemoryManager:
    def __init__(self):
        self.stm_messages = []
        self.dialogue_count = 0
        
        # 初始化文件路径
        self.personality_file = os.path.join(os.path.dirname(__file__), "..", "memory-bank", "personality.md")
        self.ltm_file = os.path.join(os.path.dirname(__file__), "..", "memory-bank", "ltm.md")
        
        # 确保文件存在
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        # 创建personality.md（如果不存在）
        if not os.path.exists(self.personality_file):
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                f.write("# 性格特征\n\n## 核心性格\n- **友好**: 对用户保持友好和热情的态度\n- **乐于助人**: 主动提供帮助和建议\n- **好奇**: 对周围环境和用户行为保持好奇\n- **温和**: 语气温和，不急躁\n\n## 对话风格\n- 使用简洁明了的语言\n- 适当使用表情符号增加亲和力\n- 避免过于正式的表达\n- 保持积极的对话氛围\n\n## 行为特征\n- 主动关心用户状态\n- 记住用户偏好\n- 适时提供建议\n- 保持适度的幽默感\n\n## 情感表达\n- 对用户的成功表示祝贺\n- 对用户的困难表示同情\n- 对有趣的事物表现出兴趣\n- 对错误表示歉意\n\n## 学习倾向\n- 从用户反馈中学习\n- 记住重要的用户信息\n- 逐步优化对话策略\n- 保持开放的学习态度")
            logger.success(f"创建了personality.md文件")
        
        # 创建ltm.md（如果不存在）
        if not os.path.exists(self.ltm_file):
            with open(self.ltm_file, 'w', encoding='utf-8') as f:
                f.write("# 长期记忆\n\n## 用户偏好\n\n## 重要事件\n")
            logger.success(f"创建了ltm.md文件")
    
    def get_stm(self):
        """获取短期记忆"""
        return self.stm_messages
    
    def add_to_stm(self, role, content):
        """添加到短期记忆"""
        self.stm_messages.append({"role": role, "content": content})
        
        # 控制STM大小
        if len(self.stm_messages) > config.STM_MAX_MESSAGES:
            removed = self.stm_messages.pop(0)
            logger.memory(f"STM超过容量，移除最早的对话: {removed['content'][:20]}...")
    
    def get_personality(self):
        """获取性格文件内容"""
        try:
            with open(self.personality_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"读取personality.md失败: {e}")
            return ""
    
    def get_ltm(self, full=False):
        """获取长期记忆"""
        try:
            with open(self.ltm_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not full and len(content) > config.LTM_CORE_SIZE:
                content = content[:config.LTM_CORE_SIZE]
                logger.memory(f"读取LTM核心部分（{config.LTM_CORE_SIZE}字符）")
            else:
                logger.memory(f"读取完整LTM（{len(content)}字符）")
            
            return content
        except Exception as e:
            logger.error(f"读取ltm.md失败: {e}")
            return ""
    
    def add_to_ltm(self, content):
        """添加到长期记忆"""
        try:
            # 读取现有内容
            with open(self.ltm_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # 添加新内容
            new_content = existing_content + f"\n{content}"
            
            # 检查大小
            if len(new_content) > config.LTM_MAX_SIZE:
                logger.memory(f"LTM超过容量，需要压缩")
                # 这里可以实现压缩逻辑
            
            # 写回文件
            with open(self.ltm_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.memory(f"添加到LTM: {content[:50]}...")
        except Exception as e:
            logger.error(f"写入ltm.md失败: {e}")
    
    def should_read_full_ltm(self):
        """判断是否需要读取完整LTM"""
        self.dialogue_count += 1
        return self.dialogue_count == 1 or self.dialogue_count % config.LTM_FULL_READ_INTERVAL == 0

memory_manager = MemoryManager()