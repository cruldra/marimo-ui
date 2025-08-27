#!/usr/bin/env python3
"""
Marimo GUI - 基于PySide6的marimo命令行工具图形界面
"""

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class CommandRunner(QObject):
    """在后台线程中运行命令"""
    finished = Signal(str)
    error = Signal(str)
    process_started = Signal(object)  # 发送进程对象

    def __init__(self, command, working_dir=None):
        super().__init__()
        self.command = command
        self.working_dir = working_dir or Path.cwd()
        self.process = None

    def run(self):
        try:
            # 对于marimo命令，使用Popen以便可以终止进程
            if "marimo" in self.command and any(cmd in self.command for cmd in ["edit", "run", "new", "tutorial"]):
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.working_dir
                )
                self.process_started.emit(self.process)
                stdout, stderr = self.process.communicate()

                if self.process.returncode == 0:
                    self.finished.emit(stdout)
                else:
                    self.error.emit(stderr or stdout)
            else:
                # 对于其他命令，使用原来的方式
                result = subprocess.run(
                    self.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.working_dir
                )
                if result.returncode == 0:
                    self.finished.emit(result.stdout)
                else:
                    self.error.emit(result.stderr or result.stdout)
        except Exception as e:
            self.error.emit(str(e))


class BaseTab(QWidget):
    """基础标签页类"""
    process_started = Signal(object)  # 发送进程对象到主窗口

    def __init__(self, working_dir=None):
        super().__init__()
        self.working_dir = working_dir or Path.cwd()
        self.layout = QVBoxLayout(self)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        
    def add_output_section(self):
        """添加输出区域"""
        output_group = QGroupBox("命令输出")
        output_layout = QVBoxLayout()
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        self.layout.addWidget(output_group)
        
    def run_command(self, command):
        """运行命令并显示输出"""
        self.output_text.clear()
        self.output_text.append(f"工作目录: {self.working_dir}")
        self.output_text.append(f"执行命令: {command}\n")

        self.thread = QThread()
        self.runner = CommandRunner(command, self.working_dir)
        self.runner.moveToThread(self.thread)

        self.thread.started.connect(self.runner.run)
        self.runner.finished.connect(self.on_command_finished)
        self.runner.error.connect(self.on_command_error)
        self.runner.process_started.connect(self.process_started.emit)  # 转发进程信号
        self.runner.finished.connect(self.thread.quit)
        self.runner.error.connect(self.thread.quit)

        self.thread.start()
    
    def on_command_finished(self, output):
        self.output_text.append("执行成功:")
        self.output_text.append(output)

    def on_command_error(self, error):
        self.output_text.append("执行错误:")
        self.output_text.append(error)


