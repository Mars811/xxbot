from logger import logger
import requests

# 技能注册表
SKILL_REGISTRY = {}
# 技能别名映射
SKILL_ALIASES = {
    "get_weather": "weather",
    "weather_query": "weather",
    "get_current_time": "time",
    "current_time": "time",
    "get_time": "time"
}

def register_skill(name):
    """技能注册装饰器"""
    def decorator(func):
        SKILL_REGISTRY[name] = func
        logger.system(f"注册技能: {name}")
        return func
    return decorator

def execute_skills(skills):
    """执行技能列表"""
    results = []
    
    for skill in skills:
        name = skill.get("name")
        params = skill.get("params", {})
        
        # 处理技能别名
        if name in SKILL_ALIASES:
            original_name = name
            name = SKILL_ALIASES[name]
            logger.system(f"技能别名映射: {original_name} -> {name}")
        
        if name in SKILL_REGISTRY:
            try:
                logger.system(f"执行技能: {name}, 参数: {params}")
                result = SKILL_REGISTRY[name](params)
                results.append(result)
                logger.success(f"技能执行成功: {name}")
            except Exception as e:
                logger.error(f"技能执行失败 {name}: {e}")
                results.append(f"技能执行失败: {e}")
        else:
            logger.error(f"技能不存在: {name}")
            results.append(f"技能不存在: {name}")
    
    return results

# 内置技能

@register_skill("weather")
def weather_skill(params):
    """天气查询技能"""
    location = params.get("location", "auto")
    
    try:
        # 这里使用一个免费的天气API
        # 实际使用时需要替换为真实的API
        logger.system(f"查询{location}的天气")
        
        # 模拟天气数据
        if location == "auto" or location == "北京":
            return "今天天气晴朗，温度25度，微风"
        elif location == "上海":
            return "今天天气多云，温度23度，有小雨"
        elif location == "广州":
            return "今天天气炎热，温度30度，湿度较大"
        else:
            return f"{location}的天气：晴朗，温度22度"
    except Exception as e:
        logger.error(f"天气查询失败: {e}")
        return "天气查询失败"

@register_skill("time")
def time_skill(params):
    """时间查询技能"""
    import datetime
    now = datetime.datetime.now()
    return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"

@register_skill("calculator")
def calculator_skill(params):
    """简单计算技能"""
    expression = params.get("expression", "")
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算失败: {e}"