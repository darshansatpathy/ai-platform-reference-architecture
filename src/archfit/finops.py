"""A small unit-economics model: tokens, caching and fixed platform cost per request.

All inputs live in finops/scenarios.toml and are placeholders. The point of the model is the
*shape* of the cost: how it splits between tokens and fixed platform cost, what caching saves,
and how sensitive the unit cost is to volume and cache hit rate.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from archfit.model import Catalog

DAYS_PER_MONTH = 30


class FinopsError(Exception):
    """The FinOps inputs are missing or inconsistent."""


@dataclass(frozen=True)
class Prices:
    input_per_mtok: float
    output_per_mtok: float
    cache_write_multiplier: float
    cache_read_multiplier: float


@dataclass(frozen=True)
class Scenario:
    name: str
    requests_per_day: float
    llm_calls_per_request: float
    avg_input_tokens: float
    avg_output_tokens: float
    cacheable_fraction: float
    cache_hit_ratio: float

    def scaled(self, volume: float = 1.0, hit: float | None = None) -> Scenario:
        return Scenario(
            self.name,
            self.requests_per_day * volume,
            self.llm_calls_per_request,
            self.avg_input_tokens,
            self.avg_output_tokens,
            self.cacheable_fraction,
            self.cache_hit_ratio if hit is None else hit,
        )


@dataclass(frozen=True)
class Inputs:
    prices: Prices
    fixed: dict[str, float]
    scenarios: list[Scenario]


@dataclass(frozen=True)
class Result:
    scenario: str
    requests_per_month: float
    token_cost: float
    token_cost_without_cache: float
    fixed_cost: float

    @property
    def total(self) -> float:
        return self.token_cost + self.fixed_cost

    @property
    def per_request(self) -> float:
        return self.total / self.requests_per_month

    @property
    def per_1k_requests(self) -> float:
        return self.per_request * 1000

    @property
    def cache_saving(self) -> float:
        return self.token_cost_without_cache - self.token_cost

    @property
    def fixed_share(self) -> float:
        return self.fixed_cost / self.total if self.total else 0.0


def load_inputs(path: Path, catalog: Catalog | None = None) -> Inputs:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise FinopsError(f"cannot read {path}: {exc}") from exc
    try:
        p = raw["prices"]
        prices = Prices(
            float(p["input_per_mtok"]),
            float(p["output_per_mtok"]),
            float(p.get("cache_write_multiplier", 1.25)),
            float(p.get("cache_read_multiplier", 0.10)),
        )
        scenarios = [
            Scenario(
                s["name"],
                float(s["requests_per_day"]),
                float(s["llm_calls_per_request"]),
                float(s["avg_input_tokens"]),
                float(s["avg_output_tokens"]),
                float(s["cacheable_fraction"]),
                float(s["cache_hit_ratio"]),
            )
            for s in raw["scenarios"]
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise FinopsError(f"scenarios file is incomplete: {exc!r}") from exc
    fixed = {k: float(v) for k, v in raw.get("fixed_monthly_usd", {}).items()}
    if any(v < 0 for v in fixed.values()) or any(
        x < 0
        for x in (
            prices.input_per_mtok,
            prices.output_per_mtok,
            prices.cache_write_multiplier,
            prices.cache_read_multiplier,
        )
    ):
        raise FinopsError("prices and costs must not be negative")
    for s in scenarios:
        if s.requests_per_day <= 0 or s.llm_calls_per_request <= 0:
            raise FinopsError(f"scenario {s.name!r}: volumes must be positive")
        if not (0 <= s.cacheable_fraction <= 1 and 0 <= s.cache_hit_ratio <= 1):
            raise FinopsError(f"scenario {s.name!r}: fractions must be between 0 and 1")
    if catalog is not None:
        tags = {c.cost_tag for c in catalog.components.values()}
        unknown = sorted(set(fixed) - tags)
        if unknown:
            raise FinopsError(f"fixed_monthly_usd has tags that match no component: {unknown}")
    return Inputs(prices, fixed, scenarios)


def evaluate(inputs: Inputs, s: Scenario) -> Result:
    pr = inputs.prices
    calls = s.requests_per_day * DAYS_PER_MONTH * s.llm_calls_per_request
    cached = s.avg_input_tokens * s.cacheable_fraction
    fresh = s.avg_input_tokens - cached
    in_rate = pr.input_per_mtok / 1_000_000
    out_cost = calls * s.avg_output_tokens * pr.output_per_mtok / 1_000_000
    per_call_hit = fresh * in_rate + cached * in_rate * pr.cache_read_multiplier
    per_call_miss = fresh * in_rate + cached * in_rate * pr.cache_write_multiplier
    token_cost = (
        calls * (s.cache_hit_ratio * per_call_hit + (1 - s.cache_hit_ratio) * per_call_miss)
        + out_cost
    )
    without = calls * s.avg_input_tokens * in_rate + out_cost
    return Result(
        s.name, s.requests_per_day * DAYS_PER_MONTH, token_cost, without, sum(inputs.fixed.values())
    )


def finops_md(inputs: Inputs) -> str:
    def usd(x: float) -> str:
        return f"${x:,.0f}" if abs(x) >= 100 else f"${x:,.2f}"

    out = [
        "<!-- Generated by `archfit cost` from finops/scenarios.toml. Do not edit by hand. -->\n\n",
        "# Unit economics\n\n> **Placeholder inputs.** Every price, volume and fixed cost in "
        "`finops/scenarios.toml` is an illustrative assumption. The outputs show how cost behaves, not "
        "what any real deployment costs.\n\n",
        "## Scenarios\n\n",
        "| Scenario | Requests / month | Token cost | Fixed platform cost | Total / month | Per 1,000 requests | Fixed share | Saved by caching |\n",
        "|---|---|---|---|---|---|---|---|\n",
    ]
    results = [evaluate(inputs, s) for s in inputs.scenarios]
    for r in results:
        out.append(
            f"| {r.scenario} | {r.requests_per_month:,.0f} | {usd(r.token_cost)} | {usd(r.fixed_cost)} | "
            f"{usd(r.total)} | {usd(r.per_1k_requests)} | {r.fixed_share:.0%} | {usd(r.cache_saving)} |\n"
        )
    out.append(
        "\n## Sensitivity\n\nCost per 1,000 requests as volume and cache hit ratio change.\n\n"
    )
    out.append(
        "| Scenario | Volume x0.5 | Volume x1 | Volume x2 | Volume x4 | Hit ratio 0% | Hit ratio 50% | Hit ratio 90% |\n"
    )
    out.append("|---|---|---|---|---|---|---|---|\n")
    for s in inputs.scenarios:
        vol = [evaluate(inputs, s.scaled(v)).per_1k_requests for v in (0.5, 1, 2, 4)]
        hit = [evaluate(inputs, s.scaled(1, h)).per_1k_requests for h in (0.0, 0.5, 0.9)]
        out.append(f"| {s.name} | " + " | ".join(usd(x) for x in [*vol, *hit]) + " |\n")
    out.append(
        "\n## Reading it\n\n- **Fixed cost dominates at low volume.** The platform has to exist before the first "
        "request, so unit cost falls steeply as traffic grows.\n"
        "- **Caching matters when the prefix is large and stable.** It reduces the input-token share "
        "only; output tokens are unaffected. At a very low hit ratio caching costs slightly more than "
        "not caching, because cache writes carry a premium.\n"
        "- **Cost per request multiplies with agent turns.** `llm_calls_per_request` is the lever to "
        "watch; a budget on turns is a budget on cost.\n"
    )
    out.append("\n## Fixed cost by component\n\n| Cost tag | Monthly |\n|---|---|\n")
    for tag, v in sorted(inputs.fixed.items(), key=lambda kv: -kv[1]):
        out.append(f"| `{tag}` | {usd(v)} |\n")
    out.append(f"| **Total** | **{usd(sum(inputs.fixed.values()))}** |\n")
    return "".join(out)
