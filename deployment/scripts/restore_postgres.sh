#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: deployment/scripts/restore_postgres.sh deployment/backups/file.sql.gz"
  exit 1
fi

gzip -dc "$1" | docker compose exec -T db psql \
  -U "${POSTGRES_USER:-abn_user}" \
  -d "${POSTGRES_DB:-abn_registration}"
