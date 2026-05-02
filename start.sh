#!/usr/bin/env bash

echo "🚀 Starting FastAPI Application..."

# Run migrations (only if alembic exists)
if [ -f "alembic.ini" ]; then
  echo "📦 Running migrations..."
  alembic upgrade head
fi

# Start server (production-ready)
exec gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 120