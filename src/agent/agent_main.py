"""
通用AI智能体系统 - 支持自定义输入/输出字段的Excel数据处理工具
支持多种场景：企业信息、产品信息、人员信息等
Universal AI Agent System - Excel Data Processing Tool with Customizable Input/Output Fields
Supports multiple scenarios: Company info, Product info, Person info, etc.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import pandas as pd
import os
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import List, Dict, Any, Optional
import re

# 导入国际化支持
try:
    from i18n import get_language_manager, t
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def t(key, default=""):
        return default or key

# 导入AI客户端
try:
    from openai_compatible_client import OpenAICompatibleClient
    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False
    OpenAICompatibleClient = None

# 导入MCP客户端
try:
    from mcp_client import create_mcp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    create_mcp_client = None


class AgentConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """载入配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[错误] 载入配置失败: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            print(f"[信息] 写入配置文件: {self.config_file}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"[信息] 配置文件保存成功")
            return True
        except Exception as e:
            print(f"[错误] 配置文件保存失败: {e}")
            return False
    
    def get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "active_schema": "company_enrichment",
            "schemas": {},
            "ai_settings": {
                "provider": "openai_compatible",
                "api_key": "",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "temperature": 0.1,
                "max_tokens": 4000
            }
        }
    
    def get_active_schema(self) -> dict:
        """获取当前激活方案"""
        schema_name = self.config.get("active_schema", "company_enrichment")
        return self.config.get("schemas", {}).get(schema_name, {})
    
    def set_active_schema(self, schema_name: str):
        """设置激活方案"""
        if schema_name in self.config.get("schemas", {}):
            self.config["active_schema"] = schema_name
            self.save_config()
            return True
        return False
    
    def list_schemas(self) -> List[str]:
        """列出所有方案"""
        return list(self.config.get("schemas", {}).keys())
    
    def add_schema(self, name: str, schema: dict):
        """新增方案"""
        if "schemas" not in self.config:
            self.config["schemas"] = {}
        self.config["schemas"][name] = schema
        self.save_config()
    
    def delete_schema(self, name: str):
        """删除方案"""
        if name in self.config.get("schemas", {}):
            del self.config["schemas"][name]
            self.save_config()
            return True
        return False


class UniversalAIAgent:
    """通用AI智能体 - 支持自定义输入输出字段"""
    
    def __init__(self, config_manager: AgentConfigManager):
        self.config_manager = config_manager
        self.ai_client = None
        self.mcp_client = None
        self.init_ai_client()
        self.init_mcp_client()
    
    def init_ai_client(self):
        """初始化AI客户端"""
        ai_settings = self.config_manager.config.get("ai_settings", {})
        
        if not AI_CLIENT_AVAILABLE:
            print("[错误] 未找到AI客户端模块")
            return False
        
        try:
            self.ai_client = OpenAICompatibleClient(
                api_key=ai_settings.get("api_key", ""),
                base_url=ai_settings.get("base_url", "https://api.deepseek.com"),
                model=ai_settings.get("model", "deepseek-chat"),
                enable_deep_thinking=ai_settings.get("enable_deep_thinking", False),
                enable_web_search=ai_settings.get("enable_web_search", True)
            )
            print("[信息] AI客户端初始化成功")
            return True
        except Exception as e:
            print(f"[错误] AI客户端初始化失败: {e}")
            return False
    
    def init_mcp_client(self):
        """初始化MCP客户端"""
        if not MCP_AVAILABLE:
            print("[警告] 未找到MCP模块，MCP功能不可用")
            return False
        
        try:
            ai_settings = self.config_manager.config.get("ai_settings", {})
            self.mcp_client = create_mcp_client(ai_settings)
            
            if self.mcp_client and self.mcp_client.is_enabled():
                print("[信息] MCP客户端初始化成功")
                return True
            else:
                print("[警告] MCP功能未启用")
                return False
        except Exception as e:
            print(f"[错误] MCP客户端初始化失败: {e}")
            return False
    
    def generate_prompt(self, input_data: dict, is_batch: bool = False) -> str:
        """生成AI提示词"""
        schema = self.config_manager.get_active_schema()
        
        # 输出字段描述
        output_fields_desc = []
        for col in schema.get("output_columns", []):
            output_fields_desc.append(
                f"- {col['name']} ({col['type']}): {col['description']}"
            )
        output_fields_description = "\n".join(output_fields_desc)
        
        if is_batch:
            template = schema.get("batch_prompt_template", "")
            # 批量处理
            batch_data_str = json.dumps(input_data, ensure_ascii=False, indent=2)
            
            # 根据不同数据类型生成列表格式
            companies_list_str = ""
            if isinstance(input_data, list) and len(input_data) > 0:
                if "公司" in input_data[0] or "company" in str(input_data[0]).lower():
                    # 编号列表
                    companies_list_str = "\n".join([f"{i+1}. {item.get('公司', item.get('company', ''))}" for i, item in enumerate(input_data)])
                elif "产品名称" in input_data[0] or "product" in str(input_data[0]).lower():
                    companies_list_str = batch_data_str
                elif "姓名" in input_data[0] or "name" in str(input_data[0]).lower():
                    companies_list_str = batch_data_str
                else:
                    companies_list_str = batch_data_str
            else:
                companies_list_str = batch_data_str
            
            try:
                return template.format(
                    batch_data=batch_data_str,
                    companies_list=companies_list_str,
                    output_fields_description=output_fields_description
                )
            except KeyError as e:
                # 模板缺少占位符，回退为简单格式
                return f"请处理以下数据：\n{batch_data_str}\n\n输出字段:\n{output_fields_description}"
        else:
            template = schema.get("prompt_template", "")
            # 单条记录处理
            input_str = "\n".join([f"{k}: {v}" for k, v in input_data.items()])
            return template.format(
                input_data=input_str,
                output_fields_description=output_fields_description,
                **input_data  # 支持字段直接引用
            )
    
    def query_single(self, input_data: dict, context: str = "") -> dict:
        """单条记录查询"""
        if not self.ai_client:
            return {"error": "AI客户端未初始化"}
        
        try:
            prompt = self.generate_prompt(input_data, is_batch=False)
            
            if context:
                prompt = f"📝 上下文信息\n{context}\n\n{prompt}"
            
            # 使用MCP增强提示词
            if self.mcp_client and self.mcp_client.is_enabled():
                prompt = self.mcp_client.enhance_prompt(prompt, input_data)
            
            # 调用AI客户端（chat方法，人工解析）
            result_dict = self.ai_client.chat(prompt, stream=False, parse_response=False)
            
            # chat方法返回已解析字典，直接用
            if result_dict and isinstance(result_dict, dict):
                response = result_dict.get("content", "") or str(result_dict)
            else:
                response = str(result_dict) if result_dict else ""
            
            # 解析JSON响应
            result = self.parse_json_response(response)
            return result
            
        except Exception as e:
            print(f"[错误] 查询失败: {e}")
            return {"error": str(e)}
    
    def query_batch(self, input_data_list: List[dict], context: str = "", batch_size: int = 15) -> List[dict]:
        """批量查询"""
        if not self.ai_client:
            return [{"error": "AI客户端未初始化"}] * len(input_data_list)
        
        results = []
        
        for i in range(0, len(input_data_list), batch_size):
            batch = input_data_list[i:i+batch_size]
            
            try:
                prompt = self.generate_prompt(batch, is_batch=True)
                
                if context:
                    prompt = f"📝 上下文信息\n{context}\n\n{prompt}"
                
                # 调用AI客户端（chat方法，人工解析）
                result_dict = self.ai_client.chat(prompt, stream=False, parse_response=False)
                
                # chat返回字符串或字典
                if isinstance(result_dict, str):
                    response = result_dict
                elif result_dict and isinstance(result_dict, dict):
                    response = result_dict.get("content", "") or json.dumps(result_dict, ensure_ascii=False)
                else:
                    response = str(result_dict) if result_dict else ""
                
                # 解析JSON数组
                batch_results = self.parse_json_array_response(response)
                
                # 确保批量结果数量正确
                if len(batch_results) != len(batch):
                    print(f"[警告] 批量结果数量不符: 期望{len(batch)}, 实际{len(batch_results)}")
                    if len(batch_results) < len(batch):
                        batch_results.extend([{"error": "无返回结果"}] * (len(batch) - len(batch_results)))
                    else:
                        batch_results = batch_results[:len(batch)]
                
                results.extend(batch_results)
                
            except Exception as e:
                print(f"[错误] 批量查询失败: {e}")
                results.extend([{"error": str(e)}] * len(batch))
        
        return results
    
    def parse_json_response(self, response: str) -> dict:
        """解析JSON响应"""
        try:
            return json.loads(response)
        except:
            # 提取JSON片段
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 从markdown块中提取
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if code_block_match:
                try:
                    return json.loads(code_block_match.group(1))
                except:
                    pass
            
            return {"error": "无法解析AI返回内容", "raw_response": response}
    
    def parse_json_array_response(self, response: str) -> List[dict]:
        """解析JSON数组响应"""
        try:
            result = json.loads(response)
            if isinstance(result, list):
                return result
            else:
                return [result]
        except Exception as e:
            # 尝试提取JSON数组
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except Exception as e2:
                    pass
            
            # 尝试从markdown块提取
            code_block_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
            if code_block_match:
                try:
                    result = json.loads(code_block_match.group(1))
                    return result
                except Exception as e3:
                    pass
            
            return [{"error": "无法解析AI返回内容", "raw_response": response}]


