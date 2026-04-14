import datetime
import sys
import io

# 确保stdout使用UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Logger:
    @staticmethod
    def _get_timestamp():
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def _print_with_color(text, color_code):
        try:
            print(f"\033[{color_code}m{text}\033[0m")
        except Exception as e:
            # 尝试使用不同的编码方式
            print(f"{text}")
    
    @staticmethod
    def info(prefix, message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【{prefix}】{message}"
        Logger._print_with_color(text, "36")  # Cyan
    
    @staticmethod
    def dialogue(message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【对话输出】{message}"
        Logger._print_with_color(text, "31")  # Red
    
    @staticmethod
    def memory(message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【记忆管理】{message}"
        Logger._print_with_color(text, "34")  # Blue
    
    @staticmethod
    def system(message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【系统处理】{message}"
        Logger._print_with_color(text, "33")  # Yellow
    
    @staticmethod
    def error(message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【错误】{message}"
        Logger._print_with_color(text, "31;1")  # Bold red
    
    @staticmethod
    def success(message):
        timestamp = Logger._get_timestamp()
        text = f"{timestamp}【成功】{message}"
        Logger._print_with_color(text, "32")  # Green

logger = Logger()