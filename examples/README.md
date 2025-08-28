# Marimo vs Jupyter 对比示例

本目录包含了一系列对比示例，通过实际代码演示了 Marimo 和 Jupyter 笔记本在相同场景下的不同表现，帮助您理解 Marimo 相对于传统笔记本工具的优势。

## 📁 目录结构

### 核心对比示例

每个问题都包含两个版本的实现：
- `*_jupyter.ipynb` - Jupyter 笔记本版本，展示传统笔记本的问题
- `*_marimo.py` - Marimo 笔记本版本，展示 Marimo 的解决方案

| 示例 | Jupyter 版本 | Marimo 版本 | 主要对比点 |
|------|-------------|-------------|-----------|
| 01_可重现性问题 | `01_可重现性问题_jupyter.ipynb` | `01_可重现性问题_marimo.py` | 隐藏状态、乱序执行、状态一致性 |
| 02_交互性问题 | `02_交互性问题_jupyter.ipynb` | `02_交互性问题_marimo.py` | UI元素同步、回调函数、状态管理 |
| 03_可维护性问题 | `03_可维护性问题_jupyter.ipynb` | `03_可维护性问题_marimo.py` | 版本控制、文件格式、代码组织 |
| 04_可重用性问题 | `04_可重用性问题_jupyter.ipynb` | `04_可重用性问题_marimo.py` | 脚本执行、模块导入、自动化 |
| 05_可共享性问题 | `05_可共享性问题_jupyter.ipynb` | `05_可共享性问题_marimo.py` | 应用部署、交互式分享、用户体验 |

### 说明文档

- `marimo-介绍.md` - Marimo 的详细介绍，包括特性、优势和适用场景
- `传统笔记本中众所周知的问题.md` - 传统笔记本工具的常见问题及 Marimo 的解决方案

## 🎯 主要对比维度

### 1. 可重现性 (Reproducibility)
**Jupyter 问题：**
- 隐藏状态导致代码和输出不匹配
- 可以乱序执行单元格
- 删除单元格后变量仍存在内存中

**Marimo 解决方案：**
- 自动依赖管理，确保执行顺序正确
- 一致的状态保证，代码、输出和程序状态始终同步
- 删除单元格时自动清理相关变量

### 2. 交互性 (Interactivity)
**Jupyter 问题：**
- 需要手动编写回调函数
- UI元素与Python状态不同步
- 复杂的状态管理

**Marimo 解决方案：**
- UI元素自动与Python同步
- 无需回调函数，拖动滑块自动重新运行相关单元格
- 简洁的交互式编程体验

### 3. 可维护性 (Maintainability)
**Jupyter 问题：**
- JSON格式难以版本控制
- Git diff 产生大量噪音
- 代码和元数据混合

**Marimo 解决方案：**
- 纯Python文件格式
- Git友好，变更清晰可见
- 更好的代码组织和模块化

### 4. 可重用性 (Reusability)
**Jupyter 问题：**
- 难以作为脚本执行
- 函数和类不易导入
- 自动化困难

**Marimo 解决方案：**
- 可直接作为Python脚本运行
- 支持函数和类的导入
- 易于集成到自动化流程

### 5. 可共享性 (Shareability)
**Jupyter 问题：**
- 需要额外工具部署为应用
- 静态输出，缺乏交互性
- 分享困难

**Marimo 解决方案：**
- 一键部署为交互式Web应用
- 保持完整的交互功能
- 易于分享和演示

## 🚀 如何运行示例

### 运行 Marimo 示例

```bash
# 安装 marimo
pip install marimo

# 以笔记本模式运行（可编辑）
marimo edit examples/01_可重现性问题_marimo.py

# 以应用模式运行（只读，适合演示）
marimo run examples/01_可重现性问题_marimo.py
```

### 运行 Jupyter 示例

```bash
# 安装 jupyter
pip install jupyter

# 启动 Jupyter
jupyter notebook examples/01_可重现性问题_jupyter.ipynb
```

## 💡 学习建议

1. **先看问题**：从 Jupyter 版本开始，体验传统笔记本的问题
2. **再看解决方案**：运行对应的 Marimo 版本，感受差异
3. **对比体验**：同时打开两个版本，直观对比
4. **实际操作**：尝试修改代码，观察不同的行为

## 📚 扩展阅读

- [Marimo 官方文档](https://docs.marimo.io/)
- [Marimo GitHub 仓库](https://github.com/marimo-team/marimo)
- [为什么选择 Marimo](./marimo-介绍.md)
- [传统笔记本的问题](./传统笔记本中众所周知的问题.md)

## 🤝 贡献

如果您发现了新的对比场景或改进建议，欢迎提交 Issue 或 Pull Request！
