#!/usr/bin/env bash
# Run Docker Compose for the stage or prod environment.
#
# Usage:
#   ./deploy/compose.sh stage up -d --build
#   ./deploy/compose.sh stage logs -f web
#   ./deploy/compose.sh prod up -d --build
#   ./deploy/compose.sh prod exec web python manage.py createsuperuser
set -euo pipefail

ENVIRONMENT="${1:-}"
case "$ENVIRONMENT" in
    stage|prod) ;;
    *)
        echo "Usage: $0 <stage|prod> <docker compose arguments...>" >&2
        exit 1
        ;;
esac
shift || true

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.${ENVIRONMENT}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Missing ${ENV_FILE}. Create it from .env.example first." >&2
    exit 1
fi

cd "$ROOT_DIR"
export ENV_FILE=".env.${ENVIRONMENT}"

exec docker compose \
    --project-name "castleforever-${ENVIRONMENT}" \
    --env-file "$ENV_FILE" \
    --file "${ROOT_DIR}/compose.yaml" \
    "$@"
