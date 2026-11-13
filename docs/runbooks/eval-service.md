# Runbook: Evaluation service (`eval-service`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Runs regression, safety and quality evaluations; gates promotion.

## Ownership and escalation

- Owner: `ml-quality-team` (owns evaluation, human review and quality gates)
- Contact: `pagerduty:ml-quality-business-hours`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `ai-gateway` (async), `lakehouse` (async), `observability-stack` (async)

Used by: `cicd-pipeline`

## Symptoms

- Evaluation runs fail or time out
- Promotion blocked waiting for results

## First checks

1. Check the gateway budget for the evaluation tenant
2. Check lakehouse access for datasets

## Mitigations

- Re-run the failed suite
- Use a documented manual approval to unblock a promotion, recorded in the change

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
