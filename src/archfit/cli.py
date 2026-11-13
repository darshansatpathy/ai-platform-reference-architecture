"""archfit command line."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections.abc import Sequence
from pathlib import Path

from archfit import __version__
from archfit.check import Report, check
from archfit.finops import FinopsError, finops_md, load_inputs
from archfit.model import SEVERITIES, CatalogError
from archfit.render import GENERATED, rules_md


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="archfit", description=__doc__)
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="run the fitness functions")
    c.add_argument("--catalog", type=Path, default=Path("catalog/platform.toml"))
    c.add_argument("--fail-on", choices=SEVERITIES, default="medium")
    c.add_argument(
        "--today", type=dt.date.fromisoformat, default=None, help="override today's date (waivers)"
    )
    c.add_argument("--format", choices=["text", "markdown"], default="text")

    d = sub.add_parser("docs", help="render generated documentation")
    d.add_argument("--catalog", type=Path, default=Path("catalog/platform.toml"))
    d.add_argument("--finops", type=Path, default=Path("finops/scenarios.toml"))
    d.add_argument("--out", type=Path, default=Path("docs/generated"))
    d.add_argument("--check", action="store_true", help="fail if committed files are stale")

    k = sub.add_parser("cost", help="print the unit-economics model")
    k.add_argument("--catalog", type=Path, default=Path("catalog/platform.toml"))
    k.add_argument("--finops", type=Path, default=Path("finops/scenarios.toml"))

    r = sub.add_parser("rules", help="list the fitness functions")
    r.add_argument("--format", choices=["text", "markdown"], default="text")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "check":
            return _check(args)
        if args.cmd == "docs":
            return _docs(args)
        if args.cmd == "cost":
            return _cost(args)
        return _rules(args.format)
    except (CatalogError, FinopsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _check(args: argparse.Namespace) -> int:
    report = check(args.catalog, args.today)
    if args.format == "markdown":
        sys.stdout.write(_markdown(report))
    else:
        sys.stdout.write(_text(report))
    return 1 if report.failing(args.fail_on) else 0


def _text(report: Report) -> str:
    lines = [
        f"{f.severity.upper():8} {f.rule_id} {f.component or '-'}: {f.message}"
        for f in report.findings
    ]
    lines += [
        f"WAIVED   {f.rule_id} {f.component or '-'}: {f.message} (until {until}; {why})"
        for f, why, until in report.waived
    ]
    n = len(report.catalog.components) if report.catalog else 0
    lines.append(
        f"{n} components, {report.rules_run} rules: {len(report.findings)} findings, {len(report.waived)} waived"
    )
    return "\n".join(lines) + "\n"


def _markdown(report: Report) -> str:
    n = len(report.catalog.components) if report.catalog else 0
    out = [
        f"## Architecture fitness\n\n{n} components checked by {report.rules_run} rules: "
        f"**{len(report.findings)} findings**, {len(report.waived)} waived.\n"
    ]
    if report.findings:
        out.append("\n| Severity | Rule | Component | Finding |\n|---|---|---|---|\n")
        out += [
            f"| {f.severity} | {f.rule_id} | {f.component or ''} | {f.message} |\n"
            for f in report.findings
        ]
    if report.waived:
        out.append(
            "\n### Waivers in force\n\n| Rule | Component | Expires | Reason |\n|---|---|---|---|\n"
        )
        out += [
            f"| {f.rule_id} | {f.component or ''} | {until} | {why} |\n"
            for f, why, until in report.waived
        ]
    return "".join(out)


def _docs(args: argparse.Namespace) -> int:
    report = check(args.catalog)
    if report.catalog is None:
        print("catalog is invalid; run `archfit check`", file=sys.stderr)
        return 1
    files = {name: fn(report.catalog) for name, fn in GENERATED.items()}
    files["fitness-functions.md"] = rules_md()
    files["finops.md"] = finops_md(load_inputs(args.finops, report.catalog))
    stale = []
    for name, text in files.items():
        target = args.out / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    if args.check:
        if stale:
            print(
                "stale generated files (run `archfit docs`): " + ", ".join(sorted(stale)),
                file=sys.stderr,
            )
            return 1
        print(f"{len(files)} generated files are current")
    else:
        print(f"wrote {len(files)} files to {args.out}")
    return 0


def _cost(args: argparse.Namespace) -> int:
    report = check(args.catalog)
    sys.stdout.write(finops_md(load_inputs(args.finops, report.catalog)))
    return 0


def _rules(fmt: str) -> int:
    from archfit.rules import all_rules

    if fmt == "markdown":
        sys.stdout.write(rules_md())
    else:
        for r in all_rules():
            sys.stdout.write(f"{r.id}  {r.severity:8} {r.title}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
