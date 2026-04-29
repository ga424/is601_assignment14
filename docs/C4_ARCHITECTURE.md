# C4 Architecture Diagrams

## System Context

```mermaid
C4Context
    title Module 13 - JWT Auth and Calculation API Context

    Person(user, "User", "Registers, logs in, and uses the web app")
    Person(developer, "Developer", "Runs the app locally and reviews the API")
    Person(ci, "CI/CD", "Runs tests and publishes the container image")

    System(api, "FastAPI Web App", "FastAPI service that serves auth pages, issues JWTs, and manages calculations")
    SystemDb(database, "PostgreSQL Database", "Persists users and calculation records")
    System_Ext(dockerHub, "Docker Hub", "Stores published container images")

    BiRel(user, api, "Uses")
    BiRel(developer, api, "Runs and tests")
    BiRel(ci, api, "Builds, tests, and publishes")
    Rel(api, database, "Reads and writes")
    Rel(api, dockerHub, "Publishes images")
```

## Container Diagram

```mermaid
C4Container
    title Module 13 - JWT Auth and Calculation API Containers

    Person(user, "User", "Consumes the API")
    Person(developer, "Developer", "Maintains the project")

    System_Boundary(system, "JWT Auth and Calculation API") {
        Container(web, "FastAPI App", "Python / FastAPI", "Serves the API, static login/register pages, and JWT auth routes")
        ContainerDb(db, "PostgreSQL", "PostgreSQL", "Stores users and calculations")
        Container(ci, "GitHub Actions", "CI/CD", "Runs unit tests, Playwright E2E, and Docker publishing")
    }

    Container_Ext(registry, "Docker Hub", "Container Registry", "Receives published images")

    Rel(user, web, "Loads pages and calls endpoints", "HTTP")
    Rel(developer, web, "Runs locally")
    Rel(web, db, "Reads/Writes", "SQL")
    Rel(ci, web, "Builds and tests")
    Rel(ci, registry, "Pushes image")
```

## Component Diagram

```mermaid
C4Component
    title Module 13 - FastAPI App Components

    ContainerDb(db, "PostgreSQL")

    System_Boundary(api, "FastAPI App") {
        Component(routes, "Route Handlers", "FastAPI", "Expose /register, /login, /calculate, and calculation CRUD")
        Component(staticFiles, "Static Front End", "HTML/CSS/JS", "Serves the login and registration pages")
        Component(schemas, "Schemas", "Pydantic", "Validate auth and calculation payloads")
        Component(security, "Security Helpers", "Passlib / PyJWT", "Hash passwords and issue JWT access tokens")
        Component(models, "ORM Models", "SQLAlchemy", "Represent users and calculations")
        Component(database, "DB Session", "SQLAlchemy", "Creates sessions and persists rows")
    }

    Rel(routes, staticFiles, "Serves")
    Rel(routes, schemas, "Validates with")
    Rel(routes, security, "Hashes passwords and creates tokens")
    Rel(routes, models, "Creates and computes")
    Rel(routes, database, "Uses")
    Rel(database, db, "Reads/Writes")
```

## Deployment Diagram

```mermaid
flowchart LR
    browser[Client Browser] -->|HTTP| app[FastAPI App Container]
    app -->|SQL| db[(PostgreSQL Container)]
    github[GitHub Actions Runner] -->|Build/Test| app
    github -->|Push Image| dockerhub[Docker Hub]
```
