import logging


def configure(level="WARNING"):
    """Configure predictable CLI logging without changing library defaults."""
    numeric = getattr(logging, str(level).upper(), None)
    if not isinstance(numeric, int):
        raise ValueError(f"未知日志级别：{level}")
    logging.basicConfig(level=numeric, format="%(levelname)s %(name)s: %(message)s")
    return logging.getLogger("recon")
