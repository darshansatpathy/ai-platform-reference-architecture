from __future__ import annotations

import pytest

from archfit.model import CatalogError, load
from tests.conftest import comp, edge


def test_real_catalog_loads(make_catalog):
    cat, problems = load(make_catalog())
    assert problems == [] and cat is not None
    assert len(cat.components) == 27 and len(cat.layers) == 6 and cat.level("restricted") == 3
    assert cat.max_rto(1) == 60 and cat.max_rto(2) == 240 and cat.max_rto(3) is None
    assert len(cat.edges()) > 40


def test_round_trip_through_the_test_writer_preserves_the_catalog(make_catalog, real):
    cat, _ = load(make_catalog())
    assert cat is not None and cat.components["ai-gateway"].egress
    assert cat.components["agent-runtime"].depends_on[0].target == "ai-gateway"


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (lambda d: comp(d, "ai-gateway").update(tier=4), "tier must be"),
        (lambda d: comp(d, "ai-gateway").update(tier=True), "tier must be"),
        (lambda d: comp(d, "ai-gateway").update(availability=120), "availability"),
        (lambda d: comp(d, "ai-gateway").update(availability="high"), "availability"),
        (lambda d: comp(d, "ai-gateway").update(id="Bad_ID"), "kebab-case"),
        (lambda d: comp(d, "ai-gateway").update(trust_zone="dmz"), "trust_zone"),
        (lambda d: comp(d, "ai-gateway").update(data_max_class="secret"), "data_max_class"),
        (lambda d: comp(d, "ai-gateway").update(rto_minutes=-1), "rto_minutes"),
        (lambda d: comp(d, "ai-gateway").update(telemetry="traces"), "telemetry"),
        (lambda d: comp(d, "ai-gateway").update(egress="yes"), "egress"),
        (lambda d: comp(d, "ai-gateway").pop("owner"), "owner"),
        (lambda d: comp(d, "ai-gateway").update(description="  "), "description"),
        (lambda d: edge(d, "ai-gateway", "identity-provider").update(kind="rpc"), "kind"),
        (lambda d: edge(d, "ai-gateway", "identity-provider").update(data="secret"), "data must"),
        (lambda d: edge(d, "ai-gateway", "identity-provider").update(optional="no"), "optional"),
        (lambda d: edge(d, "ai-gateway", "identity-provider").pop("target"), "needs a target"),
        (lambda d: d["components"].append(dict(comp(d, "ai-gateway"))), "duplicate component"),
        (lambda d: d["layers"].append(dict(d["layers"][0])), "duplicate layer"),
        (lambda d: d["teams"].append(dict(d["teams"][0])), "duplicate team"),
        (lambda d: d["data_classes"][1].update(level=0), "distinct"),
        (lambda d: d["platform"].pop("name"), "[platform]"),
        (lambda d: d.update(waivers=[{"rule": "FIT005"}]), "waivers[0]"),
        (
            lambda d: d.update(
                waivers=[
                    {
                        "rule": "FIT005",
                        "component": "ai-gateway",
                        "reason": "short",
                        "expires": "2027-01-01",
                    }
                ]
            ),
            "20+ characters",
        ),
        (
            lambda d: d.update(
                waivers=[
                    {
                        "rule": "FIT005",
                        "component": "ai-gateway",
                        "reason": "a long enough reason here",
                        "expires": "not-a-date",
                    }
                ]
            ),
            "ISO",
        ),
    ],
)
def test_schema_problems_are_findings(make_catalog, mutate, needle):
    cat, problems = load(make_catalog(mutate))
    assert cat is None
    assert any(needle in p.message for p in problems), [p.message for p in problems]
    assert all(p.rule_id == "FIT001" for p in problems)


def test_missing_and_malformed_files_raise(tmp_path):
    with pytest.raises(CatalogError):
        load(tmp_path / "nope.toml")
    bad = tmp_path / "bad.toml"
    bad.write_text("this is = = not toml")
    with pytest.raises(CatalogError):
        load(bad)


def test_empty_catalog_is_invalid(make_catalog):
    cat, problems = load(
        make_catalog(lambda d: d.update(components=[], layers=[], data_classes=[]))
    )
    assert cat is None and len(problems) >= 2
