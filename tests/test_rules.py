"""Every fitness function must pass on the real design and fail on a deliberately broken copy."""

from __future__ import annotations

import datetime as dt

import pytest

from archfit.check import check
from archfit.rules import all_rules
from tests.conftest import comp, edge

TODAY = dt.date(2026, 11, 13)


def run(make_catalog, mutate=None, today=TODAY):
    return check(make_catalog(mutate), today)


def ids(report):
    return {(f.rule_id, f.component) for f in report.findings}


def test_the_real_design_passes_every_rule(make_catalog):
    report = run(make_catalog)
    assert report.findings == [] and report.waived == []
    assert report.rules_run == len(all_rules()) + 1 == 13


def _unknown_dep(d):
    comp(d, "web-assistant")["depends_on"].append(
        {"target": "ghost", "kind": "sync", "data": "internal"}
    )


def _self_dep(d):
    comp(d, "web-assistant")["depends_on"].append(
        {"target": "web-assistant", "kind": "sync", "data": "internal"}
    )


def _same_fallback(d):
    edge(d, "ai-gateway", "primary-model-provider")["fallback"] = "primary-model-provider"


def _lower_layer_calls_up(d):
    comp(d, "identity-provider")["depends_on"].append(
        {"target": "agent-runtime", "kind": "async", "data": "internal"}
    )


def _sync_cycle(d):
    comp(d, "network-fabric").setdefault("depends_on", []).append(
        {"target": "identity-provider", "kind": "sync", "data": "internal"}
    )


def _library_cycle(d):
    comp(d, "prompt-registry")["depends_on"].append(
        {"target": "model-router", "kind": "library", "data": "internal"}
    )


def _restricted_to_provider(d):
    edge(d, "ai-gateway", "primary-model-provider")["data"] = "restricted"


def _fallback_less_cleared(d):
    comp(d, "secondary-model-provider")["data_max_class"] = "internal"


def _source_not_cleared(d):
    comp(d, "agent-runtime")["data_max_class"] = "internal"


def _agent_calls_saas(d):
    comp(d, "agent-runtime")["depends_on"].append(
        {"target": "enterprise-saas-apis", "kind": "async", "data": "internal"}
    )


def _external_fallback_without_egress(d):
    edge(d, "tool-registry", "enterprise-saas-apis")["fallback"] = "secondary-model-provider"
    comp(d, "tool-registry")["egress"] = False


def _external_egress(d):
    comp(d, "primary-model-provider")["egress"] = True


CASES = [
    ("FIT002", "web-assistant", _unknown_dep, "unknown component"),
    ("FIT002", "web-assistant", _self_dep, "depends on itself"),
    ("FIT002", "ai-gateway", _same_fallback, "different component"),
    (
        "FIT002",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(owner="nobody"),
        "not a defined team",
    ),
    ("FIT002", "ai-gateway", lambda d: comp(d, "ai-gateway").update(layer="space"), "not defined"),
    (
        "FIT002",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(adrs=["0099"]),
        "does not exist",
    ),
    (
        "FIT002",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(runbook="docs/runbooks/none.md"),
        "does not exist",
    ),
    (
        "FIT002",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(reference_impl="ftp://x/y"),
        "GitHub repository",
    ),
    ("FIT003", "identity-provider", _lower_layer_calls_up, "may not depend on"),
    ("FIT004", "identity-provider", _sync_cycle, "dependency cycle"),
    ("FIT004", "model-router", _library_cycle, "dependency cycle"),
    (
        "FIT005",
        "web-assistant",
        lambda d: comp(d, "web-assistant").update(availability=99.9),
        "allow at most",
    ),
    (
        "FIT005",
        "ai-gateway",
        lambda d: comp(d, "identity-provider").update(availability=99.0),
        "allow at most",
    ),
    ("FIT006", "ai-gateway", _restricted_to_provider, "cleared only for confidential"),
    ("FIT006", "ai-gateway", _fallback_less_cleared, "fallback"),
    ("FIT006", "agent-runtime", _source_not_cleared, "is itself cleared"),
    ("FIT007", "agent-runtime", _agent_calls_saas, "not an egress"),
    ("FIT007", "tool-registry", _external_fallback_without_egress, "not an egress"),
    ("FIT007", "primary-model-provider", _external_egress, "external component cannot"),
    (
        "FIT008",
        "web-assistant",
        lambda d: comp(d, "identity-provider").update(tier=3),
        "hard-depends",
    ),
    (
        "FIT009",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").pop("rto_minutes"),
        "needs rto_minutes",
    ),
    ("FIT009", "ai-gateway", lambda d: comp(d, "ai-gateway").update(rto_minutes=120), "exceeds"),
    ("FIT009", "ai-gateway", lambda d: comp(d, "ai-gateway").pop("runbook"), "needs a runbook"),
    ("FIT010", "ai-gateway", lambda d: d["teams"][0].update(contact="slack:#platform"), "no pager"),
    (
        "FIT011",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(telemetry=["logs"]),
        "traces, metrics",
    ),
    (
        "FIT012",
        "lonely",
        lambda d: d["components"].append(
            {
                **{
                    k: v
                    for k, v in comp(d, "data-catalog").items()
                    if k not in {"id", "depends_on", "cost_tag", "runbook"}
                },
                "id": "lonely",
                "cost_tag": "lonely",
                "depends_on": [],
            }
        ),
        "nothing depends",
    ),
    (
        "FIT013",
        "ai-gateway",
        lambda d: comp(d, "ai-gateway").update(cost_tag="Not Kebab"),
        "kebab-case",
    ),
    (
        "FIT013",
        "model-router",
        lambda d: comp(d, "model-router").update(cost_tag="ai-gateway"),
        "already used",
    ),
]


