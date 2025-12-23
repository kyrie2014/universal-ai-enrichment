# 通用AI数据补全工具

[English](README.md) | 简体中文

一个功能强大、灵活的Excel数据AI补全工具。支持多种AI服务商和自定义数据架构。

## 功能特性

- **多AI服务商支持**：兼容OpenAI、DeepSeek、通义千问等OpenAI兼容API
- **自定义架构**：为不同数据类型自定义输入/输出列
- **批量处理**：可配置批次大小，高效处理大型数据集
- **智能缓存**：通过智能缓存避免重复API调用
- **网络搜索集成**：可选的MCP（模型上下文协议）集成，支持实时网络搜索
- **多种处理模式**：
  - 标准批处理模式：速度与准确性的平衡
  - 单次模式：适合小数据集的快速处理
  - 涡轮模式：适合大数据集的高速并发处理

## 安装说明

### 系统要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 必需的包

- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- openai >= 1.0.0

## 快速开始

### 1. 配置AI设置

创建或编辑 `src/agent/agent_config.json`：

```json
{
  "active_schema": "company_enrichment",
  "ai_settings": {
    "provider": "openai_compatible",
    "api_key": "your_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "temperature": 0.1,
    "max_tokens": 4000
  }
}
```

### 2. 运行应用程序

```bash
cd src/agent
python agent_main.py
```

### 3. 处理数据

1. 选择配置架构
2. 选择输入的Excel文件
3. 选择输出目录
4. 配置处理选项
5. 点击"开始处理"

## 配置架构

本工具支持多种数据架构，适用于不同场景：

### 内置架构

- **公司信息补全**：使用官方数据增强公司信息
- **产品信息**：补全产品详情和规格
- **人物信息**：添加传记和专业详情
- **餐厅信息**：补全餐厅数据，包括评论和评分
- **电影信息**：增强电影元数据，包括演员、评分和评论

### 自定义架构

通过定义以下内容创建自己的架构：
- 输入列（Excel中的必填字段）
- 输出列（AI生成的字段）
- 自定义提示词模板

## API服务商设置

### DeepSeek

1. 在 [DeepSeek平台](https://platform.deepseek.com) 注册
2. 生成API密钥
3. 配置：
   - Base URL: `https://api.deepseek.com`
   - Model: `deepseek-chat` 或 `deepseek-reasoner`

### 阿里云通义千问

1. 在 [阿里云DashScope](https://dashscope.aliyuncs.com) 注册
2. 获取API密钥
3. 配置：
   - Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
   - Model: `qwen-plus`、`qwen-turbo` 或 `qwen-max`

### OpenAI

1. 从 [OpenAI平台](https://platform.openai.com) 获取API密钥
2. 配置：
   - Base URL: `https://api.openai.com/v1`
   - Model: `gpt-4`、`gpt-3.5-turbo` 等

## 高级功能

### 批量处理

根据数据量调整批次大小：
- 小数据集（< 100行）：批次大小 5-10
- 中等数据集（100-1000行）：批次大小 10-20
- 大数据集（> 1000行）：批次大小 20-50

### MCP集成

启用MCP（模型上下文协议）进行实时网络搜索：
1. 在AI设置中设置 `enable_mcp: true`
2. 需要兼容的AI模型（DeepSeek-R1、Qwen等）
3. 提高当前信息的准确性

### 深度思考模式

适用于复杂查询（DeepSeek-V3/Reasoner模型）：
- 启用链式思考推理
- 提高准确性但使用更多token
- 推荐用于关键数据补全

## 构建可执行文件

创建独立的可执行文件：

```bash
pyinstaller build_agent.spec
```

可执行文件将在 `dist/` 目录中生成。

## 贡献指南

欢迎贡献！请：

1. Fork本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 提交Pull Request

### 代码风格

- 遵循PEP 8规范
- 为所有函数和类添加文档字符串
- 编写有意义的提交信息
- 为新功能添加测试

## 故障排除

### API连接问题

- 验证API密钥是否正确
- 检查网络连接
- 确保Base URL与服务商匹配
- 检查API配额/余额

### 处理错误

- 验证Excel文件格式
- 确保必需列存在
- 检查架构配置
- 检查AI模型设置

### 性能问题

- 减小批次大小
- 启用缓存
- 使用更快的AI模型
- 对于大数据集考虑使用涡轮模式

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- OpenAI提供的API标准
- DeepSeek提供的强大语言模型
- 阿里云提供的通义千问模型
- 所有贡献者和用户

## 支持

如有问题、疑问或建议：
- 在GitHub上提交issue
- 查看现有文档
- 查看测试示例

## 更新日志

### 版本 1.0
- 初始版本
- 多服务商AI支持
- 可自定义架构
- 批量处理
- MCP集成
- 多种处理模式

