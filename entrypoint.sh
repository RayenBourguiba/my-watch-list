#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${POSTGRES_HOST:-postgres-service}:${POSTGRES_PORT:-5432}..."

python - <<'PY'
import os, socket, time
host = os.getenv("POSTGRES_HOST", "postgres-service")
port = int(os.getenv("POSTGRES_PORT", "5432"))

for i in range(60):  # up to ~60 seconds
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print("PostgreSQL is reachable.")
        break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("PostgreSQL not reachable after 60s")
PY

python manage.py migrate --noinput

exec gunicorn --bind 0.0.0.0:8000 todo.wsgi:application