"""Fitness functions. Each rule has an id, severity, rationale and fix, and yields findings."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from archfit.graph import availability_ceiling, find_cycle, incoming
from archfit.model import KEBAB, Catalog, Finding

REPO_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


RuleFunc = Callable[[Catalog], Iterator[tuple[str | None, str]]]


@dataclass(frozen=True)
class RuleInfo:
    id: str
    title: str
    severity: str
    why: str
    fix: str
    func: RuleFunc


REGISTRY: dict[str, RuleInfo] = {}


def rule(id_: str, title: str, severity: str, why: str, fix: str) -> Callable[[RuleFunc], RuleFunc]:
    def deco(func: RuleFunc) -> RuleFunc:
        REGISTRY[id_] = RuleInfo(id_, title, severity, why, fix, func)
        return func

    return deco


def all_rules() -> list[RuleInfo]:
    return [REGISTRY[k] for k in sorted(REGISTRY)]


@rule(
    "FIT002",
    "Every reference in the catalog must resolve",
    "critical",
    "A dependency, owner, ADR or runbook that does not exist is a gap in the design, not a typo.",
    "Fix the id, or add the missing component, team, ADR or runbook.",
)
def references(c: Catalog) -> Iterator[tuple[str | None, str]]:
    adr_numbers = {p.name[:4] for p in (c.root / "docs" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md")}
    for comp in c.components.values():
        if comp.layer not in c.layers:
            yield comp.id, f"layer {comp.layer!r} is not defined"
        if comp.owner not in c.teams:
            yield comp.id, f"owner {comp.owner!r} is not a defined team"
        for n in comp.adrs:
            if n not in adr_numbers:
                yield comp.id, f"ADR {n} does not exist in docs/adr"
        if comp.runbook and not (c.root / comp.runbook).is_file():
            yield comp.id, f"runbook {comp.runbook!r} does not exist"
        if comp.reference_impl and not REPO_URL.match(comp.reference_impl):
            yield comp.id, f"reference_impl {comp.reference_impl!r} is not a GitHub repository URL"
        for e in comp.depends_on:
            if e.target not in c.components:
                yield comp.id, f"depends on unknown component {e.target!r}"
            if e.target == comp.id:
                yield comp.id, "depends on itself"
            if e.fallback is not None:
                if e.fallback not in c.components:
                    yield comp.id, f"fallback {e.fallback!r} for {e.target} is not a component"
                elif e.fallback in {e.target, comp.id}:
                    yield comp.id, f"fallback for {e.target} must be a different component"
    for w in c.waivers:
        if w.component not in c.components:
            yield w.component, f"waiver for {w.rule} names an unknown component"


@rule(
    "FIT003",
    "Dependencies must respect the layering",
    "high",
    "Layers exist so that change and failure flow one way. A lower layer calling upward couples "
    "the foundation to the products built on it.",
    "Move the call behind an interface in an allowed layer, or change the layer rules by ADR.",
)
def layering(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for comp in c.components.values():
        layer = c.layers.get(comp.layer)
        if layer is None:
            continue
        for e in comp.depends_on:
            target = c.components.get(e.target)
            if target is None or target.layer == comp.layer:
                continue
            if target.layer not in layer.may_depend_on:
                yield comp.id, f"{comp.layer} may not depend on {target.layer} ({e.target})"


@rule(
    "FIT004",
    "No cycles among synchronous or in-process dependencies",
    "high",
    "A cycle means two components cannot start, deploy or fail independently.",
    "Break the cycle with an asynchronous event or by extracting the shared part.",
)
def cycles(c: Catalog) -> Iterator[tuple[str | None, str]]:
    cycle = find_cycle(c)
    if cycle:
        yield cycle[0], "dependency cycle: " + " -> ".join(cycle)


@rule(
    "FIT005",
    "A component may not promise more availability than its hard dependencies allow",
    "high",
    "Availability multiplies along a chain of synchronous calls. A target above the product of "
    "its dependencies is arithmetically unreachable.",
    "Lower the target, add a fallback, make the call optional or asynchronous, or raise the dependency.",
)
def slo_feasibility(c: Catalog) -> Iterator[tuple[str | None, str]]:
    tol = float(c.policy.get("sync_availability_tolerance", 0.0))
    for comp in c.components.values():
        ceiling = availability_ceiling(c, comp.id)
        if comp.availability > ceiling + tol:
            yield (
                comp.id,
                (
                    f"declares {comp.availability}% but its hard dependencies allow at most {ceiling:.4f}%"
                ),
            )


@rule(
    "FIT006",
    "Data may only flow to components cleared for its classification",
    "critical",
    "Sending restricted data to a component cleared only for confidential data is a "
    "classification breach, whatever the reason.",
    "Redact before the call, route to a component cleared for the class, or reclassify with approval.",
)
def classification(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for e in c.edges():
        target = c.components.get(e.target)
        source = c.components.get(e.source)
        if target is None or source is None:
            continue
        lvl = c.level(e.data)
        if lvl > c.level(target.data_max_class):
            yield (
                e.source,
                (
                    f"sends {e.data} data to {e.target}, which is cleared only for {target.data_max_class}"
                ),
            )
        if lvl > c.level(source.data_max_class):
            yield (
                e.source,
                f"sends {e.data} data but is itself cleared only for {source.data_max_class}",
            )
        if e.fallback and e.fallback in c.components:
            fb = c.components[e.fallback]
            if lvl > c.level(fb.data_max_class):
                yield (
                    e.source,
                    (
                        f"fallback {e.fallback} is cleared only for {fb.data_max_class}, "
                        f"but the primary path carries {e.data} data"
                    ),
                )


@rule(
    "FIT007",
    "Only designated egress components may call external systems",
    "critical",
    "Every outbound path to a model provider or SaaS API is a place data can leave. Keeping the "
    "set small is what makes policy, logging and cost control complete.",
    "Route the call through an egress component, or designate the component as egress by ADR.",
)
def egress(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for comp in c.components.values():
        targets = [
            e.target
            for e in comp.depends_on
            if c.components.get(e.target) and c.components[e.target].external
        ]
        targets += [
            e.fallback
            for e in comp.depends_on
            if e.fallback and e.fallback in c.components and c.components[e.fallback].external
        ]
        if targets and not comp.egress:
            yield comp.id, f"calls external {sorted(set(targets))} but is not an egress component"
        if comp.egress and comp.external:
            yield comp.id, "an external component cannot be an egress point"


@rule(
    "FIT008",
    "A critical component may not hard-depend on a less critical one",
    "high",
    "A tier 1 service that cannot run without a tier 3 service is really tier 3.",
    "Raise the dependency's tier and its obligations, add a fallback, or make the call optional.",
)
def tier_inversion(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for comp in c.components.values():
        for e in comp.depends_on:
            target = c.components.get(e.target)
            if target is None or e.kind == "async" or e.optional or e.fallback:
                continue
            if target.tier > comp.tier:
                yield (
                    comp.id,
                    (
                        f"tier {comp.tier} hard-depends on {e.target} (tier {target.tier}) with no fallback"
                    ),
                )


@rule(
    "FIT009",
    "Tier 1 and 2 components need recovery objectives and a runbook",
    "high",
    "If nobody has written down how fast it must come back and how, it will be decided during an outage.",
    "Set rto_minutes and rpo_minutes within policy and add the runbook.",
)
def resilience(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for comp in c.components.values():
        if comp.external or comp.tier > 2:
            continue
        if comp.rto_minutes is None or comp.rpo_minutes is None:
            yield comp.id, f"tier {comp.tier} needs rto_minutes and rpo_minutes"
        else:
            limit = c.max_rto(comp.tier)
            if limit is not None and comp.rto_minutes > limit:
                yield (
                    comp.id,
                    f"rto {comp.rto_minutes} min exceeds the tier {comp.tier} limit of {limit}",
                )
        if not comp.runbook:
            yield comp.id, f"tier {comp.tier} needs a runbook"


@rule(
    "FIT010",
    "Tier 1 components need an owner reachable around the clock",
    "high",
    "A critical component owned by a business-hours team is unowned at 3 a.m.",
    "Give the owning team a pager rotation, or move ownership.",
)
def oncall(c: Catalog) -> Iterator[tuple[str | None, str]]:
    for comp in c.components.values():
        team = c.teams.get(comp.owner)
        if (
            comp.tier == 1
            and not comp.external
            and team
            and not team.contact.startswith("pagerduty:")
        ):
            yield comp.id, f"owner {team.id} has no pager (contact {team.contact!r})"


@rule(
    "FIT011",
    "Tier 1 and 2 components must emit traces, metrics and logs",
    "medium",
    "A component you cannot observe cannot meet an SLO you cannot measure.",
    "Declare the telemetry the component emits, and emit it.",
)
def observability(c: Catalog) -> Iterator[tuple[str | None, str]]:
    required = list(c.policy.get("telemetry_required", ["traces", "metrics", "logs"]))
    for comp in c.components.values():
        if comp.external or comp.tier > 2:
            continue
        missing = [t for t in required if t not in comp.telemetry]
        if missing:
            yield comp.id, f"missing telemetry: {', '.join(missing)}"


@rule(
    "FIT012",
    "Every component must be used or be an entry point",
    "low",
    "A component nothing depends on is cost and attack surface with no purpose in the design.",
    "Remove it, connect it, or mark it as an entrypoint.",
)
def orphans(c: Catalog) -> Iterator[tuple[str | None, str]]:
    refs = incoming(c)
    for comp in c.components.values():
        if not refs[comp.id] and not comp.entrypoint:
            yield comp.id, "nothing depends on it and it is not an entrypoint"


@rule(
    "FIT013",
    "Every component needs a unique, well-formed cost tag",
    "low",
    "Showback and unit economics need every cost attributed to exactly one component.",
    "Give the component a distinct kebab-case cost_tag.",
)
def cost_tags(c: Catalog) -> Iterator[tuple[str | None, str]]:
    seen: dict[str, str] = {}
    for comp in c.components.values():
        if not KEBAB.match(comp.cost_tag):
            yield comp.id, f"cost_tag {comp.cost_tag!r} must be kebab-case"
        if comp.cost_tag in seen:
            yield comp.id, f"cost_tag {comp.cost_tag!r} is already used by {seen[comp.cost_tag]}"
        seen[comp.cost_tag] = comp.id


def run_rules(catalog: Catalog) -> list[Finding]:
    out: list[Finding] = []
    for info in all_rules():
        for comp, message in info.func(catalog):
            out.append(Finding(info.id, info.severity, message, comp))
    return out
