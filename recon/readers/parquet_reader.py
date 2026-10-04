from ..errors import ReadError
from ..model import Table


def read(path, encoding=None):
    try:
        import pyarrow.parquet as parquet

        table = parquet.read_table(path)
        rows = table.to_pylist()
        columns = list(table.column_names)
        records = [[row.get(column) for column in columns] for row in rows]
        result = Table.from_records(columns, records)
        return Table(result.columns, result.rows, str(path), "parquet", None, None)
    except ImportError as exc:
        raise ReadError("读取 Parquet 需要安装 pyarrow") from exc
    except Exception as exc:
        raise ReadError(f"Parquet 文件读取失败：{exc}") from exc
