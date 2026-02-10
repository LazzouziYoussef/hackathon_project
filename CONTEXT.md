# Sadaqa Tech

## Project Metadata

| Field            | Value                                                             |
| ---------------- | ----------------------------------------------------------------- |
| **Project Name** | Sadaqa Tech                                                       |
| **Hackathon**    | RamadanIA Hackathon 2026                                          |
| **Location**     | Morocco                                                           |
| **Type**         | Infrastructure observability and predictive scaling assistant     |
| **Maturity**     | Hackathon MVP. Research-informed prototype. Not production-ready. |

## One-Sentence Definition

Sadaqa Tech is a read-only infrastructure observability system that predicts short-term traffic surges during Ramadan and produces guarded scaling recommendations that require human approval.

**If a future contribution does not fit this sentence, it is out of scope.**

## What This Project Is

- A monitoring and prediction layer
- A decision-support system
- An admin-facing operational tool

The system observes existing platforms. The system does not replace them.

## What This Project Is Not

**Explicit exclusions. These are permanent.**

- Not a donation platform
- Not a payment processor
- Not donor-facing
- Not a cloud cost optimizer
- Not an autonomous scaling system
- Not a general-purpose AIOps platform

**Any feature proposal touching these areas must be rejected.**

## Problem Ownership

**The problem is not traffic spikes.**

**The problem is delayed reaction to predictable spikes.**

- Ramadan traffic follows patterns
- Failures happen because teams respond after degradation
- NGOs overprovision due to fear
- Budgets suffer
- Trust erodes

**This project exists to shift reaction earlier in time.**

## Target Users

### Primary Users

- NGO administrators responsible for uptime decisions
- Technical operators managing deployments

### Non-Users

- Donors
- Payment providers
- Marketing teams
- End users of charity platforms

**All interfaces, APIs, and outputs target admins only.**

Core operating principles

These principles override all technical preferences.

Prediction never bypasses rules.

## Core Operating Principles

**These principles override all technical preferences.**

1. **Prediction never bypasses rules.**
2. **Rules never bypass humans.**
3. **Humans never bypass visibility.**
4. **Simplicity beats sophistication.**
5. **Failure must be visible and explainable.**

## System Boundaries

### In Scope

- Metric ingestion
- Time-series storage
- Traffic forecasting
- Anomaly flagging
- Rule-based recommendations
- Manual approval workflows
- Kubernetes demo scaling
- Dashboards and alerts

### Out of Scope

- Payment flows
- Donor personal data
- Automatic cloud purchasing
- Cross-region failover
- Legal compliance enforcement

**These boundaries are intentional.**traints.

Multi-tenant by design.

Strong tenant isolation.

Deterministic decision logic.

Conservative defaults.

Safe degradation.

## Architecture Constraints

**The system must follow these constraints.**

## Data Model Rules

### Accepted Data Types

- Request rate
- Error rate
- Latency percentiles
- Resource utilization

### Rejected Data Types

- Donor identity
- Payment details
- Behavioral profiling

**Every record must include a tenant identifier.**
Baseline behavior.

Seasonal averages.

Hourly and daily cycles.

Ramadan day indexing.

## Machine Learning Rules

**ML is optional. Guardrails are mandatory.**

### Baseline Behavior

- Seasonal averages
- Hourly and daily cycles
- Ramadan day indexing

### Advanced Behavior

- Neural forecasting only with sufficient history
- Confidence scoring required
- Fallback paths required

**ML output never triggers actions directly.**

No silent automation.

## Decision Logic Rules

**Decisions are rule-driven.**

- Predictions inform rules
- Rules generate recommendations
- Humans approve actions

## Observability Requirements

**The system must explain itself.**

### Dashboards Must Show

- Current state
- Predicted state
- Capacity margin
- Reason for each alert

**No alert without context.**

## Security Posture

### Security Goals

- Prevent cross-tenant access
- Protect admin endpoints
- Record administrative actions

### Security Limits

- No donor-facing attack surface
- No payment compliance claims
- No zero-trust claims

**Security is defensive, not aspirational.**nd validation only.

Its purpose.

Generate Ramadan-like traffic.

Create controlled spikes.

## Simulator Role

**The simulator exists for demonstration and validation only.**

### Its Purpose

- Generate Ramadan-like traffic
- Create controlled spikes
- Test prediction lead time
- Test rule behavior under stress

**Simulator code is never production logic.**

## Contribution Contract

**For all contributors, human or AI.**

### Before Contributing

- Read this file fully
- Identify the layer you touch
- Declare assumptions

### When Proposing Changes

- State scope impact
- Define failure behavior
- Define guardrails first
- Prefer clarity over novelty

### Forbidden Behaviors

- Inflated claims
- Hidden automation
- Implicit scope expansion
- Unverifiable metricsad time.

Transparent logic.

Honest limits.

For future development.

Incremental automation.

Better confidence handling.

Broader event support.

## Evaluation Criteria

### For Hackathon Judging

- Clear problem framing
- Working demo
- Visible prediction lead time
- Transparent logic
- Honest limits

### For Future Development

- Incremental automation
- Better confidence handling
- Broader event support
- Maintained trust

## Final Constraint

**This project optimizes for trust, not spectacle.**

- If a feature impresses but cannot be explained in one minute, it does not belong here
- If a feature hides failure modes, it does not belong here
