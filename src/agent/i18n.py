"""
国际化语言支持模块
Internationalization Language Support Module
"""

class LanguageManager:
    """语言管理器"""
    
    def __init__(self, language="zh_CN"):
        self.language = language
        self.translations = {
            "zh_CN": self._get_chinese_translations(),
            "en_US": self._get_english_translations()
        }
    
    def set_language(self, language):
        """设置语言"""
        if language in self.translations:
            self.language = language
            return True
        return False
    
    def get(self, key, default=""):
        """获取翻译文本"""
        return self.translations.get(self.language, {}).get(key, default)
    
    def _get_chinese_translations(self):
        """中文翻译"""
        return {
            # 窗口标题
            "app_title": "通用AI智能体工具 v1.0 - AI智能数据增强助手",
            "app_header": "🤖 通用AI智能体工具",
            "app_subtitle": "📊 自定义输入输出字段 | 📁 灵活Excel处理 | ⚡ AI赋能数据",
            
            # 配置方案
            "schema_section": " 📋  配置方案",
            "current_schema": "当前方案：",
            "edit_button": "✏️ 编辑",
            "new_button": "➕ 新建",
            "schema_name": "方案名称",
            "schema_description": "方案说明",
            "input_fields": "输入字段",
            "output_fields": "输出字段",
            "required": "必填",
            "optional": "选填",
            
            # 文件设置
            "file_section": " 📁  文件设置",
            "input_file": "输入文件：",
            "output_dir": "输出目录：",
            "browse_button": "📂 浏览",
            
            # 处理选项
            "options_section": " ⚙️  处理选项",
            "skip_existing": "跳过已处理行",
            "enable_batch": "启用批量处理模式",
            "batch_size": "批量大小：",
            "enable_mcp": "启用MCP增强（提升准确率）",
            "mcp_hint": "💡 MCP开启后可实时联网检索信息，提升结果准确性",
            
            # 进度显示
            "progress_section": " 📊  处理进度",
            
            # 操作按钮
            "start_button": " 🚀  开始处理",
            "ai_settings_button": " ⚙️  AI设置",
            "help_button": " 📖  使用指南",
            "language_button": " 🌐  Language",
            
            # 消息提示
            "warning": "警告",
            "error": "错误",
            "success": "成功",
            "info": "提示",
            "processing_warning": "正在处理中，请勿重复操作",
            "select_valid_input": "请选择有效的输入文件",
            "select_valid_output": "请选择有效的输出目录",
            "missing_columns": "输入文件缺少必须字段",
            "processing_complete": "处理成功！\n结果已保存至：",
            "processing_failed": "处理失败：",
            
            # AI设置对话框
            "ai_settings_title": "AI设置 - 增强版",
            "basic_config": "基础配置",
            "model_preset": "模型预设：",
            "api_key": "API密钥：",
            "api_url": "API地址：",
            "model_name": "模型名：",
            "enable_mcp_settings": "启用MCP增强（联网检索提升准确率）",
            "mcp_hint_settings": "💡 MCP让AI实时联网检索，准确率最高可达96%+",
            
            # 高级设置
            "advanced": "高级",
            "deep_thinking": " 🧠  深度思考模式（适用于DeepSeek V3）",
            "enable_deep_thinking": "启用深度思考模式（更高准确率，消耗更多tokens）",
            "deep_thinking_hint": "💡 深度思考适用于DeepSeek-Reasoner，显著提升准确率",
            
            # 查询模式
            "query_mode": "查询模式",
            "query_mode_title": " ⚡  查询模式选择（根据数据量选择）",
            "batch_mode": "📦 普通批量模式（推荐）",
            "batch_mode_desc": "📊 适合：100-1000条数据\n⏱️ 速度：中等（约3-5秒/条）\n💰 成本：中等（节省93%费用）\n✅ 准确率：高",
            "one_shot_mode": "⚡ 一镜直通模式（实验）",
            "one_shot_mode_desc": "📊 适合：<100条数据\n⏱️ 速度：极快（一次性全部处理）\n💰 成本：极低（仅1次API调用）\n✅ 准确率：高（AI全局把控）",
            "turbo_mode": "🚀 极速模式（大规模）",
            "turbo_mode_desc": "📊 适合：1000+数据\n⏱️ 速度：超快（5000条仅2分钟）\n💰 成本：较高（并发API调用）\n⚠️ 准确率：中等（需复核）",
            
            # 按钮
            "cancel_button": " ❌  取消",
            "test_button": " 🔍  测试配置",
            "save_button": " 💾  保存配置",
            "test_success": "✅ AI连接成功！\n\n模型: {}\n返回: {}",
            "test_failed": "❌ 连接失败：\n\n{}\n\n请检查：\n- API Key 是否正确\n- API地址是否正确\n- 网络正常",
            "config_saved": "AI配置保存成功！\n\n已更新：\n- 模型设置\n- 批量处理\n- 极速模式\n- MCP增强",
            
            # 使用指南
            "help_title": "使用指南",
            "help_content": """通用AI智能体系统 - 用户指南

1. 选择配置方案
   - 从下拉列表选择合适方案
   - 内置多种范例：企业信息、产品信息、人员信息等
   - 支持自定义方案

2. 准备Excel文件
   - 确保Excel包含方案要求的输入字段
   - 如"企业增强"需有"公司"字段

3. 选择文件及输出目录
   - 点击"浏览"选择输入Excel文件
   - 选择输出目录保存结果

4. 设置处理选项
   - 跳过已处理行：避免重复处理
   - 启用批量模式：多条记录同时询问，效率提升

5. 配置AI
   - 点击"AI设置"填写API密钥
   - 支持OpenAI、DeepSeek等兼容接口

6. 开始处理
   - 点击"开始处理"
   - 等待进度完成
   - 结果将保存在指定目录

提示：
- 新用户建议先用小文件测试
- 批量模式大幅加速并节约成本
- 实时查看进度日志
""",
            
            # 日志消息
            "reading_file": "正在读取输入文件...",
            "rows_read": "读取数据行数：{}",
            "batch_mode_enabled": "使用批量处理模式，批量大小：{}",
            "single_mode_enabled": "使用单条记录处理模式",
            "saving_result": "正在保存结果到：{}",
            "complete": "处理完成！",
            "skip_processed": "跳过第{}行（已处理）",
            "processing_row": "正在处理第{}/{}行: {}",
            "processing_batch": "正在处理批次{}：第{} - {}行",
            "need_process": "需处理{}条数据",
            "mcp_enabled": "MCP功能已开启",
            "mcp_disabled": "MCP功能已关闭",
            "mcp_help_text": "MCP将帮助AI联网并提升结果准确性",
            "mcp_offline_text": "MCP已关闭，仅使用AI模型内知识",
        }
    
    def _get_english_translations(self):
        """英文翻译"""
        return {
            # Window titles
            "app_title": "Universal AI Agent Tool v1.0 - AI Data Enrichment Assistant",
            "app_header": "🤖 Universal AI Agent Tool",
            "app_subtitle": "📊 Customizable Fields | 📁 Flexible Excel Processing | ⚡ AI-Powered Data",
            
            # Schema section
            "schema_section": " 📋  Configuration Schema",
            "current_schema": "Current Schema:",
            "edit_button": "✏️ Edit",
            "new_button": "➕ New",
            "schema_name": "Schema Name",
            "schema_description": "Description",
            "input_fields": "Input Fields",
            "output_fields": "Output Fields",
            "required": "Required",
            "optional": "Optional",
            
            # File settings
            "file_section": " 📁  File Settings",
            "input_file": "Input File:",
            "output_dir": "Output Directory:",
            "browse_button": "📂 Browse",
            
            # Processing options
            "options_section": " ⚙️  Processing Options",
            "skip_existing": "Skip Processed Rows",
            "enable_batch": "Enable Batch Processing Mode",
            "batch_size": "Batch Size:",
            "enable_mcp": "Enable MCP Enhancement (Improve Accuracy)",
            "mcp_hint": "💡 MCP enables real-time web search to improve result accuracy",
            
            # Progress section
            "progress_section": " 📊  Processing Progress",
            
            # Action buttons
            "start_button": " 🚀  Start Processing",
            "ai_settings_button": " ⚙️  AI Settings",
            "help_button": " 📖  User Guide",
            "language_button": " 🌐  语言",
            
            # Message prompts
            "warning": "Warning",
            "error": "Error",
            "success": "Success",
            "info": "Info",
            "processing_warning": "Processing in progress, please wait",
            "select_valid_input": "Please select a valid input file",
            "select_valid_output": "Please select a valid output directory",
            "missing_columns": "Input file missing required columns",
            "processing_complete": "Processing completed!\nResults saved to:",
            "processing_failed": "Processing failed:",
            
            # AI Settings dialog
            "ai_settings_title": "AI Settings - Advanced",
            "basic_config": "Basic Configuration",
            "model_preset": "Model Preset:",
            "api_key": "API Key:",
            "api_url": "API URL:",
            "model_name": "Model Name:",
            "enable_mcp_settings": "Enable MCP Enhancement (Web Search)",
            "mcp_hint_settings": "💡 MCP enables real-time web search, accuracy up to 96%+",
            
            # Advanced settings
            "advanced": "Advanced",
            "deep_thinking": " 🧠  Deep Thinking Mode (For DeepSeek V3)",
            "enable_deep_thinking": "Enable Deep Thinking Mode (Higher accuracy, more tokens)",
            "deep_thinking_hint": "💡 Deep Thinking works best with DeepSeek-Reasoner for improved accuracy",
            
            # Query mode
            "query_mode": "Query Mode",
            "query_mode_title": " ⚡  Query Mode Selection (Based on Data Volume)",
            "batch_mode": "📦 Standard Batch Mode (Recommended)",
            "batch_mode_desc": "📊 Best for: 100-1000 records\n⏱️ Speed: Medium (~3-5 sec/record)\n💰 Cost: Medium (Save 93% cost)\n✅ Accuracy: High",
            "one_shot_mode": "⚡ One-Shot Mode (Experimental)",
            "one_shot_mode_desc": "📊 Best for: <100 records\n⏱️ Speed: Very fast (Process all at once)\n💰 Cost: Very low (Only 1 API call)\n✅ Accuracy: High (AI global control)",
            "turbo_mode": "🚀 Turbo Mode (Large Scale)",
            "turbo_mode_desc": "📊 Best for: 1000+ records\n⏱️ Speed: Super fast (5000 in 2 mins)\n💰 Cost: Higher (Concurrent API calls)\n⚠️ Accuracy: Medium (Needs review)",
            
            # Buttons
            "cancel_button": " ❌  Cancel",
            "test_button": " 🔍  Test Config",
            "save_button": " 💾  Save Config",
            "test_success": "✅ AI Connection Successful!\n\nModel: {}\nResponse: {}",
            "test_failed": "❌ Connection Failed:\n\n{}\n\nPlease check:\n- API Key is correct\n- API URL is correct\n- Network connection",
            "config_saved": "AI Configuration Saved!\n\nUpdated:\n- Model Settings\n- Batch Processing\n- Turbo Mode\n- MCP Enhancement",
            
            # User guide
            "help_title": "User Guide",
            "help_content": """Universal AI Agent System - User Guide

1. Select Configuration Schema
   - Choose appropriate schema from dropdown
   - Built-in examples: Company info, Product info, Person info, etc.
   - Support custom schemas

2. Prepare Excel File
   - Ensure Excel contains required input fields
   - E.g., "Company Enrichment" requires "Company" field

3. Select Files and Output Directory
   - Click "Browse" to select input Excel file
   - Choose output directory for results

4. Configure Processing Options
   - Skip processed rows: Avoid duplicate processing
   - Enable batch mode: Process multiple records simultaneously for efficiency

5. Configure AI
   - Click "AI Settings" to enter API key
   - Support OpenAI, DeepSeek and compatible APIs

6. Start Processing
   - Click "Start Processing"
   - Wait for progress to complete
   - Results will be saved in specified directory

Tips:
- New users should test with small files first
- Batch mode significantly speeds up and reduces costs
- Monitor progress in real-time logs
""",
            
            # Log messages
            "reading_file": "Reading input file...",
            "rows_read": "Rows read: {}",
            "batch_mode_enabled": "Using batch processing mode, batch size: {}",
            "single_mode_enabled": "Using single record processing mode",
            "saving_result": "Saving results to: {}",
            "complete": "Processing complete!",
            "skip_processed": "Skip row {} (already processed)",
            "processing_row": "Processing row {}/{}: {}",
            "processing_batch": "Processing batch {}: rows {} - {}",
            "need_process": "Need to process {} records",
            "mcp_enabled": "MCP function enabled",
            "mcp_disabled": "MCP function disabled",
            "mcp_help_text": "MCP will help AI search the web and improve accuracy",
            "mcp_offline_text": "MCP disabled, using AI model knowledge only",
        }


# 全局语言管理器实例
_language_manager = None

def get_language_manager(language="zh_CN"):
    """获取语言管理器实例"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager(language)
    return _language_manager

def set_language(language):
    """设置全局语言"""
    manager = get_language_manager()
    return manager.set_language(language)

def t(key, default=""):
    """翻译快捷函数"""
    manager = get_language_manager()
    return manager.get(key, default)

