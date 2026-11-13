from __future__ import annotations

import pytest

from archfit import cli
from tests.conftest import ROOT, comp

CATALOG = str(ROOT / "catalog" / "platform.toml")
FINOPS = str(ROOT / "finops" / "scenarios.toml")


def test_check_passes_on_the_real_catalog(capsys):
    assert cli.main(["check", "--catalog", CATALOG]) == 0
    assert "27 components, 13 rules: 0 findings" in capsys.readouterr().out


def test_check_fails_and_reports_on_a_broken_catalog(make_catalog, capsys):
    path = make_catalog(lambda d: comp(d, "ai-gateway").update(tier=1, availability=99.999))
    assert cli.main(["check", "--catalog", str(path)]) == 1
    out = capsys.readouterr().out
    assert "FIT005" in out and "ai-gateway" in out


def test_fail_on_threshold_and_markdown(make_catalog, capsys):
    path = make_catalog(lambda d: comp(d, "ai-gateway").update(cost_tag="Not Kebab"))
    assert (
        cli.main(["check", "--catalog", str(path)]) == 0
    )  # low severity, default threshold is medium
    capsys.readouterr()
    assert (
        cli.main(["check", "--catalog", str(path), "--fail-on", "low", "--format", "markdown"]) == 1
    )
    out = capsys.readouterr().out
    assert out.startswith("## Architecture fitness") and "| low | FIT013 |" in out


def test_waivers_are_listed_in_both_formats(make_catalog, capsys):
    def mutate(d):
        comp(d, "ai-gateway")["cost_tag"] = "Not Kebab"
        d["waivers"] = [
            {
                "rule": "FIT013",
                "component": "ai-gateway",
                "reason": "Tag migration in progress, tracked in backlog",
                "expires": "2030-01-01",
            }
        ]

    path = str(make_catalog(mutate))
    assert cli.main(["check", "--catalog", path, "--today", "2026-11-13"]) == 0
    assert "WAIVED" in capsys.readouterr().out
    assert (
        cli.main(["check", "--catalog", path, "--format", "markdown", "--today", "2026-11-13"]) == 0
    )
    assert "Waivers in force" in capsys.readouterr().out
    assert cli.main(["check", "--catalog", path, "--today", "2031-01-01", "--fail-on", "high"]) == 1


def test_missing_catalog_is_a_clean_error(tmp_path, capsys):
    assert cli.main(["check", "--catalog", str(tmp_path / "x.toml")]) == 2
    assert "error:" in capsys.readouterr().err


def test_docs_writes_then_verifies_then_detects_staleness(tmp_path, capsys):
    out = tmp_path / "gen"
    assert cli.main(["docs", "--catalog", CATALOG, "--finops", FINOPS, "--out", str(out)]) == 0
    assert len(list(out.glob("*.md"))) == 7
    assert (
        cli.main(["docs", "--catalog", CATALOG, "--finops", FINOPS, "--out", str(out), "--check"])
        == 0
    )
    (out / "components.md").write_text("tampered")
    capsys.readouterr()
    assert (
        cli.main(["docs", "--catalog", CATALOG, "--finops", FINOPS, "--out", str(out), "--check"])
        == 1
    )
    assert "components.md" in capsys.readouterr().err
    (out / "ownership.md").unlink()
    assert (
        cli.main(["docs", "--catalog", CATALOG, "--finops", FINOPS, "--out", str(out), "--check"])
        == 1
    )


def test_docs_refuses_an_invalid_catalog(make_catalog, tmp_path, capsys):
    path = make_catalog(lambda d: comp(d, "ai-gateway").update(tier=9))
    assert (
        cli.main(["docs", "--catalog", str(path), "--finops", FINOPS, "--out", str(tmp_path / "g")])
        == 1
    )


def test_cost_and_rules_commands(capsys):
    assert cli.main(["cost", "--catalog", CATALOG, "--finops", FINOPS]) == 0
    assert "Unit economics" in capsys.readouterr().out
    assert cli.main(["rules"]) == 0
    assert "FIT007" in capsys.readouterr().out
    assert cli.main(["rules", "--format", "markdown"]) == 0
    assert "## FIT005" in capsys.readouterr().out


def test_cost_with_a_bad_input_file_is_a_clean_error(tmp_path, capsys):
    f = tmp_path / "s.toml"
    f.write_text("")
    assert cli.main(["cost", "--catalog", CATALOG, "--finops", str(f)]) == 2


def test_version(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--version"])
    assert "0.1.0" in capsys.readouterr().out
