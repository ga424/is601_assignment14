#!/usr/bin/env bash

set -euo pipefail

# Color outputs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

help() {
    cat << 'EOF'
Usage: ./start.sh [COMMAND]

Commands:
    up          Start all services (db + app)
    down        Stop all services
    logs        View all service logs (pass extra args, e.g. -f)
    logs-app    View app service logs
    logs-db     View db service logs
    build       Build Docker images
    rebuild     Rebuild Docker images from scratch (no cache)
    ps          Show running services
    clean       Remove containers, volumes, and networks
    test        Run pytest in a disposable app container
    scan        Run Trivy filesystem security scan
    shell       Open a shell in the app container
    help        Show this help message

Docs:
    README      Project overview: README.md
    docs        Documentation index: docs/README.md

Examples:
    ./start.sh up
    ./start.sh logs -f
    ./start.sh logs-app
    ./start.sh down
EOF
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ensure local env file exists for convenience.
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created .env from .env.example${NC}"
fi

compose() {
    docker compose "$@"
}

case "${1:-help}" in
    up)
        echo -e "${GREEN}Starting services...${NC}"
        compose up -d
        echo -e "${GREEN}Services started.${NC}"
        compose ps
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}  Endpoints${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "  ${GREEN}App${NC}"
        echo -e "    Register:   http://localhost:8013/register"
        echo -e "    Login:      http://localhost:8013/login"
        echo -e "    Dashboard:  http://localhost:8013/dashboard"
        echo -e "    API root:   http://localhost:8013/"
        echo -e "    Health:     http://localhost:8013/health"
        echo -e "    API docs:   http://localhost:8013/docs"
        echo -e "    OpenAPI:    http://localhost:8013/openapi.json"
        echo ""
        echo -e "  ${GREEN}pgAdmin${NC}"
        echo -e "    URL:        http://localhost:5051"
        echo -e "    Email:      admin@admin.com"
        echo -e "    Password:   admin"
        echo -e "    DB host:    db  (port 5432 inside Docker)"
        echo ""
        echo -e "  ${GREEN}PostgreSQL (direct)${NC}"
        echo -e "    Host:       localhost:55432"
        echo -e "    User:       postgres"
        echo -e "    Password:   postgres"
        echo -e "    Database:   module14_db"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        ;;
    down)
        echo -e "${GREEN}Stopping services...${NC}"
        compose down
        echo -e "${GREEN}Services stopped.${NC}"
        ;;
    logs)
        compose logs "${@:2}"
        ;;
    logs-app)
        compose logs -f app
        ;;
    logs-db)
        compose logs -f db
        ;;
    build)
        echo -e "${GREEN}Building images...${NC}"
        compose build
        ;;
    rebuild)
        echo -e "${GREEN}Rebuilding images (no cache)...${NC}"
        compose build --no-cache
        ;;
    ps)
        compose ps
        ;;
    clean)
        echo -e "${YELLOW}Removing containers, volumes, and networks...${NC}"
        compose down -v --remove-orphans
        echo -e "${GREEN}Cleanup complete.${NC}"
        ;;
    test)
        echo -e "${GREEN}Running tests in container...${NC}"
        compose run --rm app pytest -q -m "not e2e"
        ;;
    scan)
        echo -e "${GREEN}Running Trivy filesystem scan...${NC}"
        docker run --rm -v "$PWD":/repo -w /repo aquasec/trivy:0.69.3 fs \
            --scanners vuln,secret,misconfig \
            --severity HIGH,CRITICAL \
            --ignore-unfixed \
            --exit-code 0 \
            .
        echo -e "${GREEN}Scan complete.${NC}"
        ;;
    shell)
        echo -e "${GREEN}Opening shell in app container...${NC}"
        compose run --rm app /bin/bash
        ;;
    help|*)
        help
        ;;
esac