class EditTab(BaseTab):
    """编辑标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()
        
    def init_ui(self):
        # 文件选择
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("notebook.py (可选)")
        file_browse_btn = QPushButton("浏览...")
        file_browse_btn.clicked.connect(self.browse_file)
        
        file_row = QHBoxLayout()
        file_row.addWidget(self.file_input)
        file_row.addWidget(file_browse_btn)
        file_layout.addRow("笔记本文件:", file_row)
        file_group.setLayout(file_layout)
        
        # 服务器设置
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(2718)
        server_layout.addRow("端口:", self.port_input)
        
        self.host_input = QLineEdit("127.0.0.1")
        server_layout.addRow("主机:", self.host_input)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("反向代理地址 (可选)")
        server_layout.addRow("代理:", self.proxy_input)
        
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("基础URL (可选)")
        server_layout.addRow("基础URL:", self.base_url_input)
        
        server_group.setLayout(server_layout)
        
        # 选项设置
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout()
        
        self.headless_check = QCheckBox("无头模式 (不启动浏览器)")
        self.token_check = QCheckBox("使用令牌认证")
        self.token_check.setChecked(True)
        self.sandbox_check = QCheckBox("沙盒模式")
        self.watch_check = QCheckBox("监视文件变化")
        self.skip_update_check = QCheckBox("跳过更新检查")
        
        options_layout.addWidget(self.headless_check)
        options_layout.addWidget(self.token_check)
        options_layout.addWidget(self.sandbox_check)
        options_layout.addWidget(self.watch_check)
        options_layout.addWidget(self.skip_update_check)
        options_group.setLayout(options_layout)
        
        # 令牌密码
        self.token_password_input = QLineEdit()
        self.token_password_input.setPlaceholderText("令牌密码 (可选)")
        self.token_password_input.setEchoMode(QLineEdit.Password)
        
        # 运行按钮
        run_btn = QPushButton("启动编辑器")
        run_btn.clicked.connect(self.run_edit)
        
        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(file_group)
        scroll_layout.addWidget(server_group)
        scroll_layout.addWidget(options_group)
        scroll_layout.addWidget(QLabel("令牌密码:"))
        scroll_layout.addWidget(self.token_password_input)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        self.layout.addWidget(scroll)
        self.add_output_section()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择笔记本文件", str(self.working_dir), "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.file_input.setText(file_path)
    
    def run_edit(self):
        command = "uv run marimo edit"
        
        if self.file_input.text().strip():
            command += f' "{self.file_input.text().strip()}"'
        
        command += f" --port {self.port_input.value()}"
        command += f" --host {self.host_input.text()}"
        
        if self.proxy_input.text().strip():
            command += f' --proxy "{self.proxy_input.text().strip()}"'
        
        if self.base_url_input.text().strip():
            command += f' --base-url "{self.base_url_input.text().strip()}"'
        
        if self.headless_check.isChecked():
            command += " --headless"
        
        if self.token_check.isChecked():
            command += " --token"
            if self.token_password_input.text().strip():
                command += f' --token-password "{self.token_password_input.text().strip()}"'
        else:
            command += " --no-token"
        
        if self.sandbox_check.isChecked():
            command += " --sandbox"
        
        if self.watch_check.isChecked():
            command += " --watch"
        
        if self.skip_update_check.isChecked():
            command += " --skip-update-check"
        
        self.run_command(command)


class RunTab(BaseTab):
    """运行标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()
        
    def init_ui(self):
        # 文件选择
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("notebook.py (必需)")
        file_browse_btn = QPushButton("浏览...")
        file_browse_btn.clicked.connect(self.browse_file)
        
        file_row = QHBoxLayout()
        file_row.addWidget(self.file_input)
        file_row.addWidget(file_browse_btn)
        file_layout.addRow("笔记本文件:", file_row)
        file_group.setLayout(file_layout)
        
        # 服务器设置
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(2718)
        server_layout.addRow("端口:", self.port_input)
        
        self.host_input = QLineEdit("127.0.0.1")
        server_layout.addRow("主机:", self.host_input)
        
        self.session_ttl_input = QSpinBox()
        self.session_ttl_input.setRange(1, 3600)
        self.session_ttl_input.setValue(120)
        server_layout.addRow("会话超时(秒):", self.session_ttl_input)
        
        server_group.setLayout(server_layout)
        
        # 选项设置
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout()
        
        self.headless_check = QCheckBox("无头模式")
        self.include_code_check = QCheckBox("包含代码")
        self.watch_check = QCheckBox("监视文件变化")
        self.sandbox_check = QCheckBox("沙盒模式")
        self.redirect_console_check = QCheckBox("重定向控制台到浏览器")
        
        options_layout.addWidget(self.headless_check)
        options_layout.addWidget(self.include_code_check)
        options_layout.addWidget(self.watch_check)
        options_layout.addWidget(self.sandbox_check)
        options_layout.addWidget(self.redirect_console_check)
        options_group.setLayout(options_layout)
        
        # 运行按钮
        run_btn = QPushButton("运行应用")
        run_btn.clicked.connect(self.run_app)
        
        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(file_group)
        scroll_layout.addWidget(server_group)
        scroll_layout.addWidget(options_group)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        self.layout.addWidget(scroll)
        self.add_output_section()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择笔记本文件", str(self.working_dir), "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.file_input.setText(file_path)
    
    def run_app(self):
        if not self.file_input.text().strip():
            QMessageBox.warning(self, "警告", "请选择要运行的笔记本文件")
            return
        
        command = f'uv run marimo run "{self.file_input.text().strip()}"'
        command += f" --port {self.port_input.value()}"
        command += f" --host {self.host_input.text()}"
        command += f" --session-ttl {self.session_ttl_input.value()}"
        
        if self.headless_check.isChecked():
            command += " --headless"
        
        if self.include_code_check.isChecked():
            command += " --include-code"
        
        if self.watch_check.isChecked():
            command += " --watch"
        
        if self.sandbox_check.isChecked():
            command += " --sandbox"
        
        if self.redirect_console_check.isChecked():
            command += " --redirect-console-to-browser"
        
        self.run_command(command)


