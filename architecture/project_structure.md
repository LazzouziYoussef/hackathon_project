# Sadaqa Tech Monorepo

## /infra

- /terraform # IaC for Cloud/K8s provisioning
- /k8s # Helm charts or Manifests (Deployment, Ingress, HPA)
- /docker # Dockerfiles for all services

## /backend (FastAPI)

- /app
  - /api # Routes (Ingest, Decisions)
  - /core # Config (Env vars, Constants)
  - /models # Pydantic Schemas (matches api_contract.json)
  - /services # Logic (Ramadan indexer, Scaling logic)
  - /db # TimescaleDB connection & CRUD

## /frontend (React + TypeScript)

- /src
  - /components # Recharts for dashboards
  - /pages # Admin Dashboard, Login
  - /hooks # API data fetching
  - /context # AuthContext (JWT handling)

## /ml_engine (Python)

- /training # Scripts to train LSTM/Seasonal models
- /inference # Service to run predictions on live data
- /notebooks # Exploratory data analysis

## /simulator

- traffic_gen.py # Locust or custom Python script
- profiles.json # The Ramadan traffic multipliers
