"""生成完全虚构的跨格式读取示例。"""

import csv
import json
from pathlib import Path

from openpyxl import Workbook


def generate(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    columns = ["order_id", "customer", "amount"]
    rows = [["001", "示例甲", "12.50"], ["002", "示例乙", "20.00"]]
    for encoding, name in [("utf-8-sig", "orders.csv"), ("gbk", "orders-gbk.csv"), ("utf-16", "orders-utf16.csv")]:
        with (directory / name).open("w", encoding=encoding, newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(rows)
    (directory / "orders.json").write_text(
        json.dumps([dict(zip(columns, row)) for row in rows], ensure_ascii=False), encoding="utf-8"
    )
    book = Workbook()
    sheet = book.active
    sheet.append(columns)
    for row in rows:
        sheet.append(row)
    book.save(directory / "orders.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent)
