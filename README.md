# Marimo UI

一个基于 PySide6 的 marimo 命令行工具图形界面，提供直观易用的可视化操作界面。

## 功能特性

### 🎯 项目管理
- **智能项目选择器**：从 VSCode 设置中自动读取项目列表
- **项目搜索过滤**：快速定位目标项目
- **项目状态检测**：自动检查项目路径有效性
- **Git 仓库识别**：显示项目的 Git 状态

### 📝 Marimo 操作界面
- **编辑模式 (Edit)**：启动 marimo 编辑器，支持完整的服务器配置
- **运行模式 (Run)**：运行 marimo 应用，支持会话管理
- **新建笔记本 (New)**：创建新的 marimo 笔记本，支持 AI 生成
- **文件转换 (Convert)**：转换 Jupyter、Markdown 等格式到 marimo
- **导出功能 (Export)**：导出为 HTML、IPYNB、Markdown 等格式
- **教程模式 (Tutorial)**：访问内置教程和示例
- **配置管理 (Config)**：可视化配置 marimo 设置

### 🔧 高级功能
- **进程管理**：实时监控运行中的 marimo 进程
- **命令输出**：实时显示命令执行结果
- **工作目录管理**：基于选择的项目自动设置工作目录
- **参数配置**：图形化配置所有 marimo 命令参数

## 安装要求

### 系统要求
- Python 3.12+
- Windows / macOS / Linux

### 依赖包
- `marimo>=0.15.0` - marimo 核心包
- `pyside6>=6.9.2` - Qt6 Python 绑定

## 安装方式

### 使用 uv（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd marimo-ui

# 使用 uv 安装依赖
uv sync

# 运行项目选择器
uv run python project_selector.py

# 或直接运行主界面
uv run python marimo_gui.py
```

### 使用 pip
```bash
# 克隆项目
git clone <repository-url>
cd marimo-ui

# 安装依赖
pip install -r requirements.txt

# 运行应用
python project_selector.py
```

## 使用指南

### 启动应用

1. **项目选择模式**（推荐）：
   ```bash
   uv run python project_selector.py
   ```
   - 自动读取 VSCode 项目配置
   - 选择目标项目后启动 marimo GUI

2. **直接启动模式**：
   ```bash
   uv run python marimo_gui.py
   ```
   - 在当前目录启动 marimo GUI

### 界面操作

#### 项目选择器
- **搜索项目**：在搜索框中输入项目名称或路径关键词
- **查看详情**：点击项目查看路径、Git 状态等信息
- **选择项目**：双击或点击"选择项目并启动Marimo GUI"按钮

#### 主界面标签页

**编辑 (Edit)**
- 选择笔记本文件（可选）
- 配置服务器参数（端口、主机、代理等）
- 设置认证选项（令牌、密码）
- 启用高级功能（沙盒模式、文件监视等）

**运行 (Run)**
- 选择要运行的笔记本文件（必需）
- 配置运行参数（会话超时、输出选项等）
- 启动应用服务器

**新建 (New)**
- 输入 AI 提示词生成笔记本内容
- 配置服务器参数
- 创建新的 marimo 笔记本

**转换 (Convert)**
- 选择输入文件（.ipynb、.md、.py）
- 指定输出路径
- 转换为 marimo 格式

**导出 (Export)**
- 选择 marimo 笔记本文件
- 选择导出格式（HTML、IPYNB、Markdown、Script）
- 导出到指定位置

**教程 (Tutorial)**
- 选择内置教程主题
- 在浏览器中打开交互式教程

**配置 (Config)**
- 可视化编辑 marimo 配置
- 支持保存、运行时、格式化等各类设置
- 实时加载当前配置状态

## 配置说明

### VSCode 项目集成

应用会自动读取 VSCode 的 `settings.json` 文件中的 `dashboard.projectData` 配置。

> **注意**：`dashboard.projectData` 配置由 VSCode 扩展 [Project Dashboard](https://marketplace.visualstudio.com/items?itemName=kruemelkatze.vscode-dashboard) 提供。请先安装此扩展并配置项目后再使用项目选择器功能。

**配置路径**：
- Windows: `%APPDATA%\Code\User\settings.json`
- macOS: `~/Library/Application Support/Code/User/settings.json`
- Linux: `~/.config/Code/User/settings.json`

**配置格式示例**：
```json
{
  "dashboard.projectData": [
    {
      "groupName": "Python 项目",
      "collapsed": false,
      "projects": [
        {
          "name": "marimo-ui",
          "path": "D:/Sources/marimo-ui",
          "id": "marimo-ui-001",
          "color": "#007ACC",
          "isGitRepo": true
        }
      ]
    }
  ]
}
```

### Marimo 配置

应用支持可视化编辑 marimo 的所有配置选项，包括：

- **保存设置**：自动保存、格式化选项
- **运行时配置**：文件监视、响应式测试、输出限制
- **代码完成**：Copilot 集成、自动激活
- **显示设置**：主题、字体、布局选项
- **包管理**：支持 uv、pip、conda、poetry
- **语言服务器**：pylsp、ruff、mypy 等工具集成

## 开发说明

### 项目结构
```
marimo-ui/
├── marimo_gui.py          # 主 GUI 界面
├── project_selector.py    # 项目选择器
├── pyproject.toml        # 项目配置
├── uv.lock              # 依赖锁定文件
└── README.md            # 项目文档
```

### 核心组件

**BaseTab 类**
- 所有标签页的基类
- 提供命令执行和输出显示功能
- 支持后台线程运行命令

**CommandRunner 类**
- 负责在后台线程执行 marimo 命令
- 支持进程管理和输出捕获
- 处理长时间运行的服务器进程

**MarimoGUI 类**
- 主窗口管理器
- 集成所有功能标签页
- 提供进程监控和状态显示

### 扩展开发

添加新的功能标签页：

1. 继承 `BaseTab` 类
2. 实现 `init_ui()` 方法构建界面
3. 实现具体的命令执行逻辑
4. 在 `MarimoGUI` 中注册新标签页

## 故障排除

### 常见问题

**Q: 项目选择器显示"找不到VSCode设置文件"**
A: 确保已安装 VSCode 和 [Project Dashboard](https://marketplace.visualstudio.com/items?itemName=kruemelkatze.vscode-dashboard) 扩展，并在扩展中配置了项目。

**Q: marimo 命令执行失败**
A: 检查是否正确安装了 marimo 包，确认 Python 环境配置正确。

**Q: 界面显示异常或崩溃**
A: 确保安装了正确版本的 PySide6，检查系统 Qt 环境。

**Q: 进程无法正常终止**
A: 应用会在关闭时自动清理所有子进程，如有问题可手动终止相关进程。

### 调试模式

启用详细输出：
```bash
# 设置环境变量启用调试
export MARIMO_GUI_DEBUG=1
uv run python project_selector.py
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd marimo-ui

# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码格式化
uv run ruff format .
uv run ruff check .
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 更新日志

### v0.1.0
- 初始版本发布
- 支持所有主要 marimo 命令的图形化操作
- 集成 VSCode 项目管理
- 提供完整的配置管理界面