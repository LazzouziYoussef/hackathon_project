# Sadaqa Tech - Operational Intelligence Layer

[![Hackathon Status](https://img.shields.io/badge/Status-ML_Complete-green?style=flat-square)](https://github.com)
[![Implementation](https://img.shields.io/badge/Implementation-55%25-yellow?style=flat-square)](#current-state)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)

> **Operational Intelligence for NGO Infrastructure During Ramadan**

A planned AI-assisted infrastructure monitoring and predictive scaling system for charitable platforms during high-traffic religious events.

**Current Status:** ML engine complete (24 files, 112 tests passing). Backend integration and frontend API connection pending.

---

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Start here! Quick commands and status overview
- **[CURRENT_STATE.md](CURRENT_STATE.md)** - Detailed implementation status and roadmap
- **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - Technical audit and dependency analysis
- **[CONTEXT.md](CONTEXT.md)** - Philosophy, constraints, and design decisions
- **[docs/ML_INTEGRATION_GUIDE.md](docs/ML_INTEGRATION_GUIDE.md)** - Backend ML integration guide (87KB)

---

## Quick Start

```bash
# 1. Start infrastructure
cd infra/docker
docker-compose up -d

# 2. Check services
docker ps
docker logs sadaqa-backend
docker logs sadaqa-frontend

# 3. Access services
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for detailed development commands.

---

## Implementation Status

### Completed Components

**ML Engine (100% Complete)**

- 24 Python files implementing full forecasting pipeline
- 112 comprehensive tests (100% passing)
- Data preprocessing and feature engineering (19 features)
- Models: Seasonal baseline, pattern learner, confidence scorer
- Hybrid forecaster (rule-based triggers + ML predictions)
- Scaling calculator with cost impact and safety constraints
- Training pipeline with CLI and model persistence
- Comprehensive integration guide for backend developers

**Frontend UI Structure (60% Complete)**

- 11 TypeScript files with React + React Router
- Tailwind CSS styling integrated
- Pages: Dashboard, Login, Register, About
- Components: Navbar, Footer, Chart (placeholder), StatCard (placeholder)
- Missing: API integration, data fetching, chart rendering

**Infrastructure (100% Complete)**

- Docker Compose with TimescaleDB, Redis, backend, frontend
- Database schema with 6 tables, row-level security
- GitHub Actions CI/CD (5 workflows)
- Code quality tools (ESLint, flake8, Black)

### Pending Implementation

**Backend Integration (0% Complete)**

- No ML service layer connecting engine to API
- No `/api/ml/predict` or `/api/ml/train` endpoints
- No `/api/metrics/ingest` endpoint
- Backend has only 2 placeholder endpoints
- Follow `docs/ML_INTEGRATION_GUIDE.md` for implementation

**Traffic Simulator (0% Complete)**

- `simulator/` directory is empty
- No Ramadan pattern generation

**Time to Working Demo:** Approximately 20 hours

- Backend ML integration: 12 hours
- Frontend API connection: 5 hours
- Traffic simulator: 3 hours

---

## Core Principle

**Prediction before automation. No feature is acceptable if it hides failure modes or lacks human approval gates.**

This project is a read-only infrastructure observability system that predicts short-term traffic surges during Ramadan and produces guarded scaling recommendations that require human approval.

---

## System Architecture

Five-layer pipeline (Analytics layer complete, Integration layer pending):

1. **Ingestion** - Metrics collection (not implemented)
2. **Storage** - TimescaleDB + PostgreSQL + Redis (schema ready)
3. **Analytics** - LSTM forecasts + seasonal baselines (COMPLETE - 24 files, 112 tests)
4. **Decision** - Rule-based recommendations (COMPLETE - scaling calculator with safety caps)
5. **Execution** - Manual approval required (not implemented)

**Key Constraint:** Data never flows backward. Scaling actions log telemetry but don't influence predictions.

---

## License

MIT License - See LICENSE file for details.

| Component    | Technology              | Notes                      |
| ------------ | ----------------------- | -------------------------- |
| Load Testing | Locust                  | Stress testing workloads   |
| Traffic Sim  | Custom Python Generator | Synthetic Ramadan patterns |

---

## Project Structure

```
sadaqa-tech/
├── README.md                          # This file
├── CONTEXT.md                         # Detailed philosophy and constraints
├── implementation_steps.md            # Step-by-step build guide (24-48 hrs)
├── .env.example                       # Environment variables template
├── .github/
│   └── copilot-instructions.md        # AI agent development guidelines
│
├── architecture/
│   ├── system_architecture.json       # Complete tech stack definition
│   ├── project_structure.md           # Directory layout explanation
│   └── system_interaction_graph.md    # Mermaid diagram of data flow
│
├── backend/
│   └── app/
│       ├── api/                       # Routes (ingest, dashboard, approval)
│       ├── core/                      # Config, constants, env vars
│       ├── db/                        # Database session and CRUD
│       ├── models/                    # Pydantic schemas
│       ├── services/                  # Business logic (forecaster, scaling)
│       └── main.py                    # FastAPI app entry point
│
├── frontend/                          # UI STRUCTURE READY (11 TypeScript files)
│   └── src/
│       ├── components/                # Navbar, Footer, Chart (placeholder), StatCard
│       ├── pages/                     # Dashboard, Login, Register, About
│       ├── router.tsx                 # Route configuration
│       └── main.tsx                   # React entry point
│
├── ml_engine/                         # COMPLETE (24 files, 112 tests)
│   ├── preprocessing/                 # Data loading and feature engineering
│   ├── models/                        # Baseline, pattern learner, confidence scorer
│   ├── forecaster.py                  # Hybrid forecasting logic
│   ├── scaling_calculator.py          # Replica calculation with cost impact
│   ├── training/                      # Training pipeline with CLI
│   ├── tests/                         # Comprehensive test suite (8 files)
│   └── utils/                         # Ramadan calendar, time utilities
│
├── simulator/                         # NOT IMPLEMENTED
│   ├── traffic_gen.py                 # Locust or custom Ramadan traffic generator
│   └── profiles.json                  # Traffic multipliers (Suhoor, Iftar, Normal)
│
├── docs/
│   └── ML_INTEGRATION_GUIDE.md        # COMPLETE - Backend integration documentation (87KB)
│
└── infra/
    ├── docker/
    │   ├── Dockerfile.backend         # FastAPI container
    │   ├── Dockerfile.frontend        # React build container
    │   ├── docker-compose.yml         # Local dev stack (TimescaleDB, Redis)
    │   └── init.sql                   # Database schema and seed data
    │
    ├── k8s/
    │   ├── deployment.yaml            # Kubernetes Deployment
    │   ├── service.yaml               # Kubernetes Service
    │   ├── hpa.yaml                   # HorizontalPodAutoscaler config
    │   └── ingress.yaml               # NGINX Ingress routing
    │
    └── terraform/
        ├── main.tf                    # Cloud/K8s resource definitions
        ├── variables.tf               # Input variables
        └── outputs.tf                 # Exported values
```

---

## Development Guide

### What's Already Done

**ML Engine (Complete)**

```bash
# Run ML tests
docker run --rm -v "$PWD":/app -e PYTHONPATH=/app/ml_engine \
  sadaqa-ml-test pytest ml_engine/ -v
# Result: 112 tests passing

# View integration guide
cat docs/ML_INTEGRATION_GUIDE.md
```

**Infrastructure (Complete)**

```bash
# Start all services
cd infra/docker
docker-compose up -d

# Verify database schema
docker exec -it timescaledb psql -U sadaqa_admin -d sadaqa_observability -c "\dt"
```

**Frontend UI (Partial)**

```bash
cd frontend
npm install
npm run dev
# Visit: http://localhost:5173
# Note: UI structure exists but no API integration
```

### What Needs Implementation

**Phase 1: Backend ML Integration (12 hours)**

Follow the complete implementation guide in `docs/ML_INTEGRATION_GUIDE.md`:

1. Create `backend/app/services/ml_service.py`
2. Add database connection layer
3. Implement `POST /api/ml/predict` endpoint
4. Implement `POST /api/ml/train` endpoint
5. Add error handling and validation

**Phase 2: Frontend API Integration (5 hours)**

```bash
cd frontend
npm install axios recharts

# Connect Chart component to backend
# Add real-time data fetching
# Implement prediction alerts display
```

**Phase 3: Traffic Simulator (3 hours)**

```bash
cd simulator
# Create traffic_gen.py with Ramadan patterns
# POST to /api/metrics/ingest every 2 seconds
```

---

## Machine Learning Implementation

### Implementation Status: COMPLETE

The ML engine is fully implemented with 24 Python files and 112 passing tests.

### Baseline Model (Fallback) - IMPLEMENTED

- **Approach:** Seasonal averages per Ramadan day and hour-of-day
- **Ramadan Day Indexing:** day 1–30 of the Hijri calendar
- **Used When:** Pattern learner confidence < 0.7 or on cold starts
- **Location:** `ml_engine/models/seasonal_baseline.py`

### Pattern Learner (Primary) - IMPLEMENTED

- **Training:** Learns Iftar, Taraweeh, Suhoor traffic multipliers
- **Horizon:** 24 hours ahead
- **Feature Engineering:** 19 features including trend, seasonality, prayer window flags
- **Fallback:** Automatic switch to baseline on model failure
- **Location:** `ml_engine/models/pattern_learner.py`

### Hybrid Forecaster - IMPLEMENTED

- **Rule-Based Triggers:** Detects when to apply learned patterns
- **ML-Learned Multipliers:** Applies pattern-specific traffic increases
- **Confidence Scoring:** 6-factor confidence calculation (data quality, seasonality, etc.)
- **Location:** `ml_engine/forecaster.py`

### Confidence Calculation - IMPLEMENTED

The confidence scorer evaluates predictions using 6 factors:

1. Data quality score (missing data penalties)
2. Seasonality match (is this a typical Ramadan pattern?)
3. Recent accuracy (how well did recent predictions perform?)
4. Pattern strength (how clear is the traffic pattern?)
5. Data recency (how fresh is the training data?)
6. Volume stability (is traffic behavior stable?)

**Threshold:** Predictions only trigger alerts when confidence ≥ 0.7

**Validation:** Output always validated against sensible bounds (0–5× current load)

**Location:** `ml_engine/models/confidence_scorer.py`

---

## Scaling Logic - IMPLEMENTED

All scaling is **recommendation-first and human-approved**.

**Implementation Status:** Scaling calculator complete in `ml_engine/scaling_calculator.py`

### Hard Limits (Implemented)

- **Max Replicas:** 50 (safety cap)
- **Cooldown:** 5 minutes between actions
- **Cost Caps:** Admin-defined per tenant

### Example Recommendation

> "Forecast shows 3× load in 4h; current replicas: 10; recommended: 25; cost impact: +$120/h."

### Human Approval Gate (Pending Backend Integration)

**Logic Implemented, UI Not Connected:**

1. System detects surge prediction (ML engine ready)
2. Dashboard displays recommendation with full context (UI structure exists, no API)
3. Admin reviews and clicks "Approve" (button exists, no backend endpoint)
4. Kubernetes scaling occurs (not implemented)

**Next Step:** Implement approval workflow endpoints following `docs/ML_INTEGRATION_GUIDE.md`

---

## Security & Tenancy

### Multi-Tenancy by Design

- **Every metric carries `tenant_id`**
- Database row-level security enforces isolation
- API layer filters all queries by tenant
- Dashboards query-scoped to authenticated tenant
- **No cross-tenant aggregation** in MVP

### Security Posture

- **In Scope:** TLS, AES-256 at rest, RBAC, audit logs, rate limiting
- **Out of Scope:** Zero-trust networking, payment PCI compliance, multi-region disaster recovery
- Secrets stored in Kubernetes Secrets (never env vars)
- JWT tokens: short-lived with tenant scope

### Explicit Exclusions

- No payment processing
- No donor personal data (PII) handling
- No autonomous cloud resource purchasing
- No multi-region replication
- No legal compliance enforcement

---

## Core Operating Principles

These principles override all technical preferences:

1. **Prediction never bypasses rules** — ML output is constrained, not autonomous
2. **Rules never bypass humans** — Every scaling action requires approval
3. **Humans never bypass visibility** — All decisions logged and explainable
4. **Simplicity beats sophistication** — Clarity > performance
5. **Failure must be visible and explainable** — No silent failures

**If a contribution violates a principle, it must be removed.**

---

## Key Documentation Files

| File                                                                                 | Purpose                                                  |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| [CONTEXT.md](CONTEXT.md)                                                             | Detailed project philosophy, constraints, and boundaries |
| [implementation_steps.md](implementation_steps.md)                                   | Step-by-step build guide for 24-48 hour hackathon        |
| [.github/copilot-instructions.md](.github/copilot-instructions.md)                   | AI agent development guidelines and patterns             |
| [architecture/system_architecture.json](architecture/system_architecture.json)       | Complete tech stack definition in JSON                   |
| [architecture/project_structure.md](architecture/project_structure.md)               | Directory layout and purpose of each folder              |
| [architecture/system_interaction_graph.md](architecture/system_interaction_graph.md) | Mermaid diagram of data flow and interactions            |

---

## For Hackathon Judges

### Evaluation Criteria

**Clear problem framing:** Ramadan traffic is predictable; teams react too late.

**Working demo:**

- Live traffic chart showing "normal" → "surge" → "drop" cycle
- Prediction alert fires 4+ hours before spike
- Admin approves scaling recommendation
- Kubernetes adjusts replicas

**Visible prediction lead time:** System demonstrates 4+ hour forecasting window.

**Transparent logic:** Every alert includes context, confidence score, and cost impact.

**Honest limits:** Documentation explicitly states MVP boundaries and out-of-scope features.

### Showcase Deliverables

**Currently Demoable:**

1. ML Engine Tests: 112 tests passing in Docker
2. ML Code Walkthrough: Show forecaster.py, scaling_calculator.py
3. Integration Documentation: 87KB comprehensive guide
4. Frontend UI: Dashboard structure with routing

**Not Yet Demoable:**

1. End-to-end flow (ML not connected to API)
2. Live predictions (no API integration)
3. Approval workflow (no backend endpoints)
4. Traffic simulation (simulator not implemented)

---

## Development Roadmap

### Phase 1: Core ML & Infrastructure (COMPLETE)

- DONE: ML forecasting engine (24 files, 112 tests)
- DONE: Frontend UI structure (11 TypeScript files)
- DONE: Docker infrastructure with TimescaleDB
- DONE: Database schema with row-level security
- DONE: CI/CD pipeline (5 GitHub Actions workflows)
- DONE: Integration documentation (87KB guide)
- PENDING: Backend API integration
- PENDING: Traffic simulator
- PENDING: End-to-end workflow

### Phase 2: Incremental Automation

- Better confidence estimation
- Multi-event support (other holidays, events)
- Expanded forecasting horizon
- More sophisticated cost impact modeling

### Phase 3: Operational Excellence

- Production-ready Kubernetes deployment
- Advanced observability (Prometheus, Grafana)
- Audit trails and compliance logging
- NGO trust through transparency

---

## Contributing

Before contributing, read [CONTEXT.md](CONTEXT.md) in full to understand project boundaries.

### When Adding Features

1. Declare explicitly: in-scope or out-of-scope
2. Define failure behavior
3. Add guardrails _before_ intelligence
4. Prefer clarity over novelty

### When Touching ML

- Avoid speculative claims
- Test fallback behavior thoroughly
- Document confidence thresholds

### When Modifying Scaling Logic

- Every rule must have written justification
- Rules are versioned and auditable
- Cost impact must be calculable before execution

### Red Flags (Do Not Merge)

- Features that bypass human approval
- Silent failure modes
- Automation presented as "safe" without proof
- Implicit assumptions about model accuracy
- Cross-tenant changes without isolation testing

---

## Support

- **Architecture Questions:** See [architecture/](architecture/)
- **Implementation Help:** See [implementation_steps.md](implementation_steps.md)
- **AI Development:** See [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Project Philosophy:** See [CONTEXT.md](CONTEXT.md)

---

## License

This project is part of the **RamadanIA Hackathon 2026**.

---

**Last Updated:** February 18, 2026 | **Status:** ML Engine Complete (24 files, 112 tests), Backend Integration Pending

_"This project exists to help charities act earlier, not gamble faster."_
