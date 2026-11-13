# Quality attribute scenarios

Each scenario states a stimulus, the response the design must produce and a measure, and says
what in this repository enforces or evidences it. Measures are targets to verify in a real
deployment, not results from one.

| # | Attribute | Stimulus | Required response | Measure | Enforced or evidenced by |
|---|---|---|---|---|---|
| Q1 | Availability | The primary model provider is unavailable | The gateway routes to the secondary provider with no change in callers | Provider outage causes no failed requests beyond detection time (target under 1 minute) | Fallback edge in the catalog; `FIT002` (fallback exists), `FIT005` (ceiling counts the fallback) |
| Q2 | Availability | A tier 3 service fails | No tier 1 request is affected | Zero tier 1 hard dependencies on tier 3 | `FIT008` |
| Q3 | Security | A request contains restricted data | It never reaches an external provider | Zero data flows above a target's clearance | `FIT006`, `FIT007`; ADR 0004 |
| Q4 | Security | A model is manipulated into calling a write tool | The call waits for a person | No state change without approval | ADR 0003; [claude-agent-reference](https://github.com/darshansatpathy/claude-agent-reference) scenario `injection-in-document-cannot-refund` |
| Q5 | Cost | An agent enters a loop | The run stops at its limits | Turns, tool calls, tokens, cost and time all bounded per run | ADR 0002; [unit economics](generated/finops.md) |
| Q6 | Modifiability | Add a third model provider | One routing and gateway change; no product change | No product repository edited | `FIT007` keeps products from bypassing the gateway |
| Q7 | Recoverability | A zone or region is lost | Components return within their tier's objective | Tier 1 RTO within 60 minutes, tier 2 within 240 | `FIT009`; [runbooks](runbooks) |
| Q8 | Observability | A customer disputes an answer | The request can be traced end to end | Trace found within 15 minutes using a request id | `FIT011`; ADR 0008 |
| Q9 | Change safety | A prompt or routing rule is changed | It is reviewed, evaluated and reversible | No production change without a passing evaluation run | ADR 0005 |
| Q10 | Operability | A tier 1 component fails at 3 a.m. | Someone with a runbook is paged | Every tier 1 owner has a pager; every tier 1 and 2 component has a runbook | `FIT009`, `FIT010` |
| Q11 | Honest targets | A team commits to an SLO | The commitment is arithmetically achievable | Every target is at or below its dependency ceiling | `FIT005`; [availability register](generated/slo-register.md) |
| Q12 | Auditability | An auditor asks who can see restricted data | Answerable from the catalog | Data flows and clearances listed per component | [data flows](generated/data-flows.md) |

## How the availability arithmetic works

For a component that calls dependencies synchronously, the best it can do is the product of
their availabilities. For example, if the gateway calls an identity service (99.99%), a
guardrails service (99.95%) and a provider with a fallback (each 99.5%, so together
1 − 0.005 × 0.005 = 99.9975%), its ceiling is 0.9999 × 0.9995 × 0.999975 ≈ 99.9375%. A 99.9%
target is feasible. A 99.99% target would not be, however carefully it is built.

Asynchronous calls, in-process libraries and optional dependencies (the request succeeds
without them) do not count, which is why moving a call off the request path is a real design
lever and not a relabelling.
