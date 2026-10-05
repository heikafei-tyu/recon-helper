from dataclasses import dataclass

from .errors import ReadError
from .readers.type_inference import infer


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str | None, ...], ...]
    source: str = ""
    format: str = ""
    encoding: str | None = None
    delimiter: str | None = None
    sheet_name: str | None = None

    @classmethod
    def from_records(cls, header, records, *, normalize_headers=True):
        raw_columns = tuple("" if c is None else str(c) for c in header)
        columns = tuple(c.strip() if normalize_headers else c for c in raw_columns)
        if not columns:
            raise ReadError("列名不能为空：表头没有任何列")
        empty = [str(index + 1) for index, column in enumerate(columns) if not column]
        if empty:
            raise ReadError(f"列名不能为空：第 {', '.join(empty)} 列为空（原始值为空）")
        if len(set(columns)) != len(columns):
            duplicates = sorted({column for column in columns if columns.count(column) > 1})
            locations = {column: [index + 1 for index, item in enumerate(columns) if item == column] for column in duplicates}
            detail = "; ".join(f"{column}: 第{','.join(map(str, indexes))}列" for column, indexes in locations.items())
            raise ReadError(f"列名不能重复：{detail}")
        rows = []
        for number, record in enumerate(records, 2):
            if len(record) != len(columns):
                raise ReadError(f"第 {number} 行列数与表头不一致：期望 {len(columns)} 列，实际 {len(record)} 列")
            rows.append(tuple(None if v is None or v == "" else str(v) for v in record))
        return cls(columns, tuple(rows))

    def summary(self):
        types = {}
        for index, column in enumerate(self.columns):
            values = [row[index] for row in self.rows if row[index] is not None]
            types[column] = infer(values)
        return {"row_count": len(self.rows), "columns": list(self.columns), "types": types}