@pytest.mark.parametrize(
    ("rule_id", "component", "mutate", "needle"),
    CASES,
    ids=[f"{c[0]}-{i}" for i, c in enumerate(CASES)],
)
def test_rule_fires_on_a_broken_design(make_catalog, rule_id, component, mutate, needle):
    report = run(make_catalog, mutate)
    hits = [f for f in report.findings if f.rule_id == rule_id and f.component == component]
    assert hits, f"{rule_id} did not fire for {component}; got {ids(report)}"
    assert any(needle in f.message for f in hits), [f.message for f in hits]


def test_every_rule_has_a_failing_case():
    covered = {c[0] for c in CASES}
    assert covered == {r.id for r in all_rules()}


def test_a_valid_alternative_clears_the_availability_finding(make_catalog):
    """Raising the target is rejected, but making the call optional removes the constraint."""

    def raise_target(d):
        comp(d, "web-assistant").update(availability=99.9)

    def raise_and_decouple(d):
        raise_target(d)
        edge(d, "web-assistant", "agent-runtime")["kind"] = "async"
        edge(d, "web-assistant", "identity-provider")["kind"] = "async"

    assert ("FIT005", "web-assistant") in ids(run(make_catalog, raise_target))
    assert ("FIT005", "web-assistant") not in ids(run(make_catalog, raise_and_decouple))


def test_a_fallback_is_what_makes_the_gateway_target_feasible(make_catalog):
    def drop_fallback(d):
        edge(d, "ai-gateway", "primary-model-provider").pop("fallback")
        comp(d, "ai-gateway")["availability"] = 99.95

    assert ("FIT005", "ai-gateway") in ids(run(make_catalog, drop_fallback))


def test_findings_are_sorted_by_severity(make_catalog):
    def two(d):
        comp(d, "ai-gateway")["cost_tag"] = "Bad Tag"
        edge(d, "ai-gateway", "primary-model-provider")["data"] = "restricted"

    sev = [f.severity for f in run(make_catalog, two).findings]
    assert sev == sorted(sev, key=("critical", "high", "medium", "low").index)


def test_schema_errors_stop_the_other_rules(make_catalog):
    report = run(make_catalog, lambda d: comp(d, "ai-gateway").update(tier=9))
    assert report.catalog is None and {f.rule_id for f in report.findings} == {"FIT001"}


def waiver(**kw):
    base = {
        "rule": "FIT013",
        "component": "ai-gateway",
        "reason": "Tag migration in progress, tracked in the platform backlog",
        "expires": "2027-02-01",
    }
    return {**base, **kw}


def test_a_waiver_suppresses_and_is_reported(make_catalog):
    def mutate(d):
        comp(d, "ai-gateway")["cost_tag"] = "Not Kebab"
        d["waivers"] = [waiver()]

    report = run(make_catalog, mutate)
    assert report.findings == [] and len(report.waived) == 1
    finding, reason, until = report.waived[0]
    assert finding.rule_id == "FIT013" and "migration" in reason and until == dt.date(2027, 2, 1)


def test_an_expired_waiver_fails_the_build_again(make_catalog):
    def mutate(d):
        comp(d, "ai-gateway")["cost_tag"] = "Not Kebab"
        d["waivers"] = [waiver(expires="2026-11-12")]

    report = run(make_catalog, mutate)
    assert {"FIT000", "FIT013"} <= {f.rule_id for f in report.findings}


def test_a_waiver_is_valid_on_its_expiry_day(make_catalog):
    def mutate(d):
        comp(d, "ai-gateway")["cost_tag"] = "Not Kebab"
        d["waivers"] = [waiver(expires="2026-11-13")]

    assert run(make_catalog, mutate).findings == []


def test_a_waiver_only_covers_its_own_component_and_rule(make_catalog):
    def mutate(d):
        comp(d, "ai-gateway")["cost_tag"] = "Not Kebab"
        comp(d, "model-router")["cost_tag"] = "Also Bad"
        d["waivers"] = [waiver()]

    report = run(make_catalog, mutate)
    assert ("FIT013", "model-router") in ids(report) and ("FIT013", "ai-gateway") not in ids(report)


def test_a_waiver_for_an_unknown_component_is_flagged(make_catalog):
    report = run(make_catalog, lambda d: d.update(waivers=[waiver(component="ghost")]))
    assert any(f.rule_id == "FIT002" and "unknown component" in f.message for f in report.findings)


def test_failing_threshold(make_catalog):
    report = run(make_catalog, lambda d: comp(d, "ai-gateway").update(cost_tag="Not Kebab"))
    assert report.failing("low") and not report.failing("medium")
