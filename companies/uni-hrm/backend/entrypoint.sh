#!/bin/bash
set -e

echo "Applying database migrations..."
uv run python manage.py migrate --noinput

echo "Seeding initial data..."
uv run python manage.py seed_roles || true

exec "$@"
