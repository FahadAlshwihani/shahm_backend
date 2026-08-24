# Shahm Public API

## Base URL

- Production: `${BACKEND_URL}/api/` (configure the deployed HTTPS origin through the environment; do not derive it from source constants)
- Local example: `http://localhost:8000/api/`

The frontend reads the complete base from `REACT_APP_API_BASE_URL`.

## Authentication

Most endpoints below use DRF `AllowAny`. Request-access updates use a short-lived access token issued after OTP verification. The token is distinct from dashboard JWT credentials and is validated by `apps.services.access`.

## Response Conventions

- JSON is the default representation.
- Collection endpoints using global DRF pagination return `count`, `next`, `previous`, and `results`; several APIViews return plain arrays/objects.
- Validation errors use field-name arrays or the project's `error`/`detail` response.
- File submission uses `multipart/form-data`; JSON schemas and ordinary messages use `application/json`.
- Bilingual resources normally expose `_ar` and `_en` fields.

## Endpoint Inventory

The following 57 distinct URL patterns were resolved from Django configuration. DRF format-suffix duplicates are omitted.

### Public CMS and Compatibility Facade

| Method | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/public/home/` | Aggregated home payload | `apps.cms.views.PublicHomeView` |
| GET | `/api/public/header/` | Public header | `apps.core.views_public.PublicHeaderView` |
| GET | `/api/public/footer/` | Public footer | `apps.core.views_public.PublicFooterView` |
| GET | `/api/public/settings/` | Public site settings | `apps.core.views_public.PublicSiteSettingsView` |
| GET | `/api/public/hero/{slug}/` | Hero by page slug | `apps.core.views_public.PublicHeroView` |
| GET | `/api/public/page/{slug}/` | Public CMS page | `apps.core.views_public.PublicPageView` |
| GET | `/api/public/legal/{slug}/` | Compatibility legal page | `apps.core.views_public.PublicLegalPageView` |
| GET | `/api/public/seo/` | Default metadata | `apps.core.views_public.PublicSEOView` |
| GET | `/api/public/seo/{slug}/` | Page metadata | `apps.core.views_public.PublicSEOView` |
| GET | `/api/public/blog/` | Compatibility blog list | `apps.core.views_public.PublicBlogListView` |
| GET | `/api/public/blog/{slug}/` | Compatibility blog detail | `apps.core.views_public.PublicBlogDetailView` |
| GET | `/api/public/team/` | Compatibility team list | `apps.core.views_public.PublicTeamView` |
| GET | `/api/cms/public/home/` | CMS home payload | `apps.cms.views.PublicHomeView` |
| GET | `/api/cms/public/header/` | CMS header tree | `apps.cms.views.PublicHeaderView` |
| GET | `/api/cms/public/footer/settings/` | Footer settings/CTA | `apps.cms.views.PublicFooterSettingsView` |
| GET | `/api/cms/public/hero/{slug}/` | CMS hero by slug | `apps.cms.views.PublicHeroView` |
| GET | `/api/cms/public/page/{slug}/` | CMS page metadata | `apps.cms.views.PublicPageView` |
| GET | `/api/cms/public/content/{slug}/` | CMS page content | `apps.cms.views.PublicPageContentView` |
| GET | `/api/cms/public/about/` | About page and child collections | `apps.cms.views.PublicAboutView` |
| GET | `/api/cms/public/contact-page/` | Contact page/cards/FAQ preview | `apps.cms.views.PublicContactPageView` |
| GET | `/api/cms/public/faq/` | Active FAQ categories/items | `apps.cms.views.PublicFAQView` |
| GET | `/api/cms/public/search/?q=&lang=` | Site search | `apps.cms.views.public_search` |

Search requires `q`; `lang` selects localized text. Example: `GET /api/cms/public/search/?q=service&lang=en`.

### Blog, Legal, SEO, and Team

| Method | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/blog/settings/` | Blog page settings | `apps.blog.views.PublicBlogSettingsView` |
| GET | `/api/blog/categories/` | Active categories | `apps.blog.views.PublicCategoryListView` |
| GET | `/api/blog/tags/` | Active tags | `apps.blog.views.PublicTagListView` |
| GET | `/api/blog/posts/` | Published posts; accepts list filters | `apps.blog.views.PublicBlogListView` |
| GET | `/api/blog/posts/{slug}/` | Published post detail | `apps.blog.views.PublicBlogDetailView` |
| GET | `/api/legal/page/{slug}/` | Structured legal page | `apps.legal.views.PublicLegalPageView` |
| GET | `/api/seo/public/` | Default SEO | `apps.seo.views.PublicSEOView` |
| GET | `/api/seo/public/{slug}/` | SEO by page slug | `apps.seo.views.PublicSEOView` |
| GET | `/api/team/public/` | Active team members | `apps.team.views.PublicTeamView` |
| GET | `/api/team/public/page/` | Team page content | `apps.team.views.PublicTeamPageView` |

Blog collections accept the query parameters implemented by the view/filter backend, including category/tag/search and pagination where configured. Unknown slugs return `404`.

### Services and Careers

