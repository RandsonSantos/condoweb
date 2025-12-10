#!/bin/bash
set -e
until python - <<PY
import sys
from sqlalchemy import create_engine
from config import Config
try:
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()
    conn.close()
except Exception as e:
    sys.exit(1)
PY
do
  echo "Aguardando o banco..."
  sleep 2
done

flask db upgrade || true
exec gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
