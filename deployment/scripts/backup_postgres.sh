#!/usr/bin/env sh
set -eu

mkdir -p deployment/backups
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
file="deployment/backups/abn-registration-${timestamp}.sql.gz"

docker compose exec -T db pg_dump \
  -U "${POSTGRES_USER:-abn_user}" \
  -d "${POSTGRES_DB:-abn_registration}" \
  | gzip > "${file}"

echo "Backup written to ${file}"
