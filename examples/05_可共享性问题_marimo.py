import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import matplotlib.pyplot as plt

    # 设置 matplotlib 使用支持中文的字体
    # 'Microsoft YaHei' 是 Windows 系统中常见的字体
    # 如果您使用 macOS，可以尝试 'PingFang SC'
    # 如果您使用 Linux，可以尝试 'WenQuanYi Micro Hei'
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] 

    # 解决负号 '-' 显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False 

    return (plt,)


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    return mo, np, pd


@app.cell
def _(mo):
    mo.md(
        r"""
    # Marimo笔记本的可共享性优势

    这个笔记本演示了marimo如何解决传统笔记本的可共享性问题：

    1. 一键部署为Web应用
    2. 保持完整的交互性
    3. 无需复杂基础设施
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案1：一键部署为Web应用""")
    return


@app.cell
def _(mo):
    # 数据生成参数 - 在Web应用中完全可用
    sample_size = mo.ui.slider(
        start=50,
        stop=1000,
        step=50,
        value=100,
        label="样本大小:"
    )

    noise_level = mo.ui.slider(
        start=0,
        stop=1,
        step=0.05,
        value=0.1,
        label="噪声水平:"
    )

    chart_type = mo.ui.dropdown(
        options=['散点图', '直方图', '箱线图'],
        value='散点图',
        label="图表类型:"
    )

    mo.vstack([sample_size, noise_level, chart_type])
    return chart_type, noise_level, sample_size


@app.cell
def _(chart_type, noise_level, np, pd, plt, sample_size):
    # 自动响应参数变化 - 在Web应用中完全交互
    size = sample_size.value
    noise = noise_level.value
    chart = chart_type.value

    # 生成数据
    np.random.seed(42)  # 为了可重现性
    x = np.linspace(0, 10, size)
    y = 2 * x + 1 + np.random.normal(0, noise * 5, size)

    data = pd.DataFrame({'X': x, 'Y': y})

    # 创建图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    if chart == '散点图':
        ax1.scatter(data['X'], data['Y'], alpha=0.6)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_title('X vs Y 散点图')
    elif chart == '直方图':
        ax1.hist(data['Y'], bins=20, alpha=0.7)
        ax1.set_xlabel('Y值')
        ax1.set_ylabel('频次')
        ax1.set_title('Y值分布直方图')
    else:  # 箱线图
        ax1.boxplot([data['X'], data['Y']], labels=['X', 'Y'])
        ax1.set_title('X和Y的箱线图')

    # 统计信息
    ax2.axis('off')
    stats_text = f"""
    数据统计信息:

    样本大小: {size}
    噪声水平: {noise:.2f}

    X统计:
    均值: {data['X'].mean():.2f}
    标准差: {data['X'].std():.2f}

    Y统计:
    均值: {data['Y'].mean():.2f}
    标准差: {data['Y'].std():.2f}

    相关系数: {data['X'].corr(data['Y']):.3f}
    """
    ax2.text(0.1, 0.9, stats_text, transform=ax2.transAxes, 
            fontsize=10, verticalalignment='top')

    plt.tight_layout()

    fig
    return (data,)


@app.cell
def _(mo):
    mo.md(
        r"""
    **一键部署**：

    要将这个交互式应用部署为Web应用，只需运行：
    ```bash
    marimo run 05_可共享性问题_marimo.py
    ```

    就这么简单！无需额外配置或工具。
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案2：完整的交互性保持""")
    return


@app.cell
def _(mo):
    # 这个交互式组件在Web应用中完全可用
    freq_slider = mo.ui.slider(0.5, 5, step=0.1, value=1, label="频率:")
    amplitude_slider = mo.ui.slider(0.1, 2, step=0.1, value=1, label="振幅:")

    mo.hstack([freq_slider, amplitude_slider])
    return amplitude_slider, freq_slider


