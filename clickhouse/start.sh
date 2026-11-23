#!/bin/bash
# Refuses to start without a password, then hands over to the official
# entrypoint, which creates the user and the database on first boot.
set -euo pipefail
if [ -z "${CLICKHOUSE_PASSWORD:-}" ]; then
  echo "railway-start: CLICKHOUSE_PASSWORD is empty; set it (the template generates one)." >&2
  exit 1
fi
exec /entrypoint.sh "$@"
