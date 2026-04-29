# Module 14 - JWT Auth + Calculation API

This project provides a FastAPI service with JWT-based user registration/login, calculation CRUD, PostgreSQL persistence, static login/register pages, Docker support, and CI/CD to Docker Hub.

## Quick Links

- [Project docs](docs/README.md)
- [Architecture diagrams](docs/C4_ARCHITECTURE.md)
- [Helper script](start.sh)
- [Login page](http://127.0.0.1:8013/login)
- [Register page](http://127.0.0.1:8013/register)
- [Docker Hub](https://hub.docker.com/r/ga424/is601_assignment14)

## What it does

- Implements user authentication endpoints:
  - `POST /register`
  - `POST /login`
- Implements calculation BREAD endpoints:
  - `GET /calculations`
  - `GET /calculations/{id}`
  - `POST /calculations`
  - `PUT /calculations/{id}`
  - `DELETE /calculations/{id}`
- Preserves legacy calculation endpoint `POST /calculate`
- Stores users and calculations in PostgreSQL
- Serves browser login/register pages from the same FastAPI app
- Exposes OpenAPI docs and a health endpoint

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