class ConvertTab(BaseTab):
    """转换标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()

    def init_ui(self):
        # 文件选择
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()

        self.input_file = QLineEdit()
        self.input_file.setPlaceholderText("选择要转换的文件 (.ipynb, .md, .py)")
        input_browse_btn = QPushButton("浏览...")
        input_browse_btn.clicked.connect(self.browse_input_file)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_file)
        input_row.addWidget(input_browse_btn)
        file_layout.addRow("输入文件:", input_row)

        self.output_file = QLineEdit()
        self.output_file.setPlaceholderText("输出文件路径 (可选)")
        output_browse_btn = QPushButton("浏览...")
        output_browse_btn.clicked.connect(self.browse_output_file)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_file)
        output_row.addWidget(output_browse_btn)
        file_layout.addRow("输出文件:", output_row)

        file_group.setLayout(file_layout)

        # 运行按钮
        run_btn = QPushButton("转换文件")
        run_btn.clicked.connect(self.convert_file)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(file_group)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择输入文件", str(self.working_dir),
            "All Supported (*.ipynb *.md *.py);;Jupyter Notebooks (*.ipynb);;Markdown Files (*.md);;Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.input_file.setText(file_path)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择输出文件", str(self.working_dir), "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.output_file.setText(file_path)

    def convert_file(self):
        if not self.input_file.text().strip():
            QMessageBox.warning(self, "警告", "请选择要转换的输入文件")
            return

        command = f'uv run marimo convert "{self.input_file.text().strip()}"'

        if self.output_file.text().strip():
            command += f' -o "{self.output_file.text().strip()}"'

        self.run_command(command)


class NewTab(BaseTab):
    """新建标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()

    def init_ui(self):
        # 提示设置
        prompt_group = QGroupBox("AI生成设置")
        prompt_layout = QVBoxLayout()

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("输入AI提示词来生成笔记本，或留空创建空白笔记本")
        self.prompt_input.setMaximumHeight(100)
        prompt_layout.addWidget(QLabel("提示词:"))
        prompt_layout.addWidget(self.prompt_input)

        prompt_group.setLayout(prompt_layout)

        # 服务器设置
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()

        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(2718)
        server_layout.addRow("端口:", self.port_input)

        self.host_input = QLineEdit("127.0.0.1")
        server_layout.addRow("主机:", self.host_input)

        server_group.setLayout(server_layout)

        # 选项设置
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout()

        self.headless_check = QCheckBox("无头模式")
        self.sandbox_check = QCheckBox("沙盒模式")

        options_layout.addWidget(self.headless_check)
        options_layout.addWidget(self.sandbox_check)
        options_group.setLayout(options_layout)

        # 运行按钮
        run_btn = QPushButton("创建新笔记本")
        run_btn.clicked.connect(self.create_new)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(prompt_group)
        scroll_layout.addWidget(server_group)
        scroll_layout.addWidget(options_group)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def create_new(self):
        command = "uv run marimo new"

        prompt_text = self.prompt_input.toPlainText().strip()
        if prompt_text:
            command += f' "{prompt_text}"'

        command += f" --port {self.port_input.value()}"
        command += f" --host {self.host_input.text()}"

        if self.headless_check.isChecked():
            command += " --headless"

        if self.sandbox_check.isChecked():
            command += " --sandbox"

        self.run_command(command)


