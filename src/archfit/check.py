"""Run the rules, apply waivers (which expire), and summarise."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from archfit.model import SEVERITIES, Catalog, Finding, load
from archfit.rules import all_rules, run_rules


@dataclass
class Report:
    catalog: Catalog | None
    findings: list[Finding] = field(default_factory=list)
    waived: list[tuple[Finding, str, dt.date]] = field(default_factory=list)
    rules_run: int = 0

    def failing(self, fail_on: str = "medium") -> list[Finding]:
        limit = SEVERITIES.index(fail_on)
        return [f for f in self.findings if SEVERITIES.index(f.severity) <= limit]


def check(path: Path, today: dt.date | None = None) -> Report:
    today = today or dt.date.today()
    catalog, schema = load(path)
    if catalog is None:
        return Report(None, schema, rules_run=1)
    findings: list[Finding] = []
    waived: list[tuple[Finding, str, dt.date]] = []
    waivers = {(w.rule, w.component): w for w in catalog.waivers}
    for f in run_rules(catalog):
        w = waivers.get((f.rule_id, f.component or ""))
        if w is not None and w.expires >= today:
            waived.append((f, w.reason, w.expires))
        else:
            findings.append(f)
    for w in catalog.waivers:
        if w.expires < today:
            findings.append(
                Finding(
                    "FIT000",
                    "high",
                    f"waiver for {w.rule} expired on {w.expires.isoformat()}",
                    w.component,
                )
            )
    findings.sort(
        key=lambda f: (SEVERITIES.index(f.severity), f.rule_id, f.component or "", f.message)
    )
    return Report(catalog, findings, waived, rules_run=len(all_rules()) + 1)
