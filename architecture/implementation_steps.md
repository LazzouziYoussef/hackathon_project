# Implementation Plan: This project (Hackathon MVP)

## Overview

| Field         | Value                                                                      |
| ------------- | -------------------------------------------------------------------------- |
| **Objective** | Go from empty directory to a working "Human-in-the-Loop" scaling simulator |
| **Timeline**  | Optimized for a 24-48 hour Hackathon sprint                                |
| **Stack**     | FastAPI, React, PostgreSQL (TimescaleDB), Python (ML/Sim), Docker          |

---

## Phase 0: Repository & Environment Setup

**Goal:** Establish the project skeleton.

### Step 0.1: Initialize Git & Directory Structure

```bash
mkdir sadaqa-tech
cd sadaqa-tech
git init

# Create the monorepo structure
mkdir -p backend/app/api backend/app/core backend/app/db backend/app/models backend/app/services
mkdir -p frontend
mkdir -p infra/docker infra/k8s
mkdir -p simulator
mkdir -p ml_engine/notebooks
```

### Step 0.2: Create Global Configuration

Create a `.env.example` in the root:

```ini
POSTGRES_USER=sadaqa_admin
POSTGRES_PASSWORD=secure_hackathon_pass
POSTGRES_DB=sadaqa_observability
SECRET_KEY=dev_secret_key_123
ALLOWED_ORIGINS=["http://localhost:5173"]
```

## Phase 1: The Foundation (Database & Docker)

**Goal:** Get TimescaleDB running to accept metrics.

### Step 1.1: Docker Compose (Local Dev)

Create `docker-compose.yml` in the root.

- **Service 1:** timescaledb (Image: `timescale/timescaledb:latest-pg14`)
- **Service 2:** redis (Image: `redis:alpine` - optional for caching)
- **Ports:** Expose DB on 5432

### Step 1.2: Database Initialization Script

Create `infra/docker/init.sql`.

- **Action:** Paste the schema defined in `database_schema.md` (Users, Tenants, Metrics, ScalingEvents)
- **Critical:** Ensure `CREATE EXTENSION IF NOT EXISTS timescaledb;` is the first line
- **Seed Data:** Insert one dummy tenant and one admin user

```sql
INSERT INTO tenants (id, name, api_key_hash) VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Demo NGO', 'hash123');
```

### Step 1.3: Verify Infrastructure

````bash
## Phase 2: The Backend (FastAPI)

**Goal:** Create the "Ingest" pipe and the "Read" pipe.

### Step 2.1: Python Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy asyncpg pydantic python-dotenv
````

### Step 2.2: Database Connection

- Create `app/db/session.py`: Setup AsyncSession using SQLAlchemy
- Create `app/models/`: Define SQLAlchemy models mirroring the SQL schema

### Step 2.3: Ingestion Endpoint (The "Write" Pipe)

Create `app/api/ingest.py`.

- **Route:** `POST /api/v1/ingest/metrics`
- **Logic:** Receive JSON list → Validate tenant_id → Bulk insert into metrics table

### Step 2.4: Dashboard Endpoints (The "Read" Pipe)

Create `app/api/dashboard.py`.

- **Route:** `GET /api/v1/metrics/live` (Fetch last 30 mins)
- **Route:** `GET /api/v1/recommendations/pending` (Fetch unapproved scaling events)
- **Route:** `POST /api/v1/recommendations/{id}/approve` (Update status to 'executed')

### Step 2.5: Run Backend

````bash
uvicorn app.main:app --reload
## Phase 3: The Simulator (Data Generator)

**Goal:** Generate "Ramadan-shaped" traffic to visualize.

### Step 3.1: Simulator Script

Create `simulator/traffic_gen.py`.

- **Libraries:** requests, random, time
- **Config:** `TARGET_URL = "http://localhost:8000/api/v1/ingest/metrics"`

**The Loop:**

1. Get current time (mocked speed: 1 second = 10 minutes)
2. Check "Ramadan Phase" (Suhoor, Iftar, Normal)
3. Generate cpu_usage and req_per_sec based on phase multipliers
4. POST to Backend
5. Sleep 0.5s

### Step 3.2: Verify Data Flow

Run the simulator. Check docker logs of the database or hit the `GET /metrics/live`

Sleep 0.5s.

## Phase 4: The Frontend (React Dashboard)

**Goal:** Visualize the surge and provide the "Approve" button.

### Step 4.1: Scaffolding

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install axios recharts lucide-react tailwindcss
````

### Step 4.2: Live Traffic Chart

Create `components/TrafficChart.tsx` using Recharts.

- Use `useEffect` to poll `GET /metrics/live` every 2 seconds
- **Visual:** Line chart showing "Requests per Second"

### Step 4.3: The "Action Center"

Create `components/PendingActions.tsx`.

- Poll `GET /recommendations/pending`
- **UI:** A list of cards. Example: "⚠️ Predicted Suhoor Surge. Scale to 40 replicas?"
- **Interaction:** [Approve] button calls `POST /approve`
  UI: A list of cards. Example: "⚠️ Predicted Suhoor Surge. Scale to 40 replicas?"

Interaction: [Approve] button calls POST /approve.

## Phase 5: The Intelligence (ML Engine)

**Goal:** The "Ramadan Indexer" logic.

### Step 5.1: The Forecaster Service

Create `backend/app/services/forecaster.py`.

**Logic:**

- Hardcode Ramadan Window (e.g., current dates)
- Function `predict_next_hour(history)`:
  - If current_hour is approaching 03:00 (Suhoor) → Return `SURGE_DETECTED`
  - If current_hour is approaching 18:30 (Iftar) → Return `DROP_EXPECTED`

### Step 5.2: The Cron Job

In `backend/app/main.py`, use `FastAPI.on_event("startup")` to launch a background task loop.

**Every 1 minute:**

1. Query recent metrics
2. Run `forecaster.predict()`
3. If surge predicted AND no pending recommendation exists → Insert into scaling_events
   If surge predicted AND no pending recommendation exists -> Insert into scaling_events.

Phase 6: Integration & Polish

## Phase 6: Integration & Polish

**Goal:** Connect the loop.

### Startup Sequence

1. **Start DB:** `docker-compose up`
2. **Start Backend:** `uvicorn ...`
3. **Start Frontend:** `npm run dev`
4. **Start Simulator:** `python traffic_gen.py`

### Testing Checklist

- Watch the chart rise
- Wait for the "Warning" to appear in the Action Center
- Click "Approve"
- See the "Executed" toast notification

## Phase 7: "Showcase" (Documentation)

**Goal:** Prepare for Judges.

### Deliverables

- **Architecture Diagram:** Add the Mermaid graph to README.md
- **Screenshots:** Capture the "Iftar Drop" and "Suhoor Spike" on the chart
- **Video:** Record a 60-second clip:
  - "Here is normal traffic..."
  - "The simulator enters Suhoor phase..."
  - "The system predicts a crash..."
  - "I click Approve..."
  - "The system logs the scaling action."
