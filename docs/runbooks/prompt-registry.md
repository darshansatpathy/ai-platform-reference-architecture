# Runbook: Prompt and config registry (`prompt-registry`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Versioned prompts, tool descriptions and routing rules, promoted through environments.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.9% (design target)
- RTO: 30 minutes; RPO: 5 minutes

## Dependencies

Depends on: `cicd-pipeline` (async)

Used by: `agent-runtime`, `model-router`

## Symptoms

- Services serve a stale or wrong prompt
- Promotion pipeline fails

## First checks

1. Compare the version served with the version promoted
2. Check the cache TTL in the consuming services

## Mitigations

- Re-promote the last good version
- Services keep the last good version in memory; confirm before restarting them

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
