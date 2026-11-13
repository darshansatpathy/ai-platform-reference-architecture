# ADR 0004: One AI gateway is the only path to models; more than one provider behind it

## Status

Accepted

## Context

Direct calls from applications to model providers scatter credentials, make cost and policy
invisible, and lock each application to one vendor. Restricted data must never go to an
external provider, and that is much easier to guarantee at one choke point.

## Decision

All model calls pass through `ai-gateway`, which authenticates callers, applies per-caller
token budgets, routes with `model-router`, calls `guardrails-service` and logs every request.
Two external providers are configured so that an outage at one is a routing change, not an
incident (`secondary-model-provider` is the declared fallback). Restricted-class requests go to
`private-model-endpoint` and the gateway has no fallback to an external provider for them.
The gateway and the tool registry are the only egress components, enforced by the fitness
function `FIT007`.

## Consequences

- The gateway is the most critical component on the request path: it is tier 1 with the
  tightest recovery targets.
- Multi-provider means a model-comparison and evaluation burden, covered by ADR 0005.
- Failing over cannot send restricted data outward. When the private endpoint is down,
  restricted requests fail with a clear error.