class ExportTab(BaseTab):
    """导出标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()

    def init_ui(self):
        # 文件选择
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()

        self.input_file = QLineEdit()
        self.input_file.setPlaceholderText("选择要导出的marimo笔记本文件")
        input_browse_btn = QPushButton("浏览...")
        input_browse_btn.clicked.connect(self.browse_input_file)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_file)
        input_row.addWidget(input_browse_btn)
        file_layout.addRow("输入文件:", input_row)

        self.output_file = QLineEdit()
        self.output_file.setPlaceholderText("输出文件路径")
        output_browse_btn = QPushButton("浏览...")
        output_browse_btn.clicked.connect(self.browse_output_file)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_file)
        output_row.addWidget(output_browse_btn)
        file_layout.addRow("输出文件:", output_row)

        file_group.setLayout(file_layout)

        # 导出格式
        format_group = QGroupBox("导出格式")
        format_layout = QVBoxLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "html - HTML文件",
            "html-wasm - WASM HTML文件",
            "ipynb - Jupyter笔记本",
            "md - Markdown文件",
            "script - Python脚本"
        ])
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)

        # 运行按钮
        run_btn = QPushButton("导出文件")
        run_btn.clicked.connect(self.export_file)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(file_group)
        scroll_layout.addWidget(format_group)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择marimo笔记本文件", str(self.working_dir), "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.input_file.setText(file_path)

    def browse_output_file(self):
        format_text = self.format_combo.currentText()
        if "html" in format_text:
            filter_text = "HTML Files (*.html);;All Files (*)"
        elif "ipynb" in format_text:
            filter_text = "Jupyter Notebooks (*.ipynb);;All Files (*)"
        elif "md" in format_text:
            filter_text = "Markdown Files (*.md);;All Files (*)"
        else:
            filter_text = "Python Files (*.py);;All Files (*)"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择输出文件", str(self.working_dir), filter_text
        )
        if file_path:
            self.output_file.setText(file_path)

    def export_file(self):
        if not self.input_file.text().strip():
            QMessageBox.warning(self, "警告", "请选择要导出的输入文件")
            return

        if not self.output_file.text().strip():
            QMessageBox.warning(self, "警告", "请指定输出文件路径")
            return

        format_text = self.format_combo.currentText()
        export_format = format_text.split(" - ")[0]

        command = f'uv run marimo export {export_format} "{self.input_file.text().strip()}" -o "{self.output_file.text().strip()}"'

        self.run_command(command)


class TutorialTab(BaseTab):
    """教程标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.init_ui()

    def init_ui(self):
        # 教程选择
        tutorial_group = QGroupBox("教程选择")
        tutorial_layout = QVBoxLayout()

        self.tutorial_combo = QComboBox()
        tutorials = [
            "intro - 介绍",
            "dataflow - 数据流",
            "ui - 用户界面",
            "markdown - Markdown",
            "plots - 图表",
            "sql - SQL",
            "layout - 布局",
            "fileformat - 文件格式",
            "markdown-format - Markdown格式",
            "for-jupyter-users - 给Jupyter用户"
        ]
        self.tutorial_combo.addItems(tutorials)
        tutorial_layout.addWidget(self.tutorial_combo)
        tutorial_group.setLayout(tutorial_layout)

        # 服务器设置
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()

        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(2718)
        server_layout.addRow("端口:", self.port_input)

        self.host_input = QLineEdit("127.0.0.1")
        server_layout.addRow("主机:", self.host_input)

        server_group.setLayout(server_layout)

        # 选项设置
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout()

        self.headless_check = QCheckBox("无头模式")
        options_layout.addWidget(self.headless_check)
        options_group.setLayout(options_layout)

        # 运行按钮
        run_btn = QPushButton("打开教程")
        run_btn.clicked.connect(self.open_tutorial)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(tutorial_group)
        scroll_layout.addWidget(server_group)
        scroll_layout.addWidget(options_group)
        scroll_layout.addWidget(run_btn)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def open_tutorial(self):
        tutorial_text = self.tutorial_combo.currentText()
        tutorial_name = tutorial_text.split(" - ")[0]

        command = f"uv run marimo tutorial {tutorial_name}"
        command += f" --port {self.port_input.value()}"
        command += f" --host {self.host_input.text()}"

        if self.headless_check.isChecked():
            command += " --headless"

        self.run_command(command)


