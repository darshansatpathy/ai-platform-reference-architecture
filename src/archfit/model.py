"""Load and validate the platform catalog. Schema problems are findings, not exceptions."""

from __future__ import annotations

import datetime as dt
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
EDGE_KINDS = ("sync", "async", "library")
TRUST_ZONES = ("internal", "external")
SEVERITIES = ("critical", "high", "medium", "low")


class CatalogError(Exception):
    """The catalog file cannot be read or is not valid TOML."""


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    component: str | None = None


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    kind: str
    data: str
    fallback: str | None = None
    optional: bool = False


@dataclass(frozen=True)
class Component:
    id: str
    name: str
    layer: str
    tier: int
    owner: str
    description: str
    trust_zone: str
    data_max_class: str
    availability: float
    cost_tag: str
    p95_latency_ms: int | None = None
    rto_minutes: int | None = None
    rpo_minutes: int | None = None
    runbook: str | None = None
    telemetry: tuple[str, ...] = ()
    adrs: tuple[str, ...] = ()
    entrypoint: bool = False
    egress: bool = False
    reference_impl: str | None = None
    depends_on: tuple[Edge, ...] = ()

    @property
    def external(self) -> bool:
        return self.trust_zone == "external"


@dataclass(frozen=True)
class Layer:
    id: str
    name: str
    order: int
    may_depend_on: tuple[str, ...]


@dataclass(frozen=True)
class Team:
    id: str
    responsibility: str
    contact: str


@dataclass(frozen=True)
class Waiver:
    rule: str
    component: str
    reason: str
    expires: dt.date


@dataclass
class Catalog:
    name: str
    version: str
    description: str
    policy: dict[str, Any]
    data_classes: dict[str, int]
    layers: dict[str, Layer]
    teams: dict[str, Team]
    components: dict[str, Component]
    waivers: list[Waiver] = field(default_factory=list)
    root: Path = Path(".")

    def level(self, data_class: str) -> int:
        return self.data_classes[data_class]

    def edges(self) -> list[Edge]:
        return [e for c in self.components.values() for e in c.depends_on]

    def max_rto(self, tier: int) -> int | None:
        table = self.policy.get("max_rto_minutes", {})
        value = table.get(str(tier))
        return int(value) if value is not None else None


