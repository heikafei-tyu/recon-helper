RED, GREEN, YELLOW, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[0m"


def colorize(text, status, enabled=True):
    if not enabled:
        return str(text)
    color = (
        RED
        if status in ("mismatch", "left_only", "right_only")
        else GREEN
        if status in ("equal", "within_tolerance")
        else YELLOW
    )
    return f"{color}{text}{RESET}"


def format_difference(row, enabled=True):
    return colorize(
        f"[{row.get('status')}] {row.get('column', '')}: {row.get('left_value', '')} -> {row.get('right_value', '')} (差值 {row.get('difference', '')})",
        row.get("status"),
        enabled,
    )


def status_icon(status):
    return {"mismatch": "!", "left_only": "<", "right_only": ">", "equal": "="}.get(status, "?")


def compact_difference(row, enabled=True):
    return colorize(
        f"{status_icon(row.get('status'))} {row.get('key', '')} {row.get('column', '')}", row.get("status"), enabled
    )


def print_report(rows, enabled=True, stream=None):
    import sys

    target = stream or sys.stdout
    text = "\n".join(format_difference(row, enabled) for row in rows)
    if text:
        target.write(text + "\n")
    return len(rows)