class ConfigTab(BaseTab):
    """配置标签页"""
    def __init__(self, working_dir=None):
        super().__init__(working_dir)
        self.config_widgets = {}
        self.init_ui()
        self.load_current_config()

    def init_ui(self):
        # 配置操作按钮
        actions_group = QGroupBox("配置操作")
        actions_layout = QHBoxLayout()

        load_btn = QPushButton("加载当前配置")
        load_btn.clicked.connect(self.load_current_config)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)

        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self.reset_config)

        actions_layout.addWidget(load_btn)
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(reset_btn)
        actions_group.setLayout(actions_layout)

        # 保存配置
        save_group = QGroupBox("保存设置")
        save_layout = QFormLayout()

        self.config_widgets['autosave_delay'] = QSpinBox()
        self.config_widgets['autosave_delay'].setRange(100, 10000)
        self.config_widgets['autosave_delay'].setValue(1000)
        self.config_widgets['autosave_delay'].setSuffix(" ms")
        save_layout.addRow("自动保存延迟:", self.config_widgets['autosave_delay'])

        self.config_widgets['format_on_save'] = QCheckBox()
        save_layout.addRow("保存时格式化:", self.config_widgets['format_on_save'])

        self.config_widgets['autosave'] = QComboBox()
        self.config_widgets['autosave'].addItems(["off", "after_delay", "on_edit"])
        save_layout.addRow("自动保存模式:", self.config_widgets['autosave'])

        save_group.setLayout(save_layout)

        # 运行时配置
        runtime_group = QGroupBox("运行时设置")
        runtime_layout = QFormLayout()

        self.config_widgets['watcher_on_save'] = QComboBox()
        self.config_widgets['watcher_on_save'].addItems(["off", "lazy", "eager"])
        runtime_layout.addRow("保存时监视:", self.config_widgets['watcher_on_save'])

        self.config_widgets['reactive_tests'] = QCheckBox()
        runtime_layout.addRow("响应式测试:", self.config_widgets['reactive_tests'])

        self.config_widgets['auto_reload'] = QComboBox()
        self.config_widgets['auto_reload'].addItems(["off", "lazy", "eager"])
        runtime_layout.addRow("自动重载:", self.config_widgets['auto_reload'])

        self.config_widgets['output_max_bytes'] = QSpinBox()
        self.config_widgets['output_max_bytes'].setRange(1000000, 100000000)
        self.config_widgets['output_max_bytes'].setValue(8000000)
        runtime_layout.addRow("输出最大字节:", self.config_widgets['output_max_bytes'])

        self.config_widgets['auto_instantiate'] = QCheckBox()
        runtime_layout.addRow("自动实例化:", self.config_widgets['auto_instantiate'])

        self.config_widgets['default_sql_output'] = QComboBox()
        self.config_widgets['default_sql_output'].addItems(["auto", "table", "chart"])
        runtime_layout.addRow("默认SQL输出:", self.config_widgets['default_sql_output'])

        self.config_widgets['on_cell_change'] = QComboBox()
        self.config_widgets['on_cell_change'].addItems(["autorun", "lazy", "disabled"])
        runtime_layout.addRow("单元格变化时:", self.config_widgets['on_cell_change'])

        self.config_widgets['std_stream_max_bytes'] = QSpinBox()
        self.config_widgets['std_stream_max_bytes'].setRange(100000, 10000000)
        self.config_widgets['std_stream_max_bytes'].setValue(1000000)
        runtime_layout.addRow("标准流最大字节:", self.config_widgets['std_stream_max_bytes'])

        runtime_group.setLayout(runtime_layout)

        # 格式化配置
        formatting_group = QGroupBox("格式化设置")
        formatting_layout = QFormLayout()

        self.config_widgets['line_length'] = QSpinBox()
        self.config_widgets['line_length'].setRange(50, 200)
        self.config_widgets['line_length'].setValue(79)
        formatting_layout.addRow("行长度:", self.config_widgets['line_length'])

        formatting_group.setLayout(formatting_layout)

        # 完成配置
        completion_group = QGroupBox("代码完成设置")
        completion_layout = QFormLayout()

        self.config_widgets['activate_on_typing'] = QCheckBox()
        completion_layout.addRow("输入时激活:", self.config_widgets['activate_on_typing'])

        self.config_widgets['copilot'] = QCheckBox()
        completion_layout.addRow("启用Copilot:", self.config_widgets['copilot'])

        completion_group.setLayout(completion_layout)

        # 键盘映射配置
        keymap_group = QGroupBox("键盘映射设置")
        keymap_layout = QFormLayout()

        self.config_widgets['keymap_preset'] = QComboBox()
        self.config_widgets['keymap_preset'].addItems(["default", "vim", "emacs"])
        keymap_layout.addRow("预设:", self.config_widgets['keymap_preset'])

        self.config_widgets['destructive_delete'] = QCheckBox()
        keymap_layout.addRow("破坏性删除:", self.config_widgets['destructive_delete'])

        keymap_group.setLayout(keymap_layout)

        # 服务器配置
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()

        self.config_widgets['browser'] = QComboBox()
        self.config_widgets['browser'].addItems(["default", "chrome", "firefox", "safari", "edge"])
        server_layout.addRow("浏览器:", self.config_widgets['browser'])

        self.config_widgets['follow_symlink'] = QCheckBox()
        server_layout.addRow("跟随符号链接:", self.config_widgets['follow_symlink'])

        server_group.setLayout(server_layout)

        # AI配置
        ai_group = QGroupBox("AI设置")
        ai_layout = QFormLayout()

        self.config_widgets['ai_mode'] = QComboBox()
        self.config_widgets['ai_mode'].addItems(["manual", "auto", "disabled"])
        ai_layout.addRow("AI模式:", self.config_widgets['ai_mode'])

        self.config_widgets['ai_rules'] = QLineEdit()
        self.config_widgets['ai_rules'].setPlaceholderText("AI规则 (可选)")
        ai_layout.addRow("AI规则:", self.config_widgets['ai_rules'])

        ai_group.setLayout(ai_layout)

        # 显示配置
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout()

        self.config_widgets['dataframes'] = QComboBox()
        self.config_widgets['dataframes'].addItems(["rich", "plain", "table"])
        display_layout.addRow("数据框显示:", self.config_widgets['dataframes'])

        self.config_widgets['code_editor_font_size'] = QSpinBox()
        self.config_widgets['code_editor_font_size'].setRange(8, 32)
        self.config_widgets['code_editor_font_size'].setValue(14)
        display_layout.addRow("代码编辑器字体大小:", self.config_widgets['code_editor_font_size'])

        self.config_widgets['cell_output'] = QComboBox()
        self.config_widgets['cell_output'].addItems(["above", "below", "inline"])
        display_layout.addRow("单元格输出位置:", self.config_widgets['cell_output'])

        self.config_widgets['default_table_max_columns'] = QSpinBox()
        self.config_widgets['default_table_max_columns'].setRange(10, 200)
        self.config_widgets['default_table_max_columns'].setValue(50)
        display_layout.addRow("表格最大列数:", self.config_widgets['default_table_max_columns'])

        self.config_widgets['reference_highlighting'] = QCheckBox()
        display_layout.addRow("引用高亮:", self.config_widgets['reference_highlighting'])

        self.config_widgets['theme'] = QComboBox()
        self.config_widgets['theme'].addItems(["system", "light", "dark"])
        display_layout.addRow("主题:", self.config_widgets['theme'])

        self.config_widgets['default_width'] = QComboBox()
        self.config_widgets['default_width'].addItems(["full", "medium", "compact"])
        display_layout.addRow("默认宽度:", self.config_widgets['default_width'])

        self.config_widgets['default_table_page_size'] = QSpinBox()
        self.config_widgets['default_table_page_size'].setRange(5, 100)
        self.config_widgets['default_table_page_size'].setValue(10)
        display_layout.addRow("表格页面大小:", self.config_widgets['default_table_page_size'])

        display_group.setLayout(display_layout)

        # 包管理配置
        package_group = QGroupBox("包管理设置")
        package_layout = QFormLayout()

        self.config_widgets['manager'] = QComboBox()
        self.config_widgets['manager'].addItems(["uv", "pip", "conda", "poetry"])
        package_layout.addRow("包管理器:", self.config_widgets['manager'])

        package_group.setLayout(package_layout)

        # 语言服务器配置
        lsp_group = QGroupBox("语言服务器设置")
        lsp_layout = QFormLayout()

        self.config_widgets['pylsp_enabled'] = QCheckBox()
        lsp_layout.addRow("启用pylsp:", self.config_widgets['pylsp_enabled'])

        self.config_widgets['enable_pyflakes'] = QCheckBox()
        lsp_layout.addRow("启用pyflakes:", self.config_widgets['enable_pyflakes'])

        self.config_widgets['enable_flake8'] = QCheckBox()
        lsp_layout.addRow("启用flake8:", self.config_widgets['enable_flake8'])

        self.config_widgets['enable_mypy'] = QCheckBox()
        lsp_layout.addRow("启用mypy:", self.config_widgets['enable_mypy'])

        self.config_widgets['enable_pylint'] = QCheckBox()
        lsp_layout.addRow("启用pylint:", self.config_widgets['enable_pylint'])

        self.config_widgets['enable_ruff'] = QCheckBox()
        lsp_layout.addRow("启用ruff:", self.config_widgets['enable_ruff'])

        self.config_widgets['enable_pydocstyle'] = QCheckBox()
        lsp_layout.addRow("启用pydocstyle:", self.config_widgets['enable_pydocstyle'])

        lsp_group.setLayout(lsp_layout)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(actions_group)
        scroll_layout.addWidget(save_group)
        scroll_layout.addWidget(runtime_group)
        scroll_layout.addWidget(formatting_group)
        scroll_layout.addWidget(completion_group)
        scroll_layout.addWidget(keymap_group)
        scroll_layout.addWidget(server_group)
        scroll_layout.addWidget(ai_group)
        scroll_layout.addWidget(display_group)
        scroll_layout.addWidget(package_group)
        scroll_layout.addWidget(lsp_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def load_current_config(self):
        """加载当前marimo配置"""
        self.output_text.clear()
        self.output_text.append("正在加载当前配置...")

        self.thread = QThread()
        self.runner = CommandRunner("uv run marimo config show")
        self.runner.moveToThread(self.thread)

        self.thread.started.connect(self.runner.run)
        self.runner.finished.connect(self.parse_config_output)
        self.runner.error.connect(self.on_command_error)
        self.runner.finished.connect(self.thread.quit)
        self.runner.error.connect(self.thread.quit)

        self.thread.start()

    def parse_config_output(self, output):
        """解析配置输出并更新表单"""
        self.output_text.append("配置加载成功:")
        self.output_text.append(output)

        # 解析配置输出（简化版本，实际应该解析TOML格式）
        lines = output.split('\n')
        current_section = None

        # 配置键映射
        key_mapping = {
            ('keymap', 'preset'): 'keymap_preset',
            ('ai', 'mode'): 'ai_mode',
            ('ai', 'rules'): 'ai_rules',
            ('package_management', 'manager'): 'manager',
            ('language_servers.pylsp', 'enabled'): 'pylsp_enabled'
        }

        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')

                # 处理布尔值
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'

                # 处理数字值
                try:
                    if '.' not in str(value) and str(value).isdigit():
                        value = int(value)
                except (ValueError, TypeError):
                    pass

                # 确定控件键名
                widget_key = key
                section_key = (current_section, key)
                if section_key in key_mapping:
                    widget_key = key_mapping[section_key]

                # 更新对应的控件
                if widget_key in self.config_widgets:
                    widget = self.config_widgets[widget_key]

                    if isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
                    elif isinstance(widget, QSpinBox):
                        try:
                            widget.setValue(int(value))
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))

    def save_config(self):
        """保存配置（这里只是演示，实际需要调用marimo config set命令）"""
        self.output_text.clear()
        self.output_text.append("保存配置功能需要marimo支持配置写入...")
        self.output_text.append("当前配置值:")

        # 显示当前表单中的所有配置值
        for key, widget in self.config_widgets.items():
            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = "未知"

            self.output_text.append(f"{key} = {value}")

    def reset_config(self):
        """重置配置为默认值"""
        # 设置默认值
        defaults = {
            'autosave_delay': 1000,
            'format_on_save': False,
            'autosave': 'after_delay',
            'watcher_on_save': 'lazy',
            'reactive_tests': True,
            'auto_reload': 'off',
            'output_max_bytes': 8000000,
            'auto_instantiate': True,
            'default_sql_output': 'auto',
            'on_cell_change': 'autorun',
            'std_stream_max_bytes': 1000000,
            'line_length': 79,
            'activate_on_typing': True,
            'copilot': False,
            'keymap_preset': 'default',
            'destructive_delete': True,
            'browser': 'default',
            'follow_symlink': False,
            'ai_mode': 'manual',
            'ai_rules': '',
            'dataframes': 'rich',
            'code_editor_font_size': 14,
            'cell_output': 'above',
            'default_table_max_columns': 50,
            'reference_highlighting': False,
            'theme': 'system',
            'default_width': 'full',
            'default_table_page_size': 10,
            'manager': 'uv',
            'pylsp_enabled': True,
            'enable_pyflakes': False,
            'enable_flake8': False,
            'enable_mypy': True,
            'enable_pylint': False,
            'enable_ruff': True,
            'enable_pydocstyle': False
        }

        for key, default_value in defaults.items():
            if key in self.config_widgets:
                widget = self.config_widgets[key]

                if isinstance(widget, QCheckBox):
                    widget.setChecked(default_value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(default_value)
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(default_value))
                    if index >= 0:
                        widget.setCurrentIndex(index)

        self.output_text.clear()
        self.output_text.append("配置已重置为默认值")


