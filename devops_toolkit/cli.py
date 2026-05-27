from __future__ import annotations

import argparse
import sys
from pathlib import Path
from .audit import audit_repository
from .reporting import render_json, render_markdown, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit DevOps repositories for production-readiness issues.")
    parser.add_argument("root", nargs="?", default=".", help="Repository path to scan")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Report format")
    parser.add_argument("--fail-on-high", action="store_true", help="Exit with code 2 when high/critical findings exist")
    parser.add_argument("--output", type=Path, help="Optional file path for the report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = audit_repository(args.root)
    if args.format == "json":
        output = render_json(summary)
    elif args.format == "markdown":
        output = render_markdown(summary)
    else:
        output = render_text(summary)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    if args.fail_on_high and summary.failed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
