# ADR 0009: Cost is allocated to a component and a caller, and reported per request

## Status

Accepted

## Context

AI cost is mostly variable (tokens) and driven by design choices such as how many model calls
an agent makes. Without attribution, the bill is a single number nobody can act on.

## Decision

Every component has a unique `cost_tag` (`FIT013`). The gateway attributes token spend to the
calling identity and use case. `cost-management` joins both to produce showback by component
and cost per request. The model in `finops/scenarios.toml` is the planning view: token cost,
fixed platform cost, caching savings and sensitivity to volume and agent turns. Budgets on
turns and tokens in the agent runtime are the enforcement mechanism.

## Consequences

- Teams see the cost of their design choices, for example three model calls per request instead
  of one.
- The planning model is only as good as its inputs, which in this repository are placeholders.
  Replace them with measured values before using the outputs for decisions.
- Tagging discipline is a prerequisite and is checked in the catalog, not left to convention.
