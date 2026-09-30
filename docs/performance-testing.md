# AWS CloudSquad — SRE & Performance Testing Guide

CloudSquad integrates **k6** to execute automated benchmark testing against deployed workloads.

---

## 1. Multi-Stage Load Scenarios

Target RPS specified in mission requirements is an engineering target, not a guarantee. Performance testing executes four distinct stages to discover actual thresholds:

```text
1. Baseline Stage (30s)
   - Target: 10% of Target RPS
   - Purpose: Validates zero-error base latency and network warm-up.

2. Load Stage (1m)
   - Target: 50% of Target RPS
   - Purpose: Verifies connection pooling stability and cache hit rates.

3. Stress Stage (2m)
   - Target: 100% of Target RPS
   - Purpose: Confirms sustained SLA compliance under designed capacity.

4. Spike Stage (30s)
   - Target: 150% of Target RPS
   - Purpose: Tests auto-scaling response time and circuit breaker resilience.
```

---

## 2. Telemetry Metrics Measured
- **Actual Throughput (RPS)**: Measured successful HTTP requests per second.
- **Latency Percentiles**:
  - `P50`: Median user experience.
  - `P95`: Key SLA threshold.
  - `P99`: Tail latency under spike conditions.
- **Error Rate**: Percentage of non-2xx/3xx HTTP responses.
- **Availability Rate**: Overall service availability percentage (e.g. `99.97%`).

---

## 3. SRE Analysis Triad
The SREAgent explicitly separates:
1. **Observed Facts**: Hard telemetry figures recorded by k6 and CloudWatch.
2. **Technical Inferences**: Engineering deductions regarding bottlenecks (e.g., cold start latency, connection pool saturation).
3. **Safety-Gated Remediation Proposals**: Actionable remediation recommendations requiring human approval prior to execution.
