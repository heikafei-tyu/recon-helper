from datetime import datetime, timedelta

from ..errors import ReadError
from ..model import Table


def read(path, encoding=None):
    try:
        import xlrd
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        header = sheet.row_values(0)
        rows = []
        for row_index in range(1, sheet.nrows):
            values = []
            for column, value in enumerate(sheet.row_values(row_index)):
                if sheet.cell_type(row_index, column) == xlrd.XL_CELL_DATE:
                    value = xlrd.xldate_as_datetime(value, book.datemode).isoformat()
                values.append(value)
            rows.append(values)
        table = Table.from_records(header, rows)
        return Table(table.columns, table.rows, str(path), "xls", encoding or "auto", None)
    except ImportError as exc:
        raise ReadError("读取 XLS 需要安装 xlrd") from exc
    except Exception as exc:
        raise ReadError(f"XLS 文件读取失败：{exc}") from exc
