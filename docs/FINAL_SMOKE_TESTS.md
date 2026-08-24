# Shahm Final Staging Smoke Tests

Run this checklist against a staging environment configured with representative CMS data, test mailboxes, disposable records, durable media, and production-equivalent proxy/TLS settings. Record date, release identifier, tester, response status, and evidence for each item. Never use real client data for destructive tests.

## Preconditions

- [ ] HTTPS, DNS, `SITE_URL`, CORS, CSRF, MySQL, persistent media, and SMTP are configured.
- [ ] Migrations and static collection completed; initial-admin bootstrap is disabled.
- [ ] Test accounts exist for super-admin, admin, editor, viewer, and unauthenticated scenarios.
- [ ] Browser developer tools show no secret/token logging or unexpected 4xx/5xx responses.

## Public Application

- [ ] Home, navbar, footer, about, FAQ, blog list/detail, legal pages, services list/detail, and SEO metadata load (`GET` success: 200).
- [ ] Search returns relevant CMS/blog/service results and a short/no-result query remains a valid 200 response.
- [ ] Contact accepts valid data, rejects invalid data with 400, stores one message, and triggers the configured email templates.
- [ ] Newsletter subscription succeeds; a duplicate remains idempotent and does not send a second welcome message.
- [ ] Public dynamic forms and careers load database-driven schemas; inactive/missing slugs return 404.
- [ ] Appointment page/settings/slots load; unavailable slots cannot be booked.

## Authentication

- [ ] Valid login returns 200 with `user`, `access`, and `refresh`; invalid credentials return 401.
- [ ] Bearer access opens protected routes; no/invalid/expired access returns 401.
- [ ] Refresh returns 200 with a new `access`; invalid/expired refresh returns 401.
- [ ] Logout clears local credentials and protected navigation redirects to login.

## Dashboard and Permissions

- [ ] Dashboard and users, CMS, messages, email templates/settings, forms, services/requests, appointments, careers, site settings, and SEO screens load for an authorized role.
- [ ] Viewer/editor/admin/super-admin boundaries match documented permissions; insufficient privileges return 403.
- [ ] Representative create returns 201 (or the documented endpoint status), update returns 200, delete returns 204 or the documented project response, invalid payload returns 400, and missing object returns 404.

## Dynamic Forms and Domain Flows

- [ ] Submit one configured form; required fields fail when omitted.
- [ ] Select/radio/checkbox store stable option values and render the configured bilingual labels.
- [ ] Phone values retain `{ "country_code": "...", "number": "..." }` structure.
- [ ] Valid multipart upload succeeds; disguised/blocked/oversized content is rejected server-side.
- [ ] Service selection creates the expected service request/reference and appears in dashboard detail.
- [ ] Appointment selection locks the correct slot, creates the booking, renders dynamic/display values, and supports an authorized status update.
- [ ] Career form creates an application tied to the intended job and appears in the admin listing.

## Request Access / OTP / Client Edit

- [ ] Authorized staff creates an access link; unknown/revoked/expired public keys are rejected.
- [ ] OTP request is rate-limited as configured and sends the `service_request_otp` template to the masked destination.
- [ ] Invalid/expired OTP is rejected; valid OTP returns the documented short-lived access token.
- [ ] Token-protected snapshot exposes only publicly editable fields and permitted files.
- [ ] Allowed updates succeed and create edit history/activity; unauthorized field/file changes are rejected.
- [ ] Revocation immediately prevents further snapshot/update access; regeneration invalidates the old link.

## Email Delivery

- [ ] Contact admin alert uses `admin_alert`; client reply uses `auto_reply` only when an address exists.
- [ ] New newsletter subscription uses `subscription_welcome` once.
- [ ] Request OTP uses `service_request_otp`.
- [ ] Missing/disabled templates follow the documented safe fallback without exposing a stack trace.
- [ ] From-address, recipients, TLS mode, and HTML/text rendering are correct in test mailboxes.

## Infrastructure and HTTP Behavior

- [ ] Uploaded media survives an application restart and is served only through the intended media origin/proxy rules.
- [ ] Collected static files load with immutable/cache headers appropriate to the deployment, and no source map exposes secrets.
- [ ] HTTP redirects to HTTPS; the reverse proxy supplies trusted forwarded-protocol headers; secure cookies and HSTS behave as configured.
- [ ] CORS allows only documented frontend origins; an untrusted origin is rejected.
- [ ] CSRF protection accepts documented trusted origins and rejects an untrusted cookie-authenticated request.
- [ ] The generated sitemap and canonical metadata use the configured `SITE_URL`, never a placeholder domain.
- [ ] Unknown API and SPA routes return the documented 404/fallback behavior without stack traces.
- [ ] Browser response headers include a deployment-reviewed Content Security Policy suitable for the SPA and its required media/font origins.

## Release Sign-off

- [ ] Frontend lint/tests/build and backend checks/tests/migration drift pass for the exact release source.
- [ ] API contract matrix reports 219 MATCH, 0 MISMATCH, 0 UNCERTAIN.
- [ ] Backup, monitoring, rollback owner, and external infrastructure owner are recorded.
- [ ] Production MySQL and SMTP validation are marked **EXTERNAL** until tested with production-equivalent services and disposable data/mailboxes.
