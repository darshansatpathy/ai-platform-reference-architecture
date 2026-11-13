# Runbook: Observability stack (`observability-stack`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Traces, metrics and logs with redaction and retention.

## Ownership and escalation

- Owner: `sre-team` (owns observability, networking and delivery pipelines)
- Contact: `pagerduty:sre-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `network-fabric` (sync)

Used by: `agent-runtime`, `ai-gateway`, `batch-pipelines`, `cost-management`, `eval-service`, `guardrails-service`, `human-review-inbox`, `ingestion-pipeline`, `internal-copilot`, `memory-service`, `private-model-endpoint`, `tool-registry`, `vector-store`, `web-assistant`, `workflow-orchestrator`

## Symptoms

- Dashboards empty
- Alerts not firing

## First checks

1. Check collector health and queue depth
2. Check storage quota

## Mitigations

- Restart collectors; they buffer to disk
- Services continue without telemetry: do not block requests on it

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
