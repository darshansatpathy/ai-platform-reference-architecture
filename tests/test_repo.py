"""The repository must agree with itself: generated docs are fresh, links resolve, claims are true."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

import archfit
from archfit import cli
from archfit.check import check
from tests.conftest import ROOT

MD = [
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    *(ROOT / "docs").rglob("*.md"),
]
CATALOG = tomllib.loads((ROOT / "catalog" / "platform.toml").read_text())
COMPONENTS = {c["id"]: c for c in CATALOG["components"]}


def test_generated_docs_are_current():
    assert (
        cli.main(
            [
                "docs",
                "--check",
                "--catalog",
                str(ROOT / "catalog/platform.toml"),
                "--finops",
                str(ROOT / "finops/scenarios.toml"),
                "--out",
                str(ROOT / "docs/generated"),
            ]
        )
        == 0
    )


def test_the_design_passes_its_own_fitness_functions():
    report = check(ROOT / "catalog" / "platform.toml")
    assert report.findings == [] and report.waived == []


def test_version_matches_pyproject():
    assert (
        tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
        == archfit.__version__
    )


def test_markdown_links_resolve():
    broken = []
    for f in MD:
        for m in re.finditer(r"\]\(([^)#\s][^)]*)\)", f.read_text()):
            target = m.group(1)
            if target.startswith("http"):
                continue
            if not (f.parent / target.split("#")[0]).resolve().exists():
                broken.append(f"{f.relative_to(ROOT)}: {target}")
    assert broken == []


def test_adrs_are_numbered_complete_and_used():
    adrs = sorted((ROOT / "docs" / "adr").glob("*.md"))
    assert [p.name[:4] for p in adrs] == [f"{i:04d}" for i in range(1, len(adrs) + 1)]
    for p in adrs:
        text = p.read_text()
        for heading in ("## Status", "## Context", "## Decision", "## Consequences"):
            assert heading in text, f"{p.name} lacks {heading}"
    used = {n for c in COMPONENTS.values() for n in c.get("adrs", [])}
    assert used == {p.name[:4] for p in adrs}, "every ADR should govern at least one component"


RUNBOOK_HEADINGS = [
    "## Purpose",
    "## Ownership and escalation",
    "## Recovery targets",
    "## Dependencies",
    "## Symptoms",
    "## First checks",
    "## Mitigations",
    "## After the incident",
]


def test_every_runbook_is_complete_and_matches_the_catalog():
    files = {p.stem for p in (ROOT / "docs" / "runbooks").glob("*.md")}
    declared = {cid for cid, c in COMPONENTS.items() if "runbook" in c}
    assert files == declared
    for cid in declared:
        text = (ROOT / "docs" / "runbooks" / f"{cid}.md").read_text()
        for h in RUNBOOK_HEADINGS:
            assert h in text, f"{cid} runbook lacks {h}"
        owner = COMPONENTS[cid]["owner"]
        assert f"`{owner}`" in text


def test_external_components_are_the_only_ones_without_runbooks():
    for cid, c in COMPONENTS.items():
        assert ("runbook" in c) == (c["trust_zone"] != "external"), cid


def test_risk_register_references_exist():
    text = (ROOT / "docs" / "risk-register.md").read_text()
    for cid in set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", text)):
        assert cid in COMPONENTS, f"risk register mentions unknown component {cid}"
    adr_numbers = {p.name[:4] for p in (ROOT / "docs" / "adr").glob("*.md")}
    for n in re.findall(r"ADR (\d{4})", text):
        assert n in adr_numbers
    risks = re.findall(r"^\| (R\d+) \|", text, re.M)
    assert risks == [f"R{i}" for i in range(1, len(risks) + 1)] and len(risks) >= 10


def test_every_risk_names_a_real_owner_team():
    teams = {t["id"] for t in CATALOG["teams"]}
    for line in (ROOT / "docs" / "risk-register.md").read_text().splitlines():
        if re.match(r"^\| R\d+ \|", line):
            assert line.strip("| ").split("|")[-1].strip() in teams, line


def test_readme_claims_match_the_catalog():
    readme = (ROOT / "README.md").read_text()
    assert f"{len(COMPONENTS)} components" in readme
    n_rules = len(
        re.findall(
            r"^\| FIT\d{3} \|", (ROOT / "docs/generated/fitness-functions.md").read_text(), re.M
        )
    )
    assert f"{n_rules} fitness functions" in readme
    assert len(re.findall(r"^\| FIT\d{3} \|", readme, re.M)) == n_rules
    for cmd in cli.build_parser()._subparsers._group_actions[0].choices:  # type: ignore[union-attr]
        assert f"archfit {cmd}" in readme, cmd


def test_reference_implementations_are_real_repositories_of_the_owner():
    for c in COMPONENTS.values():
        if "reference_impl" in c:
            assert c["reference_impl"].startswith("https://github.com/darshansatpathy/")


def test_all_numbers_are_flagged_as_design_targets_or_placeholders():
    assert "DESIGN TARGETS" in (ROOT / "catalog" / "platform.toml").read_text()
    assert "PLACEHOLDER" in (ROOT / "finops" / "scenarios.toml").read_text()
    assert "Placeholder inputs" in (ROOT / "docs/generated/finops.md").read_text()


@pytest.mark.parametrize("name", ["ci.yml", "codeql.yml"])
def test_workflows_exist(name):
    assert (Path(ROOT) / ".github" / "workflows" / name).exists()
