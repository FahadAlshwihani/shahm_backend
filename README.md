# Shahm Backend

## Overview

The Shahm backend is the Django REST API and content-management backend for the Shahm public website and administrative dashboard. It provides CMS content, services, dynamic forms, appointments, careers, messaging, SEO, temporary request-access links, and JWT authentication.

## Tech Stack

- Python 3, Django 5.2, Django REST Framework 3.16
- Simple JWT and MySQL (`mysqlclient`)
- WhiteNoise, Gunicorn-compatible WSGI, Pillow, and OpenPyXL

## Architecture

`config/` owns project configuration and selects development or production settings from `DEBUG`. Installed Django applications live under `apps/`; every AppConfig explicitly preserves the historical app label used by migrations, ContentTypes, permissions, relationships, and tables. Cross-application infrastructure lives in `common/`; SMTP delivery lives in `integrations/email/`.

## Repository Structure

```text
manage.py
config/              Canonical URL, ASGI, WSGI, and development/production/test settings
apps/                Installed domain applications with stable Django labels
  accounts/          Custom users, roles, JWT
  blog/              Blog content
  cms/               Pages, hero, header/footer, FAQ, contact, about
  core/              Visits/system-seed models and public API facade
  form_builder/      Dynamic forms, submissions, files, information modals
  legal/             Structured legal pages
  messaging/         Contact, subscribers, broadcasts, email templates
  seo/               Default and per-page metadata
  services/          Services, requests, appointments, careers, access links
  settings_app/      Site and SMTP settings
  team/              Team content
common/              Shared middleware, permissions, pagination, errors
integrations/email/  Database-configured SMTP delivery
docs/                API and architecture documentation
```

## Django Applications

### accounts

Email-based `User`, roles (`super_admin`, `admin`, `editor`, `viewer`), login, refresh, and user management. Initial administrator setup is disabled unless explicitly enabled.

### blog

Posts, sections, categories, tags, public listing/detail APIs, and dashboard CRUD.

### cms

Hero media, pages, header/footer, FAQ, contact, about, and database-driven public content.

### core

The migration-owning app for visits and system seeds, plus the public compatibility API. Shared middleware, permissions, exceptions, pagination, and generic utilities live in `common/`.

### form_builder

Database-driven form templates, sections, fields, options, submissions, uploaded values, success responses, and information modals.

### legal, messaging, seo, settings_app, team

Legal documents; contact/subscriber/email workflows; metadata; site/SMTP configuration; and team content respectively.

### services

Service catalog, requests, appointments, careers, client files, spreadsheet imports, temporary edit links, OTP, snapshots, and access audit activity.

## Important Cross-Cutting Systems

### Dynamic Form Builder

`FormTemplate` defines database-driven schemas. Sections, fields, options, validation, `system_key`, and `dynamic_source` are runtime contracts. Public submission supports JSON and multipart payloads.

### Services and Appointment Booking

Models remain in `apps.services.models`. Appointment serializers and views are under `apps/services/appointments/`; submissions can synchronize into domain records.

### Request Access Links and OTP Verification

Model-bearing `apps/services/request_access.py` and `request_otp.py` remain at the app root. `apps/services/access/` contains API, snapshot, session, security, update, and audit logic.

### Email Templates

Stable keys such as `admin_alert`, `auto_reply`, `subscription_welcome`, and `service_request_otp` are persisted contracts.
`integrations.email.services.DynamicEmailService` reads SMTP configuration from `apps.settings_app.models.SiteSettings` and preserves all template, OTP, and notification flows.

### Media Uploads

Uploads live beneath `MEDIA_ROOT` and are not committed. Validation checks size, extension, MIME family, blocked MIME types, and supported file signatures.

### Authentication / Authorization

Dashboard APIs use `Authorization: Bearer <access-token>`. Refresh tokens are posted to `/api/accounts/refresh/`. DRF is configured for JWT authentication, not session-cookie API authentication.

## Environment Variables

Copy `.env.example` to `.env` and supply deployment values. Never commit `.env`.

`SITE_URL` is the canonical public frontend origin used by sitemap generation. Set it to the externally visible HTTPS site URL without a trailing slash.

## Local Development

### Requirements and Virtual Environment

Install Python and MySQL, then:

```bash
python -m venv venv
python -m pip install -r requirements.txt
```

Activate the virtual environment using the operating-system-specific command.

### Configure Environment and Database

