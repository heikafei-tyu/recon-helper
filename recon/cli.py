import argparse
import json
import sys
from zipfile import BadZipFile

from .readers import read_table
from .engine import run_rules
from .benchmark import benchmark
from .report import create_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="本地表格核对工具")
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("read", help="读取表格并输出 JSON 摘要")
    read.add_argument("file")
    read.add_argument("--encoding", help="覆盖自动编码判断")
    read.add_argument("--sheet-name")
    read.add_argument("--sheet-index", type=int, default=0)
    run = commands.add_parser("run", help="按 YAML 规则输出对账差异")
    run.add_argument("rules")
    validate = commands.add_parser("validate", help="预检查规则和输入字段")
    validate.add_argument("rules")
    bench = commands.add_parser("bench", help="流式统计 CSV 性能")
    bench.add_argument("file", nargs="?", default="examples/orders.csv")
    bench.add_argument("--key", default="id")
    bench.add_argument("--no-duplicate-check", action="store_true")
    bench.add_argument("--timeout", type=float)
    report = commands.add_parser("report", help="生成 Excel 差异报告")
    report.add_argument("rules")
    report.add_argument("--out", default="output/reconciliation.xlsx")
    report.add_argument("--incremental", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            run_rules(args.rules)
            result = {"valid": True, "rules": args.rules}
        elif args.command == "run":
            result = run_rules(args.rules)
        elif args.command == "bench":
            result = benchmark(args.file, args.key, not args.no_duplicate_check, args.timeout)
        elif args.command == "report":
            result = create_report(args.rules, args.out, args.incremental)
        else:
            result = read_table(args.file, args.encoding, args.sheet_name, args.sheet_index).summary()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except TimeoutError as exc:
        print(f"RECON_TIMEOUT: {exc}", file=sys.stderr)
        return 2
    except (ValueError, OSError, BadZipFile) as exc:
        code = "RECON_READ_ERROR" if args.command == "read" else "RECON_RULE_ERROR" if args.command == "run" else "RECON_REPORT_ERROR" if args.command == "report" else "RECON_BENCH_ERROR"
        print(f"{code}: {exc}", file=sys.stderr)
        return 2
