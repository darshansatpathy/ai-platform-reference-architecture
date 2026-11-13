# ADR 0008: One telemetry standard, with redaction before storage

## Status

Accepted

## Context

Traces and logs of AI traffic contain prompts, documents and personal data. They are also what
makes the system operable. Each service redacting on its own leaves gaps.

## Decision

All components emit traces, metrics and logs in OpenTelemetry formats to `observability-stack`.
Redaction and sampling happen in the collector, before storage, with content capture off by
default and a fingerprint recorded instead. Telemetry is asynchronous: a component never fails
a request because telemetry is down. Tier 1 and 2 components must declare traces, metrics and
logs (`FIT011`). [agent-tracing-otel](https://github.com/darshansatpathy/agent-tracing-otel)
shows the span model for agent runs.

## Consequences

- One place to change what is retained, and for how long.
- Observability is tier 2, not tier 1, by design; losing it is serious but not an outage of the
  product.
- Debugging a specific prompt needs a deliberate, audited switch to content capture.
