# 云端架构设计方案

## 1. 核心决策逻辑（一条消息的完整生命周期）

```mermaid
flowchart TD
    A[MQTT收到消息] --> B[JSON解析]
    B --> C{command.type?}
    C -->|talk| D[读取记忆]
    C -->|其他命令| Z[预留扩展]
    
    D --> D1[从STM读取最近N轮对话]
    D --> D2[从LTM读取用户偏好/关键信息]
    
    D1 --> E[组装messages数组]
    D2 --> E
    
    E --> E1[system: 系统提示词 + LTM内容]
    E1 --> E2[历史对话: STM中的对话记录]
    E2 --> E3[user: 当前用户消息]
    
    E3 --> F[HTTP POST 调用LLM API]
    F --> G[拿到LLM响应文本]
    
    G --> H[解析响应文本]
    H --> H1[提取reply: 给用户的回复]
    H --> H2[提取instructions: LLM对云端的指令]
    
    H2 --> I{指令类型分发}
    I -->|memory| J[写入记忆]
    I -->|skill| K[执行技能]
    I -->|esp_cmd| L[转发给设备]
    
    J --> J1[STM: 追加当前对话]
    J --> J2[LTM: LLM认为重要的信息]
    
    K --> K1[调用对应skill函数]
    K1 --> K2[拿到skill返回值]
    
    H1 --> M[构建响应JSON]
    K2 --> M
    L --> M
    
    M --> N[通过MQTT发送回设备]
```

## 2. LLM响应格式

LLM的响应不是纯文本，而是结构化的。云端通过提示词约束LLM的输出格式：

### 2.1 LLM输出格式
```
你好！今天天气很好，阳光明媚。

```json
{
  "memory": {
    "stm": "用户问天气，回答天气好",
    "ltm": "用户关注天气"
  },
  "skills": [
    {"name": "weather", "params": {"location": "auto"}}
  ],
  "esp_cmd": {
    "skill": "expression",
    "params": {"type": "happy"}
  }
}
```
```

### 2.2 解析规则
- ```json ``` 代码块之前的内容 → `reply`（给用户的回复）
- ```json ``` 代码块内的JSON → `instructions`（LLM对云端的指令）

### 2.3 instructions字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| memory.stm | string | 写入短期记忆的内容 |
| memory.ltm | string | 写入长期记忆的内容 |
| skills | array | 云端需要执行的技能列表 |
| esp_cmd | object | 需要转发给设备执行的命令 |

## 3. 记忆系统

```mermaid
flowchart LR
    subgraph 写入
        A[LLM返回memory指令] --> B{memory类型}
        B -->|stm| C[追加到对话历史列表]
        B -->|ltm| D[追加到长期记忆文件]
    end
    
    subgraph 读取
        E[收到新消息] --> F[读取STM: 最近N轮对话]
        E --> G[读取LTM: 用户偏好/关键信息]
        F --> H[组装到LLM的messages中]
        G --> H
    end
    
    subgraph 清理
        I[STM超过N轮] --> J[删除最早的对话]
        K[LTM定期整理] --> L[LLM压缩冗余信息]
    end
```

### 3.1 STM（短期记忆）
- **存储方式**：内存中的列表 `[{role, content}, ...]`
- **容量**：最近10轮对话
- **用途**：作为LLM的对话历史传入messages
- **清理**：超过10轮时，删除最早的

### 3.2 LTM（长期记忆）
- **存储方式**：文件 `memory-bank/ltm.md`
- **内容**：LLM认为需要长期记住的信息（用户偏好、重要事件等）
- **用途**：拼接到system prompt中
- **清理**：当文件过大时，让LLM重新整理压缩

## 4. 技能系统

```mermaid
flowchart TD
    A[LLM返回skills指令] --> B[遍历skills列表]
    B --> C{skill.name}
    C -->|weather| D[调用weather函数]
    C -->|time| E[调用time函数]
    C -->|其他| F[查找注册的自定义skill]
    
    D --> G[获取skill返回值]
    E --> G
    F --> G
    
    G --> H[将结果追加到reply中]
```

### 4.1 技能注册
```python
SKILL_REGISTRY = {
    "weather": weather_skill,
    "time": time_skill,
}

def register_skill(name, func):
    SKILL_REGISTRY[name] = func
```

