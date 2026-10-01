from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .errors import ReadError


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str | None, ...], ...]

    @classmethod
    def from_records(cls, header, records):
        columns = tuple(str(c).strip() if c is not None else "" for c in header)
        if not columns or any(not c for c in columns):
            raise ReadError("列名不能为空")
        if len(set(columns)) != len(columns):
            raise ReadError("列名不能重复")
        rows = []
        for number, record in enumerate(records, 2):
            if len(record) != len(columns):
                raise ReadError(f"第 {number} 行列数与表头不一致")
            rows.append(tuple(None if v is None or v == "" else str(v) for v in record))
        return cls(columns, tuple(rows))

    def summary(self):
        types = {}
        for index, column in enumerate(self.columns):
            values = [row[index] for row in self.rows if row[index] is not None]
            numeric = bool(values)
            for value in values:
                try:
                    numeric = numeric and Decimal(value).is_finite()
                except InvalidOperation:
                    numeric = False
            types[column] = "number" if numeric else "text" if values else "empty"
        return {"row_count": len(self.rows), "columns": list(self.columns), "types": types}
