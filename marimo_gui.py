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
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class CommandRunner(QObject):
    """在后台线程中运行命令"""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        try:
            result = subprocess.run(
                self.command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                self.finished.emit(result.stdout)
            else:
                self.error.emit(result.stderr or result.stdout)
        except Exception as e:
            self.error.emit(str(e))


class BaseTab(QWidget):
    """基础标签页类"""
    def __init__(self):
        super().__init__()
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
        self.output_text.append(f"执行命令: {command}\n")
        
        self.thread = QThread()
        self.runner = CommandRunner(command)
        self.runner.moveToThread(self.thread)
        
        self.thread.started.connect(self.runner.run)
        self.runner.finished.connect(self.on_command_finished)
        self.runner.error.connect(self.on_command_error)
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
    def __init__(self):
        super().__init__()
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
            self, "选择笔记本文件", "", "Python Files (*.py);;All Files (*)"
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
    def __init__(self):
        super().__init__()
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
            self, "选择笔记本文件", "", "Python Files (*.py);;All Files (*)"
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
    def __init__(self):
        super().__init__()
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
            self, "选择输入文件", "",
            "All Supported (*.ipynb *.md *.py);;Jupyter Notebooks (*.ipynb);;Markdown Files (*.md);;Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.input_file.setText(file_path)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择输出文件", "", "Python Files (*.py);;All Files (*)"
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
    def __init__(self):
        super().__init__()
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
    def __init__(self):
        super().__init__()
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
            self, "选择marimo笔记本文件", "", "Python Files (*.py);;All Files (*)"
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
            self, "选择输出文件", "", filter_text
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
    def __init__(self):
        super().__init__()
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
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 配置操作
        config_group = QGroupBox("配置操作")
        config_layout = QVBoxLayout()

        show_btn = QPushButton("显示配置")
        show_btn.clicked.connect(self.show_config)

        describe_btn = QPushButton("描述配置")
        describe_btn.clicked.connect(self.describe_config)

        config_layout.addWidget(show_btn)
        config_layout.addWidget(describe_btn)
        config_group.setLayout(config_layout)

        # 布局
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(config_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        self.layout.addWidget(scroll)
        self.add_output_section()

    def show_config(self):
        command = "uv run marimo config show"
        self.run_command(command)

    def describe_config(self):
        command = "uv run marimo config describe"
        self.run_command(command)


class MarimoGUI(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Marimo GUI")
        self.setGeometry(100, 100, 900, 700)

        # 创建标签页
        tab_widget = QTabWidget()

        # 添加各个标签页
        tab_widget.addTab(EditTab(), "编辑 (Edit)")
        tab_widget.addTab(RunTab(), "运行 (Run)")
        tab_widget.addTab(NewTab(), "新建 (New)")
        tab_widget.addTab(ConvertTab(), "转换 (Convert)")
        tab_widget.addTab(ExportTab(), "导出 (Export)")
        tab_widget.addTab(TutorialTab(), "教程 (Tutorial)")
        tab_widget.addTab(ConfigTab(), "配置 (Config)")

        self.setCentralWidget(tab_widget)


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
