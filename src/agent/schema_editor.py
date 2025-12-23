"""
配置方案编辑器 - 可视化编辑AI Agent配置
"""

import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import json
import copy


class SchemaEditorDialog:
    """配置方案编辑器对话框"""
    
    def __init__(self, parent, config_manager, schema_name=None):
        self.parent = parent
        self.config_manager = config_manager
        self.schema_name = schema_name
        self.is_new = schema_name is None
        
        # 如果是编辑现有方案，加载数据
        if not self.is_new:
            self.schema_data = copy.deepcopy(
                config_manager.config['schemas'][schema_name]
            )
        else:
            # 新建方案的默认模板
            self.schema_data = {
                "name": "",
                "description": "",
                "input_columns": [],
                "output_columns": [],
                "prompt_template": "",
                "batch_prompt_template": ""
            }
        
        self.result = None
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        self.dialog = tk.Toplevel(self.parent)
        title = "编辑配置方案" if not self.is_new else "新建配置方案"
        self.dialog.title(title)
        self.dialog.geometry("900x750")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 主框架
        main_frame = tk.Frame(self.dialog, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息
        basic_frame = tk.LabelFrame(
            main_frame,
            text="基本信息",
            font=("Microsoft YaHei UI", 10, "bold"),
            padx=10,
            pady=10
        )
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 方案名称
        name_frame = tk.Frame(basic_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            name_frame,
            text="方案名称：",
            font=("Microsoft YaHei UI", 9),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.name_var = tk.StringVar(value=self.schema_data.get('name', ''))
        tk.Entry(
            name_frame,
            textvariable=self.name_var,
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 方案描述
        desc_frame = tk.Frame(basic_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            desc_frame,
            text="方案描述：",
            font=("Microsoft YaHei UI", 9),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.desc_var = tk.StringVar(value=self.schema_data.get('description', ''))
        tk.Entry(
            desc_frame,
            textvariable=self.desc_var,
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建Notebook用于分页（不使用expand=True，给按钮留出空间）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 输入列页面
        input_frame = tk.Frame(notebook)
        notebook.add(input_frame, text="输入列配置")
        self.create_columns_editor(input_frame, "input")
        
        # 输出列页面
        output_frame = tk.Frame(notebook)
        notebook.add(output_frame, text="输出列配置")
        self.create_columns_editor(output_frame, "output")
        
        # 提示词页面
        prompt_frame = tk.Frame(notebook)
        notebook.add(prompt_frame, text="提示词模板")
        self.create_prompt_editor(prompt_frame)
        
    
    def create_columns_editor(self, parent, column_type):
        """创建列配置编辑器"""
        # 列表显示
        list_frame = tk.Frame(parent, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 树形控件显示列
        columns = ('name', 'type', 'required', 'description')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        tree.heading('name', text='列名')
        tree.heading('type', text='类型')
        tree.heading('required', text='必填')
        tree.heading('description', text='描述')
        
        tree.column('name', width=150)
        tree.column('type', width=80)
        tree.column('required', width=60)
        tree.column('description', width=300)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 保存树形控件引用
        if column_type == "input":
            self.input_tree = tree
            columns_data = self.schema_data.get('input_columns', [])
        else:
            self.output_tree = tree
            columns_data = self.schema_data.get('output_columns', [])
        
        # 加载数据
        for col in columns_data:
            values = (
                col.get('name', ''),
                col.get('type', 'string'),
                '是' if col.get('required', False) else '否',
                col.get('description', '')
            )
            tree.insert('', tk.END, values=values)
        
        # 操作按钮
        button_frame = tk.Frame(parent, padx=10, pady=5)
        button_frame.pack(fill=tk.X)
        
        tk.Button(
            button_frame,
            text="Add",
            font=("Microsoft YaHei UI", 9),
            command=lambda: self.add_column(column_type),
            relief=tk.FLAT,
            bg="#5CB85C",
            fg="white",
            padx=13,
            pady=4
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            button_frame,
            text="Edit",
            font=("Microsoft YaHei UI", 9),
            command=lambda: self.edit_column(column_type),
            relief=tk.FLAT,
            bg="#4A90E2",
            fg="white",
            padx=13,
            pady=4
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            button_frame,
            text="Delete",
            font=("Microsoft YaHei UI", 9),
            command=lambda: self.delete_column(column_type),
            relief=tk.FLAT,
            bg="#D9534F",
            fg="white",
            padx=13,
            pady=4
        ).pack(side=tk.LEFT, padx=3)
        
        # Save button
        tk.Button(
            button_frame,
            text="Save",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FF8C00",
            fg="white",
            command=self.save_schema,
            relief=tk.FLAT,
            padx=13,
            pady=4
        ).pack(side=tk.LEFT, padx=3)
        
        # Cancel button
        tk.Button(
            button_frame,
            text="Cancel",
            font=("Microsoft YaHei UI", 9),
            bg="#808080",
            fg="white",
            command=self.dialog.destroy,
            relief=tk.FLAT,
            padx=13,
            pady=4
        ).pack(side=tk.LEFT, padx=3)
    
    def create_prompt_editor(self, parent):
        """创建提示词编辑器"""
        # 单条提示词
        single_frame = tk.LabelFrame(
            parent,
            text="单条查询提示词模板",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=10,
            pady=10
        )
        single_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.prompt_text = scrolledtext.ScrolledText(
            single_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.insert('1.0', self.schema_data.get('prompt_template', ''))
        
        # 批量提示词
        batch_frame = tk.LabelFrame(
            parent,
            text="批量查询提示词模板",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=10,
            pady=10
        )
        batch_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.batch_prompt_text = scrolledtext.ScrolledText(
            batch_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.batch_prompt_text.pack(fill=tk.BOTH, expand=True)
        self.batch_prompt_text.insert('1.0', self.schema_data.get('batch_prompt_template', ''))
        
        # 提示信息
        hint_text = """
提示词模板支持以下变量：
- {input_data}: 输入数据
- {output_fields_description}: 输出字段描述
- {companies_list} / {batch_data}: 批量数据列表
- 以及所有输入列的名称（如 {company_name}, {产品名称} 等）
        """
        hint_label = tk.Label(
            parent,
            text=hint_text,
            font=("Microsoft YaHei UI", 8),
            fg="gray",
            justify=tk.LEFT
        )
        hint_label.pack(padx=10, pady=5)
    
    def add_column(self, column_type):
        """添加列"""
        dialog = ColumnEditDialog(self.dialog, column_type)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            tree = self.input_tree if column_type == "input" else self.output_tree
            values = (
                dialog.result['name'],
                dialog.result.get('type', 'string'),
                '是' if dialog.result.get('required', False) else '否',
                dialog.result.get('description', '')
            )
            tree.insert('', tk.END, values=values)
    
    def edit_column(self, column_type):
        """编辑列"""
        tree = self.input_tree if column_type == "input" else self.output_tree
        selected = tree.selection()
        
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的列")
            return
        
        item = selected[0]
        values = tree.item(item, 'values')
        
        # 构造原始数据
        original_data = {
            'name': values[0],
            'type': values[1],
            'required': values[2] == '是',
            'description': values[3]
        }
        
        dialog = ColumnEditDialog(self.dialog, column_type, original_data)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            new_values = (
                dialog.result['name'],
                dialog.result.get('type', 'string'),
                '是' if dialog.result.get('required', False) else '否',
                dialog.result.get('description', '')
            )
            tree.item(item, values=new_values)
    
    def delete_column(self, column_type):
        """删除列"""
        tree = self.input_tree if column_type == "input" else self.output_tree
        selected = tree.selection()
        
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的列")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的列吗？"):
            for item in selected:
                tree.delete(item)
    
    def save_schema(self):
        """保存配置方案"""
        # 验证基本信息
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请输入方案名称")
            return
        
        # 如果是新建，检查方案名是否已存在
        if self.is_new and name in self.config_manager.config.get('schemas', {}):
            messagebox.showerror("错误", "方案名称已存在")
            return
        
        # 收集输入列数据
        input_columns = []
        for item in self.input_tree.get_children():
            values = self.input_tree.item(item, 'values')
            input_columns.append({
                'name': values[0],
                'type': values[1] if len(values) > 1 else 'string',
                'required': values[2] == '是' if len(values) > 2 else False,
                'description': values[3] if len(values) > 3 else ''
            })
        
        # 收集输出列数据
        output_columns = []
        for item in self.output_tree.get_children():
            values = self.output_tree.item(item, 'values')
            output_columns.append({
                'name': values[0],
                'type': values[1] if len(values) > 1 else 'string',
                'description': values[3] if len(values) > 3 else ''
            })
        
        # 构建方案数据
        schema_data = {
            'name': name,
            'description': self.desc_var.get().strip(),
            'input_columns': input_columns,
            'output_columns': output_columns,
            'prompt_template': self.prompt_text.get('1.0', tk.END).strip(),
            'batch_prompt_template': self.batch_prompt_text.get('1.0', tk.END).strip()
        }
        
        # 生成方案ID（如果是新建）
        if self.is_new:
            # 使用拼音或简单转换作为ID
            schema_id = name.replace(' ', '_').lower()
            # 如果ID已存在，添加数字后缀
            counter = 1
            original_id = schema_id
            while schema_id in self.config_manager.config.get('schemas', {}):
                schema_id = f"{original_id}_{counter}"
                counter += 1
            
            self.schema_name = schema_id
        
        # 保存到配置管理器
        self.config_manager.add_schema(self.schema_name, schema_data)
        
        messagebox.showinfo("成功", "配置方案保存成功")
        self.result = self.schema_name
        self.dialog.destroy()


class ColumnEditDialog:
    """列编辑对话框"""
    
    def __init__(self, parent, column_type, column_data=None):
        self.parent = parent
        self.column_type = column_type
        self.column_data = column_data or {}
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        self.dialog = tk.Toplevel(self.parent)
        title = "编辑列" if self.column_data else "添加列"
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 列名
        name_frame = tk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            name_frame,
            text="列名：",
            font=("Microsoft YaHei UI", 9),
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.name_var = tk.StringVar(value=self.column_data.get('name', ''))
        tk.Entry(
            name_frame,
            textvariable=self.name_var,
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 类型（仅输出列需要）
        if self.column_type == "output":
            type_frame = tk.Frame(main_frame)
            type_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                type_frame,
                text="类型：",
                font=("Microsoft YaHei UI", 9),
                width=10,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            self.type_var = tk.StringVar(value=self.column_data.get('type', 'string'))
            type_combo = ttk.Combobox(
                type_frame,
                textvariable=self.type_var,
                font=("Microsoft YaHei UI", 9),
                values=['string', 'number', 'boolean', 'date'],
                state='readonly'
            )
            type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 是否必填（仅输入列需要）
        if self.column_type == "input":
            self.required_var = tk.BooleanVar(value=self.column_data.get('required', False))
            tk.Checkbutton(
                main_frame,
                text="必填列",
                variable=self.required_var,
                font=("Microsoft YaHei UI", 9)
            ).pack(anchor='w', pady=5)
        
        # 描述
        desc_frame = tk.Frame(main_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(
            desc_frame,
            text="描述：",
            font=("Microsoft YaHei UI", 9),
            anchor="nw"
        ).pack(anchor='w')
        
        self.desc_text = scrolledtext.ScrolledText(
            desc_frame,
            height=8,
            font=("Microsoft YaHei UI", 9),
            wrap=tk.WORD
        )
        self.desc_text.pack(fill=tk.BOTH, expand=True)
        self.desc_text.insert('1.0', self.column_data.get('description', ''))
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            button_frame,
            text="确定",
            font=("Microsoft YaHei UI", 9),
            bg="#5CB85C",
            fg="white",
            command=self.save,
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft YaHei UI", 9),
            bg="#D9534F",
            fg="white",
            command=self.dialog.destroy,
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """保存"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请输入列名")
            return
        
        result = {
            'name': name,
            'description': self.desc_text.get('1.0', tk.END).strip()
        }
        
        if self.column_type == "output":
            result['type'] = self.type_var.get()
        
        if self.column_type == "input":
            result['required'] = self.required_var.get()
        
        self.result = result
        self.dialog.destroy()


def test_editor():
    """测试编辑器"""
    root = tk.Tk()
    root.withdraw()
    
    # 创建临时配置管理器
    from agent_main import AgentConfigManager
    config_manager = AgentConfigManager()
    
    # 打开编辑器
    editor = SchemaEditorDialog(root, config_manager)
    root.wait_window(editor.dialog)
    
    if editor.result:
        print(f"保存的方案ID: {editor.result}")
    
    root.destroy()


if __name__ == "__main__":
    test_editor()

