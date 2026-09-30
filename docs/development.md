# AWS CloudSquad — Developer & Operations Guide

This guide details how to develop, test, run, and operate AWS CloudSquad locally and in production.

---

## 1. Prerequisites

- **Docker & Docker Compose**: v20+ with Compose v2+
- **Python**: 3.11+ (if running backend locally outside Docker)
- **Node.js**: 20+ & npm 10+ (if running frontend locally outside Docker)
- **AWS CLI**: configured if testing live AWS provisioning mode (`DEPLOYMENT_MODE=apply`)

---

## 2. Quickstart with Docker Compose

Launch the entire ecosystem (Frontend, FastAPI Core, Temporal Engine, Temporal Web UI, Worker, PostgreSQL, Redis) with a single command:

```bash
docker compose up --build
```

### Service Map
| Service | Role | Port | Health Check |
|---|---|---|---|
| **frontend** | Cockpit Dashboard (Next.js) | `http://localhost:3000` | Automated Next.js probe |
| **backend** | Core API & Event Bus (FastAPI) | `http://localhost:8000` | `GET /health` |
| **temporal-ui**| Temporal Workflow Web UI | `http://localhost:8088` | HTTP 200 OK |
| **temporal** | Temporal Server Cluster | `localhost:7233` | gRPC ping |
| **worker** | Mission Workflow Activity Worker| N/A (background) | Polling loop |
| **postgres** | Database (Metadata & Runs) | `localhost:5432` | `pg_isready` |
| **redis** | Event Bus & Message Distribution| `localhost:6379` | `redis-cli ping` |

---

## 3. Running Locally Without Docker

### Step 1: Start Supporting Infrastructure
```bash
docker compose up -d postgres redis temporal temporal-ui
```

### Step 2: Run Backend API & Worker
```bash
# Terminal 1: Backend
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Worker
cd backend
python -m workers.worker
```

### Step 3: Run Frontend Cockpit
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 4. Running Backend Automated Tests

Run the full pytest suite:
```bash
python -m pytest backend/tests -v
```

All 11 unit and integration tests (agents, CRUD API, workflow execution, validation gates) will run in parallel.
