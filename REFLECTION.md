# Module 11 Reflection

## Project Demonstrations

### 1. Core API and Validation Demonstration
- Demonstrated `POST /calculate` for all supported operation types: addition, subtraction, multiplication, and division.
- Demonstrated multi-operand support (for example: `[10, 5, 5, 5]`) and correct computed results.
- Demonstrated validation behavior:
  - invalid operation type returns request validation error
  - divide-by-zero denominator is rejected
  - insufficient input length is rejected

### 2. Persistence and Data Integrity Demonstration
- Demonstrated successful storage of each calculation in PostgreSQL with `id`, `a`, `b`, `type`, `inputs`, and `result`.
- Demonstrated read-back verification via integration tests to confirm data was persisted correctly.
- Demonstrated startup schema repair for older databases missing newly introduced columns (`a`, `b`).

### 3. Testing and Automation Demonstration
- Demonstrated passing unit tests for operation logic and factory selection.
- Demonstrated schema validation tests for invalid inputs.
- Demonstrated integration tests for database insert/read behavior.
- Demonstrated GitHub Actions CI with PostgreSQL service container.

### 4. Containerization and Delivery Demonstration
- Demonstrated Dockerized local runtime via `docker compose`.
- Demonstrated Docker Hub image publication to `ga424/module11`.
- Demonstrated security scanning with Trivy:
  - local command via `./start.sh scan`
  - CI workflow scan in GitHub Actions

## Key Challenges Faced

### 1. Database Schema Drift During Iteration
- Challenge: existing Postgres volume had an older `calculations` table shape while the model evolved.
- Impact: runtime 500 errors during insert (`UndefinedColumn` for `a`).
- Resolution: added startup schema reconciliation to add missing columns and backfill from legacy `inputs` values.

### 2. Input Handling Consistency
- Challenge: support for more than two operands needed to work consistently in API, factory, and persistence.
- Impact: confusion around passing list inputs versus positional arguments.
- Resolution: factory updated to normalize both list and variadic inputs; API route now unpacks inputs explicitly.

### 3. CI/CD Trigger Visibility
- Challenge: Docker publish status was initially unclear due to branch/tag event timing.
- Impact: uncertainty whether image push was executed.
- Resolution: confirmed workflow triggers, pushed synchronization updates, and published a version tag to force a deterministic release trigger.

### 4. Security Scan Reliability
- Challenge: initial scan setup using action pinning had resolution problems, and Trivy DB download occasionally timed out.
- Impact: scan workflow reliability concerns.
- Resolution: switched to direct Trivy Docker image invocation and re-ran scan successfully.

## Lessons Learned

1. Schema evolution needs explicit strategy even in small projects.
- `create_all()` is not enough for schema changes once data already exists.
- Lightweight migration/repair paths reduce downtime and debugging overhead.

2. Validation should exist at multiple boundaries.
- Request-level validation prevents bad input early.
- Runtime guardrails in core computation logic provide a second safety net.

3. Keep feature changes small and independently verifiable.
- Feature-by-feature commits made debugging and rollback decisions easier.
- Running tests after each meaningful change prevented compound failures.

4. Align local developer tooling with CI behavior.
- Matching local commands (`start.sh`, compose, scan) with CI jobs improves confidence before pushing.

5. Operational observability matters as much as code correctness.
- Container logs and health endpoints were essential for quickly isolating startup, DB, and runtime issues.

## What I Would Improve Next

- Introduce formal database migrations (for example, Alembic) instead of startup repair logic.
- Add non-root user in Dockerfile to satisfy current Trivy hardening recommendation.
- Migrate startup event usage to FastAPI lifespan handlers to remove deprecation warnings.
- Expand API tests to include additional edge cases and response contracts over time.
