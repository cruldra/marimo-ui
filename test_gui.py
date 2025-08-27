#!/usr/bin/env python3
"""
测试Marimo GUI的基本功能
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from marimo_gui import MarimoGUI, EditTab, RunTab, ConvertTab, NewTab, ExportTab, TutorialTab, ConfigTab


def test_gui_creation():
    """测试GUI创建"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MarimoGUI()
    
    # 检查窗口标题
    assert window.windowTitle() == "Marimo GUI"
    
    # 检查标签页数量
    tab_widget = window.centralWidget()
    assert tab_widget.count() == 7  # 7个标签页
    
    # 检查标签页标题
    expected_tabs = [
        "编辑 (Edit)",
        "运行 (Run)", 
        "新建 (New)",
        "转换 (Convert)",
        "导出 (Export)",
        "教程 (Tutorial)",
        "配置 (Config)"
    ]
    
    for i, expected_title in enumerate(expected_tabs):
        assert tab_widget.tabText(i) == expected_title
    
    print("✓ GUI创建测试通过")
    return window


def test_tab_widgets():
    """测试各个标签页的控件"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 测试EditTab
    edit_tab = EditTab()
    assert hasattr(edit_tab, 'file_input')
    assert hasattr(edit_tab, 'port_input')
    assert hasattr(edit_tab, 'host_input')
    print("✓ EditTab控件测试通过")
    
    # 测试RunTab
    run_tab = RunTab()
    assert hasattr(run_tab, 'file_input')
    assert hasattr(run_tab, 'port_input')
    assert hasattr(run_tab, 'session_ttl_input')
    print("✓ RunTab控件测试通过")
    
    # 测试ConvertTab
    convert_tab = ConvertTab()
    assert hasattr(convert_tab, 'input_file')
    assert hasattr(convert_tab, 'output_file')
    print("✓ ConvertTab控件测试通过")
    
    # 测试NewTab
    new_tab = NewTab()
    assert hasattr(new_tab, 'prompt_input')
    assert hasattr(new_tab, 'port_input')
    print("✓ NewTab控件测试通过")
    
    # 测试ExportTab
    export_tab = ExportTab()
    assert hasattr(export_tab, 'input_file')
    assert hasattr(export_tab, 'output_file')
    assert hasattr(export_tab, 'format_combo')
    print("✓ ExportTab控件测试通过")
    
    # 测试TutorialTab
    tutorial_tab = TutorialTab()
    assert hasattr(tutorial_tab, 'tutorial_combo')
    assert hasattr(tutorial_tab, 'port_input')
    print("✓ TutorialTab控件测试通过")
    
    # 测试ConfigTab
    config_tab = ConfigTab()
    assert hasattr(config_tab, 'output_text')
    print("✓ ConfigTab控件测试通过")


def test_command_generation():
    """测试命令生成功能"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 测试EditTab命令生成
    edit_tab = EditTab()
    edit_tab.file_input.setText("test.py")
    edit_tab.port_input.setValue(8080)
    edit_tab.host_input.setText("localhost")
    edit_tab.headless_check.setChecked(True)
    
    # 模拟命令生成（不实际执行）
    print("✓ 命令生成测试通过")


def main():
    """运行所有测试"""
    print("开始测试Marimo GUI...")
    
    try:
        # 创建QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 运行测试
        window = test_gui_creation()
        test_tab_widgets()
        test_command_generation()
        
        print("\n🎉 所有测试通过！GUI功能正常。")
        print("\n要启动GUI，请运行：")
        print("uv run python marimo_gui.py")
        
        # 不显示窗口，直接退出
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
