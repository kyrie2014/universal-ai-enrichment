# 更新日志（Changelog）

本项目所有重要变更均记录于此文件。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，  
版本号管理遵循 [语义化版本规范（Semantic Versioning）](https://semver.org/spec/v2.0.0.html)。

## [未发布]

### 变更
- 移除了 UI 中的 emoji 表情符号，以提升国际兼容性  
- 改进了代码文档和注释  
- 重构代码库，使其符合开源项目最佳实践  

### 新增
- 完整的 `README.md`，包含安装与使用说明  
- `CONTRIBUTING.md` 贡献指南  
- `CODE_OF_CONDUCT.md` 社区行为准则  
- GitHub Actions 的 CI/CD 工作流  
- `CHANGELOG.md` 变更日志文件  

## [1.0.0] - 2025-01-XX

### 新增
- 初始版本发布  
- 支持多 AI 提供商（OpenAI、DeepSeek、Qwen）  
- 可自定义的数据 Schema 配置  
- 支持可配置批次大小的批量处理  
- 集成 MCP（Model Context Protocol，模型上下文协议）  
- 多种处理模式：
  - 标准批量模式（Standard Batch Mode）  
  - 一次性模式（One-Shot Mode）  
  - 涡轮模式（Turbo Mode）  
- 智能缓存系统  
- 基于 Tkinter 的图形用户界面（GUI）  
- Schema 编辑器，用于自定义配置  
- 支持 Excel 数据处理  
- “深度思考”模式，用于复杂查询  
- 网络搜索集成  

### 功能亮点
- 高效处理 100–1000 条记录  
- 实时进度追踪  
- 自动跳过已处理的行  
- 可配置的 AI 设置  
- 多种预设 AI 模型  
- 配置测试功能  
- 完善的错误处理机制  
- 日志记录系统  
