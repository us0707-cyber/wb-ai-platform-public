#!/bin/sh
set -eu

STATE=$(python - <<'PY'
from sqlalchemy import inspect
from src.database.session import engine
with engine.connect() as connection:
    tables = set(inspect(connection).get_table_names())
print("existing" if "users" in tables and "alembic_version" not in tables else "managed")
PY
)

if [ "$STATE" = "existing" ]; then
  echo "Existing schema detected; stamping baseline migration."
  alembic stamp 0001_initial
fi

alembic upgrade head
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
