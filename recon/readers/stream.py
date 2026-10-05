"""统一的逐行读取接口。"""

import csv
from dataclasses import replace
from pathlib import Path

from ..errors import ReadError
from .encoding_detector import decode
from .options import ReaderOptions


def iter_delimited(path: str | Path, options: ReaderOptions, default_delimiter=None):
    text = decode(Path(path).read_bytes(), options.encoding)
    delimiter = options.delimiter or default_delimiter
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.reader(text.splitlines(), delimiter=delimiter, strict=True)
    yielded = 0
    for index, row in enumerate(reader):
        if index < options.header_row:
            continue
        if options.comment and row and row[0].startswith(options.comment):
            continue
        if options.skip_blank and not any(cell.strip() for cell in row):
            continue
        if options.max_rows is not None and yielded >= options.max_rows:
            break
        yielded += 1
        yield row


def iter_rows(path, options=None):
    """逐行返回数据行；第一行表头不会作为数据返回。"""
    options = options or ReaderOptions()
    suffix = Path(path).suffix.lower()
    stream_options = replace(options, max_rows=None)
    if suffix == ".csv":
        rows = iter_delimited(path, stream_options)
    elif suffix == ".tsv":
        rows = iter_delimited(path, stream_options, "\t")
    elif suffix == ".xlsx":
        from .xlsx_reader import iter_rows as xlsx_iter_rows

        yield from xlsx_iter_rows(path, options)
        return
    else:
        raise ReadError(f"流式读取暂不支持：{suffix}")
    iterator = iter(rows)
    next(iterator, None)
    yielded = 0
    for row in iterator:
        if options.max_rows is not None and yielded >= options.max_rows:
            break
        yielded += 1
        yield row
