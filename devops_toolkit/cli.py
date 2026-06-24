from __future__ import annotations

import argparse
import sys
from pathlib import Path
from .audit import audit_repository
from .baseline import filter_new_findings, write_baseline
from .config import load_config
from .reporting import render_html, render_json, render_markdown, render_text
from .sarif import render_sarif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit DevOps repositories for production-readiness issues.")
    parser.add_argument("root", nargs="?", default=".", help="Repository path to scan")
    parser.add_argument("--config", type=Path, help="Optional JSON/YAML policy configuration")
    parser.add_argument("--baseline", type=Path, help="Existing baseline JSON; only new findings are reported")
    parser.add_argument("--write-baseline", type=Path, help="Write a baseline JSON for current findings")
    parser.add_argument("--format", choices=["text", "json", "markdown", "html", "sarif"], help="Report format")
    parser.add_argument("--fail-on-high", action="store_true", help="Exit with code 2 when high/critical findings exist")
    parser.add_argument("--output", type=Path, help="Optional file path for the report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    try:
        summary = audit_repository(args.root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    summary.findings = config.policy.filter_findings(summary.findings)
    if args.write_baseline:
        write_baseline(args.write_baseline, summary.findings)
    summary.findings = filter_new_findings(summary.findings, args.baseline)

    report_format = args.format or config.default_format
    if report_format == "json":
        output = render_json(summary)
    elif report_format == "markdown":
        output = render_markdown(summary)
    elif report_format == "sarif":
        output = render_sarif(summary)
    elif report_format == "html":
        output = render_html(summary)
    else:
        output = render_text(summary)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    if args.fail_on_high and config.policy.should_fail(summary.findings):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
