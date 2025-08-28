import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


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
def _(mo):
    mo.md(
        r"""
    # Marimo笔记本的可维护性优势

    这个笔记本演示了marimo如何解决传统笔记本的可维护性问题：

    1. 纯Python文件格式
    2. 友好的版本控制
    3. 无输出污染
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案1：纯Python文件格式""")
    return


@app.cell
def _():
    # 简单的计算 - 在marimo中这就是纯Python代码
    a = 6
    b = 7
    result = a * b
    print("这是一个简单的计算")
    print(f"结果: {result}")
    return


@app.cell
def _(mo):
    mo.md(
        f"""
    **marimo的优势**：

    - 这个笔记本存储为纯Python文件（.py）
    - 没有JSON元数据
    - 没有嵌入的输出数据
    - 可以直接用任何文本编辑器查看和编辑
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案2：版本控制友好""")
    return


@app.cell
def _(plt):
    import numpy as np

    # 创建图表 - 输出不会保存在文件中
    x = np.linspace(1, 10, 10)
    y = x ** 2

    fig, ax = plt.subplots()
    ax.bar(x, y)
    ax.set_title("简单的柱状图")

    fig
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **版本控制优势**：

    - 图表输出不会保存在源文件中
    - Git diff 显示的是纯Python代码的变化
    - 合并冲突更容易解决
    - 文件大小保持较小
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案3：无输出污染""")
    return


@app.cell
def _():
    from datetime import datetime
    import random

    # 每次运行产生不同输出，但不影响源文件
    current_time = datetime.now()
    random_number = random.random()

    print(f"当前时间: {current_time}")
    print(f"随机数: {random_number}")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **无输出污染的好处**：

    - 即使输出每次都不同，源文件保持不变
    - 版本历史只记录真正的代码变更
    - 不会因为重新运行而产生无意义的提交
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案4：简化的合并冲突""")
    return


@app.cell
def _():
    # 这是一个可能引起合并冲突的单元格
    def process_data(data):
        # 在marimo中，这只是普通的Python函数
        result = data * 2
        return result

    # 多个开发者可以更容易地合并代码变更
    test_data = [1, 2, 3, 4, 5]
    processed = [process_data(x) for x in test_data]

    print("marimo中的合并冲突更容易解决")
    print("因为它们只涉及Python代码，没有JSON元数据")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **合并冲突的简化**：

    在marimo中，合并冲突看起来像这样：

    ```python
    <<<<<<< HEAD
    def process_data(data):
        # 开发者A的实现
        result = data * 2 + 1
        return result
    =======
    def process_data(data):
        # 开发者B的实现  
        result = data * 3
        return result
    >>>>>>> feature-branch
    ```

    这比JSON格式的冲突更容易理解和解决！
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案5：可以作为脚本执行""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **脚本执行能力**：

    这个marimo笔记本可以直接作为Python脚本运行：

    ```bash
    python 03_可维护性问题_marimo.py
    ```

    或者作为交互式应用运行：

    ```bash
    marimo run 03_可维护性问题_marimo.py
    ```

    这在Jupyter中需要额外的转换步骤。
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 总结

    marimo的可维护性优势：

    1. **纯Python格式**：易于阅读、编辑和理解
    2. **版本控制友好**：清晰的diff，简单的合并
    3. **无输出污染**：源文件不包含运行时输出
    4. **标准工具兼容**：可以使用任何Python工具
    5. **脚本执行**：可以直接作为Python脚本运行
    6. **团队协作**：减少合并冲突，提高协作效率

    这些特性使得marimo笔记本更适合专业的软件开发工作流程！
    """
    )
    return


if __name__ == "__main__":
    app.run()