class AgentApp:
    """通用AI智能体应用界面"""
    
    def __init__(self, root):
        self.root = root
        
        # 初始化语言管理器
        if I18N_AVAILABLE:
            self.lang_manager = get_language_manager("zh_CN")
            self.current_language = "zh_CN"
        else:
            self.lang_manager = None
            self.current_language = "zh_CN"
        
        self.root.title(t("app_title", "通用AI智能体工具 v1.0 - AI智能数据增强助手"))
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小为屏幕的70%，最大不超过1200x900
        window_width = min(int(screen_width * 0.7), 1200)
        window_height = min(int(screen_height * 0.8), 900)
        
        # 居中显示
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 700)  # 最小窗口尺寸
        self.root.resizable(True, True)
        self.root.configure(bg="#F5F5F5")
        
        # 配置管理器
        self.config_manager = AgentConfigManager()
        
        # AI智能体
        self.agent = UniversalAIAgent(self.config_manager)
        
        # 变量
        self.input_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.schema_var = tk.StringVar()
        self.processing = False
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置方案列表
        self.load_schema_list()
    
    def create_widgets(self):
        """创建界面控件""" 
        # 标题区域
        title_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            title_frame,
            text=t("app_header", "🤖 通用AI智能体工具"),
            font=("Microsoft YaHei UI", 22, "bold"),
            bg="#4A90E2",
            fg="white"
        )
        self.title_label.pack(pady=20)
        
        self.subtitle_label = tk.Label(
            title_frame,
            text=t("app_subtitle", "📊 自定义输入输出字段 | 📁 灵活Excel处理 | ⚡ AI赋能数据"),
            font=("Microsoft YaHei UI", 10),
            bg="#4A90E2",
            fg="white"
        )
        self.subtitle_label.pack()
        
        # 主内容区（可滚动）
        container = tk.Frame(self.root, bg="#F5F5F5")
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, bg="#F5F5F5", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = tk.Frame(canvas, bg="#F5F5F5", padx=20, pady=20)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind("<Configure>", on_frame_configure)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 配置方案选择
        self.schema_frame = tk.LabelFrame(
            main_frame,
            text=t("schema_section", " 📋  配置方案"),
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            padx=15,
            pady=10
        )
        self.schema_frame.pack(fill=tk.X, pady=(0, 10))
        
        schema_select_frame = tk.Frame(self.schema_frame, bg="white")
        schema_select_frame.pack(fill=tk.X)
        
        self.schema_label = tk.Label(
            schema_select_frame,
            text=t("current_schema", "当前方案："),
            font=("Microsoft YaHei UI", 10),
            bg="white"
        )
        self.schema_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.schema_combo = ttk.Combobox(
            schema_select_frame,
            textvariable=self.schema_var,
            font=("Microsoft YaHei UI", 10),
            state="readonly",
            width=30
        )
        self.schema_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.schema_combo.bind("<<ComboboxSelected>>", self.on_schema_changed)
        
        self.edit_schema_btn = tk.Button(
            schema_select_frame,
            text=t("edit_button", "✏️ 编辑"),
            font=("Microsoft YaHei UI", 9),
            bg="#4A90E2",
            fg="white",
            command=self.edit_schema,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.edit_schema_btn.pack(side=tk.LEFT, padx=5)
        
        self.new_schema_btn = tk.Button(
            schema_select_frame,
            text=t("new_button", "➕ 新建"),
            font=("Microsoft YaHei UI", 9),
            bg="#5CB85C",
            fg="white",
            command=self.create_new_schema,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.new_schema_btn.pack(side=tk.LEFT, padx=5)
        
        # 方案信息显示（只读）
        self.schema_info_text = scrolledtext.ScrolledText(
            self.schema_frame,
            height=6,
            font=("Microsoft YaHei UI", 9),
            bg="#F8F9FA",
            wrap=tk.WORD,
            state=tk.DISABLED  # 设置为只读
        )
        self.schema_info_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 文件选择区域
        self.file_frame = tk.LabelFrame(
            main_frame,
            text=t("file_section", " 📁  文件设置"),
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            padx=15,
            pady=10
        )
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = tk.Frame(self.file_frame, bg="white")
        input_frame.pack(fill=tk.X, pady=5)
        
        self.input_file_label = tk.Label(
            input_frame,
            text=t("input_file", "输入文件："),
            font=("Microsoft YaHei UI", 10),
            bg="white",
            width=12,
            anchor="w"
        )
        self.input_file_label.pack(side=tk.LEFT)
        
        tk.Entry(
            input_frame,
            textvariable=self.input_file_var,
            font=("Microsoft YaHei UI", 9),
            width=50
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_input_btn = tk.Button(
            input_frame,
            text=t("browse_button", "📂 浏览"),
            font=("Microsoft YaHei UI", 9),
            bg="#4A90E2",
            fg="white",
            command=self.browse_input_file,
            relief=tk.FLAT,
            padx=15,
            pady=3,
            cursor="hand2"
        )
        self.browse_input_btn.pack(side=tk.LEFT)
        
        output_frame = tk.Frame(self.file_frame, bg="white")
        output_frame.pack(fill=tk.X, pady=5)
        
        self.output_dir_label = tk.Label(
            output_frame,
            text=t("output_dir", "输出目录："),
            font=("Microsoft YaHei UI", 10),
            bg="white",
            width=12,
            anchor="w"
        )
        self.output_dir_label.pack(side=tk.LEFT)
        
        tk.Entry(
            output_frame,
            textvariable=self.output_dir_var,
            font=("Microsoft YaHei UI", 9),
            width=50
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_output_btn = tk.Button(
            output_frame,
            text=t("browse_button", "📂 浏览"),
            font=("Microsoft YaHei UI", 9),
            bg="#4A90E2",
            fg="white",
            command=self.browse_output_dir,
            relief=tk.FLAT,
            padx=15,
            pady=3,
            cursor="hand2"
        )
        self.browse_output_btn.pack(side=tk.LEFT)
        
        # 处理选项
        self.options_frame = tk.LabelFrame(
            main_frame,
            text=t("options_section", " ⚙️  处理选项"),
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            padx=15,
            pady=10
        )
        self.options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.skip_existing_var = tk.BooleanVar(value=True)
        self.batch_mode_var = tk.BooleanVar(value=True)
        self.batch_size_var = tk.IntVar(value=15)
        self.enable_mcp_var = tk.BooleanVar(
            value=self.config_manager.config.get("ai_settings", {}).get("enable_mcp", False)
        )
        
        self.skip_existing_cb = tk.Checkbutton(
            self.options_frame,
            text=t("skip_existing", "跳过已处理行"),
            variable=self.skip_existing_var,
            font=("Microsoft YaHei UI", 10),
            bg="white"
        )
        self.skip_existing_cb.pack(anchor="w", pady=2)
        
        batch_frame = tk.Frame(self.options_frame, bg="white")
        batch_frame.pack(anchor="w", pady=2)
        
        self.batch_mode_cb = tk.Checkbutton(
            batch_frame,
            text=t("enable_batch", "启用批量处理模式"),
            variable=self.batch_mode_var,
            font=("Microsoft YaHei UI", 10),
            bg="white"
        )
        self.batch_mode_cb.pack(side=tk.LEFT)
        
        self.batch_size_label = tk.Label(
            batch_frame,
            text=t("batch_size", "批量大小："),
            font=("Microsoft YaHei UI", 10),
            bg="white"
        )
        self.batch_size_label.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Spinbox(
            batch_frame,
            from_=5,
            to=100,
            textvariable=self.batch_size_var,
            font=("Microsoft YaHei UI", 9),
            width=10
        ).pack(side=tk.LEFT)
        
        mcp_frame = tk.Frame(self.options_frame, bg="white")
        mcp_frame.pack(anchor="w", pady=2)
        
        self.mcp_checkbox = tk.Checkbutton(
            mcp_frame,
            text=t("enable_mcp", "启用MCP增强（提升准确率）"),
            variable=self.enable_mcp_var,
            font=("Microsoft YaHei UI", 10),
            bg="white",
            command=self.toggle_mcp
        )
        self.mcp_checkbox.pack(side=tk.LEFT)
        
        self.mcp_hint_label = tk.Label(
            mcp_frame,
            text=t("mcp_hint", "💡 MCP开启后可实时联网检索信息，提升结果准确性"),
            font=("Microsoft YaHei UI", 9),
            bg="white",
            fg="#7F8C8D"
        )
        self.mcp_hint_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 进度显示
        self.progress_frame = tk.LabelFrame(
            main_frame,
            text=t("progress_section", " 📊  处理进度"),
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            padx=15,
            pady=10
        )
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = scrolledtext.ScrolledText(
            self.progress_frame,
            height=10,
            font=("Consolas", 9),
            bg="#F8F9FA",
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 操作按钮
        button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = tk.Button(
            button_frame,
            text=t("start_button", " 🚀  开始处理"),
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#5CB85C",
            fg="white",
            command=self.start_processing,
            relief=tk.FLAT,
            padx=16,
            pady=4,
            width=16
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.ai_config_btn = tk.Button(
            button_frame,
            text=t("ai_settings_button", " ⚙️  AI设置"),
            font=("Microsoft YaHei UI", 12),
            bg="#4A90E2",
            fg="white",
            command=self.open_ai_settings,
            relief=tk.FLAT,
            padx=16,
            pady=4,
            width=16
        )
        self.ai_config_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = tk.Button(
            button_frame,
            text=t("help_button", " 📖  使用指南"),
            font=("Microsoft YaHei UI", 12),
            bg="#F0AD4E",
            fg="white",
            command=self.show_help,
            relief=tk.FLAT,
            padx=16,
            pady=4,
            width=16
        )
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # 语言切换按钮
        self.lang_btn = tk.Button(
            button_frame,
            text=t("language_button", " 🌐  Language"),
            font=("Microsoft YaHei UI", 12),
            bg="#9B59B6",
            fg="white",
            command=self.toggle_language,
            relief=tk.FLAT,
            padx=16,
            pady=4,
            width=16
        )
        self.lang_btn.pack(side=tk.LEFT, padx=5)
    
    def toggle_language(self):
        """切换语言"""
        if not I18N_AVAILABLE or not self.lang_manager:
            messagebox.showinfo("Info", "Internationalization module not available")
            return
        
        # 切换语言
        if self.current_language == "zh_CN":
            self.current_language = "en_US"
        else:
            self.current_language = "zh_CN"
        
        self.lang_manager.set_language(self.current_language)
        
        # 更新所有界面文本
        self.update_ui_texts()
        
        messagebox.showinfo(
            t("info", "提示"),
            "Language switched successfully!" if self.current_language == "en_US" else "语言切换成功！"
        )
    
    def update_ui_texts(self):
        """更新界面文本"""
        # 更新窗口标题
        self.root.title(t("app_title", "通用AI智能体工具 v1.0"))
        
        # 更新标题
        self.title_label.config(text=t("app_header", "🤖 通用AI智能体工具"))
        self.subtitle_label.config(text=t("app_subtitle", "📊 自定义输入输出字段 | 📁 灵活Excel处理 | ⚡ AI赋能数据"))
        
        # 更新各个区域标题
        self.schema_frame.config(text=t("schema_section", " 📋  配置方案"))
        self.schema_label.config(text=t("current_schema", "当前方案："))
        self.edit_schema_btn.config(text=t("edit_button", "✏️ 编辑"))
        self.new_schema_btn.config(text=t("new_button", "➕ 新建"))
        
        self.file_frame.config(text=t("file_section", " 📁  文件设置"))
        self.input_file_label.config(text=t("input_file", "输入文件："))
        self.output_dir_label.config(text=t("output_dir", "输出目录："))
        self.browse_input_btn.config(text=t("browse_button", "📂 浏览"))
        self.browse_output_btn.config(text=t("browse_button", "📂 浏览"))
        
        self.options_frame.config(text=t("options_section", " ⚙️  处理选项"))
        self.skip_existing_cb.config(text=t("skip_existing", "跳过已处理行"))
        self.batch_mode_cb.config(text=t("enable_batch", "启用批量处理模式"))
        self.batch_size_label.config(text=t("batch_size", "批量大小："))
        self.mcp_checkbox.config(text=t("enable_mcp", "启用MCP增强（提升准确率）"))
        self.mcp_hint_label.config(text=t("mcp_hint", "💡 MCP开启后可实时联网检索信息"))
        
        self.progress_frame.config(text=t("progress_section", " 📊  处理进度"))
        
        # 更新按钮
        self.start_btn.config(text=t("start_button", " 🚀  开始处理"))
        self.ai_config_btn.config(text=t("ai_settings_button", " ⚙️  AI设置"))
        self.help_btn.config(text=t("help_button", " 📖  使用指南"))
        self.lang_btn.config(text=t("language_button", " 🌐  Language"))
        
        # 更新方案信息
        self.update_schema_info()
    
    def load_schema_list(self):
        """加载配置方案列表"""
        schemas = self.config_manager.list_schemas()
        self.schema_combo['values'] = schemas
        
        if schemas:
            active_schema = self.config_manager.config.get("active_schema", schemas[0])
            self.schema_var.set(active_schema)
            self.update_schema_info()
    
    def on_schema_changed(self, event=None):
        """方案变更"""
        schema_name = self.schema_var.get()
        self.config_manager.set_active_schema(schema_name)
        self.update_schema_info()
    
    def update_schema_info(self):
        """更新方案信息展示"""
        schema = self.config_manager.get_active_schema()
        
        schema_name_label = t("schema_name", "方案名称")
        schema_desc_label = t("schema_description", "方案说明")
        input_fields_label = t("input_fields", "输入字段")
        output_fields_label = t("output_fields", "输出字段")
        required_label = t("required", "必填")
        optional_label = t("optional", "选填")
        
        info_text = f"{schema_name_label}：{schema.get('name', 'N/A')}\n"
        info_text += f"{schema_desc_label}：{schema.get('description', 'N/A')}\n\n"
        
        info_text += f"{input_fields_label}：\n"
        for col in schema.get('input_columns', []):
            required = required_label if col.get('required', False) else optional_label
            info_text += f"  - {col['name']}（{required}）：{col.get('description', '')}\n"
        
        info_text += f"\n{output_fields_label}：\n"
        for col in schema.get('output_columns', []):
            info_text += f"  - {col['name']}（{col['type']}）：{col.get('description', '')}\n"
        
        self.schema_info_text.config(state=tk.NORMAL)
        self.schema_info_text.delete('1.0', tk.END)
        self.schema_info_text.insert('1.0', info_text)
        self.schema_info_text.config(state=tk.DISABLED)
    
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="请选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="请选择输出目录")
        if dirname:
            self.output_dir_var.set(dirname)
    
    def log(self, message: str):
        """日志信息打印"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        self.root.update()
    
    def start_processing(self):
        """开始处理"""
        if self.processing:
            messagebox.showwarning(
                t("warning", "警告"), 
                t("processing_warning", "正在处理中，请勿重复操作")
            )
            return
        
        # 参数校验
        input_file = self.input_file_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror(
                t("error", "错误"), 
                t("select_valid_input", "请选择有效的输入文件")
            )
            return
        
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror(
                t("error", "错误"), 
                t("select_valid_output", "请选择有效的输出目录")
            )
            return
        
        # 新线程处理
        self.processing = True
        thread = threading.Thread(target=self.process_file, daemon=True)
        thread.start()
    
    def process_file(self):
        """处理文件"""
        try:
            input_file = self.input_file_var.get()
            output_dir = self.output_dir_var.get()
            
            self.log(t("reading_file", "正在读取输入文件..."))
            
            df = pd.read_excel(input_file)
            total_rows = len(df)
            
            self.log(t("rows_read", "读取数据行数：{}").format(total_rows))
            
            schema = self.config_manager.get_active_schema()
            
            # 检查输入字段
            input_columns = [col['name'] for col in schema.get('input_columns', [])]
            missing_columns = [col for col in input_columns if col not in df.columns]
            
            if missing_columns:
                error_msg = f"{t('missing_columns', '输入文件缺少必须字段')}：{', '.join(missing_columns)}"
                self.log(f"{t('error', '错误')}：{error_msg}")
                messagebox.showerror(t("error", "错误"), error_msg)
                self.processing = False
                return
            
            # 初始化输出字段
            output_columns = [col['name'] for col in schema.get('output_columns', [])]
            for col in output_columns:
                if col not in df.columns:
                    df[col] = "N/A"
            
            batch_mode = self.batch_mode_var.get()
            batch_size = self.batch_size_var.get()
            skip_existing = self.skip_existing_var.get()
            
            if batch_mode:
                self.log(t("batch_mode_enabled", "使用批量处理模式，批量大小：{}").format(batch_size))
                self.process_batch_mode(df, input_columns, output_columns, batch_size, skip_existing)
            else:
                self.log(t("single_mode_enabled", "使用单条记录处理模式"))
                self.process_single_mode(df, input_columns, output_columns, skip_existing)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            extension = os.path.splitext(os.path.basename(input_file))[1]
            output_filename = f"{base_name}_{timestamp}{extension}"
            output_path = os.path.join(output_dir, output_filename)
            
            self.log(t("saving_result", "正在保存结果到：{}").format(output_path))
            df.to_excel(output_path, index=False)
            
            self.log(t("complete", "处理完成！"))
            success_msg = t('processing_complete', '处理成功！\n结果已保存至：')
            messagebox.showinfo(
                t("success", "完成"), 
                f"{success_msg}{output_path}"
            )
            
        except Exception as e:
            error_msg = f"{t('processing_failed', '处理失败：')}{str(e)}"
            self.log(error_msg)
            messagebox.showerror(t("error", "错误"), error_msg)
        finally:
            self.processing = False
            self.progress_var.set(0)
    
    def process_single_mode(self, df: pd.DataFrame, input_columns: List[str], 
                           output_columns: List[str], skip_existing: bool):
        """单条处理模式"""
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            if skip_existing and not pd.isna(row.get(output_columns[0])) and row.get(output_columns[0]) != "N/A":
                self.log(t("skip_processed", "跳过第{}行（已处理）").format(idx+1))
                continue
            
            input_data = {col: str(row[col]) if not pd.isna(row[col]) else "" for col in input_columns}
            
            self.log(t("processing_row", "正在处理第{}/{}行: {}").format(idx+1, total_rows, input_data))
            
            result = self.agent.query_single(input_data)
            
            for col in output_columns:
                if col in result:
                    df.at[idx, col] = result[col]
            
            progress = (idx + 1) / total_rows * 100
            self.progress_var.set(progress)
            self.root.update()
    
    def process_batch_mode(self, df: pd.DataFrame, input_columns: List[str], 
                          output_columns: List[str], batch_size: int, skip_existing: bool):
        """批量处理模式"""
        total_rows = len(df)
        
        rows_to_process = []
        for idx, row in df.iterrows():
            if skip_existing and not pd.isna(row.get(output_columns[0])) and row.get(output_columns[0]) != "N/A":
                continue
            rows_to_process.append(idx)
        
        self.log(t("need_process", "需处理{}条数据").format(len(rows_to_process)))
        
        for i in range(0, len(rows_to_process), batch_size):
            batch_indices = rows_to_process[i:i+batch_size]
            
            self.log(t("processing_batch", "正在处理批次{}：第{} - {}行").format(
                (i//batch_size)+1, batch_indices[0]+1, batch_indices[-1]+1
            ))
            
            batch_input = []
            for idx in batch_indices:
                row = df.iloc[idx]
                input_data = {col: str(row[col]) if not pd.isna(row[col]) else "" for col in input_columns}
                batch_input.append(input_data)
            
            results = self.agent.query_batch(batch_input)
            written_count = 0
            for idx, result in zip(batch_indices, results):
                for col in output_columns:
                    if col in result:
                        df.at[idx, col] = result[col]
                        written_count += 1
            progress = (i + len(batch_indices)) / len(rows_to_process) * 100
            self.progress_var.set(progress)
            self.root.update()
    
    def edit_schema(self):
        """编辑方案"""
        schema_name = self.schema_var.get()
        if not schema_name:
            messagebox.showwarning("提示", "请先选择要编辑的方案")
            return
        
        try:
            from schema_editor import SchemaEditorDialog
            editor = SchemaEditorDialog(self.root, self.config_manager, schema_name)
            self.root.wait_window(editor.dialog)
            
            if editor.result:
                self.config_manager.config = self.config_manager.load_config()
                self.load_schema_list()
                self.update_schema_info()
        except Exception as e:
            messagebox.showerror("错误", f"打开编辑器失败：{str(e)}")
    
    def create_new_schema(self):
        """新建方案"""
        try:
            from schema_editor import SchemaEditorDialog
            editor = SchemaEditorDialog(self.root, self.config_manager)
            self.root.wait_window(editor.dialog)
            
            if editor.result:
                self.config_manager.config = self.config_manager.load_config()
                self.load_schema_list()
                self.schema_var.set(editor.result)
                self.config_manager.set_active_schema(editor.result)
                self.update_schema_info()
        except Exception as e:
            messagebox.showerror("错误", f"打开编辑器失败：{str(e)}")
    
    def open_ai_settings(self):
        """打开AI设置"""
        try:
            from ai_settings_dialog import AISettingsDialog
            dialog = AISettingsDialog(self.root, self.config_manager)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                self.agent.init_ai_client()
        except ImportError:
            self.show_simple_ai_settings()
        except Exception as e:
            messagebox.showerror("错误", f"打开AI设置失败：{str(e)}")
    
    def toggle_mcp(self):
        """切换MCP增强开关"""
        enable_mcp = self.enable_mcp_var.get()
        
        if "ai_settings" not in self.config_manager.config:
            self.config_manager.config["ai_settings"] = {}
        
        self.config_manager.config["ai_settings"]["enable_mcp"] = enable_mcp
        self.config_manager.save_config()
        
        self.agent.init_mcp_client()
        
        status = t("mcp_enabled", "MCP功能已开启") if enable_mcp else t("mcp_disabled", "MCP功能已关闭")
        self.log(status)
        
        if enable_mcp:
            self.log(t("mcp_help_text", "MCP将帮助AI联网并提升结果准确性"))
        else:
            self.log(t("mcp_offline_text", "MCP已关闭，仅使用AI模型内知识"))
    
    def show_simple_ai_settings(self):
        """显示AI增强设置窗口"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI设置")
        dialog.geometry("750x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_container = tk.Frame(dialog, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        notebook_container = tk.Frame(main_container, bg="white")
        notebook_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        notebook = ttk.Notebook(notebook_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基础配置页
        basic_frame = tk.Frame(notebook, bg="white")
        notebook.add(basic_frame, text="基础配置")
        
        main_frame = tk.Frame(basic_frame, padx=20, pady=20, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ai_settings = self.config_manager.config.get("ai_settings", {})
        
        # 模型预设
        tk.Label(
            main_frame,
            text="模型预设：",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        model_presets = {
            "DeepSeek-Chat（官方）": {
                "api_url": "https://api.deepseek.com",
                "model": "deepseek-chat"
            },
            "DeepSeek-Reasoner（官方）": {
                "api_url": "https://api.deepseek.com",
                "model": "deepseek-reasoner"
            },
            "DeepSeek-V3（阿里云）": {
                "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "deepseek-v3"
            },
            "Qwen（阿里云）": {
                "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "qwen-plus"
            },
            "GPT-4（OpenAI）": {
                "api_url": "https://api.openai.com/v1",
                "model": "gpt-4"
            },
            "自定义": {
                "api_url": "",
                "model": ""
            }
        }
        
        current_base_url = ai_settings.get("base_url", "https://api.deepseek.com")
        current_model = ai_settings.get("model", "deepseek-chat")
        detected_preset = "自定义"
        for preset_name, preset_config in model_presets.items():
            if preset_name == "自定义":
                continue
            if (preset_config["api_url"] == current_base_url and 
                preset_config["model"] == current_model):
                detected_preset = preset_name
                break
        
        preset_var = tk.StringVar(value=detected_preset)
        preset_combo = ttk.Combobox(
            main_frame,
            textvariable=preset_var,
            values=list(model_presets.keys()),
            font=("Microsoft YaHei UI", 9),
            state="readonly",
            width=35
        )
        preset_combo.grid(row=0, column=1, pady=5, sticky="ew")
        
        def on_preset_change(event=None):
            preset = preset_var.get()
            if preset in model_presets:
                config = model_presets[preset]
                base_url_var.set(config["api_url"])
                model_var.set(config["model"])
        
        preset_combo.bind("<<ComboboxSelected>>", on_preset_change)
        
        # API Key
        tk.Label(
            main_frame,
            text="API密钥：",
            font=("Microsoft YaHei UI", 10),
            bg="white"
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        api_key_var = tk.StringVar(value=ai_settings.get("api_key", ""))
        tk.Entry(
            main_frame,
            textvariable=api_key_var,
            font=("Microsoft YaHei UI", 9),
            width=50,
            show="*"
        ).grid(row=1, column=1, pady=5, sticky="ew")
        
        tk.Label(
            main_frame,
            text="API地址：",
            font=("Microsoft YaHei UI", 10),
            bg="white"
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        base_url_var = tk.StringVar(value=ai_settings.get("base_url", "https://api.deepseek.com"))
        tk.Entry(
            main_frame,
            textvariable=base_url_var,
            font=("Microsoft YaHei UI", 9),
            width=50
        ).grid(row=2, column=1, pady=5, sticky="ew")
        
        tk.Label(
            main_frame,
            text="模型名：",
            font=("Microsoft YaHei UI", 10),
            bg="white"
        ).grid(row=3, column=0, sticky="w", pady=5)
        
        model_var = tk.StringVar(value=ai_settings.get("model", "deepseek-chat"))
        tk.Entry(
            main_frame,
            textvariable=model_var,
            font=("Microsoft YaHei UI", 9),
            width=50
        ).grid(row=3, column=1, pady=5, sticky="ew")
        
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        enable_mcp_var = tk.BooleanVar(value=ai_settings.get("enable_mcp", True))
        
        mcp_checkbox = tk.Checkbutton(
            main_frame,
            text="启用MCP增强（联网检索提升准确率）",
            variable=enable_mcp_var,
            font=("Microsoft YaHei UI", 10),
            bg="white"
        )
        mcp_checkbox.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(
            main_frame,
            text="💡 MCP让AI实时联网检索，准确率最高可达96%+",
            font=("Microsoft YaHei UI", 8),
            fg="gray",
            bg="white",
            justify=tk.LEFT
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # 高级设置
        advanced_frame = tk.Frame(notebook, bg="white")
        notebook.add(advanced_frame, text="高级")
        
        advanced_main = tk.Frame(advanced_frame, padx=20, pady=20, bg="white")
        advanced_main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            advanced_main,
            text=" 🧠  深度思考模式（适用于DeepSeek V3）",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg="white",
            fg="#2C3E50"
        ).pack(anchor="w", pady=(0, 5))
        
        enable_deep_thinking_var = tk.BooleanVar(value=ai_settings.get("enable_deep_thinking", False))
        tk.Checkbutton(
            advanced_main,
            text="启用深度思考模式（更高准确率，消耗更多tokens）",
            variable=enable_deep_thinking_var,
            font=("Microsoft YaHei UI", 9),
            bg="white"
        ).pack(anchor="w", pady=5)
        
        tk.Label(
            advanced_main,
            text="💡 深度思考适用于DeepSeek-Reasoner，显著提升准确率",
            font=("Microsoft YaHei UI", 8),
            fg="gray",
            bg="white",
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0, 15))
        
        ttk.Separator(advanced_main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 查询模式
        mode_frame = tk.Frame(notebook, bg="white")
        notebook.add(mode_frame, text="查询模式")
        
        mode_canvas = tk.Canvas(mode_frame, bg="white", highlightthickness=0)
        mode_scrollbar = ttk.Scrollbar(mode_frame, orient="vertical", command=mode_canvas.yview)
        mode_scrollable = tk.Frame(mode_canvas, bg="white")
        
        mode_scrollable.bind(
            "<Configure>",
            lambda e: mode_canvas.configure(scrollregion=mode_canvas.bbox("all"))
        )
        
        mode_canvas.create_window((0, 0), window=mode_scrollable, anchor="nw", width=700)
        mode_canvas.configure(yscrollcommand=mode_scrollbar.set)
        
        def _on_mode_mousewheel(event):            
            mode_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):            
            dialog.bind("<MouseWheel>", _on_mode_mousewheel)
        
        def _unbind_from_mousewheel(event):            
            dialog.unbind("<MouseWheel>")
        
        mode_canvas.bind("<Enter>", _bind_to_mousewheel)
        mode_canvas.bind("<Leave>", _unbind_from_mousewheel)
        mode_scrollable.bind("<Enter>", _bind_to_mousewheel)
        mode_scrollable.bind("<Leave>", _unbind_from_mousewheel)
        
        mode_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mode_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        mode_main = tk.Frame(mode_scrollable, padx=20, pady=20, bg="white")
        mode_main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            mode_main,
            text=" ⚡  查询模式选择（根据数据量选择）",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="white",
            fg="#2C3E50"
        ).pack(anchor="w", pady=(0, 15))
        
        if ai_settings.get("enable_turbo_mode", False):
            current_mode = "turbo"
        elif ai_settings.get("enable_one_shot_mode", False):
            current_mode = "one_shot"
        else:
            current_mode = "batch"
        
        query_mode_var = tk.StringVar(value=current_mode)
        
        # 普通批量模式
        mode1_frame = tk.Frame(mode_main, bg="white", relief=tk.RIDGE, borderwidth=1)
        mode1_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            mode1_frame,
            text="📦 普通批量模式（推荐）",
            variable=query_mode_var,
            value="batch",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="white",
            fg="#27AE60"
        ).pack(anchor="w", padx=10, pady=5)
        
        info1_frame = tk.Frame(mode1_frame, bg="white")
        info1_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        tk.Label(info1_frame, text="📊 适合：100-1000条数据", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info1_frame, text="⏱️ 速度：中等（约3-5秒/条）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info1_frame, text="💰 成本：中等（节省93%费用）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info1_frame, text="✅ 准确率：高", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        
        batch_size_frame = tk.Frame(info1_frame, bg="white")
        batch_size_frame.pack(anchor="w", pady=5)
        tk.Label(batch_size_frame, text="批量大小：", font=("Microsoft YaHei UI", 9), bg="white").pack(side=tk.LEFT)
        batch_size_var = tk.IntVar(value=ai_settings.get("batch_size", 15))
        tk.Spinbox(batch_size_frame, from_=5, to=50, textvariable=batch_size_var, font=("Microsoft YaHei UI", 9), width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(batch_size_frame, text="条（推荐10-20）", font=("Microsoft YaHei UI", 8), fg="gray", bg="white").pack(side=tk.LEFT)
        
        # 一镜直通模式
        mode2_frame = tk.Frame(mode_main, bg="white", relief=tk.RIDGE, borderwidth=1)
        mode2_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            mode2_frame,
            text="⚡ 一镜直通模式（实验）",
            variable=query_mode_var,
            value="one_shot",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="white",
            fg="#3498DB"
        ).pack(anchor="w", padx=10, pady=5)
        
        info2_frame = tk.Frame(mode2_frame, bg="white")
        info2_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        tk.Label(info2_frame, text="📊 适合：<100条数据", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info2_frame, text="⏱️ 速度：极快（一次性全部处理）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info2_frame, text="💰 成本：极低（仅1次API调用）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info2_frame, text="✅ 准确率：高（AI全局把控）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        
        one_shot_frame = tk.Frame(info2_frame, bg="white")
        one_shot_frame.pack(anchor="w", pady=5)
        tk.Label(one_shot_frame, text="最大条数：", font=("Microsoft YaHei UI", 9), bg="white").pack(side=tk.LEFT)
        one_shot_max_var = tk.IntVar(value=ai_settings.get("one_shot_max_companies", 100))
        tk.Spinbox(one_shot_frame, from_=10, to=200, textvariable=one_shot_max_var, font=("Microsoft YaHei UI", 9), width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(one_shot_frame, text="条（建议≤100）", font=("Microsoft YaHei UI", 8), fg="gray", bg="white").pack(side=tk.LEFT)
        
        # 超高速模式
        mode3_frame = tk.Frame(mode_main, bg="white", relief=tk.RIDGE, borderwidth=1)
        mode3_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            mode3_frame,
            text="🚀 极速模式（大规模）",
            variable=query_mode_var,
            value="turbo",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="white",
            fg="#E74C3C"
        ).pack(anchor="w", padx=10, pady=5)
        
        info3_frame = tk.Frame(mode3_frame, bg="white")
        info3_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        tk.Label(info3_frame, text="📊 适合：1000+数据", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info3_frame, text="⏱️ 速度：超快（5000条仅2分钟）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info3_frame, text="💰 成本：较高（并发API调用）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        tk.Label(info3_frame, text="⚠️ 准确率：中等（需复核）", font=("Microsoft YaHei UI", 9), bg="white").pack(anchor="w")
        
        turbo_batch_frame = tk.Frame(info3_frame, bg="white")
        turbo_batch_frame.pack(anchor="w", pady=5)
        tk.Label(turbo_batch_frame, text="批量并发：", font=("Microsoft YaHei UI", 9), bg="white").pack(side=tk.LEFT)
        turbo_batch_var = tk.IntVar(value=ai_settings.get("turbo_batch_size", 100))
        tk.Spinbox(turbo_batch_frame, from_=50, to=200, textvariable=turbo_batch_var, font=("Microsoft YaHei UI", 9), width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(turbo_batch_frame, text="条/批（推荐60-80）", font=("Microsoft YaHei UI", 8), fg="gray", bg="white").pack(side=tk.LEFT)
        
        concurrent_frame_inner = tk.Frame(info3_frame, bg="white")
        concurrent_frame_inner.pack(anchor="w", pady=5)
        tk.Label(concurrent_frame_inner, text="并发任务：", font=("Microsoft YaHei UI", 9), bg="white").pack(side=tk.LEFT)
        concurrent_var = tk.IntVar(value=ai_settings.get("turbo_concurrent_requests", 5))
        tk.Spinbox(concurrent_frame_inner, from_=1, to=10, textvariable=concurrent_var, font=("Microsoft YaHei UI", 9), width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(concurrent_frame_inner, text="个（建议3-5）", font=("Microsoft YaHei UI", 8), fg="gray", bg="white").pack(side=tk.LEFT)
        
        
        def cleanup_and_close():
            try:
                dialog.unbind("<MouseWheel>")
            except:
                pass
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", cleanup_and_close)
        
        button_frame = tk.Frame(notebook_container, bg="white")
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5), before=notebook)
        
        print("[信息] 按钮区域初始化")     
        
        def save_settings():
            print("正在保存配置...")
            
            ai_settings["api_key"] = api_key_var.get()
            ai_settings["base_url"] = base_url_var.get()
            ai_settings["model"] = model_var.get()
            ai_settings["enable_mcp"] = enable_mcp_var.get()
            ai_settings["enable_deep_thinking"] = enable_deep_thinking_var.get()
            
            query_mode = query_mode_var.get()
            ai_settings["enable_batch_mode"] = (query_mode == "batch")
            ai_settings["enable_one_shot_mode"] = (query_mode == "one_shot")
            ai_settings["enable_turbo_mode"] = (query_mode == "turbo")
            
            ai_settings["batch_size"] = batch_size_var.get()
            ai_settings["one_shot_max_companies"] = one_shot_max_var.get()
            ai_settings["turbo_batch_size"] = turbo_batch_var.get()
            ai_settings["turbo_concurrent_requests"] = concurrent_var.get()
            
            print(f"🔧 配置数据就绪: query_mode={query_mode}, batch_size={ai_settings['batch_size']}")
            
            self.config_manager.config["ai_settings"] = ai_settings
            save_result = self.config_manager.save_config()
            
            print(f"保存结果: {save_result}, 文件: {self.config_manager.config_file}")
            
            self.agent.init_ai_client()
            self.agent.init_mcp_client()
            
            self.enable_mcp_var.set(enable_mcp_var.get())
            query_mode = query_mode_var.get()
            self.batch_mode_var.set(query_mode in ["batch", "one_shot", "turbo"])
            self.batch_size_var.set(batch_size_var.get())
            
            messagebox.showinfo("成功", "AI配置保存成功！\n\n已更新：\n- 模型设置\n- 批量处理\n- 极速模式\n- MCP增强")
            dialog.destroy()
        
        def test_config():
            try:
                from openai_compatible_client import OpenAICompatibleClient
                test_client = OpenAICompatibleClient(
                    api_key=api_key_var.get(),
                    base_url=base_url_var.get(),
                    model=model_var.get(),
                    enable_web_search=enable_mcp_var.get()
                )
                response = test_client.chat("你好，请回复：测试成功", stream=False, parse_response=False)
                if response and isinstance(response, dict):
                    content = response.get("content", "") or str(response)
                    messagebox.showinfo("测试通过", f"✅ AI连接成功！\n\n模型: {model_var.get()}\n返回: {content[:100]}...")
                elif response:
                    messagebox.showinfo("测试通过", f"✅ AI连接成功！\n\n模型: {model_var.get()}\n返回: {str(response)[:100]}...")
                else:
                    messagebox.showwarning("测试失败", "AI返回为空，请检查配置")
            except Exception as e:
                messagebox.showerror("测试失败", f"❌ 连接失败：\n\n{str(e)}\n\n请检查：\n- API Key 是否正确\n- API地址是否正确\n- 网络正常")
        
        tk.Button(
            button_frame,
            text=" ❌  取消",
            font=("Microsoft YaHei UI", 10),
            bg="#D9534F",
            fg="white",
            command=cleanup_and_close,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=3)
        
        tk.Button(
            button_frame,
            text=" 🔍  测试配置",
            font=("Microsoft YaHei UI", 10),
            bg="#4A90E2",
            fg="white",
            command=test_config,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=3)
        
        tk.Button(
            button_frame,
            text=" 💾  保存配置",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#5CB85C",
            fg="white",
            command=save_settings,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=3)
    
    def show_help(self):
        """显示使用帮助"""
        help_text = t("help_content", """通用AI智能体系统 - 用户指南

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
""")
        
        help_window = tk.Toplevel(self.root)
        help_window.title(t("help_title", "使用指南"))
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(
            help_window,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)


def main():
    """主入口"""
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()


if __name__ == "__main__":
    print("[信息] 启动通用AI智能体工具 v1.0")
    main()