import logging
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text


class UIManager:
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        self.message_count = 0
        self.api_call_count = 0
        self.error_count = 0
    
    def show_welcome(self):
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              XXBOT Host System - 上位机监控系统               ║
║                                                              ║
║  功能: MQTT消息处理 | LLM对话管理 | 设备控制                  ║
║  版本: v1.0.0                                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(welcome_text, style="bold cyan")
    
    def show_mqtt_message(self, topic: str, payload: str, direction: str = "接收"):
        self.message_count += 1
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if direction == "接收":
            icon = "[IN]"
            color = "green"
        else:
            icon = "[OUT]"
            color = "blue"
        
        panel = Panel(
            f"[bold]{payload}[/bold]",
            title=f"{icon} MQTT消息 #{self.message_count} [{timestamp}]",
            subtitle=f"主题: {topic}",
            border_style=color
        )
        
        self.console.print(panel)
    
    def show_api_request(self, request_data: dict):
        self.api_call_count += 1
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        table = Table(title=f"[REQ] API请求 #{self.api_call_count} [{timestamp}]")
        table.add_column("字段", style="cyan")
        table.add_column("内容", style="white")
        
        if "messages" in request_data:
            for i, msg in enumerate(request_data["messages"]):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if len(content) > 100:
                    content = content[:100] + "..."
                table.add_row(f"消息{i+1} ({role})", content)
        
        if "model" in request_data:
            table.add_row("模型", request_data["model"])
        
        if "temperature" in request_data:
            table.add_row("温度", str(request_data["temperature"]))
        
        self.console.print(table)
    
    def show_api_response(self, response_text: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        panel = Panel(
            f"[bold]{response_text}[/bold]",
            title=f"[RESP] API响应 [{timestamp}]",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def show_parsed_command(self, command):
        table = Table(title="[PARSER] 解析后的命令")
        table.add_column("字段", style="cyan")
        table.add_column("值", style="white")
        
        table.add_row("来源", command.object)
        table.add_row("时间", command.time)
        table.add_row("命令类型", command.command_type)
        table.add_row("数据", str(command.data))
        
        self.console.print(table)
    
    def show_skills(self, esp_skills: list, host_skills: list):
        if not esp_skills and not host_skills:
            return
        
        table = Table(title="[SKILLS] 技能列表")
        table.add_column("类型", style="cyan")
        table.add_column("技能", style="green")
        table.add_column("参数", style="yellow")
        
        for skill in esp_skills:
            table.add_row(
                "ESP",
                skill.get("skill", ""),
                str(skill.get("params", {}))
            )
        
        for skill in host_skills:
            table.add_row(
                "HOST",
                skill.get("skill", ""),
                str(skill.get("params", {}))
            )
        
        self.console.print(table)
    
    def show_error(self, error_msg: str):
        self.error_count += 1
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        panel = Panel(
            f"[bold red]{error_msg}[/bold red]",
            title=f"[ERROR] 错误 #{self.error_count} [{timestamp}]",
            border_style="red"
        )
        
        self.console.print(panel)
    
    def show_status(self, status: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if "成功" in status or "连接" in status:
            style = "green"
            icon = "[OK]"
        elif "失败" in status or "错误" in status:
            style = "red"
            icon = "[ERROR]"
        else:
            style = "yellow"
            icon = "[INFO]"
        
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append(f"{icon} {status}", style=style)
        
        self.console.print(text)
    
    def show_statistics(self):
        table = Table(title="[STATS] 系统统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="green")
        
        table.add_row("MQTT消息数", str(self.message_count))
        table.add_row("API调用数", str(self.api_call_count))
        table.add_row("错误数", str(self.error_count))
        
        self.console.print(table)
    
    def show_separator(self):
        self.console.print("\n" + "─" * 80 + "\n", style="dim")


ui_manager = UIManager()
