# Copilot Instructions for Sadaqa Tech

## Project Overview

Sadaqa Tech is an **operational intelligence layer** for NGO infrastructure during Ramadan. It observes metrics, predicts traffic, and recommends (never auto-executes) scaling actions. Read `CONTEXT.md` for the full philosophy.

**Core principle**: Prediction before automation. No feature is acceptable if it hides failure modes or lacks human approval gates.

## Architecture Layers

The system has five layers (see `architecture/system_architecture.json`):

1. **Ingestion**: Agents or HTTP APIs deliver metrics (request rate, error rate, latency, utilization)
2. **Storage**: TimescaleDB for time-series, PostgreSQL for state, Redis for caching—all tenant-scoped
3. **Analytics**: Seasonal baselines (fallback) + LSTM forecasts (primary) when confidence ≥ 0.7
4. **Decision Engine**: Rule-based logic (capacity thresholds, cooldowns, max replicas, cost caps)
5. **Execution**: Manual approval required; no auto-scaling in MVP

**Data never flows backward**. Scaling actions log telemetry; they do not influence predictions.

## Multi-Tenancy and Isolation

- Every metric carries `tenant_id`
- Database: row-level security enforces isolation
- API layer: all queries filtered by tenant
- Dashboards: query-scoped to authenticated tenant
- **No cross-tenant aggregation** in MVP

Treat tenant context as immutable and mandatory in every database operation.

## ML Pipeline Specifics

### Baseline Model (Fallback)

- Seasonal averages (per day-of-year, hour-of-day)
- Ramadan day indexing (day 1–30 of Hijri calendar)
- Used when LSTM confidence < 0.7 or on cold starts

### LSTM Forecast (Primary)

- Trained daily on 60+ days of history
- 24-hour horizon
- Requires explicit feature engineering (trend, seasonality, event flags)
- Failure → graceful fallback to baseline

**Pattern**: Always validate model output against sensible bounds (0–5× current load) before passing to decision engine.

## Scaling Logic Constraints

All scaling is **recommendation-first and human-approved**:

- Max replicas: 50 (safety cap)
- Cooldown: 5 minutes between actions
- Cost caps: admin-defined per tenant
- Alerts must include reason string (no reason = invalid alert)

Example rule: "Forecast shows 3× load in 4h; current replicas: 10; recommended: 25; cost impact: +$120/h."

## Tech Stack Anchors

| Layer         | Technology                                 | Notes                                          |
| ------------- | ------------------------------------------ | ---------------------------------------------- |
| Frontend      | React + TypeScript + Recharts              | JWT in HTTP-only cookies                       |
| Backend API   | FastAPI + Pydantic (Python 3.11)           | OAuth2 JWT validation                          |
| ML            | scikit-learn, TensorFlow, NumPy, Pandas    | Python                                         |
| Data          | TimescaleDB, PostgreSQL, Redis             | Column encryption for sensitive fields         |
| Observability | Prometheus + Grafana + Fluentd             | All admin actions audited                      |
| Orchestration | Kubernetes 1.28 + NGINX Ingress            | HPA for auto-scaling of demo workloads         |
| IaC           | Terraform + ArgoCD                         | GitOps for deployments                         |
| Testing       | Locust (load), custom Python (traffic sim) | Simulator generates synthetic Ramadan patterns |

## Critical Development Patterns

### When Adding Features

1. Declare explicitly: in-scope or out-of-scope (see `CONTEXT.md` boundaries)
2. Define failure behavior (what happens if this component fails?)
3. Add guardrails _before_ intelligence (constraints before models)
4. Prefer clarity over novelty (explainability > performance)

### When Touching Metrics Ingestion

- Validate schema at API boundary
- Reject unknown metric types (whitelist: request_rate, error_rate, latency_p50/p95/p99, cpu, memory)
- Enforce `tenant_id` presence
- Log ingestion path for debugging

### When Contributing ML

- Avoid speculative claims ("this will improve accuracy by X%")
- Avoid invented metrics (use only ingested data)
- Test fallback behavior thoroughly
- Document confidence thresholds and cold-start behavior

### When Modifying Decision Engine

- Every rule must have a written justification (why this threshold?)
- Rules are versioned and auditable
- Cost impact must be calculable before execution
- Cooldown windows prevent thrashing

## Developer Workflows (TBD—Repo Structure to Come)

Once code structure is established:

- API testing: FastAPI test suite + request fixtures
- ML validation: cross-validation splits, confidence plots
- Integration tests: end-to-end metric → recommendation flow
- Load testing: Locust scripts simulate Ramadan traffic patterns
- Kubernetes verification: ensure HPA scaling is safe and reversible

## Observability Requirements

Every feature must be observable:

- **Metrics**: emit to Prometheus (e.g., `forecast_confidence`, `recommendation_cost_impact`)
- **Logs**: structured logs with tenant context (use correlation IDs)
- **Dashboards**: show prediction quality, decision logic execution, approval workflow
- **Alerts**: always include reason and tenant context

## Security Boundaries

- **In scope**: TLS, AES-256 at rest, RBAC, audit logs, rate limiting (Kong gateway)
- **Out of scope**: zero-trust networking, payment PCI compliance, multi-region disaster recovery
- Secrets: Kubernetes Secrets only (no env vars in code)
- API tokens: short-lived JWT with tenant scope

## Out-of-Scope (Do Not Implement)

- Payment processing
- Donor personal data (PII) handling
- Autonomous cloud resource purchasing
- Multi-region replication
- Legal compliance enforcement (that's NGO responsibility)

## Testing Simulator

A traffic simulator generates synthetic Ramadan patterns to validate scaling logic safely. Reference it when:

- Testing forecast accuracy
- Validating recommendation thresholds
- Demonstrating prediction lead time (goal: 4+ hour warning)
- Stress-testing scaling workflows

Simulator code is **not production code**—it exists for validation only.

## Red Flags (Do Not Merge)

- Features that bypass human approval
- Silent failure modes (errors without logging or alerts)
- Automation presented as "safe" without proof
- Implicit assumptions about model accuracy
- Changes that affect one tenant without isolation testing

---

**Last Updated**: Feb 2026 | **Status**: Hackathon MVP, code scaffolding phase
