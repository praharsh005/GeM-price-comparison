#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import sys, time
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set")
    sys.exit(1)

for i in range(30):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database ready.")
        sys.exit(0)
    except Exception as exc:
        print(f"db not ready: {exc}")
        time.sleep(2)
print("Database not reachable in time.")
sys.exit(1)
PY

echo "Running migrations..."
alembic upgrade head

echo "Seeding if empty..."
python - <<'PY'
from app.database import SessionLocal
from app.models import Product
from app.seed import run as seed_run

db = SessionLocal()
try:
    count = db.query(Product).count()
    print(f"Existing products: {count}")
    if count == 0:
        print("No products found, running seed...")
        seed_run(db=db)
        db.commit()
        print("Seed committed.")
    else:
        print("Database already seeded, skipping seed.")
finally:
    db.close()
PY

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2