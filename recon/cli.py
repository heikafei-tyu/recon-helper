import argparse
import json
import sys
from zipfile import BadZipFile

from .benchmark import benchmark
from .engine import run_rules
from .readers import read_table
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
    bench.add_argument("--progress", action="store_true")
    bench.add_argument("--json-out")
    report = commands.add_parser("report", help="生成 Excel 差异报告")
    report.add_argument("rules")
    report.add_argument("--out", default="output/reconciliation.xlsx")
    report.add_argument("--incremental", action="store_true")
    report.add_argument("--force", action="store_true")
    report.add_argument("--html")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            run_rules(args.rules)
            result = {"valid": True, "rules": args.rules}
        elif args.command == "run":
            result = run_rules(args.rules)
        elif args.command == "bench":
            result = benchmark(args.file, args.key, not args.no_duplicate_check, args.timeout, args.progress)
            if args.json_out:
                from pathlib import Path
                Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        elif args.command == "report":
            if args.html:
                from .report import create_html_report
                result = create_html_report(args.rules, args.html)
            else:
                result = create_report(args.rules, args.out, args.incremental, args.force)
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