| Method | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/services/public/main-services/` | Main service groups | `apps.services.views.PublicMainServiceViewSet` |
| GET | `/api/services/public/main-services/{slug}/` | Main service detail | same ViewSet |
| GET | `/api/services/public/services/` | Active services | `apps.services.views.PublicServiceViewSet` |
| GET | `/api/services/public/services/{slug}/` | Service detail | same ViewSet |
| GET | `/api/services/public/services-page/` | Services CMS page collection | `apps.services.views.PublicServicePageCMSViewSet` |
| GET | `/api/services/public/services-page/{id}/` | Services CMS page detail | same ViewSet |
| GET | `/api/services/services/filter/?main_service=` | Services for a main service | `apps.services.views.PublicServicesByMainServiceView` |
| GET | `/api/services/public/careers/jobs/` | Active career jobs | `apps.services.views.PublicCareerJobsViewSet` |
| GET | `/api/services/public/careers/jobs/{id}/` | Career job detail | same ViewSet |

Read-only ViewSets support collection and detail `GET` only. Service payloads may contain database-selected form templates and CMS action types.

### Dynamic Forms and Information Modals

| Method | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/public/forms/` | Active form templates | `apps.form_builder.views.PublicFormListView` |
| GET | `/api/public/forms/{slug}/` | Full database-driven schema | `apps.form_builder.views.PublicFormDetailView` |
| POST | `/api/public/forms/{slug}/submit/` | Submit JSON or multipart values | `apps.form_builder.views.PublicFormSubmitView` |
| PATCH | `/api/public/submissions/{reference}/edit/` | Compatibility public edit flow | `apps.form_builder.views.PublicSubmissionUpdateView` |
| POST | `/api/public/forms/access/send-otp/` | Form-submission edit OTP | `apps.form_builder.views.PublicFormSendOTPView` |
| POST | `/api/public/forms/access/verify-otp/` | Verify form edit OTP | `apps.form_builder.views.PublicFormVerifyOTPView` |
| GET | `/api/public/info-modals/{slug}/` | Active information modal | `apps.form_builder.views.PublicInfoModalDetailView` |

Form detail responses contain sections, fields, `key`, `system_key`, field type, localized labels, options, validation, `dynamic_source`, and success-response configuration. These are CMS/database driven rather than a fixed request schema.

Representative multipart submission:

```http
POST /api/public/forms/service-request/submit/
Content-Type: multipart/form-data

name=Example
email=user@example.com
attachment=<binary>
```

Representative success shape:

```json
{
  "success": true,
  "reference": "REQ-2026-0001",
  "success_response": {
    "title_en": "Request received",
    "title_ar": "تم استلام الطلب"
  }
}
```

Possible errors include missing/unknown fields, required validation, invalid option values, upload rejection, inactive form, and throttled/invalid OTP.

### Appointments

| Method | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/services/public/appointments/page/` | Appointment page content | `apps.services.appointments.public_views.PublicAppointmentPageView` |
| GET | `/api/services/public/appointments/settings/` | Booking settings/pricing | `apps.services.appointments.public_views.PublicAppointmentSettingsView` |
| GET | `/api/services/public/appointments/slots/` | Available slots; date/shift query support | `apps.services.appointments.public_views.PublicAvailableSlotsView` |

Appointment creation is driven through configured public dynamic forms; there is no standalone `/appointments/book/` endpoint.

### Contact and Newsletter

| Method | Path | Request | Implementation |
|---|---|---|---|
| POST | `/api/messaging/contact/` | Contact identity, subject/message fields | `apps.messaging.views.ContactMessageView` |
| POST | `/api/messaging/subscribe/` | `{ "email": "user@example.com" }` | `apps.messaging.views.SubscriberView` |

Success responses confirm storage/subscription. Invalid email, required-field errors, duplicate-state handling, and configured email-delivery errors use `400`/project error responses.

### Request Access / OTP

| Method | Path | Authentication | Implementation |
|---|---|---|---|
| POST | `/api/services/public/request-access/send-otp/` | Public key + recipient verification data | `apps.services.access.views.SendOTPView` |
| POST | `/api/services/public/request-access/verify-otp/` | Public key + OTP | `apps.services.access.views.VerifyOTPView` |
| GET | `/api/services/public/request-access/{public_key}/` | Temporary access token | `apps.services.access.views.EditableSubmissionSnapshotView` |
| PATCH | `/api/services/public/request-access/{public_key}/update/` | Temporary access token | `apps.services.access.views.EditableSubmissionUpdateView` |

Sequence:

1. Request an OTP for the public key.
2. Verify the OTP and retain the returned temporary token.
3. Fetch the editable snapshot.
4. PATCH only fields marked publicly editable; use multipart for files.

Expired, revoked, exhausted, mismatched, or invalid links/tokens return `400`, `401`, `403`, or `404` according to the view guard. Updates create activity and edit-history records.

## Common Error Examples

```json
{"detail": "Not found."}
```

```json
{"email": ["Enter a valid email address."]}
```

```json
{"error": "Invalid or expired verification code."}
```

## Source of Truth

This reference was rebuilt from `config/urls.py`, included URL modules, DRF router actions, view methods, serializers, and permission declarations. Update it whenever those contracts change.
