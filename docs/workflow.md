# AWS CloudSquad — Temporal Workflow Orchestration

CloudSquad uses **Temporal** as its durable workflow orchestrator to manage the end-to-end cloud engineering lifecycle.

---

## 1. Why Temporal?

Rather than running asynchronous scripts or unstable loops, CloudSquad represents each mission execution as a durable, stateful workflow. If a network blip, container restart, or timeout occurs, Temporal resumes the workflow from the exact activity where it left off with exponential backoff retries.

```text
MissionWorkflow
    │
    ├── Step 1: architect_activity      (Retry: 3x, Timeout: 5m)
    ├── Step 2: database_activity       (Retry: 3x, Timeout: 5m)
    ├── Step 3: application_activity    (Retry: 3x, Timeout: 5m)
    ├── Step 4: infrastructure_activity (Retry: 3x, Timeout: 5m)
    ├── Step 5: security_activity       (Non-retryable on policy violation)
    ├── Step 6: deployment_activity     (Deterministic apply & health check)
    ├── Step 7: sre_activity            (k6 benchmark & telemetry analysis)
    └── Step 8: final_report_activity   (Report synthesis & closure)
```

---

## 2. Activity Contract

Every activity in `backend/workflows/activities.py` adheres to the following contract:
1. **Database Stage Synchronization**: Updates the stage status (`RUNNING`, `COMPLETED`, `FAILED`) in PostgreSQL via `MissionService`.
2. **Audit Event Emission**: Records a timestamped event into the database and broadcasts it over the Redis Pub/Sub event bus to active WebSocket cockpits.
3. **Artifact Persistence**: Saves generated code, schemas, and reports to object storage (`generated-output/{mission_id}/` or S3) and registers metadata in the `artifacts` table.
4. **Structured Error Handling**: Traps exceptions and sets `stage_info.error` with human-readable error messages before raising to Temporal.

---

## 3. Mission State Transitions

```text
CREATED 
  ──► PLANNING 
  ──► ARCHITECTURE_READY 
  ──► DATABASE_READY 
  ──► APPLICATION_READY 
  ──► INFRASTRUCTURE_READY 
  ──► SECURITY_VALIDATING 
  ──► SECURITY_PASSED (or SECURITY_BLOCKED ──► FAILED)
  ──► DEPLOYING 
  ──► DEPLOYED (or DEPLOYMENT_FAILED ──► RECOVERING)
  ──► OBSERVING 
  ──► BENCHMARKING 
  ──► ANALYZING 
  ──► COMPLETED (or FAILED)
```

---

## 4. Local Execution & Worker Configuration

The Temporal worker runs in its own container:
```bash
python -m workers.worker
```
- Listens to task queue: `cloudsquad-mission-queue`
- Namespace: `default`
- Temporal Web UI is accessible on port `8088` (`http://localhost:8088`).
