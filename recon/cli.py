import argparse
import json
import sys
from zipfile import BadZipFile

from .readers import read_table
from .engine import run_rules


def main(argv=None):
    parser = argparse.ArgumentParser(description="本地表格核对工具")
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("read", help="读取表格并输出 JSON 摘要")
    read.add_argument("file")
    read.add_argument("--encoding", help="覆盖自动编码判断")
    run = commands.add_parser("run", help="按 YAML 规则输出对账差异")
    run.add_argument("rules")
    args = parser.parse_args(argv)
    try:
        result = run_rules(args.rules) if args.command == "run" else read_table(args.file, args.encoding).summary()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, BadZipFile) as exc:
        print(f"RECON_READ_ERROR: {exc}", file=sys.stderr)
        return 2
