-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ===== TENANTS TABLE =====
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ===== USERS TABLE =====
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(tenant_id, email)
);

-- ===== METRICS TABLE (TimescaleDB hypertable) =====
CREATE TABLE IF NOT EXISTS metrics (
    time TIMESTAMP NOT NULL,
    tenant_id UUID NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convert metrics to a hypertable for time-series optimization
SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_metrics_tenant_time ON metrics (tenant_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_type_time ON metrics (metric_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_tags ON metrics USING GIN (tags);

-- ===== FORECASTS TABLE =====
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    forecast_time TIMESTAMP NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    predicted_value FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forecasts_tenant_time ON forecasts (tenant_id, forecast_time DESC);

-- ===== SCALING_EVENTS TABLE =====
CREATE TABLE IF NOT EXISTS scaling_events (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'SURGE_DETECTED', 'DROP_EXPECTED', etc.
    current_replicas INT NOT NULL,
    recommended_replicas INT NOT NULL,
    cost_impact_usd FLOAT,
    confidence FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'executed', 'rejected'
    reason TEXT NOT NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scaling_events_tenant_status ON scaling_events (tenant_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scaling_events_created_at ON scaling_events (created_at DESC);

-- ===== AUDIT_LOGS TABLE =====
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_time ON audit_logs (tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_time ON audit_logs (user_id, created_at DESC);

-- ===== SEED DATA =====
-- Insert demo tenant
INSERT INTO tenants (id, name, api_key_hash, is_active)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Demo NGO',
    'demo_api_key_hash_placeholder',
    true
)
ON CONFLICT (id) DO NOTHING;

-- Insert demo admin user
-- WARNING: Replace 'hashed_password_placeholder' with bcrypt/argon2 hash in production
INSERT INTO users (id, tenant_id, email, password_hash, full_name, role, is_active)
VALUES (
    '650e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    'admin@demo-ngo.org',
    'hashed_password_placeholder',
    'Admin User',
    'admin',
    true
)
ON CONFLICT (tenant_id, email) DO NOTHING;

-- ===== ROW LEVEL SECURITY (Tenant Isolation) =====
-- NOTE: Application must call: SET app.current_tenant_id = 'tenant-uuid';
-- before queries for RLS policies to enforce tenant isolation correctly.
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE scaling_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (example - adjust to your auth implementation)
CREATE POLICY tenant_isolation_tenants ON tenants
    USING (true); -- Replace with actual tenant context check

CREATE POLICY tenant_isolation_users ON users
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_metrics ON metrics
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_forecasts ON forecasts
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_scaling_events ON scaling_events
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_audit_logs ON audit_logs
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
