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
            types[column] = infer(values)
        return {"row_count": len(self.rows), "columns": list(self.columns), "types": types}
