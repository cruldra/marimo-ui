import marimo

__generated_with = "0.15.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, np, plt


@app.cell
def __(mo):
    mo.md(
        r"""
        # 示例Marimo笔记本
        
        这是一个用于测试Marimo GUI的示例笔记本。
        
        ## 功能演示
        
        - 数据可视化
        - 交互式控件
        - Markdown渲染
        """
    )
    return


@app.cell
def __(mo):
    # 创建一个滑块控件
    slider = mo.ui.slider(1, 100, value=50, label="数据点数量:")
    slider
    return slider,


@app.cell
def __(np, plt, slider):
    # 根据滑块值生成数据并绘图
    n_points = slider.value
    x = np.linspace(0, 2*np.pi, n_points)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
    plt.plot(x, np.cos(x), 'r--', linewidth=2, label='cos(x)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'三角函数图 (数据点: {n_points})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return n_points, x, y


@app.cell
def __(mo, n_points):
    mo.md(
        f"""
        ## 数据统计
        
        当前使用了 **{n_points}** 个数据点来绘制图形。
        
        这个笔记本演示了：
        1. Markdown文本渲染
        2. 交互式UI控件（滑块）
        3. 数据可视化（matplotlib）
        4. 响应式计算（当滑块值改变时，图形自动更新）
        """
    )
    return


if __name__ == "__main__":
    app.run()
