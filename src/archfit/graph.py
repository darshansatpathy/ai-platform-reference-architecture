"""Graph analysis over the catalog: cycles and availability ceilings."""

from __future__ import annotations

from archfit.model import Catalog, Edge

HARD_KINDS = ("sync",)


def sync_edges(catalog: Catalog) -> list[Edge]:
    return [
        e
        for e in catalog.edges()
        if e.kind in {"sync", "library"} and e.target in catalog.components
    ]


def find_cycle(catalog: Catalog) -> list[str] | None:
    """Return one dependency cycle among synchronous and library edges, or None."""
    graph: dict[str, list[str]] = {c: [] for c in catalog.components}
    for e in sync_edges(catalog):
        graph[e.source].append(e.target)
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph[node]):
            if state.get(nxt) == 1:
                return [*stack[stack.index(nxt) :], nxt]
            if state.get(nxt) is None and (found := visit(nxt)) is not None:
                return found
        stack.pop()
        state[node] = 2
        return None

    for start in sorted(graph):
        if state.get(start) is None and (found := visit(start)) is not None:
            return found
    return None


def availability_ceiling(catalog: Catalog, component_id: str) -> float:
    """Best availability (percent) the component can promise given its hard dependencies.

    A hard dependency is a synchronous, non-optional call. With a fallback, the dependency is
    only down when both it and the fallback are down. Optional, asynchronous and in-process
    library dependencies do not count: the request can succeed without them.
    """
    ceiling = 1.0
    for e in catalog.components[component_id].depends_on:
        target = catalog.components.get(e.target)
        if target is None or e.kind != "sync" or e.optional:
            continue
        a = target.availability / 100.0
        if e.fallback and e.fallback in catalog.components:
            b = catalog.components[e.fallback].availability / 100.0
            a = 1.0 - (1.0 - a) * (1.0 - b)
        ceiling *= a
    return ceiling * 100.0


def incoming(catalog: Catalog) -> dict[str, set[str]]:
    """Who depends on each component, counting fallback references."""
    refs: dict[str, set[str]] = {c: set() for c in catalog.components}
    for e in catalog.edges():
        if e.target in refs:
            refs[e.target].add(e.source)
        if e.fallback and e.fallback in refs:
            refs[e.fallback].add(e.source)
    return refs
