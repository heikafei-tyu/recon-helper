"""共享测试夹具：给各测试文件提供可复用的样例表格。"""
from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_orders() -> pd.DataFrame:
    """三行订单样例：含千分位来源的金额列。"""
    return pd.DataFrame(
        {
            "order_id": ["A001", "A002", "A003"],
            "salesperson": ["张三", "李四", "张三"],
            "amount": [100000.0, 98000.0, 2500.5],
        }
    )


@pytest.fixture
def sample_summary() -> pd.DataFrame:
    """与 sample_orders 对应的汇总样例：合计故意差 2000.5 以便测试差异路径。"""
    return pd.DataFrame(
        {
            "salesperson": ["张三", "李四"],
            "total": [100250.5, 98000.0],
        }
    )


@pytest.fixture
def write_csv(tmp_path):
    """把 DataFrame 写成指定编码的 csv 并返回路径的工厂夹具。"""

    def _write(df: pd.DataFrame, name: str = "data.csv", encoding: str = "utf-8") -> str:
        path = tmp_path / name
        df.to_csv(path, index=False, encoding=encoding)
        return str(path)

    return _write
