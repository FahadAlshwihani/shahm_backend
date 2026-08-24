# Shahm Operational Handoff

## Repository Purpose

The backend repository is the Django/DRF API and CMS. The companion frontend repository is the React SPA. The browser uses `REACT_APP_API_BASE_URL`; Django permits the deployed frontend through its CORS/CSRF origin settings.

## Required Configuration

Start from the backend `.env.example` and the frontend `.env.example`. At minimum, production must provide a strong Django secret, MySQL credentials, allowed hosts, trusted frontend/backend origins, and the canonical `SITE_URL`. SMTP values can be stored through the privileged settings API and must never be committed.

## Local Startup

Backend:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
npm ci
npm start
```

The committed `.npmrc` makes npm use the peer-dependency behavior required by the React 19 / Create React App 5 toolchain.

## Validation and Production Build

```bash
# backend
python manage.py check
python manage.py check --deploy --settings=config.settings.production
python manage.py test
python manage.py makemigrations --check --dry-run --settings=config.settings.test

# frontend
npm ci
npm run lint
npm test -- --watchAll=false
npm run build
```

The frontend build output is generated in `build/`. Django production deployment must run `python manage.py collectstatic`; generated `staticfiles/` is not source.

## Migration Procedure

Back up the database, review unapplied migrations, and run `python manage.py migrate`. Migration `cms.0022` changes only `ContactCard.subtitle_ar` and `subtitle_en` from 255-character fields to optional text fields. Reversing to `0021` can fail or lose compatibility if stored values exceed 255 characters, so review data before rollback.

## Deployment Expectations

- Canonical WSGI entry point: `config.wsgi:application`; canonical ASGI entry point: `config.asgi:application`.
- Installed domain applications are imported through `apps.*`; their Django labels remain the historical unprefixed values.
- `config.settings` selects production whenever `DEBUG=False`; production may be selected explicitly with `DJANGO_SETTINGS_MODULE=config.settings.production`.
- TLS terminates at the hosting proxy; forwarded HTTPS must be configured correctly.
- MySQL, SMTP, DNS/TLS, and durable media storage are external services.
- `media/` contains runtime uploads and requires persistence and backups.
- `ENABLE_INITIAL_ADMIN_SETUP` remains false except during a controlled, one-time empty-database bootstrap. Prefer `createsuperuser`.
- Apply migrations and collect static files before switching application traffic.

## Runtime and Ignored Paths

`.env`, virtual environments, caches, logs, local SQLite databases, runtime `media/`, generated `staticfiles/`, frontend `node_modules/`, `coverage/`, and `build/` are intentionally ignored. Do not remove a developer or production `.env` or media store as part of source deployment.

## Security-Sensitive Configuration

Use non-default secrets; keep `DEBUG=False`; restrict `ALLOWED_HOSTS`, CORS, and CSRF origins; set the public `SITE_URL`; protect SMTP/database credentials; and retain JWT role/object checks and upload validation. Dashboard tokens are sent as Bearer tokens. CMS rich text is sanitized by the frontend before HTML rendering. Frontend JWTs remain in browser `localStorage`; deploy a restrictive Content Security Policy and preserve the sanitizer/safe-navigation controls. An HttpOnly-cookie redesign is a separate authentication project.

## Known Technical Debt

- The CRA 5 frontend currently reports 30 npm advisories after safe non-forced transitive updates: 9 low, 7 moderate, 14 high, and 0 critical. Most are inherited by the build, development-server, Jest/jsdom, Workbox, and webpack toolchain; React Router v6 also has direct runtime advisories whose offered fix is a v7 major upgrade. Do not report these as zero known frontend vulnerabilities. A CRA-to-Vite/current-router migration is recommended as a separate tested project.
- Frontend JWTs use local storage, so the residual impact of any future XSS defect is higher; maintain the sanitizer and avoid unsafe script injection.
- Automated tests cover critical HTTP semantics, routing, uploads, sanitization, and boot smoke paths, but are not a full end-to-end browser suite.

## External Infrastructure Requirements

Receiving teams need a reachable MySQL database, production migration-history access, SMTP configuration, DNS/TLS, and persistent media storage to complete live-environment verification. Source validation does not modify or probe production data.

See the [documentation index](README.md) and the exhaustive [API contract matrix](API_CONTRACT_MATRIX.md).

## Source Delivery Manifest

### INCLUDE

- Backend: `apps/`, `config/`, `common/`, `integrations/`, `docs/`, source static assets, migrations, `manage.py`, `requirements.txt`, `README.md`, `.env.example`, and `.gitignore`.
- Frontend: `src/`, `public/`, `package.json`, `package-lock.json`, `.npmrc`, `README.md`, `.env.example`, and `.gitignore`.

### EXCLUDE

- Secrets and local state: `.env*` except `.env.example`, IDE metadata, logs, SQLite files, virtual environments, `node_modules/`, coverage, caches, and OS metadata.

### RUNTIME-GENERATED

- Backend `media/`, `staticfiles/`, logs, caches, and process sockets.
- Frontend `build/` and coverage output.

### ENVIRONMENT-SPECIFIC

- MySQL credentials/history, SMTP credentials and delivery reputation, DNS/TLS, reverse-proxy/process-manager configuration, durable media storage/backups, and build-time public/API origins.

## Production Deployment Checklist

1. Create and activate a dedicated virtual environment.
2. Install pinned backend dependencies with `pip install -r requirements.txt` and run `pip check`.
3. Create `.env` from `.env.example`; inject strong secrets outside source control.
4. Create/configure the MySQL database and least-privilege application account.
5. Back up the production database and verify restore procedures.
6. Run `python manage.py showmigrations --settings=config.settings.production`.
7. Review `python manage.py migrate --plan --settings=config.settings.production`.
8. Apply `python manage.py migrate --settings=config.settings.production` during the approved window.
9. Run `python manage.py collectstatic --noinput --settings=config.settings.production`.
10. Mount persistent `media/` storage and configure backups; never deploy local runtime uploads as source.
11. Run Gunicorn with `gunicorn config.wsgi:application` under the selected process manager.
12. Configure the reverse proxy for HTTPS forwarding, static files, media policy, request size, and timeouts.
13. Configure TLS certificates and renewal monitoring.
14. Configure and test SMTP from the privileged application settings without exposing credentials.
15. Configure canonical DNS and set `SITE_URL`, hosts, CORS, and CSRF origins to the deployed HTTPS domains.
16. In the frontend source, run `npm ci`.
17. Set `REACT_APP_API_BASE_URL` and run `npm run build`.
18. Deploy `build/` to the static host with SPA history fallback.
19. Execute [FINAL_SMOKE_TESTS.md](FINAL_SMOKE_TESTS.md) on staging, then production read-only/safe flows.
20. Roll back application artifacts first if needed; reverse database migrations only after data-compatibility review and a verified backup. In particular, values longer than 255 characters make reversing `cms.0022` unsafe.

## Project Attribution

Project source developed by **ENG. FAHAD ALSHWIHANI**. Portfolio: [fyaa.io](https://fyaa.io) · [GitHub](https://github.com/FahadAlshwihani) · [LinkedIn](https://www.linkedin.com/in/fahad-alshwihani/).

Copyright © 2026 ENG. FAHAD ALSHWIHANI.
