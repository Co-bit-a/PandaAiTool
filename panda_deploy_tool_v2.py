#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PandaAI工具部署助手 V2.0
重新设计的版本，分为部署和启动两个页面，支持状态管理和持久化
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import os
import sys
import threading
from pathlib import Path
import time
import json
import webbrowser
from datetime import datetime

class ProjectStatus:
    """项目状态管理类"""
    def __init__(self, status_file="project_status.json"):
        self.status_file = status_file
        self.default_status = {
            "project_path": "",
            "conda_env": "pandaaitool",
            "git_url": "https://github.com/PandaAI-Tech/panda_factor.git",
            "quantflow_git_url": "https://github.com/PandaAI-Tech/panda_quantflow.git",
            "mongodb_path": "",
            "mongodb_status": "unknown",  # unknown, ok, error, not_configured
            "deployment_status": "not_started",  # not_started, in_progress, completed, failed
            "last_update": "",
            "git_commit": "",
            "quantflow_commit": "",
            "environment_status": "unknown",  # unknown, ok, error
            "server_status": "stopped",  # stopped, running, error
            "completed_steps": [],
            "last_check": ""
        }
        self.status = self.load_status()
    
    def load_status(self):
        """加载状态"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                # 合并默认状态和已保存状态
                merged_status = self.default_status.copy()
                merged_status.update(status)
                return merged_status
            return self.default_status.copy()
        except Exception as e:
            print(f"加载状态失败: {e}")
            return self.default_status.copy()
    
    def save_status(self):
        """保存状态"""
        try:
            self.status["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")
    
    def update_status(self, **kwargs):
        """更新状态"""
        self.status.update(kwargs)
        self.save_status()
    
    def get_status(self, key):
        """获取状态"""
        return self.status.get(key, self.default_status.get(key))

class PandaDeployToolV2:
    def __init__(self, root):
        self.root = root
        self.root.title("PandaAI工具管理助手 V2.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # 状态管理
        self.project_status = ProjectStatus()
        
        # 设置样式
        self.setup_styles()
        
        # 创建主界面
        self.create_main_interface()
        
        # 启动时检查状态
        self.root.after(1000, self.check_all_status)
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='#f39c12', font=('Arial', 10, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        
        # 按钮样式
        style.configure('Deploy.TButton', font=('Arial', 11, 'bold'))
        style.configure('Launch.TButton', font=('Arial', 11, 'bold'))
    
    def create_main_interface(self):
        """创建主界面"""
        # 标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(title_frame, text="🐼 PandaAI工具管理助手", style='Title.TLabel').pack()
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 部署页面
        self.deploy_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.deploy_frame, text="📦 项目部署")
        self.create_deploy_page()
        
        # 启动页面
        self.launch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.launch_frame, text="🚀 项目启动")
        self.create_launch_page()
        
        # 操作页面
        self.operations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operations_frame, text="⚙️ 数据操作")
        self.create_operations_page()
        
        # 状态栏
        self.create_status_bar()
    
    def create_deploy_page(self):
        """创建部署页面"""
        # 项目配置区域
        config_frame = ttk.LabelFrame(self.deploy_frame, text="🔧 项目配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Factor Git地址
        git_frame = ttk.Frame(config_frame)
        git_frame.pack(fill=tk.X, pady=2)
        ttk.Label(git_frame, text="Factor Git：", width=12).pack(side=tk.LEFT)
        self.git_url_var = tk.StringVar(value=self.project_status.get_status("git_url"))
        ttk.Entry(git_frame, textvariable=self.git_url_var, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # QuantFlow Git地址
        quantflow_git_frame = ttk.Frame(config_frame)
        quantflow_git_frame.pack(fill=tk.X, pady=2)
        ttk.Label(quantflow_git_frame, text="QuantFlow Git：", width=12).pack(side=tk.LEFT)
        self.quantflow_git_url_var = tk.StringVar(value=self.project_status.get_status("quantflow_git_url"))
        ttk.Entry(quantflow_git_frame, textvariable=self.quantflow_git_url_var, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 安装路径
        path_frame = ttk.Frame(config_frame)
        path_frame.pack(fill=tk.X, pady=2)
        ttk.Label(path_frame, text="安装路径：").pack(side=tk.LEFT)
        self.project_path_var = tk.StringVar(value=self.project_status.get_status("project_path"))
        ttk.Entry(path_frame, textvariable=self.project_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="浏览", command=self.browse_project_path).pack(side=tk.RIGHT)
        
        # Conda环境
        env_frame = ttk.Frame(config_frame)
        env_frame.pack(fill=tk.X, pady=2)
        ttk.Label(env_frame, text="Conda环境：").pack(side=tk.LEFT)
        self.conda_env_var = tk.StringVar(value=self.project_status.get_status("conda_env"))
        ttk.Entry(env_frame, textvariable=self.conda_env_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # MongoDB路径
        mongodb_frame = ttk.Frame(config_frame)
        mongodb_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mongodb_frame, text="MongoDB路径：").pack(side=tk.LEFT)
        self.mongodb_path_var = tk.StringVar(value=self.project_status.get_status("mongodb_path"))
        ttk.Entry(mongodb_frame, textvariable=self.mongodb_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(mongodb_frame, text="浏览", command=self.browse_mongodb_path).pack(side=tk.RIGHT)
        
        # 部署状态区域
        status_frame = ttk.LabelFrame(self.deploy_frame, text="📊 部署状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 状态显示
        self.deploy_status_frame = ttk.Frame(status_frame)
        self.deploy_status_frame.pack(fill=tk.X)
        
        self.create_status_indicators()
        
        # 操作按钮
        button_frame = ttk.Frame(self.deploy_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="🚀 开始部署", command=self.start_deployment, style='Deploy.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 检查更新", command=self.check_git_updates).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 清除状态", command=self.clear_status).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.deploy_progress = ttk.Progressbar(self.deploy_frame, mode='determinate')
        self.deploy_progress.pack(fill=tk.X, padx=10, pady=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.deploy_frame, text="📄 部署日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.deploy_log = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, font=('Consolas', 9))
        self.deploy_log.pack(fill=tk.BOTH, expand=True)
    
    def create_launch_page(self):
        """创建启动页面"""
        # 环境状态区域
        env_frame = ttk.LabelFrame(self.launch_frame, text="🔍 环境状态", padding=10)
        env_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 环境状态显示
        self.env_status_frame = ttk.Frame(env_frame)
        self.env_status_frame.pack(fill=tk.X)
        
        self.create_env_status_indicators()
        
        # 项目信息区域
        info_frame = ttk.LabelFrame(self.launch_frame, text="📋 项目信息", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.project_info_frame = ttk.Frame(info_frame)
        self.project_info_frame.pack(fill=tk.X)
        
        self.create_project_info()
        
        # 启动控制区域
        control_frame = ttk.LabelFrame(self.launch_frame, text="🎮 启动控制", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        self.launch_button = ttk.Button(button_frame, text="🚀 启动项目", command=self.launch_project, style='Launch.TButton')
        self.launch_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🛑 停止项目", command=self.stop_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🌐 打开浏览器", command=self.open_browser).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新状态", command=self.check_all_status).pack(side=tk.LEFT, padx=5)
        
        # 服务器状态
        server_frame = ttk.LabelFrame(self.launch_frame, text="🖥️ 服务器状态", padding=10)
        server_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.server_status_var = tk.StringVar(value="未知")
        self.server_status_label = ttk.Label(server_frame, textvariable=self.server_status_var, style='Status.TLabel')
        self.server_status_label.pack()
        
        # 启动日志
        launch_log_frame = ttk.LabelFrame(self.launch_frame, text="📄 启动日志", padding=10)
        launch_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.launch_log = scrolledtext.ScrolledText(launch_log_frame, height=10, wrap=tk.WORD, font=('Consolas', 9))
        self.launch_log.pack(fill=tk.BOTH, expand=True)
    
    def create_operations_page(self):
        """创建操作页面"""
        # 页面说明
        info_frame = ttk.LabelFrame(self.operations_frame, text="ℹ️ 操作说明", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
        📊 数据操作功能：
        • 数据更新：访问数据清理页面，管理和更新数据源
        • 数据列表：查看当前系统中的所有数据列表
        • 超级图表：使用QuantFlow的可视化图表功能
        • 工作流：创建和管理QuantFlow量化工作流
        
        ⚠️ 注意：
        • Factor功能需要服务器运行在 localhost:8111
        • QuantFlow功能需要服务器运行在 localhost:8000
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=('Arial', 10)).pack(anchor=tk.W)
        
        # 数据操作区域
        operations_frame = ttk.LabelFrame(self.operations_frame, text="🛠️ 数据操作", padding=15)
        operations_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 按钮容器
        button_container = ttk.Frame(operations_frame)
        button_container.pack(expand=True)
        
        # 创建按钮框架，使用网格布局
        button_frame = ttk.Frame(button_container)
        button_frame.pack()
        
        # 数据更新按钮
        data_update_frame = ttk.Frame(button_frame)
        data_update_frame.grid(row=0, column=0, padx=20, pady=10)
        
        ttk.Button(
            data_update_frame, 
            text="📈 数据更新", 
            command=self.open_data_update,
            style='Launch.TButton',
            width=15
        ).pack(pady=5)
        
        ttk.Label(
            data_update_frame, 
            text="打开数据清理页面\n管理和更新数据源", 
            justify=tk.CENTER,
            font=('Arial', 9),
            foreground='#666'
        ).pack()
        
        # 数据列表按钮
        data_list_frame = ttk.Frame(button_frame)
        data_list_frame.grid(row=0, column=1, padx=20, pady=10)
        
        ttk.Button(
            data_list_frame, 
            text="📋 数据列表", 
            command=self.open_data_list,
            style='Launch.TButton',
            width=15
        ).pack(pady=5)
        
        ttk.Label(
            data_list_frame, 
            text="查看系统中的\n所有数据列表", 
            justify=tk.CENTER,
            font=('Arial', 9),
            foreground='#666'
        ).pack()
        
        # QuantFlow操作按钮（第二行）
        quantflow_frame = ttk.Frame(button_frame)
        quantflow_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(
            quantflow_frame, 
            text="📊 QuantFlow工作流平台", 
            font=('Arial', 11, 'bold'),
            foreground='#2c3e50'
        ).pack(pady=(0, 5))
        
        # QuantFlow按钮容器
        qf_button_container = ttk.Frame(quantflow_frame)
        qf_button_container.pack()
        
        # 超级图表按钮
        charts_frame = ttk.Frame(qf_button_container)
        charts_frame.grid(row=0, column=0, padx=15, pady=5)
        
        ttk.Button(
            charts_frame, 
            text="📈 超级图表", 
            command=self.open_charts,
            style='Launch.TButton',
            width=15
        ).pack(pady=5)
        
        ttk.Label(
            charts_frame, 
            text="打开QuantFlow\n超级图表界面", 
            justify=tk.CENTER,
            font=('Arial', 9),
            foreground='#666'
        ).pack()
        
        # 工作流按钮
        workflow_frame = ttk.Frame(qf_button_container)
        workflow_frame.grid(row=0, column=1, padx=15, pady=5)
        
        ttk.Button(
            workflow_frame, 
            text="🔗 工作流", 
            command=self.open_quantflow,
            style='Launch.TButton',
            width=15
        ).pack(pady=5)
        
        ttk.Label(
            workflow_frame, 
            text="打开QuantFlow\n工作流界面", 
            justify=tk.CENTER,
            font=('Arial', 9),
            foreground='#666'
        ).pack()
        
        # 服务器状态检查区域
        status_frame = ttk.LabelFrame(self.operations_frame, text="🔍 服务器状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.server_check_frame = ttk.Frame(status_frame)
        self.server_check_frame.pack(fill=tk.X)
        
        # 状态显示
        self.server_url_status = tk.StringVar(value="检查中...")
        ttk.Label(self.server_check_frame, text="服务器状态: ").pack(side=tk.LEFT)
        self.server_url_label = ttk.Label(self.server_check_frame, textvariable=self.server_url_status)
        self.server_url_label.pack(side=tk.LEFT)
        
        ttk.Button(self.server_check_frame, text="🔄 检查服务器", command=self.check_server_status).pack(side=tk.RIGHT)
        
        # 操作日志区域
        log_frame = ttk.LabelFrame(self.operations_frame, text="📄 操作日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.operations_log = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD, font=('Consolas', 9))
        self.operations_log.pack(fill=tk.BOTH, expand=True)
        
        # 初始化时检查服务器状态
        self.check_server_status()
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.status_bar, textvariable=self.status_var).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 最后检查时间
        self.last_check_var = tk.StringVar()
        ttk.Label(self.status_bar, textvariable=self.last_check_var).pack(side=tk.RIGHT, padx=10, pady=5)
    
    def create_status_indicators(self):
        """创建状态指示器"""
        # 清除现有内容
        for widget in self.deploy_status_frame.winfo_children():
            widget.destroy()
        
        steps = [
            ("环境检查", "check_environment"),
            ("创建目录", "create_directory"),
            ("克隆项目", "clone_project"),
            ("配置环境", "setup_conda_env"),
            ("安装依赖", "install_dependencies"),
            ("创建脚本", "create_scripts")
        ]
        
        completed_steps = self.project_status.get_status("completed_steps")
        
        for i, (step_name, step_id) in enumerate(steps):
            row = i // 3
            col = i % 3
            
            frame = ttk.Frame(self.deploy_status_frame)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            # 状态指示器
            if step_id in completed_steps:
                status_text = "✅"
                style = 'Success.TLabel'
            else:
                status_text = "⭕"
                style = 'Warning.TLabel'
            
            ttk.Label(frame, text=status_text, style=style).pack(side=tk.LEFT)
            ttk.Label(frame, text=step_name, style='Status.TLabel').pack(side=tk.LEFT, padx=5)
    
    def create_env_status_indicators(self):
        """创建环境状态指示器"""
        # 清除现有内容
        for widget in self.env_status_frame.winfo_children():
            widget.destroy()
        
        # Git状态
        git_frame = ttk.Frame(self.env_status_frame)
        git_frame.pack(fill=tk.X, pady=2)
        self.git_status_label = ttk.Label(git_frame, text="⭕ Git", style='Warning.TLabel')
        self.git_status_label.pack(side=tk.LEFT)
        
        # Conda状态
        conda_frame = ttk.Frame(self.env_status_frame)
        conda_frame.pack(fill=tk.X, pady=2)
        self.conda_status_label = ttk.Label(conda_frame, text="⭕ Conda", style='Warning.TLabel')
        self.conda_status_label.pack(side=tk.LEFT)
        
        # Python环境状态
        python_frame = ttk.Frame(self.env_status_frame)
        python_frame.pack(fill=tk.X, pady=2)
        self.python_status_label = ttk.Label(python_frame, text="⭕ Python环境", style='Warning.TLabel')
        self.python_status_label.pack(side=tk.LEFT)
        
        # 项目状态
        project_frame = ttk.Frame(self.env_status_frame)
        project_frame.pack(fill=tk.X, pady=2)
        self.project_status_label = ttk.Label(project_frame, text="⭕ 项目文件", style='Warning.TLabel')
        self.project_status_label.pack(side=tk.LEFT)
        
        # MongoDB状态
        mongodb_frame = ttk.Frame(self.env_status_frame)
        mongodb_frame.pack(fill=tk.X, pady=2)
        self.mongodb_status_label = ttk.Label(mongodb_frame, text="⭕ MongoDB", style='Warning.TLabel')
        self.mongodb_status_label.pack(side=tk.LEFT)
    
    def create_project_info(self):
        """创建项目信息显示"""
        # 清除现有内容
        for widget in self.project_info_frame.winfo_children():
            widget.destroy()
        
        # 获取项目实际路径
        base_path = self.project_status.get_status("project_path")
        actual_panda_factor_path = os.path.join(base_path, "panda_factor") if base_path else "未设置"
        actual_panda_quantflow_path = os.path.join(base_path, "panda_quantflow") if base_path else "未设置"
        
        info_items = [
            ("安装目录", base_path or "未设置"),
            ("项目factor路径", actual_panda_factor_path),
            ("项目QuantFlow路径", actual_panda_quantflow_path),
            ("Conda环境", self.project_status.get_status("conda_env")),
            ("MongoDB路径", self.project_status.get_status("mongodb_path") or "未设置"),
            ("部署状态", self.get_deployment_status_text()),
            ("最后更新", self.project_status.get_status("last_update")),
            ("Git提交", self.project_status.get_status("git_commit")[:8] if self.project_status.get_status("git_commit") else "未知")
        ]
        
        for i, (label, value) in enumerate(info_items):
            frame = ttk.Frame(self.project_info_frame)
            frame.pack(fill=tk.X, pady=1)
            
            ttk.Label(frame, text=f"{label}:", style='Status.TLabel').pack(side=tk.LEFT)
            
            # 根据内容设置不同颜色
            if label == "部署状态":
                style = 'Success.TLabel' if value == "部署完成" else 'Warning.TLabel' if value == "部署中" else 'Error.TLabel'
            else:
                style = 'Status.TLabel'
                
            ttk.Label(frame, text=value or "未设置", style=style).pack(side=tk.LEFT, padx=10)
    
    def browse_project_path(self):
        """浏览项目路径"""
        path = filedialog.askdirectory()
        if path:
            self.project_path_var.set(path)
    
    def browse_mongodb_path(self):
        """浏览MongoDB路径"""
        path = filedialog.askdirectory(title="选择MongoDB安装目录")
        if path:
            self.mongodb_path_var.set(path)
            # 保存到状态文件
            self.project_status.update_status(mongodb_path=path)
    
    def log_deploy(self, message):
        """部署日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.deploy_log.insert(tk.END, log_message)
        self.deploy_log.see(tk.END)
        self.root.update()
    
    def log_launch(self, message):
        """启动日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.launch_log.insert(tk.END, log_message)
        self.launch_log.see(tk.END)
        self.root.update()
    
    def check_all_status(self):
        """检查所有状态"""
        self.status_var.set("正在检查状态...")
        
        # 在新线程中检查状态
        thread = threading.Thread(target=self._check_status_thread)
        thread.daemon = True
        thread.start()
    
    def _check_status_thread(self):
        """状态检查线程"""
        try:
            # 检查Git
            git_ok = self.check_git_status()
            
            # 检查Conda
            conda_ok = self.check_conda_status()
            
            # 检查Python环境
            python_ok = self.check_python_env()
            
            # 检查项目文件
            project_ok = self.check_project_files()
            
            # 检查MongoDB
            mongodb_ok = self.check_mongodb_status()
            
            # 更新UI
            self.root.after(0, self.update_status_ui, git_ok, conda_ok, python_ok, project_ok, mongodb_ok)
            
            # 更新最后检查时间
            self.last_check_var.set(f"最后检查: {datetime.now().strftime('%H:%M:%S')}")
            
            self.status_var.set("状态检查完成")
            
        except Exception as e:
            error_msg = f"状态检查失败: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
    
    def check_git_status(self):
        """检查Git状态"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_conda_status(self):
        """检查Conda状态"""
        try:
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_python_env(self):
        """检查Python环境"""
        env_name = self.conda_env_var.get()
        if not env_name:
            return False
        
        try:
            result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
            return env_name in result.stdout
        except:
            return False
    
    def check_project_files(self):
        """检查项目文件"""
        # 从状态文件获取项目路径
        base_path = self.project_status.get_status("project_path")
        if not base_path:
            base_path = self.project_path_var.get()
        
        if not base_path or not os.path.exists(base_path):
            return False
        
        # 实际项目路径应该是 base_path/panda_factor
        project_path = os.path.join(base_path, "panda_factor")
        if not os.path.exists(project_path):
            return False
        
        # 检查关键文件
        server_path1 = os.path.join(project_path, "panda_factor_server", "panda_factor_server", "__main__.py")
        server_path2 = os.path.join(project_path, "panda_factor_server", "__main__.py")
        
        return os.path.exists(server_path1) or os.path.exists(server_path2)
    
    def check_mongodb_status(self):
        """检查MongoDB状态"""
        mongodb_path = self.project_status.get_status("mongodb_path")
        if not mongodb_path:
            mongodb_path = self.mongodb_path_var.get()
        
        if not mongodb_path or not os.path.exists(mongodb_path):
            return False
        
        # 检查MongoDB可执行文件
        mongod_path = os.path.join(mongodb_path, "bin", "mongod.exe")
        mongo_path = os.path.join(mongodb_path, "bin", "mongo.exe")
        mongosh_path = os.path.join(mongodb_path, "bin", "mongosh.exe")
        
        return os.path.exists(mongod_path) and (os.path.exists(mongo_path) or os.path.exists(mongosh_path))
    
    def update_status_ui(self, git_ok, conda_ok, python_ok, project_ok, mongodb_ok):
        """更新状态UI"""
        # 更新环境状态指示器
        self.git_status_label.config(text="✅ Git" if git_ok else "❌ Git", 
                                    style='Success.TLabel' if git_ok else 'Error.TLabel')
        
        self.conda_status_label.config(text="✅ Conda" if conda_ok else "❌ Conda",
                                     style='Success.TLabel' if conda_ok else 'Error.TLabel')
        
        self.python_status_label.config(text="✅ Python环境" if python_ok else "❌ Python环境",
                                      style='Success.TLabel' if python_ok else 'Error.TLabel')
        
        self.project_status_label.config(text="✅ 项目文件" if project_ok else "❌ 项目文件",
                                       style='Success.TLabel' if project_ok else 'Error.TLabel')
        
        self.mongodb_status_label.config(text="✅ MongoDB" if mongodb_ok else "❌ MongoDB",
                                       style='Success.TLabel' if mongodb_ok else 'Error.TLabel')
        
        # 更新启动按钮状态
        can_launch = all([git_ok, conda_ok, python_ok, project_ok, mongodb_ok])
        self.launch_button.config(state='normal' if can_launch else 'disabled')
    
    def check_git_updates(self):
        """检查Git更新"""
        project_path = self.project_path_var.get()
        if not project_path or not os.path.exists(project_path):
            messagebox.showerror("错误", "项目路径不存在")
            return
        
        self.log_deploy("检查Git更新...")
        
        def check_updates():
            try:
                # 获取远程更新
                result = subprocess.run(['git', 'fetch'], cwd=project_path, capture_output=True, text=True)
                if result.returncode != 0:
                    error_msg = f"获取远程更新失败: {result.stderr}"
                    self.root.after(0, lambda: self.log_deploy(error_msg))
                    return
                
                # 检查是否有更新
                result = subprocess.run(['git', 'status', '-uno'], cwd=project_path, capture_output=True, text=True)
                if "behind" in result.stdout:
                    self.root.after(0, lambda: self.log_deploy("发现新版本，可以更新"))
                    # 获取最新提交信息
                    result = subprocess.run(['git', 'log', 'HEAD..origin/main', '--oneline'], 
                                          cwd=project_path, capture_output=True, text=True)
                    if result.stdout:
                        update_content = f"更新内容:\n{result.stdout}"
                        self.root.after(0, lambda: self.log_deploy(update_content))
                else:
                    self.root.after(0, lambda: self.log_deploy("项目已是最新版本"))
                
                # 获取当前提交
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    commit = result.stdout.strip()
                    self.project_status.update_status(git_commit=commit)
                    
            except Exception as e:
                error_msg = f"检查更新失败: {str(e)}"
                self.root.after(0, lambda: self.log_deploy(error_msg))
        
        thread = threading.Thread(target=check_updates)
        thread.daemon = True
        thread.start()
    
    def start_deployment(self):
        """开始部署"""
        # 验证配置
        if not self.project_path_var.get():
            messagebox.showerror("错误", "请设置项目安装路径")
            return
        
        if not self.conda_env_var.get():
            messagebox.showerror("错误", "请设置Conda环境名称")
            return
        
        if not self.git_url_var.get():
            messagebox.showerror("错误", "请设置Git仓库地址")
            return
        
        # 保存配置
        self.project_status.update_status(
            project_path=self.project_path_var.get(),
            conda_env=self.conda_env_var.get(),
            git_url=self.git_url_var.get(),
            mongodb_path=self.mongodb_path_var.get(),
            deployment_status="in_progress"
        )
        
        # 禁用部署按钮
        for widget in self.deploy_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and "部署" in child.cget("text"):
                        child.config(state='disabled')
        
        # 在新线程中执行部署
        thread = threading.Thread(target=self.deploy_process)
        thread.daemon = True
        thread.start()
    
    def deploy_process(self):
        """部署过程"""
        try:
            self.log_deploy("🚀 开始部署PandaAI工具...")
            self.deploy_progress['value'] = 0
            
            # 获取配置
            project_path = self.project_path_var.get()
            env_name = self.conda_env_var.get()
            git_url = self.git_url_var.get()
            
            # 加载已完成步骤
            completed_steps = self.project_status.get_status("completed_steps")
            
            if completed_steps:
                self.log_deploy("🔄 检测到之前的部署进度，将继续之前的部署...")
                self.log_deploy(f"✅ 已完成步骤: {', '.join(completed_steps)}")
            
            # 步骤1: 检查环境
            if not self.is_step_completed("check_environment", completed_steps):
                self.log_deploy("📋 步骤1: 检查环境...")
                if not self.check_environment_v2():
                    self.log_deploy("❌ 环境检查失败，请先安装Git和Conda")
                    return
                completed_steps.append("check_environment")
                self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤1: 环境检查 (已完成)")
            self.deploy_progress['value'] = 15
            
            # 步骤2: 创建安装目录
            if not self.is_step_completed("create_directory", completed_steps):
                self.log_deploy("📋 步骤2: 创建安装目录...")
                os.makedirs(project_path, exist_ok=True)
                self.log_deploy(f"✅ 安装目录已创建: {project_path}")
                completed_steps.append("create_directory")
                self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤2: 创建安装目录 (已完成)")
            self.deploy_progress['value'] = 30
            
            # 步骤3: 克隆项目
            if not self.is_step_completed("clone_project", completed_steps):
                self.log_deploy("📋 步骤3: 下载PandaFactor项目...")
                panda_factor_path = os.path.join(project_path, "panda_factor")
                
                if os.path.exists(panda_factor_path):
                    self.log_deploy("⚠️ 项目目录已存在，将更新项目...")
                    if not self.run_command_v2("git pull", cwd=panda_factor_path):
                        self.log_deploy("❌ 项目更新失败")
                        return
                else:
                    clone_command = f'git clone "{git_url}" "{panda_factor_path}"'
                    if not self.run_command_v2(clone_command):
                        self.log_deploy("❌ 项目下载失败")
                        return
                
                completed_steps.append("clone_project")
                self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤3: 下载PandaFactor项目 (已完成)")
                panda_factor_path = os.path.join(project_path, "panda_factor")
            self.deploy_progress['value'] = 50
            
            # 步骤4: 创建或激活Conda环境
            if not self.is_step_completed("setup_conda_env", completed_steps):
                self.log_deploy("📋 步骤4: 配置Conda环境...")
                
                # 检查环境是否存在
                result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
                if env_name not in result.stdout:
                    self.log_deploy(f"🔧 创建Conda环境: {env_name}")
                    create_env_command = f'conda create -n {env_name} python=3.12 -y'
                    if not self.run_command_v2(create_env_command):
                        self.log_deploy("❌ 环境创建失败")
                        return
                else:
                    self.log_deploy(f"✅ Conda环境 '{env_name}' 已存在")
                
                completed_steps.append("setup_conda_env")
                self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤4: 配置Conda环境 (已完成)")
            self.deploy_progress['value'] = 65
            
            # 步骤5: 安装依赖
            if not self.is_step_completed("install_dependencies", completed_steps):
                self.log_deploy("📋 步骤5: 安装项目依赖...")
                requirements_path = os.path.join(panda_factor_path, "requirements.txt")
                
                if os.path.exists(requirements_path):
                    # 激活环境并安装依赖
                    if os.name == 'nt':  # Windows
                        activate_command = f'conda activate {env_name} && pip install -r "{requirements_path}" --ignore-installed'
                    else:  # Linux/Mac
                        activate_command = f'source activate {env_name} && pip install -r "{requirements_path}" --ignore-installed'
                    
                    if not self.run_command_v2(activate_command, cwd=panda_factor_path):
                        self.log_deploy("⚠️ 部分依赖安装失败，但继续部署...")
                        self.log_deploy("💡 提示: 你可以稍后手动安装缺失的依赖包")
                    
                    # 安装所有子模块为可编辑包（按照官方文档的正确方式）
                    self.log_deploy("🔧 安装项目子模块为可编辑包...")
                    submodules = [
                        "./panda_common",
                        "./panda_factor", 
                        "./panda_data",
                        "./panda_data_hub",
                        "./panda_llm",
                        "./panda_factor_server"
                    ]
                    
                    # 检查子模块是否存在
                    existing_submodules = []
                    for submodule in submodules:
                        submodule_path = os.path.join(panda_factor_path, submodule.replace("./", ""))
                        if os.path.exists(submodule_path):
                            existing_submodules.append(submodule)
                            self.log_deploy(f"✅ 找到子模块: {submodule}")
                        else:
                            self.log_deploy(f"⚠️ 子模块目录不存在: {submodule}")
                    
                    if existing_submodules:
                        # 使用官方文档推荐的安装方式：一次性安装所有子模块
                        submodules_str = " ".join(existing_submodules)
                        self.log_deploy(f"📦 安装子模块: {submodules_str}")
                        
                        if os.name == 'nt':  # Windows
                            install_command = f'conda activate {env_name} && pip install -e {submodules_str}'
                        else:  # Linux/Mac
                            install_command = f'source activate {env_name} && pip install -e {submodules_str}'
                        
                        if not self.run_command_v2(install_command, cwd=panda_factor_path):
                            self.log_deploy("⚠️ 部分子模块安装失败，但继续部署...")
                            self.log_deploy("💡 这可能导致模块导入问题，可以手动执行安装")
                    else:
                        self.log_deploy("⚠️ 未找到任何子模块目录")
                    
                    completed_steps.append("install_dependencies")
                    self.update_completed_steps(completed_steps)
                else:
                    self.log_deploy("⚠️ 未找到requirements.txt文件")
                    completed_steps.append("install_dependencies")
                    self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤5: 安装项目依赖 (已完成)")
            self.deploy_progress['value'] = 70
            
            # 步骤6: 部署QuantFlow
            if not self.is_step_completed("deploy_quantflow", completed_steps):
                self.log_deploy("📋 步骤6: 部署PandaQuantFlow...")
                
                # 保存quantflow git url
                quantflow_git_url = self.quantflow_git_url_var.get()
                if quantflow_git_url:
                    self.project_status.update_status(quantflow_git_url=quantflow_git_url)
                    
                    # 克隆或更新quantflow
                    quantflow_path = os.path.join(project_path, "panda_quantflow")
                    
                    if os.path.exists(quantflow_path):
                        self.log_deploy("🔄 更新QuantFlow仓库...")
                        git_pull_command = "git pull"
                        if not self.run_command_v2(git_pull_command, cwd=quantflow_path):
                            self.log_deploy("⚠️ QuantFlow更新失败，但继续部署...")
                    else:
                        self.log_deploy("📥 克隆QuantFlow仓库...")
                        git_clone_command = f'git clone "{quantflow_git_url}" panda_quantflow'
                        if not self.run_command_v2(git_clone_command, cwd=project_path):
                            self.log_deploy("❌ QuantFlow克隆失败")
                            raise Exception("QuantFlow克隆失败")
                    
                    # 安装quantflow
                    if os.path.exists(quantflow_path):
                        self.log_deploy("🔧 安装QuantFlow...")
                        if os.name == 'nt':  # Windows
                            quantflow_install_command = f'conda activate {env_name} && pip install -e .'
                        else:  # Linux/Mac
                            quantflow_install_command = f'source activate {env_name} && pip install -e .'
                        
                        if not self.run_command_v2(quantflow_install_command, cwd=quantflow_path):
                            self.log_deploy("⚠️ QuantFlow安装失败，但继续部署...")
                            self.log_deploy("💡 你可以稍后手动安装: pip install -e .")
                        else:
                            self.log_deploy("✅ QuantFlow安装完成")
                    
                    completed_steps.append("deploy_quantflow")
                    self.update_completed_steps(completed_steps)
                else:
                    self.log_deploy("⚠️ 跳过QuantFlow部署（未配置Git地址）")
                    completed_steps.append("deploy_quantflow")
                    self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤6: 部署PandaQuantFlow (已完成)")
            self.deploy_progress['value'] = 85
            
            # 步骤7: 完成部署
            if not self.is_step_completed("create_scripts", completed_steps):
                self.log_deploy("📋 步骤7: 完成部署配置...")
                
                # 创建启动脚本
                self.create_startup_scripts_v2(project_path, panda_factor_path, env_name)
                
                completed_steps.append("create_scripts")
                self.update_completed_steps(completed_steps)
            else:
                self.log_deploy("✅ 步骤7: 完成部署配置 (已完成)")
            
            self.deploy_progress['value'] = 100
            
            # 部署完成
            self.project_status.update_status(
                deployment_status="completed",
                last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                completed_steps=completed_steps
            )
            
            # 获取Git提交信息
            try:
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                      cwd=panda_factor_path, capture_output=True, text=True)
                if result.returncode == 0:
                    self.project_status.update_status(git_commit=result.stdout.strip())
            except:
                pass
            
            self.log_deploy("🎉 部署完成！")
            self.log_deploy(f"📁 项目位置: {panda_factor_path}")
            self.log_deploy(f"🐍 Conda环境: {env_name}")
            self.log_deploy("")
            self.log_deploy("🚀 快速开始:")
            self.log_deploy("1. 切换到 '🚀 项目启动' 页面")
            self.log_deploy("2. 点击 '🚀 启动项目' 按钮即可启动服务器")
            self.log_deploy("3. 系统会自动打开浏览器访问项目界面")
            
            # 更新UI
            self.root.after(0, self.create_status_indicators)
            self.root.after(0, self.create_project_info)
            
            messagebox.showinfo("部署完成", f"PandaAI工具部署成功！\n\n项目位置: {panda_factor_path}\nConda环境: {env_name}")
            
        except Exception as e:
            self.log_deploy(f"❌ 部署过程中出现错误: {str(e)}")
            self.project_status.update_status(deployment_status="failed")
            messagebox.showerror("部署失败", f"部署过程中出现错误:\n{str(e)}")
        
        finally:
            # 重新启用部署按钮
            self.root.after(0, self.enable_deploy_button)
    
    def launch_project(self):
        """启动项目"""
        # 从状态文件读取配置
        project_path = self.project_status.get_status("project_path")
        env_name = self.project_status.get_status("conda_env")
        
        # 如果状态文件中没有配置，尝试从界面获取
        if not project_path:
            project_path = self.project_path_var.get()
        if not env_name:
            env_name = self.conda_env_var.get()
        
        if not project_path or not env_name:
            messagebox.showerror("错误", "请先在部署页面完成项目配置")
            # 自动切换到部署页面
            self.notebook.select(0)
            return
        
        # 检查部署状态
        deployment_status = self.project_status.get_status("deployment_status")
        if deployment_status != "completed":
            if messagebox.askyesno("部署未完成", "项目尚未完成部署，是否切换到部署页面？"):
                self.notebook.select(0)
            return
        
        self.log_launch("启动项目...")
        
        def launch():
            try:
                # 项目实际路径
                panda_factor_path = os.path.join(project_path, "panda_factor")
                panda_quantflow_path = os.path.join(project_path, "panda_quantflow")
                mongodb_path = self.project_status.get_status("mongodb_path")
                
                # 检查MongoDB路径
                if not mongodb_path or not os.path.exists(mongodb_path):
                    self.root.after(0, lambda: self.log_launch("❌ MongoDB路径未配置或不存在"))
                    return
                
                # 检查Factor服务器文件
                server_path1 = os.path.join(panda_factor_path, "panda_factor_server", "panda_factor_server", "__main__.py")
                server_path2 = os.path.join(panda_factor_path, "panda_factor_server", "__main__.py")
                
                if os.path.exists(server_path1):
                    start_factor_command = "python ./panda_factor_server/panda_factor_server/__main__.py"
                    self.root.after(0, lambda: self.log_launch(f"✅ 找到Factor服务器文件: {server_path1}"))
                elif os.path.exists(server_path2):
                    start_factor_command = "python ./panda_factor_server/__main__.py"
                    self.root.after(0, lambda: self.log_launch(f"✅ 找到Factor服务器文件: {server_path2}"))
                else:
                    self.root.after(0, lambda: self.log_launch("❌ Factor服务器启动文件不存在"))
                    self.root.after(0, lambda: self.log_launch(f"检查路径1: {server_path1}"))
                    self.root.after(0, lambda: self.log_launch(f"检查路径2: {server_path2}"))
                    return

                # 检查QuantFlow服务器文件
                quantflow_main_path = os.path.join(panda_quantflow_path, "src", "panda_server", "main.py")
                if os.path.exists(quantflow_main_path):
                    start_quantflow_command = "python src/panda_server/main.py"
                    self.root.after(0, lambda: self.log_launch(f"✅ 找到QuantFlow服务器文件: {quantflow_main_path}"))
                else:
                    start_quantflow_command = None
                    self.root.after(0, lambda: self.log_launch("⚠️ 未找到QuantFlow服务器启动文件，跳过QuantFlow启动"))
                    self.root.after(0, lambda: self.log_launch(f"检查路径: {quantflow_main_path}"))

                # 创建启动脚本
                temp_script = os.path.join(project_path, "temp_launch.bat")
                
                script_content = f"""@echo off
chcp 65001 >nul
title PandaAI Factor Server
echo 启动PandaAI Factor服务器...
echo Factor路径: {panda_factor_path}
echo QuantFlow路径: {panda_quantflow_path}
echo MongoDB路径: {mongodb_path}
echo Conda环境: {env_name}
echo.

echo ========================================
echo 步骤1: 启动MongoDB数据库
echo ========================================
cd /d "{mongodb_path}"
echo 创建数据目录...
if not exist "data\\db" mkdir data\\db
if not exist "conf" mkdir conf
echo 启动MongoDB副本集...
start "MongoDB Server" bin\\mongod.exe --replSet rs0 --dbpath data\\db --keyFile conf\\mongo.key --port 27017 --quiet --auth
echo MongoDB启动命令已执行
echo 等待MongoDB初始化...
timeout /t 5 /nobreak >nul
echo.

echo ========================================
echo 步骤2: 启动PandaFactor服务器
echo ========================================
cd /d "{panda_factor_path}"
REM 直接用start启动cmd窗口并执行命令
call conda activate {env_name}
if errorlevel 1 (
    echo 激活Conda环境失败，请检查环境名称是否正确: {env_name}
    pause
    exit /b 1
)
set PYTHONPATH=%CD%;%CD%\panda_factor_server;%CD%\panda_common;%CD%\panda_data;%CD%\panda_data_hub;%CD%\panda_factor;%CD%\panda_llm;%PYTHONPATH%
echo 启动PandaFactor服务器 (后台运行)...
start "PandaFactor Server" cmd /c "{start_factor_command} & pause"
if errorlevel 1 (
    echo 启动PandaFactor服务器时发生错误，可能是Python环境或路径问题。
    echo 请检查Conda环境和PYTHONPATH设置。
    pause
    exit /b 1
)
echo PandaFactor服务器启动命令已执行
echo 等待服务器初始化...
timeout /t 5 /nobreak >nul
echo.

echo ========================================
echo 步骤3: 启动QuantFlow服务器
echo ========================================
cd /d "{project_path}"
cd /d "{panda_quantflow_path}"
REM 直接用start启动cmd窗口并执行命令
call conda activate {env_name}
if errorlevel 1 (
    echo 激活Conda环境失败，请检查环境名称是否正确: {env_name}
    pause
    exit /b 1
)
set PYTHONPATH=%CD%;%CD%\panda_factor_server;%CD%\panda_common;%CD%\panda_data;%CD%\panda_data_hub;%CD%\panda_factor;%CD%\panda_llm;%PYTHONPATH%
echo 启动QuantFlow服务器 (后台运行)...
start "QuantFlow Server" cmd /c "{start_quantflow_command} & pause"
if errorlevel 1 (
    echo 启动QuantFlow服务器时发生错误，可能是Python环境或路径问题。
    echo 请检查Conda环境和PYTHONPATH设置。
    pause
    exit /b 1
)
timeout /t 10 /nobreak >nul
echo 如需停止所有服务，请使用工具的"停止项目"按钮

REM 启动浏览器访问QuantFlow页面
start "" "http://127.0.0.1:8000/quantflow/"

pause
"""
                
                with open(temp_script, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                # 启动服务器
                subprocess.Popen(f'start "PandaAI Server" "{temp_script}"', shell=True)
                
                self.root.after(0, lambda: self.log_launch("✅ 服务器启动命令已执行"))
                self.root.after(0, lambda: self.server_status_var.set("启动中..."))
                
                # 延迟打开浏览器
                # self.root.after(5000, self.open_browser)
                
            except Exception as e:
                error_msg = f"❌ 启动失败: {str(e)}"
                self.root.after(0, lambda: self.log_launch(error_msg))
        
        thread = threading.Thread(target=launch)
        thread.daemon = True
        thread.start()
    
    def stop_project(self):
        """停止项目"""
        self.log_launch("正在停止项目...")
        
        def stop():
            try:
                # 停止MongoDB进程
                self.log_launch("正在停止MongoDB服务...")
                result = subprocess.run(['taskkill', '/f', '/im', 'mongod.exe'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.root.after(0, lambda: self.log_launch("✅ MongoDB服务已停止"))
                else:
                    self.root.after(0, lambda: self.log_launch("⚠️ 未找到运行中的MongoDB服务"))
                
                # 停止所有Python进程（PandaFactor和QuantFlow）
                self.log_launch("正在停止PandaFactor和QuantFlow服务...")
                result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.root.after(0, lambda: self.log_launch("✅ PandaFactor和QuantFlow服务已停止"))
                else:
                    self.root.after(0, lambda: self.log_launch("⚠️ 未找到运行中的Python服务"))
                
                self.root.after(0, lambda: self.server_status_var.set("已停止"))
                self.root.after(0, lambda: self.log_launch("🎉 项目停止完成"))
                
            except Exception as e:
                error_msg = f"❌ 停止项目时出错: {str(e)}"
                self.root.after(0, lambda: self.log_launch(error_msg))
        
        thread = threading.Thread(target=stop)
        thread.daemon = True
        thread.start()
    
    def open_browser(self):
        """打开浏览器"""
        # 优先打开Factor服务器，然后尝试QuantFlow
        urls = [
            "http://localhost:8111",  # Factor服务器
            "http://127.0.0.1:8111",  # Factor服务器
            "http://localhost:8000",  # QuantFlow服务器
            "http://127.0.0.1:8000"   # QuantFlow服务器
        ]
        
        for url in urls:
            try:
                webbrowser.open(url)
                if "8111" in url:
                    self.log_launch(f"✅ 已打开Factor服务器: {url}")
                else:
                    self.log_launch(f"✅ 已打开QuantFlow服务器: {url}")
                break
            except:
                continue
        else:
            self.log_launch("⚠️ 无法自动打开浏览器")
    
    def open_data_update(self):
        """打开数据更新页面"""
        url = "http://localhost:8111/factor/#/datahubdataclean"
        try:
            webbrowser.open(url)
            self.log_operations(f"✅ 已打开数据更新页面: {url}")
            self.log_operations("📊 在此页面可以管理和更新数据源")
        except Exception as e:
            self.log_operations(f"❌ 打开数据更新页面失败: {str(e)}")
            messagebox.showerror("错误", f"无法打开浏览器\n{url}\n\n请手动复制链接到浏览器打开")
    
    def open_data_list(self):
        """打开数据列表页面"""
        url = "http://localhost:8111/factor/#/datahublist"
        try:
            webbrowser.open(url)
            self.log_operations(f"✅ 已打开数据列表页面: {url}")
            self.log_operations("📋 在此页面可以查看系统中的所有数据列表")
        except Exception as e:
            self.log_operations(f"❌ 打开数据列表页面失败: {str(e)}")
            messagebox.showerror("错误", f"无法打开浏览器\n{url}\n\n请手动复制链接到浏览器打开")
    
    def open_charts(self):
        """打开QuantFlow超级图表页面"""
        url = "http://127.0.0.1:8000/charts/"
        try:
            webbrowser.open(url)
            self.log_operations(f"✅ 已打开超级图表页面: {url}")
            self.log_operations("📈 在此页面可以使用QuantFlow的超级图表功能")
        except Exception as e:
            self.log_operations(f"❌ 打开超级图表页面失败: {str(e)}")
            messagebox.showerror("错误", f"无法打开浏览器\n{url}\n\n请手动复制链接到浏览器打开")
    
    def open_quantflow(self):
        """打开QuantFlow工作流页面"""
        url = "http://127.0.0.1:8000/quantflow/"
        try:
            webbrowser.open(url)
            self.log_operations(f"✅ 已打开工作流页面: {url}")
            self.log_operations("🔗 在此页面可以创建和管理QuantFlow工作流")
        except Exception as e:
            self.log_operations(f"❌ 打开工作流页面失败: {str(e)}")
            messagebox.showerror("错误", f"无法打开浏览器\n{url}\n\n请手动复制链接到浏览器打开")
    
    def check_server_status(self):
        """检查服务器状态"""
        def check():
            try:
                import urllib.request
                import socket
                
                # 检查端口是否开放
                self.root.after(0, lambda: self.log_operations("🔍 正在检查服务器状态..."))
                
                # 设置超时
                socket.setdefaulttimeout(3)
                
                # 尝试连接服务器
                url = "http://localhost:8111"
                try:
                    response = urllib.request.urlopen(url)
                    if response.getcode() == 200:
                        self.root.after(0, lambda: self.server_url_status.set("✅ 服务器运行正常 (localhost:8111)"))
                        self.root.after(0, lambda: self.server_url_label.configure(foreground='green'))
                        self.root.after(0, lambda: self.log_operations("✅ 服务器状态：运行正常"))
                    else:
                        self.root.after(0, lambda: self.server_url_status.set("⚠️ 服务器响应异常"))
                        self.root.after(0, lambda: self.server_url_label.configure(foreground='orange'))
                        self.root.after(0, lambda: self.log_operations("⚠️ 服务器响应异常"))
                except urllib.error.URLError:
                    self.root.after(0, lambda: self.server_url_status.set("❌ 服务器未启动 (localhost:8111)"))
                    self.root.after(0, lambda: self.server_url_label.configure(foreground='red'))
                    self.root.after(0, lambda: self.log_operations("❌ 服务器未启动，请先在启动页面启动项目"))
                except Exception as e:
                    error_msg = f"❌ 检查服务器状态失败: {str(e)}"
                    self.root.after(0, lambda: self.server_url_status.set("❌ 连接失败"))
                    self.root.after(0, lambda: self.server_url_label.configure(foreground='red'))
                    self.root.after(0, lambda: self.log_operations(error_msg))
                    
            except Exception as e:
                outer_error_msg = f"❌ 检查服务器状态时出错: {str(e)}"
                self.root.after(0, lambda: self.server_url_status.set("❌ 检查失败"))
                self.root.after(0, lambda: self.server_url_label.configure(foreground='red'))
                self.root.after(0, lambda: self.log_operations(outer_error_msg))
        
        # 在后台线程中检查
        threading.Thread(target=check, daemon=True).start()
    
    def log_operations(self, message):
        """记录操作日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'operations_log'):
            self.operations_log.insert(tk.END, log_message)
            self.operations_log.see(tk.END)
    
    def clear_status(self):
        """清除状态"""
        if messagebox.askyesno("确认", "确定要清除所有状态记录吗？"):
            self.project_status.status = self.project_status.default_status.copy()
            self.project_status.save_status()
            self.create_status_indicators()
            self.create_project_info()
            self.log_deploy("状态已清除")
    
    def get_deployment_status_text(self):
        """获取部署状态文本"""
        status = self.project_status.get_status("deployment_status")
        status_map = {
            "not_started": "未开始",
            "in_progress": "部署中",
            "completed": "部署完成",
            "failed": "部署失败"
        }
        return status_map.get(status, "未知")
    
    def is_step_completed(self, step_name, completed_steps):
        """检查步骤是否已完成"""
        return step_name in completed_steps
    
    def update_completed_steps(self, completed_steps):
        """更新已完成步骤"""
        self.project_status.update_status(completed_steps=completed_steps)
        # 更新UI显示
        self.root.after(0, self.create_status_indicators)
    
    def check_environment_v2(self):
        """检查环境状态"""
        self.log_deploy("🔍 检查环境状态...")
        
        # 检查Git
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log_deploy(f"✅ Git已安装: {result.stdout.strip()}")
            else:
                self.log_deploy("❌ Git未安装或不在PATH中")
                return False
        except:
            self.log_deploy("❌ Git未安装或不在PATH中")
            return False
        
        # 检查Conda
        try:
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log_deploy(f"✅ Conda已安装: {result.stdout.strip()}")
            else:
                self.log_deploy("❌ Conda未安装或不在PATH中")
                return False
        except:
            self.log_deploy("❌ Conda未安装或不在PATH中")
            return False
        
        return True
    
    def run_command_v2(self, command, cwd=None):
        """执行命令并实时显示输出"""
        try:
            self.log_deploy(f"执行命令: {command}")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=cwd,
                encoding='utf-8',
                errors='replace'
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_deploy(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                self.log_deploy("✅ 命令执行成功")
                return True
            else:
                self.log_deploy(f"❌ 命令执行失败，返回码: {return_code}")
                return False
                
        except Exception as e:
            self.log_deploy(f"❌ 执行命令时出错: {str(e)}")
            return False
    
    def create_startup_scripts_v2(self, install_path, project_path, env_name):
        """创建启动脚本"""
        try:
            # Windows批处理脚本 - 交互式终端
            bat_content = f"""@echo off
chcp 65001 >nul
echo 启动PandaAI工具...
cd /d "{project_path}"
call conda activate {env_name}
echo 环境已激活: {env_name}
echo 项目目录: {project_path}
echo.
echo 正在设置Python路径...
set PYTHONPATH=%CD%;%CD%\\panda_factor_server;%CD%\\panda_common;%CD%\\panda_data;%CD%\\panda_data_hub;%CD%\\panda_factor;%CD%\\panda_llm;%PYTHONPATH%
echo 环境准备完成，所有子模块已在部署阶段安装
echo.
echo 你现在可以运行项目中的脚本了！
echo 例如: python ./panda_factor_server/panda_factor_server/__main__.py
echo.
cmd /k
"""
            
            bat_path = os.path.join(install_path, "启动PandaAI.bat")
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.log_deploy(f"✅ 已创建启动脚本: {bat_path}")
            
            # 创建直接启动服务器的脚本
            mongodb_path = self.project_status.get_status("mongodb_path")
            if mongodb_path:
                server_bat_content = f"""@echo off
chcp 65001 >nul
title PandaAI Factor Server
echo 启动PandaAI Factor服务器...
echo 项目路径: {project_path}
echo MongoDB路径: {mongodb_path}
echo.

echo ========================================
echo 步骤1: 启动MongoDB数据库
echo ========================================
cd /d "{mongodb_path}"
echo 创建数据目录...
if not exist "data\\db" mkdir data\\db
if not exist "conf" mkdir conf
echo 启动MongoDB副本集...
start "MongoDB Server" bin\\mongod.exe --replSet rs0 --dbpath data\\db --keyFile conf\\mongo.key --port 27017 --quiet --auth
echo MongoDB启动命令已执行
echo 等待MongoDB初始化...
timeout /t 5 /nobreak >nul
echo.

echo ========================================
echo 步骤2: 启动PandaFactor服务器
echo ========================================
cd /d "{project_path}"
call conda activate {env_name}
if errorlevel 1 (
    echo 激活Conda环境失败，请检查环境名称是否正确: {env_name}
    pause
    exit /b 1
)
echo 环境已激活
echo 正在设置Python路径...
set PYTHONPATH=%CD%;%CD%\\panda_factor_server;%CD%\\panda_common;%CD%\\panda_data;%CD%\\panda_data_hub;%CD%\\panda_factor;%CD%\\panda_llm;%PYTHONPATH%
echo 启动PandaFactor服务器 (后台运行)...
start "PandaFactor Server" cmd /c "call conda activate {env_name} && python ./panda_factor_server/panda_factor_server/__main__.py && pause"
echo PandaFactor服务器启动命令已执行
echo 等待服务器初始化...
timeout /t 3 /nobreak >nul
echo.

echo ========================================
echo 步骤3: 启动QuantFlow服务器
echo ========================================
cd /d "{install_path}"
if exist panda_quantflow (
    cd panda_quantflow
    echo 启动QuantFlow服务器 (后台运行)...
    start "QuantFlow Server" cmd /c "call conda activate {env_name} && python src/panda_server/main.py && pause"
    echo QuantFlow服务器启动命令已执行
    echo.
    echo ========================================
    echo 所有服务启动完成
    echo ========================================
    echo Factor服务器: http://localhost:8111
    echo QuantFlow服务器: http://localhost:8000
    echo MongoDB数据库: localhost:27017
    echo.
    echo 提示: 
    echo - 所有服务都在后台运行
    echo - 关闭此窗口不会停止服务
    echo - 使用工具的停止项目按钮来停止所有服务
    echo.
) else (
    echo 未找到QuantFlow目录，跳过QuantFlow启动
    echo 如需使用QuantFlow，请在部署页面重新部署项目
    echo.
)
echo 注意: 所有服务可能仍在后台运行
echo 如需停止所有服务，请使用工具的"停止项目"按钮
pause
"""
            else:
                server_bat_content = f"""@echo off
chcp 65001 >nul
title PandaAI Factor Server
echo 启动PandaAI Factor服务器...
echo 警告: MongoDB路径未配置，跳过MongoDB启动
echo.
cd /d "{project_path}"
call conda activate {env_name}
if errorlevel 1 (
    echo 激活Conda环境失败，请检查环境名称是否正确: {env_name}
    pause
    exit /b 1
)
echo 环境已激活
echo 正在设置Python路径...
set PYTHONPATH=%CD%;%CD%\\panda_factor_server;%CD%\\panda_common;%CD%\\panda_data;%CD%\\panda_data_hub;%CD%\\panda_factor;%CD%\\panda_llm;%PYTHONPATH%
echo 启动PandaFactor服务器 (后台运行)...
start "PandaFactor Server" cmd /c "call conda activate {env_name} && python ./panda_factor_server/panda_factor_server/__main__.py && pause"
echo PandaFactor服务器启动命令已执行
echo 等待服务器初始化...
timeout /t 3 /nobreak >nul
echo.

echo ========================================
echo 启动QuantFlow服务器
echo ========================================
cd /d "{install_path}"
if exist panda_quantflow (
    cd panda_quantflow
    echo 启动QuantFlow服务器 (后台运行)...
    start "QuantFlow Server" cmd /c "call conda activate {env_name} && python src/panda_server/main.py && pause"
    echo QuantFlow服务器启动命令已执行
    echo.
    echo ========================================
    echo 所有服务启动完成
    echo ========================================
    echo Factor服务器: http://localhost:8111
    echo QuantFlow服务器: http://localhost:8000
    echo MongoDB数据库: 未配置
    echo.
    echo 提示: 
    echo - 所有服务都在后台运行
    echo - MongoDB未配置，部分功能可能受限
    echo - 使用工具的停止项目按钮来停止所有服务
    echo.
) else (
    echo 未找到QuantFlow目录，跳过QuantFlow启动
    echo 如需使用QuantFlow，请在部署页面重新部署项目
    echo.
)
pause
"""
            
            server_bat_path = os.path.join(install_path, "启动PandaAI服务器.bat")
            with open(server_bat_path, 'w', encoding='utf-8') as f:
                f.write(server_bat_content)
            
            self.log_deploy(f"✅ 已创建服务器启动脚本: {server_bat_path}")
            
        except Exception as e:
            self.log_deploy(f"⚠️ 创建启动脚本失败: {str(e)}")
    
    def enable_deploy_button(self):
        """重新启用部署按钮"""
        for widget in self.deploy_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and "部署" in child.cget("text"):
                        child.config(state='normal')

def main():
    """主函数"""
    root = tk.Tk()
    app = PandaDeployToolV2(root)
    
    # 设置窗口居中
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()
