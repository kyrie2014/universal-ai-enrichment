# API 文档

本文档描述了应用程序中使用的主要 API 和接口。

## 核心类

### AgentConfigManager

用于管理 Schema（数据模式）和 AI 设置的配置类。

```python
class AgentConfigManager:
    def __init__(self, config_file: str = "agent_config.json")
```

#### 方法

##### load_config()
```python
def load_config(self) -> dict
```
从 JSON 文件加载配置。

**返回值：** 配置字典

##### save_config()
```python
def save_config(self) -> bool
```
将当前配置保存到文件。

**返回值：** 成功返回 `True`，否则返回 `False`

##### get_active_schema()
```python
def get_active_schema(self) -> dict
```
获取当前激活的 Schema 配置。

**返回值：** Schema 字典

##### set_active_schema()
```python
def set_active_schema(self, schema_name: str) -> bool
```
设置激活的 Schema。

**参数：**
- `schema_name` (str)：要激活的 Schema 名称

**返回值：** 成功返回 `True`，若 Schema 不存在则返回 `False`

##### add_schema()
```python
def add_schema(self, name: str, schema: dict)
```
添加或更新一个 Schema。

**参数：**
- `name` (str)：Schema 标识符
- `schema` (dict)：Schema 配置内容

##### delete_schema()
```python
def delete_schema(self, name: str) -> bool
```
删除指定 Schema。

**参数：**
- `name` (str)：Schema 标识符

**返回值：** 成功删除返回 `True`，未找到则返回 `False`

---

### UniversalAIAgent

用于 AI 驱动的数据增强的核心代理类。

```python
class UniversalAIAgent:
    def __init__(self, config_manager: AgentConfigManager)
```

#### 方法

##### query_single()
```python
def query_single(self, input_data: dict, context: str = "") -> dict
```
对单条记录发起 AI 查询。

**参数：**
- `input_data` (dict)：来自 Schema 的输入字段
- `context` (str)：可选上下文信息

**返回值：** 包含输出字段的字典

**示例：**
```python
input_data = {"company_name": "Apple Inc."}
result = agent.query_single(input_data)
# 返回结果示例：{
#   "full_name": "Apple Inc.",
#   "legal_representative": "Tim Cook",
#   ...
# }
```

##### query_batch()
```python
def query_batch(
    self, 
    input_data_list: List[dict], 
    context: str = "", 
    batch_size: int = 15
) -> List[dict]
```
对多条记录进行批量 AI 查询。

**参数：**
- `input_data_list` (List[dict])：输入记录列表
- `context` (str)：可选上下文
- `batch_size` (int)：每批处理的记录数

**返回值：** 结果字典列表

**示例：**
```python
input_data_list = [
    {"company_name": "Apple Inc."},
    {"company_name": "Microsoft Corporation"}
]
result = agent.query_batch(input_data_list, batch_size=10)
```

##### generate_prompt()
```python
def generate_prompt(self, input_data: dict, is_batch: bool = False) -> str
```
根据模板和数据生成 AI 提示词。

**参数：**
- `input_data` (dict 或 list)：输入数据
- `is_batch` (bool)：是否为批量处理

**返回值：** 格式化后的提示字符串

---

### OpenAICompatibleClient

用于调用 OpenAI 兼容 API 的客户端。

```python
class OpenAICompatibleClient:
    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "",
        enable_deep_thinking: bool = False,
        enable_web_search: bool = False
    )
```

#### 方法

##### chat()
```python
def chat(
    self,
    prompt: str,
    stream: bool = True,
    parse_response: bool = True
) -> Optional[Dict[str, Any]]
```
向 AI 发送聊天请求。

**参数：**
- `prompt` (str)：要发送的提示词
- `stream` (bool)：是否使用流式响应
- `parse_response` (bool)：是否将响应解析为结构化数据

**返回值：**  
- 若 `parse_response=True`：返回解析后的字典  
- 若 `parse_response=False`：返回原始响应字符串

**示例：**
```python
client = OpenAICompatibleClient(
    api_key="sk-...",
    base_url="https://api.deepseek.com",
    model="deepseek-chat"
)

result = client.chat("什么是 Python？", stream=False)
```

##### test_connection()
```python
def test_connection(self) -> tuple[bool, str]
```
测试 API 连接是否正常。

**返回值：** `(是否成功, 消息文本)` 的元组

**示例：**
```python
success, message = client.test_connection()
if success:
    print("连接成功")
else:
    print(f"连接失败：{message}")
```

---

## Schema 配置

### Schema 结构

