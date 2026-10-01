from openpyxl import load_workbook

from ..errors import ReadError
from ..model import Table


def read(path, encoding=None):
    book = load_workbook(path, read_only=True, data_only=False)
    try:
        sheet = book.worksheets[0]
        def records():
            for cells in sheet.iter_rows():
                if any(cell.data_type == "f" for cell in cells):
                    raise ReadError("XLSX 包含公式，请先转为已核验的值")
                yield [cell.value for cell in cells]
        rows = records()
        header = next(rows, None)
        if header is None:
            raise ReadError("XLSX 工作表为空")
        return Table.from_records(header, rows)
    finally:
        book.close()
