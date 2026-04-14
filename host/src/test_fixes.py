#!/usr/bin/env python3
# 测试修复后的功能
import sys
import os

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

# 导入模块
from skill import SKILL_REGISTRY, SKILL_ALIASES, execute_skills
from logger import logger

print("\n=== 测试技能别名映射 ===")
print(f"技能注册表: {list(SKILL_REGISTRY.keys())}")
print(f"技能别名: {SKILL_ALIASES}")

# 测试技能别名映射
test_skills = [
    {"name": "get_weather", "params": {"location": "北京"}},
    {"name": "get_current_time", "params": {}},
    {"name": "weather", "params": {"location": "上海"}},
    {"name": "time", "params": {}}
]

print("\n=== 测试技能执行 ===")
results = execute_skills(test_skills)
print(f"技能执行结果: {results}")

print("\n=== 测试完成 ===")