```json
{
  "name": "公司信息增强",
  "description": "丰富公司相关信息",
  "input_columns": [
    {
      "name": "company_name",
      "type": "string",
      "required": true,
      "description": "公司名称"
    }
  ],
  "output_columns": [
    {
      "name": "full_name",
      "type": "string",
      "description": "公司官方全称"
    },
    {
      "name": "legal_representative",
      "type": "string",
      "description": "法定代表人/CEO"
    }
  ],
  "prompt_template": "请提供关于 {company_name} 的信息……",
  "batch_prompt_template": "请处理以下公司列表……"
}
```

### 输入列 Schema

```typescript
{
  name: string;          // Excel 中的列名
  type: string;          // 数据类型（string、number、boolean、date）
  required: boolean;     // 是否必填
  description: string;   // 列说明
}
```

### 输出列 Schema

```typescript
{
  name: string;          // 要创建的列名
  type: string;          // 数据类型
  description: string;   // 该字段含义说明
}
```

---

## 配置文件格式

### agent_config.json

```json
{
  "active_schema": "company_enrichment",
  "schemas": {
    "company_enrichment": {
      "name": "公司信息增强",
      "description": "...",
      "input_columns": [...],
      "output_columns": [...],
      "prompt_template": "...",
      "batch_prompt_template": "..."
    }
  },
  "ai_settings": {
    "provider": "openai_compatible",
    "api_key": "your-api-key",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "temperature": 0.1,
    "max_tokens": 4000,
    "enable_mcp": true,
    "enable_deep_thinking": false,
    "enable_web_search": false,
    "batch_size": 15,
    "enable_turbo_mode": false,
    "turbo_batch_size": 100,
    "turbo_concurrent_requests": 5
  }
}
```

---

## 错误处理

### 错误响应格式

```python
{
  "error": "错误信息",
  "raw_response": "原始响应（如有）"
}
```

### 常见错误码

| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 401 | API 密钥无效 | 检查 API 密钥配置 |
| 402 | 余额不足 | 充值账户 |
| 404 | 模型未找到 | 核对模型名称 |
| 429 | 触发速率限制 | 等待或升级套餐 |
| 500 | 服务器内部错误 | 稍后重试 |

---

## 使用示例

### 基础用法

```python
from agent_main import AgentConfigManager, UniversalAIAgent

# 初始化
config_mgr = AgentConfigManager("config.json")
agent = UniversalAIAgent(config_mgr)

# 单条查询
result = agent.query_single({"company_name": "Apple"})
print(result)

# 批量查询
data_list = [
    {"company_name": "Apple"},
    {"company_name": "Microsoft"}
]
results = agent.query_batch(data_list, batch_size=10)
for result in results:
    print(result)
```

### 自定义 Schema

```python
# 创建自定义 Schema
schema = {
    "name": "产品信息",
    "description": "产品信息增强",
    "input_columns": [
        {"name": "product_name", "type": "string", "required": True}
    ],
    "output_columns": [
        {"name": "description", "type": "string"},
        {"name": "price", "type": "number"}
    ],
    "prompt_template": "请提供 {product_name} 的详细信息",
    "batch_prompt_template": "请提供以下产品的详细信息……"
}

config_mgr.add_schema("product_info", schema)
config_mgr.set_active_schema("product_info")
```

### AI 提供商配置

```python
# DeepSeek
config_mgr.config["ai_settings"] = {
    "api_key": "sk-...",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
}

# 阿里巴巴 Qwen
config_mgr.config["ai_settings"] = {
    "api_key": "sk-...",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-plus"
}

# OpenAI
config_mgr.config["ai_settings"] = {
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
}

config_mgr.save_config()
```

> ⚠️ 注意：`https://dashscope.aliyuncs.com/compatible-mode/v1` 路径可能已变更，请参考阿里云最新文档确认兼容模式端点。

---

## 最佳实践

### 性能优化
- 对超过 100 条记录的数据集使用批量处理
- 启用缓存以避免重复查询
- 根据数据复杂度调整批次大小
- 仅在处理大规模数据时启用 Turbo 模式

### 准确性提升
- 启用 MCP（Model Context Protocol）以获取实时信息
- 对复杂查询启用“深度思考”模式
- 编写清晰明确的提示词模板
- 处理完成后验证结果

### 成本控制
- 批量处理可节省约 93% 的 API 调用费用
- 积极使用缓存机制
- 根据任务复杂度选择合适模型（简单任务用小模型）
- 监控 Token 使用情况

### 错误处理
- 始终检查结果中是否包含 `error` 键
- 对临时性故障实现重试逻辑
- 在处理前校验输入数据
- 记录错误日志以便调试