# Risk register

Likelihood and impact are qualitative (low, medium, high) for a typical enterprise deployment,
meant to be re-scored with your own context. Each risk names the components and decisions that
mitigate it, so that the register and the catalog cannot drift apart: a test checks every
reference.

| ID | Risk | Likelihood | Impact | Mitigations | Early indicator | Owner |
|---|---|---|---|---|---|---|
| R1 | A model provider has an extended outage | Medium | High | `secondary-model-provider` fallback (ADR 0004); `model-router`; failover rehearsed in staging | Provider error rate and fallback share | platform-team |
| R2 | Prompt injection causes a harmful action | High | High | Approval at the tool boundary (ADR 0003); `guardrails-service`; `human-review-inbox` | Rate of denied tool calls | security-team |
| R3 | Sensitive data leaks through logs or traces | Medium | High | Redaction at the collector, content capture off by default (ADR 0008) | Redaction miss rate in sampled logs | security-team |
| R4 | Runaway cost from agent loops or traffic spikes | Medium | Medium | Runtime budgets (ADR 0002); per-caller gateway budgets; `cost-management` alerts | Spend against forecast; turns per request | finops-team |
| R5 | A provider changes price, terms or retires a model | High | Medium | Multi-provider gateway; config-as-code routing (ADR 0005); model comparisons in `eval-service` | Notices from providers; cost per request | vendor-management |
| R6 | Model behaviour drifts after a provider update | Medium | Medium | Evaluation gates and scheduled regression runs (ADR 0005); pinned model versions | Evaluation pass rate over time | ml-quality-team |
| R7 | Evaluation sets go stale and stop catching regressions | Medium | High | Named owner; production samples reviewed into the set monthly | Share of incidents not covered by an evaluation | ml-quality-team |
| R8 | The gateway is a single point of failure | Low | High | Tier 1 with 30-minute RTO; multi-instance; runbook; availability ceiling checked by `FIT005` | Gateway error budget burn | platform-team |
| R9 | Identity provider outage stops everything | Low | High | Tier 1 and ceiling-checked; documented break-glass; token lifetimes sized for short outages | Token issuance latency | security-team |
| R10 | Regulation changes obligations for AI systems | High | Medium | Controls mapped to evidence; [ai-governance-evidence-pack](https://github.com/darshansatpathy/ai-governance-evidence-pack) tracks it | Change log of applicable regulation | security-team |
| R11 | Restricted data sent to an external provider by a design change | Low | High | `FIT006` and `FIT007` fail the build; private endpoint for restricted class (ADR 0006) | Catalog changes touching data flows | security-team |
| R12 | A temporary exception becomes permanent | Medium | Medium | Waivers expire and fail the build after the date | Count of waivers and age | platform-team |

## Reviewing it

Review monthly with the architecture review. Re-score after any incident, and add the
indicator to a dashboard rather than relying on someone remembering. A risk with no mitigation
that you can point at in the catalog or an ADR is an open issue, not a managed risk.
