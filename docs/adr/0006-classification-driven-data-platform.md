# ADR 0006: Data classification drives where data may go, and how long it stays

## Status

Accepted

## Context

Retrieval and memory make an assistant useful and also concentrate sensitive data. Without a
classification that is machine-readable, "do not send restricted data to that system" is a
convention, not a control.

## Decision

Every dataset and every dependency carries one of four classes (public, internal, confidential,
restricted). Every component declares the highest class it is cleared to hold. Each dependency
in the catalog states the class of data it carries, and the fitness function `FIT006` fails the
build when a flow exceeds what either end is cleared for. Vector stores enforce row-level
security from the caller's identity. Memory has per-class retention and supports erasure.

## Consequences

- Reclassifying a component is a visible change to the catalog and goes through review.
- Redaction in the guardrails service is what lets confidential-cleared providers be used for
  requests that began with restricted content.
- Ingestion must classify documents before indexing; unclassified content is quarantined.
