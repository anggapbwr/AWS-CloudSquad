"""
Agent 2: DatabaseAgent
Consumes ArchitectAgent output to design PostgreSQL schemas, migrations, indexing, and connection configurations.
"""
import json
from typing import Any, Dict
from agents.base import BaseAgent


class DatabaseAgent(BaseAgent):
    async def run(self) -> Dict[str, Any]:
        arch_spec = self.context.get("architecture_spec", {})
        components = arch_spec.get("components", {})
        db_engine = components.get("database", "RDS PostgreSQL (Multi-AZ)")
        target_rps = self.requirements.get("target_rps", 1000)

        schema_sql = """-- AWS CloudSquad Canonical Schema
-- Engine: PostgreSQL 16
-- Workload: E-Commerce Transactional Microservice

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price_cents BIGINT NOT NULL CHECK (price_cents >= 0),
    inventory_count INT NOT NULL DEFAULT 0 CHECK (inventory_count >= 0),
    version INT NOT NULL DEFAULT 1, -- Optimistic concurrency control
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    total_amount_cents BIGINT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price_cents BIGINT NOT NULL
);

-- Indexes for high-throughput queries
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_idempotency ON orders(idempotency_key);
"""

        migration_sql = """-- Migration: 0001_initial_schema.sql
-- Up Migration
BEGIN;

""" + schema_sql + """

-- Seed default initial inventory item for benchmark testing
INSERT INTO products (id, sku, title, description, price_cents, inventory_count, version)
VALUES ('00000000-0000-0000-0000-000000000001', 'FLASH-SALE-ITEM-1', 'CloudSquad Prime Device', 'High volume demo product', 9900, 1000000, 1)
ON CONFLICT (sku) DO NOTHING;

COMMIT;
"""

        database_config = {
            "engine": db_engine,
            "version": "16.3",
            "connection_pooling": {
                "max_connections": 100 if target_rps < 5000 else 250,
                "pool_size": 20,
                "max_overflow": 10,
                "pool_timeout_seconds": 30,
                "pool_recycle_seconds": 1800,
            },
            "parameters": {
                "shared_buffers": "512MB",
                "work_mem": "16MB",
                "maintenance_work_mem": "128MB",
                "effective_cache_size": "1536MB",
                "synchronous_commit": "off" if target_rps >= 5000 else "on",
                "checkpoint_completion_target": 0.9,
            },
            "backup_retention_days": 7,
            "storage_encrypted": True,
            "multi_az": True,
        }

        database_design_md = f"""# Database Architecture Specification

## Engine Selection
Architectural alignment: **{db_engine}**.
Optimized for high-concurrency ACID transactions with read/write splitting readiness.

## Concurrency & Idempotency Controls
1. **Optimistic Locking**: Handled via `products.version`. When updating inventory, application checks:
   `UPDATE products SET inventory_count = inventory_count - :qty, version = version + 1 WHERE id = :id AND version = :v AND inventory_count >= :qty`
2. **Idempotency**: Orders table enforces a unique `idempotency_key` constraint to prevent double charges during retry spikes.

## High-RPS Index Strategy
- Compound B-Tree on `(user_id, created_at DESC)` for sub-millisecond user order history.
- Unique B-Tree index on `orders.idempotency_key` for $O(1)$ duplicate checks.
- B-Tree index on `products.sku` for product catalog queries.
"""

        mission_id_str = str(self.mission_id)
        await self.storage.save_artifact(mission_id_str, "schema.sql", schema_sql, "application/sql")
        await self.storage.save_artifact(mission_id_str, "migration.sql", migration_sql, "application/sql")
        await self.storage.save_artifact(mission_id_str, "database-config.json", json.dumps(database_config, indent=2), "application/json")
        await self.storage.save_artifact(mission_id_str, "database-design.md", database_design_md, "text/markdown")

        return {
            "summary": f"Designed normalized PostgreSQL 16 schema with 4 tables, optimistic locking, and compound indexing for {target_rps:,} RPS.",
            "artifacts": [
                "schema.sql",
                "migration.sql",
                "database-config.json",
                "database-design.md",
            ],
            "schema_sql": schema_sql,
            "database_config": database_config,
        }
