RED, GREEN, YELLOW, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[0m"
def colorize(text, status, enabled=True):
    if not enabled:
        return str(text)
    color = RED if status in ("mismatch", "left_only", "right_only") else GREEN if status in ("equal", "within_tolerance") else YELLOW
    return f"{color}{text}{RESET}"
def format_difference(row, enabled=True):
    return colorize(f"[{row.get('status')}] {row.get('column', '')}: {row.get('left_value', '')} -> {row.get('right_value', '')} (差值 {row.get('difference', '')})", row.get("status"), enabled)
