"""规则模板生成器：按场景生成带注释的 rules.yaml 骨架，降低手写规则的成本。

用法: python examples/generate_rules.py --scenario salary --out rules.yaml
"""
from __future__ import annotations

import argparse

TEMPLATES: dict[str, str] = {
    "salary": """# 场景：月薪核对（明细加总 = 汇总合计）
rules:
  - name: 月薪明细与汇总核对
    type: row_compare
    left:  { table: orders.csv,  key: salesperson, value: amount }
    right: { table: summary.csv, key: salesperson, value: total }
    tolerance:
      mode: absolute        # absolute=差额绝对值, relative=比例
      value: 1.0            # 差 1 元以内算对
    priority: 10
""",
    "quarterly": """# 场景：季度汇总核对（含相对容差）
rules:
  - name: 季度销售额核对
    type: row_compare
    left:  { table: q_detail.csv, key: product, value: revenue }
    right: { table: q_report.csv, key: product, value: revenue }
    tolerance:
      mode: relative        # 差异占比例 < 0.5% 算对
      value: 0.005
    transforms:
      - { column: revenue, from_unit: 万元, to_unit: 元 }
    priority: 10
""",
    "cross_year": """# 场景：跨年度勾稽（上年末 = 今年初）
rules:
  - name: 期末期初勾稽
    type: chain_check
    chain:
      - { table: balance_2023.csv, column: closing_balance }
      - { table: balance_2024.csv, column: opening_balance }
    tolerance: { mode: absolute, value: 0.0 }
    priority: 20
""",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 rules.yaml 模板")
    parser.add_argument("--scenario", choices=sorted(TEMPLATES), default="salary")
    parser.add_argument("--out", default="rules.yaml")
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(TEMPLATES[args.scenario])
    print(f"已生成 {args.out}（场景: {args.scenario}）——按实际表名/列名修改后即可 recon run")


if __name__ == "__main__":
    main()
