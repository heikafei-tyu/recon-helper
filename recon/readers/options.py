"""读取层的统一配置。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReaderOptions:
    encoding: str | None = None
    delimiter: str | None = None
    header_row: int = 0
    skip_blank: bool = True
    comment: str | None = None
    max_rows: int | None = None
    normalize_headers: bool = True

    def __post_init__(self):
        if self.header_row < 0:
            raise ValueError("header_row 不能为负数")
        if self.max_rows is not None and self.max_rows < 0:
            raise ValueError("max_rows 不能为负数")
        if self.delimiter is not None and len(self.delimiter) != 1:
            raise ValueError("delimiter 必须是单个字符")

