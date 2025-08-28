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
    # Marimo笔记本的可重用性优势

    这个笔记本演示了marimo如何解决传统笔记本的可重用性问题：

    1. 可以直接作为脚本执行
    2. 可以导入函数和类
    3. 易于部署和自动化
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案1：直接作为脚本执行""")
    return


@app.cell
def _():
    # 这是一个有用的数据处理函数
    def clean_data(data):
        """
        清理数据：移除空值，标准化格式
        """
        import pandas as pd
        import numpy as np

        if isinstance(data, list):
            data = pd.DataFrame(data)

        # 移除空值
        data = data.dropna()

        # 标准化数值列
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            data[col] = (data[col] - data[col].mean()) / data[col].std()

        return data

    print("数据清理函数已定义")
    return (clean_data,)


@app.cell
def _():
    # 另一个有用的分析函数
    def analyze_data(data):
        """
        分析数据：计算基本统计信息
        """
        import pandas as pd

        results = {
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'summary': data.describe().to_dict()
        }

        return results

    print("数据分析函数已定义")
    return (analyze_data,)


@app.cell
def _(analyze_data, clean_data):
    # 主要的处理流程
    def main_pipeline(raw_data):
        """
        完整的数据处理流程
        """
        print("开始数据处理流程...")

        # 清理数据
        cleaned_data = clean_data(raw_data)
        print(f"数据清理完成，剩余 {len(cleaned_data)} 行")

        # 分析数据
        analysis_results = analyze_data(cleaned_data)
        print("数据分析完成")

        return cleaned_data, analysis_results

    print("主流程函数已定义")
    return (main_pipeline,)


@app.cell
def _(main_pipeline, mo):
    mo.md(
        f"""
    **直接执行能力**：

    这个marimo笔记本可以直接运行：
    ```bash
    python 04_可重用性问题_marimo.py
    ```

    无需任何转换步骤！函数 `{main_pipeline.__name__}` 等都可以直接使用。
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案2：可以导入函数和类""")
    return


@app.cell
def _():
    # 这个有用的工具类可以被其他程序直接导入
    class DataProcessor:
        """
        数据处理工具类
        """

        def __init__(self, config=None):
            self.config = config or {}
            self.processed_count = 0

        def process_batch(self, data_batch):
            """
            批量处理数据
            """
            results = []
            for item in data_batch:
                processed_item = self._process_single(item)
                results.append(processed_item)
                self.processed_count += 1

            return results

        def _process_single(self, item):
            """
            处理单个数据项
            """
            # 简单的处理逻辑
            if isinstance(item, (int, float)):
                return item * 2
            elif isinstance(item, str):
                return item.upper()
            else:
                return str(item)

        def get_stats(self):
            """
            获取处理统计信息
            """
            return {
                'processed_count': self.processed_count,
                'config': self.config
            }

    print("DataProcessor类已定义")
    return (DataProcessor,)


@app.cell
def _(DataProcessor):
    # 测试工具类
    processor = DataProcessor({'batch_size': 10})

    test_batch = [1, 2, 'hello', 3.14, 'world', [1, 2, 3]]
    results = processor.process_batch(test_batch)

    print("处理结果:", results)
    print("统计信息:", processor.get_stats())
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **导入能力**：

    其他Python程序可以直接导入这个文件中的类和函数：

    ```python
    # 这样做完全可行！
    from examples.04_可重用性问题_marimo import DataProcessor, clean_data

    # 使用导入的类和函数
    processor = DataProcessor()
    cleaned = clean_data(my_data)
    ```

    无需任何特殊工具或转换步骤！
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案3：易于部署和自动化""")
    return


@app.cell
def _():
    # 这个函数可以在生产环境中直接使用
    def generate_report(data, output_path):
        """
        生成数据报告
        """
        import matplotlib.pyplot as plt
        import pandas as pd
        from datetime import datetime
        import json

        # 创建报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': {
                'total_rows': len(data),
                'columns': list(data.columns),
                'memory_usage': data.memory_usage(deep=True).sum()
            }
        }

        # 生成图表
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # 数值列的分布
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            data[numeric_cols[0]].hist(ax=axes[0, 0])
            axes[0, 0].set_title(f'{numeric_cols[0]} 分布')

        # 保存报告
        plt.savefig(f"{output_path}_charts.png")
        plt.close()

        # 保存数据摘要
        with open(f"{output_path}_summary.json", 'w') as f:
            json.dump(report, f, indent=2)

        print(f"报告已保存到 {output_path}")
        return report

    print("报告生成函数已定义")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **部署优势**：

    1. **直接调度**：
    ```bash
    # cron作业可以直接运行
    0 2 * * * python /path/to/04_可重用性问题_marimo.py
    ```

    2. **容器化简单**：
    ```dockerfile
    FROM python:3.9
    COPY 04_可重用性问题_marimo.py /app/
    CMD ["python", "/app/04_可重用性问题_marimo.py"]
    ```

    3. **CI/CD友好**：
    ```yaml
    - name: Run data processing
      run: python examples/04_可重用性问题_marimo.py
    ```

    4. **命令行参数**：
    ```python
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## 解决方案4：模块化和包管理""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    **模块化能力**：

    marimo笔记本可以轻松组织为Python包：

    ```
    my_project/
    ├── __init__.py
    ├── data_processing.py      # 这个marimo文件
    ├── analysis.py            # 另一个marimo文件
    └── utils/
        ├── __init__.py
        └── helpers.py         # 普通Python模块
    ```

    然后可以这样使用：
    ```python
    from my_project.data_processing import DataProcessor
    from my_project.analysis import run_analysis
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 总结

    marimo的可重用性优势：

    1. **直接执行**：无需转换，直接运行Python文件
    2. **标准导入**：可以像普通Python模块一样导入
    3. **生产就绪**：适合部署到生产环境
    4. **工具兼容**：与所有Python工具和框架兼容
    5. **自动化友好**：易于集成到自动化流程中
    6. **模块化**：支持标准的Python包结构
    7. **版本管理**：可以使用标准的Python包管理工具

    这使得marimo笔记本不仅适合探索性分析，也适合构建可维护的生产系统！
    """
    )
    return


if __name__ == "__main__":
    app.run()