```bash
cp .env.example .env
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Prefer the management command. Enable `ENABLE_INITIAL_ADMIN_SETUP` only for a controlled bootstrap window.

### Run Development Server

```bash
python manage.py runserver
```

## Production Deployment

- Canonical WSGI: `config.wsgi:application`; canonical ASGI: `config.asgi:application`.
- `config.settings` selects `development` when `DEBUG=True` and `production` otherwise. Operators may also set `DJANGO_SETTINGS_MODULE=config.settings.production` explicitly.
- Supply every `.env.example` value through deployment configuration.
- Review/apply migrations, then run `collectstatic`.
- Generated `staticfiles/` is not committed; `media/` requires persistent storage and backups.
- Terminate TLS at the server/proxy and forward `X-Forwarded-Proto`.

The repository does not prescribe a process manager. The canonical command is `gunicorn config.wsgi:application`.

## API Documentation

- [Public API](docs/API_PUBLIC_DOC.md)
- [Dashboard API](docs/API_DASHBOARD_DOC.md)
- [Documentation index](docs/README.md)
- [Frontend/backend API contract matrix](docs/API_CONTRACT_MATRIX.md)
- [Operational handoff](docs/HANDOFF.md)

## Testing

```bash
python manage.py check
python manage.py check --deploy --settings=config.settings.production
python manage.py test
python manage.py makemigrations --check --dry-run --settings=config.settings.test
```

Current tests cover authentication and role boundaries, URL/security contracts, email-template selection with mocked delivery, sitemap configuration, architecture identity, and upload signatures. The staging smoke matrix covers flows that require deployed CMS data or external infrastructure.

Migration `cms.0022` is required by the current model state and changes only the Arabic and English `ContactCard.subtitle` fields from `CharField(max_length=255)` to `TextField(blank=True)`. Its source file is `apps/cms/migrations/0022_alter_contactcard_subtitle_ar_and_more.py`; its Django migration label remains `cms.0022`. Apply it with the normal `python manage.py migrate` deployment step. A rollback to `cms.0021` requires checking for values longer than 255 characters first.

## Rate Limiting and Account Lockout

`ScopedRateThrottle` is registered as the default throttle class. It limits only
views that declare `throttle_scope`, so no endpoint is limited implicitly. The
limited scopes are `login`, `otp`, `otp_send`, `otp_verify`, `search`,
`contact`, `subscribe`, `form_submit`, and `public_edit`. Every rate is
overridable per deployment through `THROTTLE_<SCOPE>` without a code change.
`/api/cms/public/search/` is a plain Django view and uses the equivalent
`common.throttling.rate_limited` decorator against the same rate table.

Sign-in is limited twice: per address by the `login` scope, and per account by
a lockout that blocks an account for `LOGIN_LOCKOUT_SECONDS` after
`LOGIN_FAILURE_LIMIT` consecutive failures, answering `429`. A successful
sign-in clears the counter. Counting per account rather than per address keeps
one mistyped password from locking out an entire office.

Both mechanisms count in the default cache. `CACHE_URL` must therefore point at
a shared backend on any deployment that runs more than one worker process;
`check --deploy` raises `shahm.W001` while it does not.

## Logging and Error Responses

`LOGGING` writes to standard output at `LOG_LEVEL`, and every line carries the
identifier of the request being served. `ErrorLoggingMiddleware` and
`common.exceptions.custom_exception_handler` log the exception in full and
return `"error": "internal_error"` with that identifier in `request_id` and in
the `X-Request-ID` response header. Exception text is never returned to a
client.

## Security Notes

Keep secrets outside Git, initial-admin setup disabled, JWT role/object checks intact, and uploads non-executable. Review dependencies and `check --deploy` for every release.

Roles are ranked `viewer` < `editor` < `admin` < `super_admin`. An account may
only assign roles at or below its own rank and only administer accounts at or
below its own rank, so an `admin` can no longer create, promote, edit, or
delete a `super_admin`. No account may delete itself or change its own role,
and the last active `super_admin` can be neither deleted nor deactivated.

## Maintenance Notes

Do not rename apps, tables, dynamic keys, template types, or email identifiers without a migration and contract review. Keep historical migrations and update API docs when URLs change.

## Handoff Checklist

- Configure environment and MySQL
- Confirm migration history and apply reviewed migrations
- Run checks/tests and collect static files
- Configure persistent media and backups
- Confirm CORS/CSRF origins and disabled initial-admin setup
- Smoke-test login, refresh, search, forms, and access-link flows

## Troubleshooting

- If MySQL cannot connect, verify `DB_HOST`, `DB_PORT`, credentials, server reachability, and database creation before running migrations.
- If cross-origin browser calls fail, align `FRONTEND_URL`, `BACKEND_URL`, CORS origins, CSRF trusted origins, and the frontend API base URL.
- If generated links use the wrong host, correct `SITE_URL` and restart the application.
- If static assets are missing, run `collectstatic` and verify the reverse proxy serves `STATIC_ROOT`; persist `MEDIA_ROOT` separately.

## Project Attribution

Project source developed by **ENG. FAHAD ALSHWIHANI**.

- Portfolio: [https://fyaa.io](https://fyaa.io)
- GitHub: [https://github.com/FahadAlshwihani](https://github.com/FahadAlshwihani)
- LinkedIn: [https://www.linkedin.com/in/fahad-alshwihani/](https://www.linkedin.com/in/fahad-alshwihani/)

Copyright © 2026 ENG. FAHAD ALSHWIHANI. No open-source license is granted by this repository unless a separate `LICENSE` file is supplied.
