#!/bin/bash
set -e

# Decode resume from base64 env var if provided
if [ -n "$RESUME_BASE64" ]; then
  mkdir -p /app/resume
  echo "$RESUME_BASE64" | base64 -d > /app/resume/resume.pdf
  export RESUME_FILE_PATH=/app/resume/resume.pdf
  echo "[entrypoint] Resume decoded from RESUME_BASE64"
fi

# Start the server (DB init and seeding happen inside lifespan)
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
