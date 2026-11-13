# ADR 0003: Side effects are controlled at the tool boundary, not in the prompt

## Status

Accepted

## Context

Prompt injection can make a model call any tool it can see, using text it read while doing
legitimate work. Instructions to the model are a mitigation. The control that holds is outside
the model.

## Decision

Tools are registered in the `tool-registry` with a side-effect class. Tools that change state
need an approval from a person (via `human-review-inbox`) or an explicit policy decision, and
the default is no. `guardrails-service` screens inputs and outputs and checks tool calls against
policy. Output from tools that return external content is marked as untrusted data.
[agent-guardrails-gateway](https://github.com/darshansatpathy/agent-guardrails-gateway) shows
task-scoped grants, taint tracking and a tamper-evident audit trail at this boundary.

## Consequences

- A manipulated model can be wrong without being harmful: its write calls wait for a person.
- Approval adds latency and needs reviewers; low-risk actions can be pre-approved by policy
  with an audit trail.
- The guardrails service is on the request path and so is tier 1. It fails closed.
