import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Marimo笔记本中的可重现性保证

    这个笔记本演示了marimo如何解决传统笔记本的可重现性问题：
    1. 自动依赖管理
    2. 一致的状态保证
    3. 无隐藏状态
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案1：自动依赖管理""")
    return


@app.cell
def _():
    # 定义变量x
    x = 15
    print(f"x = {x}")
    return (x,)


@app.cell
def _(x):
    # 使用变量x - marimo会自动跟踪依赖关系
    y = x * 2
    print(f"y = x * 2 = {y}")
    return (y,)


@app.cell
def _(mo, x, y):
    mo.md(
        f"""
    **当前状态**：

    - x = {x}

    - y = {y}

    **试试修改上面x的值** - y会自动重新计算！
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案2：无幽灵变量""")
    return


@app.cell
def _():
    # 定义一个变量
    temp_variable = "我是一个临时变量"
    print(temp_variable)
    return (temp_variable,)


@app.cell
def _(temp_variable):
    # 使用这个变量
    result = f"处理结果：{temp_variable}"
    print(result)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **在marimo中**：
    - 如果你删除定义`temp_variable`的单元格
    - 使用它的单元格会立即显示错误
    - 不会有隐藏的幽灵变量
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案3：明确的依赖关系""")
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np

    # 创建数据
    data = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100)
    })
    print("数据已创建")
    return (data,)


@app.cell
def _(data):
    # 数据处理 - 自动依赖于data
    processed_data = data.copy()
    processed_data['C'] = processed_data['A'] + processed_data['B']
    print(f"处理后的数据形状：{processed_data.shape}")
    return (processed_data,)


@app.cell
def _(processed_data):
    # 分析结果 - 自动依赖于processed_data
    mean_c = processed_data['C'].mean()
    print(f"C列的平均值：{mean_c}")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **在marimo中**：
    - 修改数据生成逻辑时，所有依赖的单元格会自动重新运行
    - 保证分析结果始终基于最新的数据
    - 代码、输出和程序状态始终一致
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 总结

    marimo通过以下方式解决可重现性问题：

    1. **静态分析**：自动分析单元格间的依赖关系
    2. **自动执行**：当依赖改变时自动重新运行相关单元格
    3. **状态清理**：删除单元格时自动清理其定义的变量
    4. **一致性保证**：确保代码、输出和程序状态始终匹配
    """
    )
    return


if __name__ == "__main__":
    app.run()
