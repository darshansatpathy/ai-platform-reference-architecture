from __future__ import annotations

import pytest

from archfit.check import check
from archfit.finops import (
    DAYS_PER_MONTH,
    FinopsError,
    Inputs,
    Prices,
    Scenario,
    evaluate,
    finops_md,
    load_inputs,
)
from archfit.graph import availability_ceiling, find_cycle, incoming
from archfit.render import critical_path
from tests.conftest import ROOT

CATALOG = ROOT / "catalog" / "platform.toml"
SCENARIOS = ROOT / "finops" / "scenarios.toml"


@pytest.fixture(scope="module")
def cat():
    report = check(CATALOG)
    assert report.catalog is not None
    return report.catalog


def test_gateway_ceiling_matches_hand_calculation(cat):
    expected = 0.9999 * 0.9995 * (1 - 0.005 * 0.005) * 100
    assert availability_ceiling(cat, "ai-gateway") == pytest.approx(expected)


def test_ceiling_ignores_optional_async_and_library_edges(cat):
    assert availability_ceiling(cat, "model-router") == 100.0  # library only
    assert availability_ceiling(cat, "eval-service") == 100.0  # async only
    web = availability_ceiling(cat, "web-assistant")
    assert web == pytest.approx(0.995 * 0.9999 * 100, rel=1e-3) or web < 99.5


def test_no_cycles_in_the_real_design(cat):
    assert find_cycle(cat) is None


def test_every_component_is_referenced_or_an_entrypoint(cat):
    refs = incoming(cat)
    assert [c for c, r in refs.items() if not r and not cat.components[c].entrypoint] == []
    assert "secondary-model-provider" in refs and refs["secondary-model-provider"] == {"ai-gateway"}


def test_critical_path_of_the_customer_assistant(cat):
    path = critical_path(cat, "web-assistant")
    assert {
        "agent-runtime",
        "ai-gateway",
        "identity-provider",
        "guardrails-service",
        "primary-model-provider",
        "secondary-model-provider",
        "network-fabric",
        "memory-service",
        "vector-store",
    } <= path
    assert "tool-registry" not in path and "private-model-endpoint" not in path  # optional
    assert "observability-stack" not in path  # asynchronous


def test_pilot_scenario_matches_hand_calculation():
    inputs = Inputs(Prices(1.0, 5.0, 1.25, 0.10), {"x": 1000.0}, [])
    s = Scenario("t", 2000, 3, 3500, 350, 0.70, 0.60)
    r = evaluate(inputs, s)
    calls = 2000 * DAYS_PER_MONTH * 3
    hit = 1050e-6 + 2450e-6 * 0.10
    miss = 1050e-6 + 2450e-6 * 1.25
    output = calls * 350 * 5e-6
    assert r.token_cost == pytest.approx(calls * (0.6 * hit + 0.4 * miss) + output)
    assert r.token_cost_without_cache == pytest.approx(calls * 3500e-6 + output)
    assert r.fixed_cost == 1000 and r.total == pytest.approx(r.token_cost + 1000)
    assert r.per_request == pytest.approx(r.total / 60000) and r.per_1k_requests == pytest.approx(
        r.per_request * 1000
    )
    assert r.cache_saving == pytest.approx(r.token_cost_without_cache - r.token_cost)
    assert 0 < r.fixed_share < 1


def test_caching_costs_more_when_nothing_hits_and_less_when_most_hit():
    inputs = Inputs(Prices(1.0, 5.0, 1.25, 0.10), {}, [])
    base = Scenario("t", 1000, 2, 4000, 200, 0.8, 0.0)
    assert evaluate(inputs, base).cache_saving < 0
    assert evaluate(inputs, base.scaled(1, 0.9)).cache_saving > 0


def test_unit_cost_falls_with_volume(cat):
    inputs = load_inputs(SCENARIOS, cat)
    s = inputs.scenarios[0]
    assert evaluate(inputs, s.scaled(4)).per_request < evaluate(inputs, s).per_request


def test_shipped_inputs_load_and_every_fixed_tag_matches_a_component(cat):
    inputs = load_inputs(SCENARIOS, cat)
    assert [s.name for s in inputs.scenarios] == ["pilot", "launch", "scale"]
    assert set(inputs.fixed) <= {c.cost_tag for c in cat.components.values()}
    assert "PLACEHOLDER" in SCENARIOS.read_text()


def test_report_marks_inputs_as_placeholders(cat):
    md = finops_md(load_inputs(SCENARIOS, cat))
    assert "Placeholder inputs" in md and "## Sensitivity" in md and "Saved by caching" in md


@pytest.mark.parametrize(
    "toml",
    [
        "",
        "[prices]\ninput_per_mtok = 1\n",
        "[prices]\ninput_per_mtok = -1\noutput_per_mtok = 1\n[[scenarios]]\nname='a'\nrequests_per_day=1\nllm_calls_per_request=1\navg_input_tokens=1\navg_output_tokens=1\ncacheable_fraction=0\ncache_hit_ratio=0\n",
        "[prices]\ninput_per_mtok = 1\noutput_per_mtok = 1\n[[scenarios]]\nname='a'\nrequests_per_day=0\nllm_calls_per_request=1\navg_input_tokens=1\navg_output_tokens=1\ncacheable_fraction=0\ncache_hit_ratio=0\n",
        "[prices]\ninput_per_mtok = 1\noutput_per_mtok = 1\n[[scenarios]]\nname='a'\nrequests_per_day=1\nllm_calls_per_request=1\navg_input_tokens=1\navg_output_tokens=1\ncacheable_fraction=1.5\ncache_hit_ratio=0\n",
        "[prices]\ninput_per_mtok = 1\noutput_per_mtok = 1\n[fixed_monthly_usd]\nx = -5\n[[scenarios]]\nname='a'\nrequests_per_day=1\nllm_calls_per_request=1\navg_input_tokens=1\navg_output_tokens=1\ncacheable_fraction=0\ncache_hit_ratio=0\n",
        "not = [valid",
    ],
)
def test_invalid_inputs_are_rejected(tmp_path, toml):
    f = tmp_path / "s.toml"
    f.write_text(toml)
    with pytest.raises(FinopsError):
        load_inputs(f)


def test_unknown_cost_tag_is_rejected(tmp_path, cat):
    f = tmp_path / "s.toml"
    f.write_text(SCENARIOS.read_text() + "\n[fixed_monthly_usd_extra]\n")
    text = SCENARIOS.read_text().replace(
        "[fixed_monthly_usd]", "[fixed_monthly_usd]\nno-such-component = 5"
    )
    f.write_text(text)
    with pytest.raises(FinopsError, match="no-such-component"):
        load_inputs(f, cat)


def test_missing_file(tmp_path):
    with pytest.raises(FinopsError):
        load_inputs(tmp_path / "missing.toml")
