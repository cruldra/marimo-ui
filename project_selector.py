#!/usr/bin/env python3
"""
项目选择界面 - 从VSCode设置中读取项目列表并选择项目
"""

import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ProjectSelector(QMainWindow):
    """项目选择主窗口"""
    project_selected = Signal(str, str)  # 项目路径, 项目名称
    
    def __init__(self):
        super().__init__()
        self.projects_data = []
        self.selected_project = None
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        self.setWindowTitle("Marimo GUI - 项目选择")
        self.setGeometry(200, 200, 800, 600)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("选择项目")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：项目树
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        projects_group = QGroupBox("项目列表")
        projects_layout = QVBoxLayout(projects_group)

        # 添加搜索框
        from PySide6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索项目名称...")
        self.search_input.textChanged.connect(self.filter_projects)
        projects_layout.addWidget(self.search_input)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["项目", "路径"])
        self.project_tree.setColumnWidth(0, 200)
        self.project_tree.itemClicked.connect(self.on_project_selected)
        projects_layout.addWidget(self.project_tree)
        
        left_layout.addWidget(projects_group)
        splitter.addWidget(left_widget)
        
        # 右侧：项目详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_group = QGroupBox("项目详情")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        
        # 状态信息
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)
        
        right_layout.addWidget(status_group)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([400, 400])
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新项目列表")
        refresh_btn.clicked.connect(self.load_projects)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        self.select_btn = QPushButton("选择项目并启动Marimo GUI")
        self.select_btn.setEnabled(False)
        self.select_btn.clicked.connect(self.confirm_selection)
        button_layout.addWidget(self.select_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def get_vscode_settings_path(self):
        """获取VSCode设置文件路径"""
        # Windows路径
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata) / "Code" / "User" / "settings.json"
        
        # macOS路径
        elif sys.platform == 'darwin':
            home = Path.home()
            return home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        
        # Linux路径
        else:
            home = Path.home()
            return home / ".config" / "Code" / "User" / "settings.json"
        
        return None
    
    def clean_json_content(self, content):
        """清理JSON内容，移除注释和尾随逗号"""
        import re

        # 移除单行注释 // ...（但不在字符串内）
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # 简单的字符串检测，避免在字符串内移除注释
            in_string = False
            escaped = False
            comment_pos = -1

            for i, char in enumerate(line):
                if escaped:
                    escaped = False
                    continue

                if char == '\\':
                    escaped = True
                elif char == '"' and not escaped:
                    in_string = not in_string
                elif not in_string and char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    comment_pos = i
                    break

            if comment_pos >= 0:
                line = line[:comment_pos].rstrip()

            cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # 移除多行注释 /* ... */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # 移除尾随逗号（在 } 或 ] 前的逗号）
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        return content

    def load_projects(self):
        """从VSCode设置文件加载项目列表"""
        self.status_text.clear()
        self.status_text.append("正在加载项目列表...")

        try:
            settings_path = self.get_vscode_settings_path()

            if not settings_path or not settings_path.exists():
                self.status_text.append("错误：找不到VSCode设置文件")
                self.status_text.append(f"预期路径: {settings_path}")
                return

            self.status_text.append(f"读取设置文件: {settings_path}")

            # 读取设置文件
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 清理JSON内容
            cleaned_content = self.clean_json_content(content)

            try:
                # 尝试解析清理后的JSON
                settings = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                self.status_text.append(f"JSON解析错误: {e}")
                self.status_text.append("尝试使用更宽松的解析方法...")

                # 尝试使用更宽松的方法
                try:
                    # 使用ast.literal_eval作为备选（仅适用于简单情况）
                    import ast
                    settings = ast.literal_eval(cleaned_content)
                except (ValueError, SyntaxError):
                    self.status_text.append("无法解析设置文件，请检查JSON格式")
                    self.status_text.append("建议：在VSCode中打开设置文件并修复语法错误")
                    return

            # 获取项目数据
            project_data = settings.get('dashboard.projectData', [])

            if not project_data:
                self.status_text.append("警告：未找到dashboard.projectData配置")
                self.status_text.append("请确认VSCode中已安装并配置了项目管理扩展")
                return

            self.projects_data = project_data
            self.populate_project_tree()

            total_projects = sum(len(group.get('projects', [])) for group in project_data)
            self.status_text.append(f"成功加载 {len(project_data)} 个项目组，共 {total_projects} 个项目")

        except json.JSONDecodeError as e:
            self.status_text.append(f"JSON解析错误: {e}")
            self.status_text.append(f"错误位置: 第{e.lineno}行，第{e.colno}列")
            self.status_text.append("建议解决方案:")
            self.status_text.append("1. 在VSCode中打开设置文件")
            self.status_text.append("2. 检查并修复JSON语法错误")
            self.status_text.append("3. 移除注释或使用正确的JSON格式")
        except Exception as e:
            self.status_text.append(f"加载项目失败: {e}")
            import traceback
            self.status_text.append("详细错误信息:")
            self.status_text.append(traceback.format_exc())
    
    def populate_project_tree(self):
        """填充项目树"""
        self.project_tree.clear()
        
        for group in self.projects_data:
            group_name = group.get('groupName', '未命名组')
            group_item = QTreeWidgetItem(self.project_tree, [group_name, ""])
            group_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            
            # 设置组展开状态
            collapsed = group.get('collapsed', False)
            group_item.setExpanded(not collapsed)
            
            projects = group.get('projects', [])
            for project in projects:
                project_name = project.get('name', '未命名项目')
                project_path = project.get('path', '')
                is_git_repo = project.get('isGitRepo', False)

                project_item = QTreeWidgetItem(group_item, [project_name, project_path])

                # 存储项目数据
                project_item.setData(0, Qt.UserRole, project)

                # 添加Git仓库标识
                if is_git_repo:
                    project_item.setText(0, f"🔗 {project_name}")
        
        self.project_tree.expandAll()

    def filter_projects(self, search_text):
        """根据搜索文本过滤项目"""
        search_text = search_text.lower().strip()

        # 遍历所有项目组
        for i in range(self.project_tree.topLevelItemCount()):
            group_item = self.project_tree.topLevelItem(i)
            group_has_visible_projects = False

            # 遍历组内的项目
            for j in range(group_item.childCount()):
                project_item = group_item.child(j)
                project_data = project_item.data(0, Qt.UserRole)

                if project_data:
                    project_name = project_data.get('name', '').lower()
                    project_path = project_data.get('path', '').lower()

                    # 检查项目名称或路径是否包含搜索文本
                    is_visible = (not search_text or
                                search_text in project_name or
                                search_text in project_path)

                    project_item.setHidden(not is_visible)

                    if is_visible:
                        group_has_visible_projects = True

            # 如果组内没有可见项目，隐藏整个组
            group_item.setHidden(not group_has_visible_projects)

    def on_project_selected(self, item, column):
        """项目选择事件"""
        _ = column  # 未使用的参数
        project_data = item.data(0, Qt.UserRole)
        
        if project_data:  # 这是一个项目项
            self.selected_project = project_data
            self.select_btn.setEnabled(True)
            
            # 显示项目详情
            self.show_project_details(project_data)
        else:  # 这是一个组项
            self.selected_project = None
            self.select_btn.setEnabled(False)
            self.details_text.clear()
    
    def show_project_details(self, project):
        """显示项目详情"""
        details = []
        details.append(f"<h3>{project.get('name', '未命名项目')}</h3>")
        details.append(f"<b>路径:</b> {project.get('path', '')}")
        details.append(f"<b>ID:</b> {project.get('id', '')}")
        details.append(f"<b>颜色:</b> {project.get('color', '#000000')}")
        details.append(f"<b>Git仓库:</b> {'是' if project.get('isGitRepo', False) else '否'}")
        
        # 检查路径是否存在
        project_path = project.get('path', '')
        if project_path:
            if Path(project_path).exists():
                details.append("<b>状态:</b> <span style='color: green;'>路径存在</span>")
            else:
                details.append("<b>状态:</b> <span style='color: red;'>路径不存在</span>")
        
        self.details_text.setHtml("<br>".join(details))
    
    def confirm_selection(self):
        """确认选择并启动Marimo GUI"""
        if not self.selected_project:
            return

        project_path = self.selected_project.get('path', '')
        project_name = self.selected_project.get('name', '')

        if not project_path:
            QMessageBox.warning(self, "警告", "项目路径为空")
            return

        if not Path(project_path).exists():
            reply = QMessageBox.question(
                self, "确认",
                f"项目路径不存在：{project_path}\n\n是否仍要继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # 发射信号
        self.project_selected.emit(project_path, project_name)

        # 直接启动Marimo GUI（简化逻辑）
        self.launch_marimo_gui(project_path, project_name)

        self.close()

    def launch_marimo_gui(self, project_path, project_name):
        """直接启动Marimo GUI"""
        try:
            from marimo_gui import MarimoGUI

            # 创建并显示Marimo GUI
            self.marimo_gui = MarimoGUI(project_path, project_name)

            # 居中显示Marimo GUI
            screen = QApplication.instance().primaryScreen().geometry()
            self.marimo_gui.move(
                (screen.width() - self.marimo_gui.width()) // 2,
                (screen.height() - self.marimo_gui.height()) // 2
            )

            self.marimo_gui.show()

            # 显示成功消息
            QMessageBox.information(
                self.marimo_gui, "项目选择成功",
                f"已选择项目: {project_name}\n工作目录: {project_path}\n\n"
                f"所有marimo命令将在此目录下执行。"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "错误",
                f"启动Marimo GUI失败：{str(e)}"
            )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Marimo Project Selector")
    
    selector = ProjectSelector()
    selector.show()
    
    # 居中显示
    screen = app.primaryScreen().geometry()
    selector.move(
        (screen.width() - selector.width()) // 2,
        (screen.height() - selector.height()) // 2
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
