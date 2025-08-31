import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    # 设置 matplotlib 使用支持中文的字体
    # 'Microsoft YaHei' 是 Windows 系统中常见的字体
    # 如果您使用 macOS，可以尝试 'PingFang SC'
    # 如果您使用 Linux，可以尝试 'WenQuanYi Micro Hei'
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] 

    # 解决负号 '-' 显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False 
    return mo, np, plt


@app.cell
def _(mo):
    mo.md(
        r"""
    # Marimo笔记本中的交互性优势

    这个笔记本演示了marimo如何简化交互性：

    1. 无需手动回调函数
    2. 自动同步UI元素
    3. 简洁的状态管理
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案1：自动同步的UI元素""")
    return


@app.cell
def _(mo):
    # 创建滑块 - 无需回调函数
    slider = mo.ui.slider(0, 100, value=50, label="值:")
    slider
    return (slider,)


@app.cell
def _(mo, slider):
    # 自动响应滑块变化
    value = slider.value
    mo.md(
        f"""
        **当前值**: {value}  
        **平方**: {value**2}

        滑块值改变时，这个单元格会自动重新运行！
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案2：多个UI元素的简单同步""")
    return


@app.cell
def _(mo):
    # 创建多个相关的UI元素
    x_slider = mo.ui.slider(0.1, 5.0, value=1.0, step=0.1, label="X:")
    y_slider = mo.ui.slider(0.1, 5.0, value=1.0, step=0.1, label="Y:")
    operation = mo.ui.dropdown(['加法', '乘法', '幂运算'], value='加法', label="操作:")

    mo.vstack([x_slider, y_slider, operation])
    return operation, x_slider, y_slider


@app.cell
def _(mo, operation, x_slider, y_slider):
    # 自动计算结果 - 任何UI元素改变都会触发重新计算
    x_val = x_slider.value
    y_val = y_slider.value
    op = operation.value

    if op == '加法':
        calc_result = x_val + y_val
    elif op == '乘法':
        calc_result = x_val * y_val
    else:  # 幂运算
        calc_result = x_val ** y_val

    mo.md(f"**{x_val} {op} {y_val} = {calc_result:.2f}**")
    return op, x_val, y_val


@app.cell
def _(np, op, plt, x_val, y_val):
    # 自动更新图表
    x_range = np.linspace(0.1, 5, 100)
    if op == '加法':
        y_range = x_range + y_val
    elif op == '乘法':
        y_range = x_range * y_val
    else:
        y_range = x_range ** y_val

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_range, y_range, label=f'f(x) = x {op} {y_val}')
    ax.axvline(x_val, color='red', linestyle='--', alpha=0.7, label=f'x = {x_val}')
    ax.set_xlabel('X')
    ax.set_ylabel('结果')
    ax.set_title(f'函数可视化')
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案3：简洁的状态管理""")
    return


@app.cell
def _(mo):
    # 数据生成控件
    data_size = mo.ui.slider(10, 1000, value=100, label="数据量:")
    noise_level = mo.ui.slider(0, 1, value=0.1, step=0.01, label="噪声水平:")

    mo.hstack([data_size, noise_level])
    return data_size, noise_level


@app.cell
def _(data_size, noise_level, np):
    # 自动生成数据 - 参数改变时自动重新生成
    size = data_size.value
    noise = noise_level.value

    # 生成数据
    current_data = np.random.normal(0, 1, size) + np.random.normal(0, noise, size)

    print(f"已生成 {size} 个数据点，噪声水平: {noise}")
    return (current_data,)


@app.cell
def _(current_data, plt):
    # 自动更新数据可视化
    hist_fig, hist_ax = plt.subplots(figsize=(10, 4))
    hist_ax.hist(current_data, bins=30, alpha=0.7, edgecolor='black')
    hist_ax.set_title('数据分布')
    hist_ax.set_xlabel('值')
    hist_ax.set_ylabel('频次')
    hist_ax.grid(True, alpha=0.3)

    hist_fig
    return


@app.cell
def _(mo):
    # 分析类型选择
    analysis_type = mo.ui.dropdown(
        ['均值', '标准差', '最大值', '最小值'], 
        value='均值', 
        label="分析类型:"
    )
    analysis_type
    return (analysis_type,)


@app.cell
def _(analysis_type, current_data, mo, np):
    # 自动计算分析结果
    analysis = analysis_type.value

    if analysis == '均值':
        analysis_result = np.mean(current_data)
    elif analysis == '标准差':
        analysis_result = np.std(current_data)
    elif analysis == '最大值':
        analysis_result = np.max(current_data)
    else:  # 最小值
        analysis_result = np.min(current_data)

    mo.md(f"**{analysis}**: {analysis_result:.4f}")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 总结

    marimo的交互性优势：

    1. **无需回调函数**：UI元素自动与Python变量同步
    2. **自动重新运行**：相关单元格在UI元素改变时自动执行
    3. **简洁的代码**：无需手动管理输出区域或状态
    4. **直观的依赖关系**：通过变量引用自动建立依赖
    5. **一致的状态**：UI和计算结果始终保持同步

    这使得创建交互式数据分析变得简单而直观！
    """
    )
    return


if __name__ == "__main__":
    app.run()
