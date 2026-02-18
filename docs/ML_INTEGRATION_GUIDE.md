# ML Engine Integration Guide for Backend Developers

**Version**: 1.0  
**Date**: February 2026  
**Status**: Ready for Integration

This document provides complete instructions for integrating the Sadaqa Tech ML Engine into the FastAPI backend.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [ML Components](#ml-components)
4. [Integration Steps](#integration-steps)
5. [API Endpoint Specifications](#api-endpoint-specifications)
6. [Database Schema Requirements](#database-schema-requirements)
7. [Example Usage](#example-usage)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Production Considerations](#production-considerations)

---

## Overview

The ML Engine provides **traffic prediction** and **scaling recommendations** for NGO infrastructure during Ramadan. It follows the principle: **Prediction before automation**.

**Core Capabilities:**

- Load historical metrics from TimescaleDB
- Engineer 19 features (time, Ramadan, rolling, lag, prayer windows)
- Train hybrid forecaster (baseline + pattern learner + confidence scorer)
- Generate 4-hour traffic predictions
- Calculate replica recommendations with cost impact
- Save/load trained models for inference

**Key Constraint:** All operations are **tenant-scoped**. No cross-tenant data access.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /api/ml/predict                                     │   │
│  │  - Validate tenant_id from JWT                            │   │
│  │  - Load trained model for tenant                          │   │
│  │  - Get recent metrics from TimescaleDB                    │   │
│  │  - Generate prediction + scaling recommendation           │   │
│  │  - Return JSON response with cost impact                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /api/ml/train                                       │   │
│  │  - Validate tenant_id from JWT (admin only)               │   │
│  │  - Trigger training pipeline                              │   │
│  │  - Store trained model to disk                            │   │
│  │  - Return training summary                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ML Engine (Python)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ml_engine/                                               │   │
│  │  ├── preprocessing/                                       │   │
│  │  │   ├── data_loader.py         (TimescaleDB → DataFrame)│   │
│  │  │   └── feature_engineering.py (19 features)            │   │
│  │  ├── models/                                              │   │
│  │  │   ├── seasonal_baseline.py   (fallback)               │   │
│  │  │   ├── pattern_learner.py     (Ramadan patterns)       │   │
│  │  │   └── confidence_scorer.py   (6 factors)              │   │
│  │  ├── forecaster.py              (hybrid predictor)       │   │
│  │  ├── scaling_calculator.py      (replica + cost)         │   │
│  │  └── training/                                            │   │
│  │      └── train.py                (end-to-end training)    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       TimescaleDB                                │
│  - metrics table (tenant_id, timestamp, metric_type, value)     │
│  - Row-level security for tenant isolation                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## ML Components

### 1. Data Loading (`MetricsDataLoader`)

**Purpose:** Load historical metrics from TimescaleDB.

**Usage:**

```python
from preprocessing.data_loader import MetricsDataLoader

loader = MetricsDataLoader(db_connection)
df = loader.load_historical_metrics(
    tenant_id="ngo_abc",
    start_date=datetime.now() - timedelta(days=60),
    end_date=datetime.now()
)
```

**Output:** DataFrame with `timestamp` index and `value` column.

---

### 2. Feature Engineering (`FeatureEngineer`)

**Purpose:** Engineer 19 features from raw metrics.

**Features Generated:**

- **Time features** (6): hour, day_of_week, is_weekend, month, day_of_month, week_of_year
- **Ramadan features** (4): is_ramadan, ramadan_day, days_until_ramadan, is_last_10_nights
- **Rolling features** (4): rolling_mean_24h, rolling_std_24h, rolling_min_24h, rolling_max_24h
- **Lag features** (3): lag_1h, lag_24h, lag_168h
- **Prayer window features** (2): is_prayer_window, minutes_to_next_prayer

**Usage:**

```python
from preprocessing.feature_engineering import FeatureEngineer

engineer = FeatureEngineer()
df = engineer.add_time_features(df)
df = engineer.add_ramadan_features(df, year=2024)
df = engineer.add_rolling_features(df, value_col='value')
df = engineer.add_lag_features(df, value_col='value')
df = engineer.add_prayer_features(df)
```

---

### 3. Hybrid Forecaster (`HybridForecaster`)

**Purpose:** Generate 4-hour traffic predictions using rule-based triggers + ML-learned patterns.

**Components:**

- `SeasonalBaselineModel`: Fallback (hourly averages per Ramadan day)
- `RamadanPatternLearner`: Learns Iftar, Taraweeh, Suhoor traffic patterns
- `ConfidenceScorer`: Scores predictions (0-1) based on 6 factors

**Usage:**

```python
from forecaster import HybridForecaster

forecaster = HybridForecaster()
forecaster.train(historical_df)

predictions = forecaster.predict(
    current_timestamp=datetime.now(),
    current_traffic=150.0
)
# Returns: {
#   'predictions': [180, 220, 250, 200],  # Next 4 hours
#   'confidence': 0.85,
#   'trigger': 'iftar_approaching',
#   'model_used': 'pattern_learner'
# }
```

**Trigger Rules:**

1. **Iftar approaching**: 2 hours before Iftar → predict surge
2. **Taraweeh time**: During evening prayers → predict sustained load
3. **Suhoor window**: 2 hours before Fajr → predict pre-dawn traffic

---

### 4. Scaling Calculator (`ScalingCalculator`)

**Purpose:** Calculate replica counts and cost impacts from predictions.

**Formula:**

```
recommended_replicas = ceil(predicted_traffic / capacity_per_pod) * safety_factor
```

**Safety Constraints:**

- MAX_REPLICAS: 50 (hard cap)
- MIN_REPLICAS: 1 (configurable)
- Hysteresis: 5-minute cooldown between scaling actions
- Cost caps: Admin-defined per tenant

**Usage:**

```python
from scaling_calculator import ScalingCalculator, WorkloadConfig

calculator = ScalingCalculator()
config = WorkloadConfig(
    service_name="donation-api",
    current_replicas=10,
    capacity_per_pod=50.0,
    cost_per_replica_hour=0.05
)

recommendation = calculator.calculate_scaling(
    predictions=[180, 220, 250, 200],
    config=config
)
# Returns: ScalingRecommendation(
#   recommended_replicas=15,
#   cost_impact_hourly=0.25,
#   reason="Predicted surge from 150 to 250 requests/min",
#   triggered_by="iftar_approaching"
# )
```

---

### 5. Training Pipeline (`TrainingPipeline`)

**Purpose:** End-to-end training workflow.

**Steps:**

1. Load 60+ days of historical data
2. Engineer features
3. Train all models (baseline, pattern learner, forecaster)
4. Save models to disk with versioning

**Usage:**

```python
from training.train import TrainingPipeline

pipeline = TrainingPipeline(
    tenant_id="ngo_abc",
    model_dir="ml_engine/models_trained",
    min_training_days=60
)

# Option 1: Load from database
summary = pipeline.run(days_history=90)

# Option 2: Provide DataFrame (for testing)
summary = pipeline.run(df=historical_data)
```

**Output:**

- Model file: `models_trained/forecaster_{tenant_id}_{timestamp}.pkl`
- Symlink: `models_trained/forecaster_{tenant_id}_latest.pkl`
- Summary dict with data stats, model config, file paths

---

## Integration Steps

### Step 1: Database Connection Setup

Create a database connection pool in your FastAPI app:

```python
# backend/app/db/connection.py
import asyncpg
from typing import Optional

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self, dsn: str):
        self.pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def fetch_all(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

db_pool = DatabasePool()

# In main.py startup event
@app.on_event("startup")
async def startup():
    await db_pool.connect("postgresql://user:pass@timescaledb:5432/sadaqa")
```

---

### Step 2: Create ML Service Layer

```python
# backend/app/services/ml_service.py
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from preprocessing.data_loader import MetricsDataLoader
from preprocessing.feature_engineering import FeatureEngineer
from forecaster import HybridForecaster
from scaling_calculator import ScalingCalculator, WorkloadConfig
from training.train import TrainingPipeline

class MLService:
    def __init__(self, db_connection, model_dir: str = "ml_engine/models_trained"):
        self.db = db_connection
        self.model_dir = Path(model_dir)
        self.data_loader = MetricsDataLoader(db_connection)
        self.feature_engineer = FeatureEngineer()
        self.scaling_calculator = ScalingCalculator()
        self._model_cache = {}  # tenant_id -> forecaster

    def _load_model(self, tenant_id: str) -> HybridForecaster:
        """Load trained model from disk (with caching)."""
        if tenant_id in self._model_cache:
            return self._model_cache[tenant_id]

        # Load from latest symlink
        model_path = self.model_dir / f"forecaster_{tenant_id}_latest.pkl"
        if not model_path.exists():
            raise FileNotFoundError(
                f"No trained model found for tenant '{tenant_id}'. "
                "Please train a model first via POST /api/ml/train"
            )

        with open(model_path, 'rb') as f:
            forecaster = pickle.load(f)

        self._model_cache[tenant_id] = forecaster
        return forecaster

    async def generate_prediction(
        self,
        tenant_id: str,
        service_name: str,
        current_replicas: int,
        capacity_per_pod: float,
        cost_per_replica_hour: float
    ) -> Dict[str, Any]:
        """Generate traffic prediction and scaling recommendation."""

        # 1. Load trained model
        forecaster = self._load_model(tenant_id)

        # 2. Get recent metrics (last 7 days for context)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        df = self.data_loader.load_historical_metrics(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        if len(df) == 0:
            raise ValueError("No recent metrics available for prediction")

        # 3. Engineer features
        df = self.feature_engineer.add_time_features(df)
        year = df.index[-1].year
        df = self.feature_engineer.add_ramadan_features(df, year=year)

        # 4. Get current traffic (last value)
        current_traffic = df['value'].iloc[-1]
        current_timestamp = df.index[-1]

        # 5. Generate prediction
        prediction_result = forecaster.predict(
            current_timestamp=current_timestamp,
            current_traffic=current_traffic
        )

        # 6. Calculate scaling recommendation
        workload_config = WorkloadConfig(
            service_name=service_name,
            current_replicas=current_replicas,
            capacity_per_pod=capacity_per_pod,
            cost_per_replica_hour=cost_per_replica_hour
        )

        recommendation = self.scaling_calculator.calculate_scaling(
            predictions=prediction_result['predictions'],
            config=workload_config
        )

        # 7. Return combined result
        return {
            'tenant_id': tenant_id,
            'timestamp': current_timestamp.isoformat(),
            'current_traffic': current_traffic,
            'predictions': {
                'values': prediction_result['predictions'],
                'confidence': prediction_result['confidence'],
                'trigger': prediction_result['trigger'],
                'model_used': prediction_result['model_used']
            },
            'scaling_recommendation': {
                'current_replicas': current_replicas,
                'recommended_replicas': recommendation.recommended_replicas,
                'cost_impact_hourly': recommendation.cost_impact_hourly,
                'reason': recommendation.reason,
                'triggered_by': recommendation.triggered_by,
                'requires_approval': True  # Always require human approval
            }
        }

    async def train_model(self, tenant_id: str, days_history: int = 60) -> Dict[str, Any]:
        """Train a new model for the tenant."""

        pipeline = TrainingPipeline(
            tenant_id=tenant_id,
            model_dir=str(self.model_dir),
            min_training_days=60
        )

        # Load data using the data_loader with DB connection
        end_date = datetime.now()
        df = self.data_loader.load_historical_metrics(
            tenant_id=tenant_id,
            start_date=end_date - timedelta(days=days_history),
            end_date=end_date
        )

        # Run training pipeline with pre-loaded data
        summary = pipeline.run(df=df)

        # Clear model cache to force reload on next prediction
        if tenant_id in self._model_cache:
            del self._model_cache[tenant_id]

        return summary
```

---

### Step 3: Create API Endpoints

````python
# backend/app/api/routes/ml.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.api.deps import get_current_user, get_ml_service
from app.services.ml_service import MLService

router = APIRouter(prefix="/ml", tags=["ml"])


class PredictionRequest(BaseModel):
    service_name: str = Field(..., description="Name of the service to scale")
    current_replicas: int = Field(..., ge=1, le=50)
    capacity_per_pod: float = Field(..., gt=0, description="Requests/min per pod")
    cost_per_replica_hour: float = Field(0.05, gt=0, description="Cost per replica per hour")


class PredictionResponse(BaseModel):
    tenant_id: str
    timestamp: str
    current_traffic: float
    predictions: Dict[str, Any]
    scaling_recommendation: Dict[str, Any]


class TrainingRequest(BaseModel):
    days_history: int = Field(60, ge=30, le=365, description="Days of historical data")


class TrainingResponse(BaseModel):
    tenant_id: str
    training_timestamp: str
    data_stats: Dict[str, Any]
    model_summaries: Dict[str, Any]
    saved_models: Dict[str, str]


@router.post("/predict", response_model=PredictionResponse)
async def generate_prediction(
    request: PredictionRequest,
    current_user = Depends(get_current_user),
    ml_service: MLService = Depends(get_ml_service)
):
    """Generate traffic prediction and scaling recommendation.

    **Authorization:** Requires valid JWT token.
    **Tenant isolation:** Uses tenant_id from JWT.
    **Returns:** 4-hour traffic forecast + replica recommendation with cost impact.

    **Example:**
    ```json
    {
      "service_name": "donation-api",
      "current_replicas": 10,
      "capacity_per_pod": 50.0,
      "cost_per_replica_hour": 0.05
    }
    ```
    """
    try:
        result = await ml_service.generate_prediction(
            tenant_id=current_user.tenant_id,
            service_name=request.service_name,
            current_replicas=request.current_replicas,
            capacity_per_pod=request.capacity_per_pod,
            cost_per_replica_hour=request.cost_per_replica_hour
        )
        return result

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    current_user = Depends(get_current_user),
    ml_service: MLService = Depends(get_ml_service)
):
    """Train a new ML model for the tenant.

    **Authorization:** Requires admin role.
    **Tenant isolation:** Trains only on tenant's historical data.
    **Duration:** May take 30-60 seconds depending on data volume.

    **Example:**
    ```json
    {
      "days_history": 90
    }
    ```
    """
    # Check admin permission
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Training requires admin privileges"
        )

    try:
        summary = await ml_service.train_model(
            tenant_id=current_user.tenant_id,
            days_history=request.days_history
        )
        return summary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )
````

---

### Step 4: Register Routes

```python
# backend/app/main.py
from fastapi import FastAPI
from app.api.routes import ml

app = FastAPI(title="Sadaqa Tech API")

# Register ML routes
app.include_router(ml.router, prefix="/api")
```

---

## Database Schema Requirements

The ML engine expects metrics to be stored in TimescaleDB with the following schema:

```sql
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    tenant_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- e.g., 'requests_per_minute'
    value DOUBLE PRECISION NOT NULL,
    metadata JSONB
);

-- Convert to hypertable
SELECT create_hypertable('metrics', 'time');

-- Indexes for tenant isolation
CREATE INDEX idx_metrics_tenant_time ON metrics (tenant_id, time DESC);
CREATE INDEX idx_metrics_tenant_type ON metrics (tenant_id, metric_type, time DESC);

-- Row-level security (optional but recommended)
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON metrics
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::TEXT);
```

**Metric Types:**

- `requests_per_minute`: HTTP request rate
- `error_rate`: Percentage of failed requests
- `latency_p50`: Median response time (ms)
- `latency_p95`: 95th percentile response time (ms)
- `latency_p99`: 99th percentile response time (ms)
- `cpu_usage`: CPU utilization (0-100%)
- `memory_usage`: Memory usage (MB)

---

## Example Usage

### 1. Train a Model (First Time Setup)

```bash
POST /api/ml/train
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "days_history": 90
}
```

**Response:**

```json
{
  "tenant_id": "ngo_abc",
  "training_timestamp": "20260218_143022",
  "data_stats": {
    "total_points": 2160,
    "date_range_start": "2023-11-20 00:00:00",
    "date_range_end": "2024-02-18 23:00:00",
    "days_of_data": 90,
    "features_count": 19
  },
  "model_summaries": {
    "forecaster": {
      "trained": true,
      "forecast_horizon_hours": 4,
      "trigger_rules": 3
    }
  },
  "saved_models": {
    "forecaster": "ml_engine/models_trained/forecaster_ngo_abc_20260218_143022.pkl"
  }
}
```

---

### 2. Generate Prediction

```bash
POST /api/ml/predict
Authorization: Bearer <user_jwt_token>
Content-Type: application/json

{
  "service_name": "donation-api",
  "current_replicas": 10,
  "capacity_per_pod": 50.0,
  "cost_per_replica_hour": 0.05
}
```

**Response:**

```json
{
  "tenant_id": "ngo_abc",
  "timestamp": "2024-03-15T16:30:00Z",
  "current_traffic": 150.0,
  "predictions": {
    "values": [180, 220, 280, 240],
    "confidence": 0.87,
    "trigger": "iftar_approaching",
    "model_used": "pattern_learner"
  },
  "scaling_recommendation": {
    "current_replicas": 10,
    "recommended_replicas": 18,
    "cost_impact_hourly": 0.4,
    "reason": "Predicted surge from 150 to 280 requests/min (Iftar in 2 hours)",
    "triggered_by": "iftar_approaching",
    "requires_approval": true
  }
}
```

---

## Error Handling

### Common Errors

| Error Code | Scenario                    | Solution                                         |
| ---------- | --------------------------- | ------------------------------------------------ |
| **404**    | No trained model found      | Train a model via POST /api/ml/train             |
| **400**    | No recent metrics available | Ensure metrics are being ingested to TimescaleDB |
| **400**    | Insufficient training data  | Requires at least 60 days of metrics             |
| **403**    | Training without admin role | Only admins can trigger training                 |
| **500**    | Model loading failure       | Check model file exists and is valid .pkl        |

### Error Response Format

```json
{
  "detail": "No trained model found for tenant 'ngo_abc'. Please train a model first via POST /api/ml/train"
}
```

---

## Testing

### Unit Tests (ML Components)

All ML components have comprehensive test coverage:

```bash
# Run all ML tests with PYTHONPATH set
docker run --rm -v "$PWD":/app -e PYTHONPATH=/app/ml_engine \
  sadaqa-ml-test pytest ml_engine/ -v

# Test coverage summary:
# - Data loading: 4 tests
# - Feature engineering: 8 tests
# - Seasonal baseline: 6 tests
# - Pattern learner: 6 tests
# - Confidence scorer: 15 tests
# - Forecaster: 16 tests
# - Scaling calculator: 27 tests
# - Training pipeline: 30 tests
# Total: 112 tests
```

---

### Integration Tests (API Endpoints)

```python
# backend/tests/test_ml_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_predict_endpoint(async_client: AsyncClient, admin_token: str):
    # First train a model
    train_response = await async_client.post(
        "/api/ml/train",
        json={"days_history": 60},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert train_response.status_code == 200

    # Then generate prediction
    predict_response = await async_client.post(
        "/api/ml/predict",
        json={
            "service_name": "donation-api",
            "current_replicas": 10,
            "capacity_per_pod": 50.0,
            "cost_per_replica_hour": 0.05
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert predict_response.status_code == 200
    data = predict_response.json()

    # Validate response structure
    assert "predictions" in data
    assert "scaling_recommendation" in data
    assert len(data["predictions"]["values"]) == 4
    assert data["scaling_recommendation"]["requires_approval"] is True
```

---

## Production Considerations

### 1. Model Versioning

Models are automatically versioned with timestamps:

- File: `forecaster_{tenant_id}_20260218_143022.pkl`
- Symlink: `forecaster_{tenant_id}_latest.pkl`

**Best Practice:** Keep last 3 versions for rollback capability.

---

### 2. Model Refresh Schedule

**Recommended:** Retrain models weekly during low-traffic periods.

```python
# Example: Celery task for scheduled retraining
from celery import shared_task

@shared_task
def retrain_all_tenants():
    for tenant in get_active_tenants():
        ml_service.train_model(tenant_id=tenant.id, days_history=90)
```

---

### 3. Caching Strategy

- **Model cache:** In-memory (per-tenant) to avoid disk I/O on every request
- **Prediction cache:** Redis (5-minute TTL) to reduce computation
- **Clear cache:** On model retrain

---

### 4. Monitoring

**Key Metrics to Track:**

```python
# Prometheus metrics
prediction_latency = Histogram('ml_prediction_latency_seconds')
prediction_confidence = Gauge('ml_prediction_confidence', ['tenant_id'])
model_age_hours = Gauge('ml_model_age_hours', ['tenant_id'])
scaling_recommendations = Counter('ml_scaling_recommendations', ['tenant_id', 'trigger'])
```

---

### 5. Resource Requirements

**Training:**

- CPU: 2 cores
- Memory: 2 GB
- Duration: 30-60 seconds per tenant

**Inference:**

- CPU: 0.5 cores
- Memory: 512 MB
- Latency: < 200ms per prediction

---

### 6. Security Checklist

- ✅ Tenant isolation enforced at database layer (row-level security)
- ✅ All operations scoped to `tenant_id` from JWT
- ✅ Admin-only training endpoint
- ✅ Model files isolated per tenant (no cross-tenant access)
- ✅ Predictions require human approval before execution
- ✅ Cost caps configurable per tenant
- ✅ Audit logs for all scaling decisions

---

## Quick Start Checklist

For backend developers integrating the ML engine:

- [ ] Set up TimescaleDB with `metrics` table and row-level security
- [ ] Configure database connection pool in FastAPI
- [ ] Create `MLService` class with database connection
- [ ] Implement `/api/ml/predict` endpoint with JWT auth
- [ ] Implement `/api/ml/train` endpoint (admin-only)
- [ ] Add dependency injection for `get_ml_service()`
- [ ] Set PYTHONPATH=/app/ml_engine in Docker environment
- [ ] Create model storage directory (`ml_engine/models_trained/`)
- [ ] Add Prometheus metrics for monitoring
- [ ] Write integration tests
- [ ] Document deployment configuration
- [ ] Schedule weekly model retraining (Celery/cron)

---

## Support

For questions or issues with ML integration:

1. **ML Component Issues:** Check test coverage and error logs
2. **Database Schema:** Verify TimescaleDB hypertable setup
3. **Performance:** Profile with `cProfile` or `py-spy`
4. **Model Accuracy:** Increase `days_history` to 90+ for better patterns

---

**Last Updated:** February 18, 2026  
**ML Engine Version:** 1.0  
**Status:** Production-Ready ✅