def load(path: Path) -> tuple[Catalog | None, list[Finding]]:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogError(f"cannot read {path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise CatalogError(f"{path} is not valid TOML: {exc}") from exc
    problems: list[Finding] = []

    def bad(msg: str, comp: str | None = None) -> None:
        problems.append(Finding("FIT001", "critical", msg, comp))

    platform = raw.get("platform", {})
    for key in ("name", "version", "description"):
        if not isinstance(platform.get(key), str) or not platform.get(key):
            bad(f"[platform] needs a non-empty string {key!r}")

    data_classes = _data_classes(raw, bad)
    layers = _layers(raw, bad)
    teams = _teams(raw, bad)
    components = _components(raw, data_classes, bad)
    waivers = _waivers(raw, bad)
    if problems:
        return None, problems
    catalog = Catalog(
        name=platform["name"],
        version=platform["version"],
        description=platform["description"],
        policy=raw.get("policy", {}),
        data_classes=data_classes,
        layers=layers,
        teams=teams,
        components=components,
        waivers=waivers,
        root=path.resolve().parent.parent,
    )
    return catalog, []


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _data_classes(raw: dict[str, Any], bad: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for i, d in enumerate(raw.get("data_classes", [])):
        if not isinstance(d.get("id"), str) or not isinstance(d.get("level"), int):
            bad(f"data_classes[{i}] needs a string id and an integer level")
            continue
        out[d["id"]] = d["level"]
    if not out:
        bad("at least one [[data_classes]] is required")
    elif len(set(out.values())) != len(out):
        bad("data class levels must be distinct")
    return out


def _layers(raw: dict[str, Any], bad: Any) -> dict[str, Layer]:
    out: dict[str, Layer] = {}
    for i, d in enumerate(raw.get("layers", [])):
        if not all(
            isinstance(d.get(k), t) for k, t in (("id", str), ("name", str), ("order", int))
        ) or not isinstance(d.get("may_depend_on", []), list):
            bad(f"layers[{i}] needs id, name, order and a may_depend_on list")
            continue
        if d["id"] in out:
            bad(f"duplicate layer {d['id']!r}")
        out[d["id"]] = Layer(d["id"], d["name"], d["order"], tuple(d.get("may_depend_on", [])))
    if not out:
        bad("at least one [[layers]] is required")
    return out


def _teams(raw: dict[str, Any], bad: Any) -> dict[str, Team]:
    out: dict[str, Team] = {}
    for i, d in enumerate(raw.get("teams", [])):
        if not all(
            isinstance(d.get(k), str) and d.get(k) for k in ("id", "responsibility", "contact")
        ):
            bad(f"teams[{i}] needs id, responsibility and contact")
            continue
        if d["id"] in out:
            bad(f"duplicate team {d['id']!r}")
        out[d["id"]] = Team(d["id"], d["responsibility"], d["contact"])
    return out


def _components(raw: dict[str, Any], classes: dict[str, int], bad: Any) -> dict[str, Component]:
    out: dict[str, Component] = {}
    for i, d in enumerate(raw.get("components", [])):
        cid = d.get("id")
        label = cid if isinstance(cid, str) else f"components[{i}]"
        if not isinstance(cid, str) or not KEBAB.match(cid):
            bad(f"{label}: id must be kebab-case", None)
            continue
        if cid in out:
            bad(f"duplicate component id {cid!r}", cid)
            continue
        ok = True
        for key in ("name", "layer", "owner", "description", "cost_tag"):
            if not isinstance(d.get(key), str) or not d[key].strip():
                bad(f"{key} must be a non-empty string", cid)
                ok = False
        if d.get("tier") not in (1, 2, 3) or isinstance(d.get("tier"), bool):
            bad("tier must be 1, 2 or 3", cid)
            ok = False
        if d.get("trust_zone") not in TRUST_ZONES:
            bad(f"trust_zone must be one of {TRUST_ZONES}", cid)
            ok = False
        if d.get("data_max_class") not in classes:
            bad(f"data_max_class must be one of {sorted(classes)}", cid)
            ok = False
        a = d.get("availability")
        if not _is_num(a) or not 0 < a <= 100:
            bad("availability must be a number above 0 and at most 100", cid)
            ok = False
        for key in ("p95_latency_ms", "rto_minutes", "rpo_minutes"):
            if key in d and (not isinstance(d[key], int) or isinstance(d[key], bool) or d[key] < 0):
                bad(f"{key} must be a non-negative integer", cid)
                ok = False
        for key in ("telemetry", "adrs"):
            if key in d and (
                not isinstance(d[key], list) or not all(isinstance(x, str) for x in d[key])
            ):
                bad(f"{key} must be a list of strings", cid)
                ok = False
        for key in ("entrypoint", "egress"):
            if key in d and not isinstance(d[key], bool):
                bad(f"{key} must be true or false", cid)
                ok = False
        edges = _edges(cid, d.get("depends_on", []), classes, bad)
        if edges is None or not ok:
            continue
        out[cid] = Component(
            id=cid,
            name=d["name"],
            layer=d["layer"],
            tier=d["tier"],
            owner=d["owner"],
            description=d["description"],
            trust_zone=d["trust_zone"],
            data_max_class=d["data_max_class"],
            availability=float(a),
            cost_tag=d["cost_tag"],
            p95_latency_ms=d.get("p95_latency_ms"),
            rto_minutes=d.get("rto_minutes"),
            rpo_minutes=d.get("rpo_minutes"),
            runbook=d.get("runbook"),
            telemetry=tuple(d.get("telemetry", [])),
            adrs=tuple(d.get("adrs", [])),
            entrypoint=bool(d.get("entrypoint", False)),
            egress=bool(d.get("egress", False)),
            reference_impl=d.get("reference_impl"),
            depends_on=tuple(edges),
        )
    if not out and not any(True for _ in raw.get("components", [])):
        bad("at least one [[components]] is required")
    return out


def _edges(cid: str, raw: Any, classes: dict[str, int], bad: Any) -> list[Edge] | None:
    if not isinstance(raw, list):
        bad("depends_on must be an array of tables", cid)
        return None
    edges: list[Edge] = []
    good = True
    for j, e in enumerate(raw):
        if not isinstance(e, dict) or not isinstance(e.get("target"), str):
            bad(f"depends_on[{j}] needs a target", cid)
            good = False
            continue
        if e.get("kind") not in EDGE_KINDS:
            bad(f"depends_on[{j}] ({e['target']}): kind must be one of {EDGE_KINDS}", cid)
            good = False
        if e.get("data") not in classes:
            bad(f"depends_on[{j}] ({e['target']}): data must be one of {sorted(classes)}", cid)
            good = False
        if "fallback" in e and not isinstance(e["fallback"], str):
            bad(f"depends_on[{j}] ({e['target']}): fallback must be a component id", cid)
            good = False
        if "optional" in e and not isinstance(e["optional"], bool):
            bad(f"depends_on[{j}] ({e['target']}): optional must be true or false", cid)
            good = False
        if good:
            edges.append(
                Edge(
                    cid,
                    e["target"],
                    e["kind"],
                    e["data"],
                    e.get("fallback"),
                    bool(e.get("optional", False)),
                )
            )
    return edges if good else None


def _waivers(raw: dict[str, Any], bad: Any) -> list[Waiver]:
    out: list[Waiver] = []
    for i, w in enumerate(raw.get("waivers", [])):
        try:
            expires = w["expires"]
            if isinstance(expires, str):
                expires = dt.date.fromisoformat(expires)
            if not isinstance(expires, dt.date):
                raise TypeError
            rule, comp, reason = w["rule"], w["component"], w["reason"]
            if not all(isinstance(x, str) for x in (rule, comp, reason)):
                raise TypeError
        except (KeyError, TypeError, ValueError):
            bad(f"waivers[{i}] needs rule, component, reason and an ISO expires date")
            continue
        if len(reason.strip()) < 20:
            bad(
                f"waivers[{i}] ({rule} on {comp}): the reason must explain the exception (20+ characters)"
            )
            continue
        out.append(Waiver(rule, comp, reason.strip(), expires))
    return out
