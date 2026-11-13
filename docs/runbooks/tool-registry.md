# Runbook: Tool registry (MCP) (`tool-registry`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Catalogue and access broker for tools exposed to agents.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.9% (design target)
- RTO: 120 minutes; RPO: 15 minutes

## Dependencies

Depends on: `identity-provider` (sync), `secrets-manager` (sync), `enterprise-saas-apis` (sync, optional), `observability-stack` (async)

Used by: `agent-runtime`

## Symptoms

- Agents cannot find or call tools
- Tool calls fail authentication

## First checks

1. Check secrets-manager reachability
2. Check for expired credentials for a downstream SaaS

## Mitigations

- Disable the failing tool so agents degrade gracefully
- Rotate the credential and re-register the tool

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
