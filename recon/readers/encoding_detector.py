from ..errors import ReadError


def decode(data: bytes, encoding: str | None = None) -> str:
    if encoding:
        try:
            return data.decode(encoding)
        except (UnicodeError, LookupError) as exc:
            raise ReadError(f"无法使用指定编码 {encoding} 解码") from exc
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        candidates = ["utf-16"]
    elif b"\x00" in data:
        raise ReadError("无 BOM 的 UTF-16 或二进制文件，请显式指定编码")
    else:
        candidates = ["utf-8-sig", "gbk"]
    for candidate in candidates:
        try:
            return data.decode(candidate)
        except UnicodeError:
            pass
    raise ReadError("无法识别编码；支持 UTF-8、GBK、带 BOM 的 UTF-16")
