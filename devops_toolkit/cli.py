import argparse
from pathlib import Path

from .audit import run_audit
from .reporting import format_json_report, format_text_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and validate a DevOps repository.")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], help="Repository root to scan.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when warnings are found.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--include-info", action="store_true", help="Include informational findings in text output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_audit(args.root)

    if args.json:
        print(format_json_report(report))
    else:
        print(format_text_report(report, include_info=args.include_info))

    has_warnings = any(finding.severity == "warning" for finding in report.findings)
    return 1 if args.strict and has_warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