### 4.2 技能执行
```python
def execute_skills(skills):
    results = []
    for skill in skills:
        func = SKILL_REGISTRY.get(skill["name"])
        if func:
            result = func(skill["params"])
            results.append(result)
    return results
```

## 5. 组装LLM请求

```mermaid
flowchart TD
    A[准备调用LLM] --> B[构建messages]
    
    B --> B1["system: 系统提示词\n（角色设定 + 可用技能说明 + 输出格式要求）"]
    B1 --> B2["system: 长期记忆\n（LTM文件内容）"]
    B2 --> B3["历史对话\n（STM中的对话记录）"]
    B3 --> B4["user: 当前用户消息"]
    
    B4 --> C["HTTP POST → LLM API"]
    C --> D["解析响应文本"]
```

### 5.1 messages数组结构
```python
messages = [
    {"role": "system", "content": system_prompt},      # 系统提示词
    {"role": "system", "content": ltm_content},         # 长期记忆
    {"role": "user", "content": "你好"},                # 历史对话
    {"role": "assistant", "content": "你好！"},          # 历史对话
    ...                                                  # 更多历史
    {"role": "user", "content": current_msg},           # 当前消息
]
```

## 6. 完整数据流（从设备到设备）

```mermaid
sequenceDiagram
    participant D as 设备
    participant M as MQTT
    participant H as 云端主循环
    participant MEM as 记忆
    participant LLM as LLM API
    participant SKILL as 技能

    D->>M: 发布JSON到GET_TOPIC
    M->>H: 收到消息
    
    H->>H: 解析JSON, 提取msg
    H->>MEM: 读取STM(对话历史)
    H->>MEM: 读取LTM(长期记忆)
    
    H->>LLM: POST messages数组
    LLM-->>H: 返回响应文本
    
    H->>H: 解析reply和instructions
    
    H->>MEM: 写入STM(当前对话)
    H->>MEM: 写入LTM(LLM指定的内容)
    
    H->>SKILL: 执行skills
    SKILL-->>H: 返回结果
    
    H->>H: 构建响应JSON
    H->>M: 发布到UPDATE_TOPIC
    M->>D: 收到响应
```

## 7. 模块划分（对应代码文件）

```
host/src/
├── main.py              # 主循环：MQTT消息驱动
├── config.py            # 配置：从host.env加载
├── mqtt_client.py       # MQTT：收发消息
├── json_parser.py       # JSON解析：解析设备消息
├── llm_client.py        # LLM调用：HTTP请求 + 响应解析
├── memory.py            # 记忆：STM + LTM读写
├── skill.py             # 技能：注册 + 执行
└── ui_manager.py        # 界面：命令行监控
```

### 7.1 各模块职责

| 模块 | 输入 | 输出 | 职责 |
|------|------|------|------|
| main.py | MQTT消息 | MQTT响应 | 串联所有模块的主循环 |
| config.py | host.env | 配置对象 | 加载环境变量 |
| mqtt_client.py | 主题+消息 | 收发确认 | MQTT连接和通信 |
| json_parser.py | JSON字符串 | 命令对象 | 解析设备发来的JSON |
| llm_client.py | messages数组 | reply + instructions | 调用API并解析响应 |
| memory.py | 读写请求 | 记忆内容 | STM和LTM的读写管理 |
| skill.py | skill指令 | 执行结果 | 技能注册和执行 |
| ui_manager.py | 事件 | 控制台输出 | 显示系统运行状态 |

## 8. 伪智能的实现原理

### 8.1 为什么叫"伪智能"
- 不是真正的AI推理，而是利用LLM的生成能力
- 通过精心设计的提示词，让LLM输出结构化指令
- 云端只是忠实地执行LLM的指令，本身不做决策

### 8.2 智能来源
1. **上下文连续性**：STM让LLM看到历史对话，实现连贯对话
2. **个性化**：LTM让LLM记住用户偏好，实现个性化回应
3. **技能扩展**：LLM决定何时调用什么技能，云端只负责执行
4. **记忆决策**：LLM自己决定什么该记、什么不该记

### 8.3 关键设计
- **LLM是唯一的决策者**：云端不做任何自主决策
- **云端是忠实的执行者**：解析LLM指令并执行
- **提示词是行为的核心**：改提示词 = 改行为