class MarimoGUI(QMainWindow):
    """主窗口"""
    def __init__(self, working_dir=None, project_name=None):
        super().__init__()
        self.working_dir = working_dir or Path.cwd()
        self.project_name = project_name or "默认项目"
        self.running_processes = []  # 跟踪运行中的进程
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Marimo GUI - {self.project_name}")
        self.setGeometry(100, 100, 1498, 1075)

        # 创建主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 创建标签页
        tab_widget = QTabWidget()

        # 添加各个标签页，传递工作目录
        edit_tab = EditTab(self.working_dir)
        run_tab = RunTab(self.working_dir)
        new_tab = NewTab(self.working_dir)
        convert_tab = ConvertTab(self.working_dir)
        export_tab = ExportTab(self.working_dir)
        tutorial_tab = TutorialTab(self.working_dir)
        config_tab = ConfigTab(self.working_dir)

        # 连接进程信号
        edit_tab.process_started.connect(self.add_process)
        run_tab.process_started.connect(self.add_process)
        new_tab.process_started.connect(self.add_process)
        tutorial_tab.process_started.connect(self.add_process)

        tab_widget.addTab(edit_tab, "编辑 (Edit)")
        tab_widget.addTab(run_tab, "运行 (Run)")
        tab_widget.addTab(new_tab, "新建 (New)")
        tab_widget.addTab(convert_tab, "转换 (Convert)")
        tab_widget.addTab(export_tab, "导出 (Export)")
        tab_widget.addTab(tutorial_tab, "教程 (Tutorial)")
        tab_widget.addTab(config_tab, "配置 (Config)")

        main_layout.addWidget(tab_widget)

        # 创建状态栏
        self.create_status_bar()

    def create_status_bar(self):
        """创建状态栏并显示项目信息"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 显示项目信息
        project_info_text = f"当前项目: {self.project_name} | 工作目录: {self.working_dir}"
        self.status_bar.showMessage(project_info_text)

        # 添加进程计数标签
        self.process_count_label = QLabel("运行进程: 0")
        self.status_bar.addPermanentWidget(self.process_count_label)

    def add_process(self, process):
        """添加进程到跟踪列表"""
        self.running_processes.append(process)
        self.update_process_count()

    def update_process_count(self):
        """更新状态栏中的进程计数"""
        # 清理已结束的进程
        self.running_processes = [p for p in self.running_processes if p.poll() is None]
        count = len(self.running_processes)
        self.process_count_label.setText(f"运行进程: {count}")

    def terminate_all_processes(self):
        """终止所有运行中的进程"""
        for process in self.running_processes:
            try:
                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    # 等待进程终止，如果超时则强制杀死
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
            except Exception as e:
                print(f"终止进程时出错: {e}")
        self.running_processes.clear()
        self.update_process_count()

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        self.terminate_all_processes()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Marimo GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Marimo UI")

    # 设置应用图标（如果有的话）
    # app.setWindowIcon(QIcon("icon.png"))

    window = MarimoGUI()
    window.show()

    # 居中显示窗口
    screen = app.primaryScreen().geometry()
    window.move(
        (screen.width() - window.width()) // 2,
        (screen.height() - window.height()) // 2
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
