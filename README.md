# Alpha Business Network Event Registration

Production-ready event registration platform for Alpha Business Network. It includes a public event landing page, validated registration workflow, secure admin login, Google Forms-style response dashboard, filtering, export, import, event settings, email confirmation tracking, optional Google Sheets sync, and Docker/Nginx deployment.

## Architecture

- Frontend: React, Vite, TypeScript, React Router, responsive CSS.
- Backend: FastAPI, Python 3.12, SQLAlchemy 2.x, Alembic, Pydantic, cookie-based JWT admin auth.
- Database: PostgreSQL with persistent Docker volume.
- Edge: Nginx exposes only ports 80/443 and proxies `/api` to FastAPI.
- Optional integrations: SMTP confirmation email and Google Sheets append sync.

## Local Development

Create `.env` from `.env.example`, then set at least `DATABASE_URL`, `SECRET_KEY`, `POSTGRES_PASSWORD`, `ALLOWED_ORIGINS`, and cookie settings.

Backend:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.create_admin
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Admin login is at `http://localhost:5173/admin/login`.

## Docker

Development-style Docker run:

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f backend
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.create_admin
```

The dev compose file maps Nginx to `http://localhost:8080`. Backend and PostgreSQL are only available inside the Compose network.

Production:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend python -m app.scripts.create_admin
```

Point the company domain A record at the Ubuntu VPS. Use Certbot on the host or in a companion container, then mount the certificate paths into Nginx and add the 443 server block for your domain.

## Environment Variables

Use `.env.example` as the source of truth. Important values:

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL.
- `SECRET_KEY`: long random signing secret.
- `ALLOWED_ORIGINS`: comma-separated frontend origins.
- `COOKIE_SECURE`: `true` in production HTTPS.
- `EVENT_TIMEZONE`: defaults to `Asia/Kolkata`.
- `SMTP_*`: SMTP configuration for confirmation emails.
- `GOOGLE_SHEETS_SYNC_ENABLED`, `GOOGLE_SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_FILE`: optional Google Sheets sync.

Do not commit `.env` or service account credentials.

## Admin Workflow

Create the first admin only from the backend command:

```bash
python -m app.scripts.create_admin
```

Admin APIs use HttpOnly JWT cookies and a CSRF cookie/header pair. There is no public admin signup route.

## Registration Workflow

Public event details load from `GET /api/public/event`. Submissions go to `POST /api/public/registrations` with an `Idempotency-Key` header. The backend validates and normalizes data, checks registration availability, prevents duplicate email/phone for the event, generates `ABN-2026-000001` style IDs, applies capacity/waitlist logic, commits to the database, then attempts email and sheet sync without rolling back the saved registration.

## Import And Export

Admins can export filtered or full registration data:

```text
GET /api/admin/registrations/export/csv
GET /api/admin/registrations/export/xlsx
```

Spreadsheet exports escape values beginning with `=`, `+`, `-`, or `@`.

CSV import flow:

1. Upload CSV at `/admin/import`.
2. Preview detected columns.
3. Map source columns to registration fields.
4. Confirm import.
5. Review imported, duplicate, invalid, and failed row counts.

## Email

Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, and `SMTP_FROM_NAME`. If SMTP fails or is not configured, the registration remains saved and `email_status` is set to `failed`; admins can retry from the detail page.

## Google Sheets

PostgreSQL remains the source of truth. To enable append sync:

```env
GOOGLE_SHEETS_SYNC_ENABLED=true
GOOGLE_SHEET_ID=your-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/google-service-account.json
```

Share the Sheet with the service account email. Sync failures are stored and can be retried from the admin detail page.

## Backup And Restore

Backup:

```bash
./deployment/scripts/backup_postgres.sh
```

Restore:

```bash
./deployment/scripts/restore_postgres.sh deployment/backups/abn-registration-YYYYMMDDTHHMMSSZ.sql.gz
```

`deployment/cron.example` contains a daily backup and 14-day retention example.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Troubleshooting

- `401` on admin APIs: sign in again; cookies may be expired.
- `403 CSRF_FAILED`: refresh the admin page and retry.
- Duplicate registration: the same normalized email or Indian mobile number already exists for the event.
- Email failed: check SMTP environment values and server firewall.
- Sheet sync failed: check service account file path, Sheet ID, and sharing permissions.
- Nginx serves frontend but API fails: inspect `docker compose logs backend nginx`.

## Known Limitations

- Google Sheets scheduled retry is not implemented yet; manual retry is available from the admin detail page.
- HTTPS is documented for Certbot, but the checked-in Nginx file is HTTP-first so it can boot before real certificates exist.
- The included tests cover core registration and validation paths, but they are not the full exhaustive acceptance-suite list.
