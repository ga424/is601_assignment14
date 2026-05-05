# IS601 Assignment 14 — BREAD Calculations API

This project demonstrates a full-stack implementation of BREAD (Browse, Read, Edit, Add, Delete) endpoints for a user-owned calculations resource, built with FastAPI, PostgreSQL, JWT authentication, and a browser-based dashboard. It includes Playwright end-to-end tests covering positive and negative scenarios, and a CI/CD pipeline that runs all tests and publishes a Docker image to Docker Hub.

## Quick Links

- [Docker Hub](https://hub.docker.com/r/ga424/is601_assignment14)
- [OpenAPI Docs](http://127.0.0.1:8013/docs) *(local)*
- [Architecture diagrams](docs/C4_ARCHITECTURE.md)
- [Helper script](start.sh)

## BREAD Endpoints

All calculation endpoints require a valid JWT (`Authorization: Bearer <token>`). Each user can only access their own calculations.

| Operation | Method | Path | Description |
|-----------|--------|------|-------------|
| Browse | `GET` | `/calculations` | List all calculations for the logged-in user |
| Read | `GET` | `/calculations/{id}` | Retrieve a single calculation by ID |
| Edit | `PUT` | `/calculations/{id}` | Update operation type, inputs, and result |
| Add | `POST` | `/calculations` | Create a new calculation |
| Delete | `DELETE` | `/calculations/{id}` | Remove a calculation |

**Authentication endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/register` | Create a new user account, returns JWT |
| `POST` | `/login` | Authenticate and receive a JWT |

## Front-End Dashboard

The browser dashboard (`/`) lets authenticated users perform all BREAD operations without leaving the page:

- **Browse** — calculations table loads automatically on login
- **Add** — form accepts operation type and comma-separated numeric inputs
- **Read** — View button displays calculation details inline
- **Edit** — Edit button pre-populates the form; saving issues a `PUT` request
- **Delete** — Delete button prompts for confirmation before removing

Client-side validation rejects non-numeric inputs, single-value inputs (minimum 2 operands required), and mismatched passwords on registration.

## Tests

Playwright E2E tests cover both happy-path and failure scenarios:

- **Positive:** register, login, create, list, view, update, delete calculations
- **Negative:** duplicate email, wrong password, tampered JWT, non-numeric inputs, single operand, division by zero, cross-user access isolation

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

## Run locally

Start PostgreSQL with Docker:

```bash
docker compose up -d db
```

Then run the app locally:

```bash
uvicorn app.main:app --reload
```

Open the app and docs:

- `http://127.0.0.1:8013/`
- `http://127.0.0.1:8013/register`
- `http://127.0.0.1:8013/login`
- `http://127.0.0.1:8013/docs`

## Example request

```bash
curl -X POST http://127.0.0.1:8013/calculations \
  -H "Content-Type: application/json" \
  -d '{"type":"addition","inputs":[3,4,5]}'
```

Register user:

```bash
curl -X POST http://127.0.0.1:8013/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"strongpassword123"}'
```

Login user:

```bash
curl -X POST http://127.0.0.1:8013/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"strongpassword123"}'
```

## Test

```bash
python3 -m pytest -q -m "not e2e"
```

If you want to target the Dockerized database explicitly, set `DATABASE_URL` to the compose PostgreSQL connection string and run the same test command.

Run API-only tests:

```bash
python3 -m pytest -q tests/test_api.py
```

Run DB integration tests:

```bash
python3 -m pytest -q tests/test_integration_db.py
```

Run Playwright end-to-end tests:

```bash
./start.sh up
python3 -m playwright install chromium
python3 -m pytest -q -m e2e
```

## Manual OpenAPI checks

1. Start services: `./start.sh up` (or `docker compose up --build`)
2. Open `http://127.0.0.1:8013/docs`
3. Verify user endpoints:
  - `POST /register` creates a user and returns a JWT (201)
  - `POST /login` validates credentials and returns a JWT (200)
4. Verify calculation endpoints:
   - `POST /calculations` creates a calculation (201)
   - `GET /calculations` lists calculations (200)
   - `GET /calculations/{id}` returns one calculation (200)
   - `PUT /calculations/{id}` updates calculation values/result (200)
   - `DELETE /calculations/{id}` removes the calculation (204)
5. Verify invalid payloads return expected error codes (e.g. 401/404/409/422)

Run local security scan:

```bash
./start.sh scan
```

## Screenshots

- **CI workflow run:** `docs/ci-workflow-screenshot.png` — successful GitHub Actions run showing all three jobs (unit, integration, e2e) passing.
- **Docker Hub deployment:** `docs/docker-hub-screenshot.png` — Docker image pushed to [hub.docker.com/r/ga424/is601_assignment14](https://hub.docker.com/r/ga424/is601_assignment14).
- **Application front-end:** `docs/app-screenshots/` — screenshots of Browse, Read, Edit, Add, and Delete operations from the dashboard.

## CI/CD

- CI workflow: `.github/workflows/ci.yml`
  - Starts PostgreSQL and the FastAPI app
  - Runs pytest unit tests and Playwright browser tests
- Docker publish workflow: `.github/workflows/docker-publish.yml`
  - Repeats the test flow, then builds and pushes the Docker image to Docker Hub on tags (`v*`) or manual dispatch
- Security scan workflow: `.github/workflows/security-scan.yml`
  - Runs Trivy filesystem and image scans

Required repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## Docker

Run full stack (PostgreSQL + app):

```bash
docker compose up --build
```

App URL:

- `http://127.0.0.1:8013/`

Build image only:

```bash
docker build -t ga424/is601_assignment14:latest .
```

Run:

```bash
docker run --rm -p 8013:8013 ga424/is601_assignment14:latest
```

## Notes

- The model stores physical `a` and `b` columns for the first two operands and keeps `inputs[]` for the full request payload.
- The documentation in `docs/` includes the C4 architecture view and a navigation index.
- Docker Hub repository: [hub.docker.com/r/ga424/is601_assignment14](https://hub.docker.com/r/ga424/is601_assignment14)