@app.cell
def _(amplitude_slider, freq_slider, np, plt):
    # 实时响应的正弦波图
    freq = freq_slider.value
    amplitude = amplitude_slider.value

    x_wave = np.linspace(0, 2*np.pi, 100)
    y_wave = amplitude * np.sin(freq * x_wave)

    fig_wave, ax_wave = plt.subplots(figsize=(10, 4))
    ax_wave.plot(x_wave, y_wave, linewidth=2)
    ax_wave.set_title(f'正弦波: 频率={freq:.1f}, 振幅={amplitude:.1f}')
    ax_wave.set_xlabel('X')
    ax_wave.set_ylabel('Y')
    ax_wave.grid(True, alpha=0.3)

    fig_wave
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **交互性保持**：

    - 在Web应用中，所有滑块和控件都完全可用
    - 用户可以实时调整参数并看到结果
    - 无需任何技术知识，普通用户也能使用
    - 响应速度快，用户体验好
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案3：数据导出功能""")
    return


@app.cell
def _(mo):
    # 数据导出按钮 - 在Web应用中完全可用
    export_button = mo.ui.button(label="导出当前数据")
    export_button
    return (export_button,)


@app.cell
def _(data, export_button, mo):
    # 响应导出按钮
    if export_button.value:
        # 在实际应用中，这里可以触发文件下载
        mo.md(
            f"""
            **数据导出成功！**

            - 文件名: `data_sample_{len(data)}_noise.csv`
            - 数据行数: {len(data)}
            - 数据列数: {len(data.columns)}

            数据预览:
            ```
            {data.head().to_string()}
            ```
            """
        )
    else:
        mo.md("点击上面的按钮导出数据")
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案4：无需复杂基础设施""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **简单的部署流程**：

    ### 本地运行
    ```bash
    marimo run 05_可共享性问题_marimo.py
    ```

    ### 生产部署
    ```bash
    # 使用任何Web服务器
    marimo run 05_可共享性问题_marimo.py --host 0.0.0.0 --port 8080
    ```

    ### Docker部署
    ```dockerfile
    FROM python:3.9
    RUN pip install marimo matplotlib pandas numpy
    COPY 05_可共享性问题_marimo.py /app/
    EXPOSE 8080
    CMD ["marimo", "run", "/app/05_可共享性问题_marimo.py", "--host", "0.0.0.0", "--port", "8080"]
    ```

    ### 云平台部署
    - 可以直接部署到Heroku、AWS、GCP等
    - 无需特殊配置或额外服务
    - 标准的Web应用部署流程
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案5：用户友好的界面""")
    return


@app.cell
def _(mo):
    # 创建一个用户友好的控制面板
    mo.md("### 数据分析控制面板")
    return


@app.cell
def _(mo):
    # 高级控制选项
    show_grid = mo.ui.checkbox(value=True, label="显示网格")
    show_trend = mo.ui.checkbox(value=False, label="显示趋势线")
    color_scheme = mo.ui.dropdown(
        options=['默认', '蓝色', '红色', '绿色'],
        value='默认',
        label="颜色方案:"
    )

    mo.hstack([show_grid, show_trend, color_scheme])
    return color_scheme, show_grid, show_trend


@app.cell
def _(color_scheme, data, np, plt, show_grid, show_trend):
    # 根据用户选择创建定制化图表
    fig_custom, ax_custom = plt.subplots(figsize=(10, 6))

    # 选择颜色
    colors = {
        '默认': 'blue',
        '蓝色': 'navy',
        '红色': 'crimson',
        '绿色': 'forestgreen'
    }
    color = colors[color_scheme.value]

    # 绘制散点图
    ax_custom.scatter(data['X'], data['Y'], alpha=0.6, color=color)

    # 添加趋势线
    if show_trend.value:
        z = np.polyfit(data['X'], data['Y'], 1)
        p = np.poly1d(z)
        ax_custom.plot(data['X'], p(data['X']), "r--", alpha=0.8, linewidth=2)

    # 设置网格
    if show_grid.value:
        ax_custom.grid(True, alpha=0.3)

    ax_custom.set_xlabel('X值')
    ax_custom.set_ylabel('Y值')
    ax_custom.set_title('定制化数据可视化')

    fig_custom
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **用户体验优势**：

    - 清晰的界面，无需技术背景
    - 实时反馈，立即看到结果
    - 直观的控件，易于理解
    - 专业的外观，适合商业使用
    - 响应式设计，支持移动设备
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 总结

    marimo的可共享性优势：

    1. **一键部署**：`marimo run` 即可启动Web应用
    2. **完整交互性**：所有UI元素在Web应用中完全可用
    3. **无需额外工具**：不需要Voilà、Binder等第三方工具
    4. **简单基础设施**：标准Web应用部署，无特殊要求
    5. **用户友好**：非技术用户也能轻松使用
    6. **生产就绪**：性能好，适合实际业务使用
    7. **移动友好**：响应式设计，支持各种设备
    8. **安全可靠**：不暴露开发环境，只提供应用功能

    这使得marimo不仅适合开发，也适合创建面向最终用户的交互式应用！
    """
    )
    return


if __name__ == "__main__":
    app.run()
