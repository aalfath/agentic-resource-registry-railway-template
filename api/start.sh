#!/bin/bash
# Railway start script for the Agentic Resource Registry API service.
#  1. checks the required variables and adapts Railway's URLs,
#  2. prepares the /data volume (JWT signing keys, migration artefacts),
#  3. runs upstream's init (PostgreSQL schema/migrations, ClickHouse migrations),
#  4. creates the first super admin from ADMIN_EMAIL / ADMIN_PASSWORD (first boot only),
#  5. runs the API (uvicorn) and the arq background worker; if either exits, the
#     container exits so Railway restarts it.
set -euo pipefail

log() { echo "railway-start: $*"; }
die() { echo "railway-start: $*" >&2; exit 1; }

for v in DATABASE_URL REDIS_URL CLICKHOUSE_URL SECRET_KEY ADMIN_EMAIL ADMIN_PASSWORD; do
  [ -n "${!v:-}" ] || die "$v is empty. Set it on this service (the template sets or generates all of them; ADMIN_EMAIL is asked at deploy)."
done
[ "${#SECRET_KEY}" -ge 32 ] || die "SECRET_KEY must be at least 32 characters."
[[ "$ADMIN_EMAIL" == *@*.* ]] || die "ADMIN_EMAIL must be an email address, got '$ADMIN_EMAIL'."
[ "${#ADMIN_PASSWORD}" -ge 12 ] || die "ADMIN_PASSWORD must be at least 12 characters."
case "$PORT" in ''|*[!0-9]*) die "PORT must be a number, got '$PORT'";; esac

# Railway's Postgres gives postgresql://; the app uses SQLAlchemy's asyncpg driver.
case "$DATABASE_URL" in
  postgres://*)   DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgres://}" ;;
  postgresql://*) DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}" ;;
esac
export DATABASE_URL

# Never seed upstream's demo accounts (they have well-known emails); the first
# admin comes from ADMIN_EMAIL / ADMIN_PASSWORD instead.
for t in SUPER_ADMIN ADMIN REVIEWER USER; do
  export "DEMO_${t}_EMAIL=" "DEMO_${t}_PASSWORD="
done
export SEED_DEMO_ACCOUNTS=false

PUBLIC_URL="${PUBLIC_URL:-}"
PUBLIC_URL="${PUBLIC_URL%/}"
[ "$PUBLIC_URL" = "https://" ] && PUBLIC_URL=""
export PUBLIC_URL
export CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS:-${PUBLIC_URL:-http://localhost:3000}}"

mkdir -p "$JWT_KEY_DIR" "$MIGRATION_ARTIFACT_ROOT"
chown -R 1001:1001 /data
chmod 0700 "$JWT_KEY_DIR"

as_app() { setpriv --reuid=1001 --regid=1001 --clear-groups "$@"; }
PY=/app/.venv/bin/python
cd /app

# On a fresh deploy Postgres, Redis and ClickHouse start at the same time as this
# service, so retry the init (it is idempotent) while they come up.
log "running database and ClickHouse migrations"
tries=0
until as_app /app/entrypoint.sh; do
  tries=$((tries + 1))
  [ "$tries" -lt 30 ] || die "init still failing after $tries tries; see the errors above."
  log "init failed (try $tries of 30), the databases may still be starting; retrying in 5 s"
  sleep 5
done

log "checking the first administrator and deployment URLs"
as_app "$PY" /railway/bootstrap.py

log "starting the API on port $PORT and the background worker"
as_app "$PY" -m uvicorn main:app --host :: --port "$PORT" &
api_pid=$!
as_app "$PY" -c "import asyncio; asyncio.set_event_loop(asyncio.new_event_loop()); from arq import run_worker; from worker import WorkerSettings; run_worker(WorkerSettings)" &
worker_pid=$!

stop() { kill -TERM "$api_pid" "$worker_pid" 2>/dev/null || true; wait || true; exit 0; }
trap stop TERM INT

set +e
wait -n "$api_pid" "$worker_pid"
code=$?
log "a process exited (code $code); stopping the container so Railway restarts it"
kill -TERM "$api_pid" "$worker_pid" 2>/dev/null
wait
exit "${code:-1}"
