# Shahm Dashboard API

## Base URL

- Production: `${BACKEND_URL}/api/` (configure the deployed HTTPS origin through the environment; do not derive it from source constants)
- Local example: `http://localhost:8000/api/`

## Authentication

Login returns a Simple JWT access/refresh pair. Send the access token as:

```http
Authorization: Bearer <access-token>
```

Refresh with `POST /api/accounts/refresh/` and `{ "refresh": "..." }`. Access lifetime is 30 minutes and refresh lifetime is seven days. Tokens are transmitted in headers/bodies, not authentication cookies.

## Roles / Permissions

- `super_admin`: full role tier and Django-superuser capability when configured.
- `admin`: administration excluding super-admin-only operations.
- `editor`: content and operational management allowed by `IsEditorOrAbove`.
- `viewer`: authenticated read access only where a view permits it.

View declarations are authoritative; some settings and user endpoints require `IsAdminOrSuper`, while content domains generally require `IsEditorOrAbove`.

## Response and CRUD Conventions

- `GET` collection: list or paginated `{count,next,previous,results}`.
- `POST` collection: create, usually returning the serialized object and `201`.
- `GET` detail: retrieve when implemented.
- `PUT` replaces; `PATCH` partially updates; `DELETE` removes.
- File/media operations use `multipart/form-data`.
- Typical errors: `400` validation, `401` missing/expired JWT, `403` role denial, `404` unknown object.

The inventory below contains 121 resolved authenticated/administrative URL patterns after excluding DRF format-suffix duplicates. The optional bootstrap URL is listed separately.

## Authentication and Users

| Methods | Path | Permission / Purpose | Implementation |
|---|---|---|---|
| POST | `/api/accounts/login/` | Public credential exchange | `apps.accounts.views.LoginView` |
| POST | `/api/accounts/refresh/` | Public refresh-token exchange | `TokenRefreshView` |
| GET | `/api/accounts/users/` | Admin/super: list users | `UsersListView` |
| POST | `/api/accounts/users/create/` | Admin/super: create user | `CreateUserView` |
| PATCH, DELETE | `/api/accounts/users/{id}/` | Admin/super: update/delete user | `UserDetailView` |

Login body: `{ "email": "admin@example.com", "password": "..." }`. Success contains `user`, `access`, and `refresh`.
Invalid credentials return `401`; malformed input returns `400`.

`POST /api/accounts/super/init/` is registered only when `ENABLE_INITIAL_ADMIN_SETUP=True`. It is disabled by default and must only be enabled during a controlled empty-database bootstrap.

## Dashboard and Settings

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/public/admin/dashboard-stats/` | Dashboard counts/statistics | `apps.core.views_public.DashboardStatsView` |
| GET, PUT | `/api/settings/` | Site settings | `apps.settings_app.views.SiteSettingsView` |
| GET, PUT | `/api/settings/email/` | SMTP/email settings | `apps.settings_app.views.EmailSettingsView` |
| POST | `/api/settings/email/test/` | Send SMTP test | `apps.settings_app.views.EmailSMTPTestView` |

Settings bodies mirror their serializers. Secrets returned by settings views should be handled as privileged data.

## CMS: Pages, Hero, Header, Footer, Contact, FAQ, About

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET, POST | `/api/cms/admin/heroes/` | List/create heroes | `HeroListCreateView` |
| GET, PATCH, DELETE | `/api/cms/admin/heroes/{id}/` | Hero detail | `HeroDetailView` |
| GET, POST | `/api/cms/admin/hero-media/{hero_id}/` | List/add hero media | `HeroMediaListCreateView` |
| PATCH, DELETE | `/api/cms/admin/hero-media/item/{id}/` | Update/delete hero media | `HeroMediaDetailView` |
| GET, POST | `/api/cms/admin/pages/` | List/create CMS pages | `PageListCreateView` |
| GET, PATCH, DELETE | `/api/cms/admin/pages/{id}/` | CMS page detail | `PageDetailView` |
| PATCH | `/api/cms/admin/page-content/{slug}/` | Update page content | `AdminPageContentView` |
| GET, POST | `/api/cms/admin/home-sections/` | Home sections | `HomeSectionListCreateView` |
| PATCH, DELETE | `/api/cms/admin/home-sections/{id}/` | Home section detail | `HomeSectionDetailView` |
| GET, POST | `/api/cms/admin/header/` | Header link tree | `HeaderLinkListCreateView` |
| PATCH, DELETE | `/api/cms/admin/header/{id}/` | Header link detail | `HeaderLinkDetailView` |
| GET, POST | `/api/cms/admin/columns/` | Footer columns | `FooterColumnListCreateView` |
| PATCH, DELETE | `/api/cms/admin/columns/{id}/` | Footer column detail | `FooterColumnDetailView` |
| POST | `/api/cms/admin/footer-links/` | Create footer link | `FooterLinkListCreateView` |
| PATCH, DELETE | `/api/cms/admin/footer-links/{id}/` | Footer link detail | `FooterLinkDetailView` |
| GET, POST | `/api/cms/admin/footer/settings/` | Footer settings | `FooterSettingsView` |
| GET, POST | `/api/cms/admin/footer/cta/` | Footer CTA list/create | `FooterCTAListCreateView` |
| PATCH, DELETE | `/api/cms/admin/footer/cta/{id}/` | Footer CTA detail | `FooterCTADetailView` |
| GET, POST | `/api/cms/admin/contact/page/` | Contact page settings | `ContactPageSettingsAdminView` |
| GET, POST | `/api/cms/admin/contact/cards/` | Contact cards | `ContactCardListCreateView` |
| PATCH, DELETE | `/api/cms/admin/contact/cards/{id}/` | Contact card detail | `ContactCardDetailView` |
| GET, POST | `/api/cms/admin/contact/faq-preview/` | FAQ preview state | `ContactFAQPreviewView` |
| POST | `/api/cms/admin/contact/faq-preview/toggle/` | Toggle FAQ preview | `ContactFAQPreviewToggleView` |
| GET, POST | `/api/cms/admin/faq/` | FAQ items | `FAQListCreateView` |
| PATCH, DELETE | `/api/cms/admin/faq/{id}/` | FAQ detail | `FAQDetailView` |
| GET, POST | `/api/cms/admin/faq-categories/` | FAQ categories | `FAQCategoryListCreateView` |
| PATCH, DELETE | `/api/cms/admin/faq-categories/{id}/` | FAQ category detail | `FAQCategoryDetailView` |
| GET, PATCH | `/api/cms/admin/about/` | About page root | `AdminAboutView` |
| POST | `/api/cms/admin/about/stats/` | Create statistic | `AdminAboutStatListCreateView` |
| PATCH, DELETE | `/api/cms/admin/about/stats/{id}/` | Statistic detail | `AdminAboutStatDetailView` |
| POST | `/api/cms/admin/about/posts/` | Create about post | `AdminAboutPostListCreateView` |
| PATCH, DELETE | `/api/cms/admin/about/posts/{id}/` | About post detail | `AdminAboutPostDetailView` |
| POST | `/api/cms/admin/about/sections/` | Create about section | `AdminAboutSectionListCreateView` |
| PATCH, DELETE | `/api/cms/admin/about/sections/{id}/` | About section detail | `AdminAboutSectionDetailView` |
| POST | `/api/cms/admin/about/icons/` | Create icon | `AdminAboutIconListCreateView` |
| PATCH, DELETE | `/api/cms/admin/about/icons/{id}/` | Icon detail | `AdminAboutIconDetailView` |
| POST | `/api/cms/admin/about/partners/` | Create partner | `AdminAboutPartnerListCreateView` |
| PATCH, DELETE | `/api/cms/admin/about/partners/{id}/` | Partner detail | `AdminAboutPartnerDetailView` |

Payloads mirror the corresponding serializers and include bilingual text, order, active flags, action types/slugs, and optional multipart media. Invalid parent IDs, duplicate constraints, and upload validation return `400`.

## Blog, Legal, and SEO

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET, POST | `/api/blog/admin/categories/` | Categories | `CategoryListCreateView` |
| PATCH, DELETE | `/api/blog/admin/categories/{id}/` | Category detail | `CategoryDetailView` |
| GET, POST | `/api/blog/admin/tags/` | Tags | `TagListCreateView` |
| PATCH, DELETE | `/api/blog/admin/tags/{id}/` | Tag detail | `TagDetailView` |
| GET, POST | `/api/blog/admin/posts/` | Posts | `BlogListCreateView` |
| GET, PATCH, DELETE | `/api/blog/admin/posts/{id}/` | Post detail | `BlogDetailView` |
| PATCH | `/api/blog/admin/settings/` | Blog page settings | `BlogSettingsUpdateView` |
| GET, POST | `/api/legal/admin/pages/` | Legal pages | `LegalPageListCreateView` |
| GET, PATCH, DELETE | `/api/legal/admin/pages/{id}/` | Legal page detail | `LegalPageDetailView` |
| GET, PUT | `/api/seo/admin/default/` | Default SEO | `DefaultSEOView` |
| GET, POST | `/api/seo/admin/pages/` | Per-page SEO | `PageSEOListCreateView` |
| GET, PATCH, DELETE | `/api/seo/admin/pages/{id}/` | Per-page SEO detail | `PageSEODetailView` |
| GET | `/api/seo/admin/all-pages/` | Pages available for SEO | `AllPagesForSEO` |

Rich-text fields are stored as HTML and sanitized by the public frontend before rendering.

## Messages, Subscribers, Broadcasts, Email Templates

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET | `/api/messaging/admin/messages/` | Contact message list | `AdminMessagesView` |
| GET, PATCH | `/api/messaging/admin/messages/{id}/` | Read/update message | `AdminSingleMessageView` |
| GET | `/api/messaging/admin/subscribers/` | Subscriber list | `SubscribersListView` |
| DELETE | `/api/messaging/admin/subscribers/{id}/` | Delete subscriber | `SubscriberDeleteView` |
| GET | `/api/messaging/admin/subscribers/export/` | CSV export | `ExportSubscribersCSV` |
| POST | `/api/messaging/admin/broadcast/` | Send broadcast HTML | `BroadcastEmailView` |
| GET | `/api/messaging/admin/broadcast/logs/` | Broadcast history | `BroadcastLogsListView` |
| GET, POST | `/api/messaging/admin/email-templates/` | List/update templates per view contract | `EmailTemplateView` |

Broadcast request bodies include subject and HTML. Email template `template_type` values are stable database/string contracts.

## Services and Service Requests

The following ViewSets use `IsEditorOrAbove` and their serializers. Collection/detail actions are explicitly listed.

| Resource | Collection | Detail | Implementation |
|---|---|---|---|
| Main services | `GET, POST /api/services/admin/main-services/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminMainServiceViewSet` |
| Services | `GET, POST /api/services/admin/services/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminServiceViewSet` |
| Service sections | `GET, POST /api/services/admin/service-sections/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminServiceSectionViewSet` |
| Services page | `GET, POST /api/services/admin/services-page/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminServicePageCMSViewSet` |
| Advisory page | `GET, POST /api/services/admin/service-advisory-page/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminServiceAdvisoryPageViewSet` |
| Advisory requests | `GET, POST /api/services/admin/service-advisory-requests/` | `GET, PUT, PATCH, DELETE /{id}/` | `AdminServiceAdvisoryRequestViewSet` |

Additional operational endpoints:

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| POST | `/api/services/admin/import-services/` | Import services spreadsheet | `AdminImportServicesView` |
| GET | `/api/services/admin/clients/` | Clients | `apps.services.clients.views.AdminClientsView` |
| GET, POST | `/api/services/admin/clients/{id}/files/` | Client files | `AdminClientFilesView` |

Import and file endpoints use multipart payloads. Import errors identify invalid workbook data without changing URL contracts.

## Service Request Access Links

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| POST | `/api/services/admin/service-advisory-requests/{request_id}/access-links/create/` | Create link | `AdminCreateAccessLinkView` |
| GET | `/api/services/admin/service-advisory-requests/{request_id}/access-links/` | List links | `AdminRequestAccessLinksView` |
| POST | `/api/services/admin/request-access-links/{link_id}/revoke/` | Revoke link | `AdminRevokeAccessLinkView` |
| POST | `/api/services/admin/request-access-links/{link_id}/regenerate/` | Regenerate link/token | `AdminRegenerateAccessLinkView` |
| PATCH | `/api/services/admin/submissions/{submission_id}/update/` | Admin edit values | `AdminEditableSubmissionUpdateView` |
| GET | `/api/services/admin/submissions/{submission_id}/history/` | Edit history | `AdminSubmissionEditHistoryView` |
| GET | `/api/services/admin/service-advisory-requests/{request_id}/logs/` | Access activity | `AdminAccessActivityLogsView` |

Bodies are defined by access serializers and include expiry/editability/email metadata. Link secrets and OTP values must not be logged.

## Dynamic Forms

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET, POST | `/api/admin/forms/` | Templates | `AdminFormTemplateListCreateView` |
| GET, PATCH, DELETE | `/api/admin/forms/{id}/` | Template detail | `AdminFormTemplateDetailView` |
| POST | `/api/admin/forms/{form_id}/sections/` | Create section | `AdminFormSectionListCreateView` |
| PATCH, DELETE | `/api/admin/forms/sections/{id}/` | Section detail | `AdminFormSectionDetailView` |
| POST | `/api/admin/forms/{form_id}/fields/` | Create field | `AdminFormFieldListCreateView` |
| PATCH, DELETE | `/api/admin/forms/fields/{id}/` | Field detail | `AdminFormFieldDetailView` |
| POST | `/api/admin/forms/fields/{field_id}/options/` | Create option | `AdminFormFieldOptionListCreateView` |
| PATCH, DELETE | `/api/admin/forms/options/{id}/` | Option detail | `AdminFormFieldOptionDetailView` |
| GET, POST | `/api/admin/success-responses/` | Success responses | `AdminSuccessResponseListCreateView` |
| GET, PATCH, DELETE | `/api/admin/success-responses/{id}/` | Success response detail | `AdminSuccessResponseDetailView` |
| GET | `/api/admin/form-submissions/` | Submission list | `AdminFormSubmissionListView` |
| GET, PATCH, DELETE | `/api/admin/form-submissions/{id}/` | Submission detail/status/delete | `AdminFormSubmissionDetailView` |
| GET, POST | `/api/admin/info-modals/` | Information modals | `AdminInfoModalListCreateView` |
| GET, PATCH, DELETE | `/api/admin/info-modals/{id}/` | Modal detail | `AdminInfoModalDetailView` |
| POST | `/api/admin/info-modals/{modal_id}/sections/` | Modal section | `AdminInfoModalSectionListCreateView` |
| PATCH, DELETE | `/api/admin/info-modal-sections/{id}/` | Modal section detail | `AdminInfoModalSectionDetailView` |

Do not rename `system_key`, field keys, slugs, dynamic sources, form types, or template types without checking persisted submissions and frontend rendering.

## Appointments

| Methods | Path | Purpose | Implementation |
|---|---|---|---|
| GET, PATCH | `/api/services/admin/appointments/page/` | Page content | `AdminAppointmentPageView` |
| GET, PATCH | `/api/services/admin/appointments/settings/` | Settings/pricing | `AdminAppointmentSettingsView` |
| GET, POST | `/api/services/admin/appointments/slots/` | Slots | `AdminAppointmentSlotsView` |
| PATCH, DELETE | `/api/services/admin/appointments/slots/{id}/` | Slot detail | `AdminAppointmentSlotDetailView` |
| POST | `/api/services/admin/appointments/slots/generate/` | Bulk slot generation | `AdminGenerateSlotsView` |
| GET | `/api/services/admin/appointments/bookings/` | Bookings | `AdminAppointmentBookingsView` |
| PATCH | `/api/services/admin/appointments/bookings/{id}/status/` | Update status | `AdminUpdateBookingStatusView` |
| PATCH | `/api/services/admin/appointments/bookings/{id}/cancel/` | Cancel booking | `AdminCancelBookingView` |

## Careers and Team

| Resource/Methods | Path | Implementation |
|---|---|---|
| GET, POST career jobs | `/api/services/admin/careers/jobs/` | `AdminCareerJobsViewSet` |
| GET, PUT, PATCH, DELETE career job | `/api/services/admin/careers/jobs/{id}/` | same ViewSet |
| GET applications | `/api/services/admin/careers/applications/` | `AdminCareerApplicationsViewSet` |
| GET application | `/api/services/admin/careers/applications/{id}/` | same ViewSet |
| GET, POST team members | `/api/team/admin/members/` | `TeamListCreateView` |
| GET, PATCH, DELETE team member | `/api/team/admin/members/{id}/` | `TeamDetailView` |
| GET, POST team page | `/api/team/admin/page/` | `TeamPageAdminView` |

Career application records are normally created through configured public dynamic-form actions rather than an independent public apply endpoint.

## Representative Requests and Errors

```http
PATCH /api/cms/admin/heroes/12/
Authorization: Bearer <token>
Content-Type: application/json

{"title_en":"Updated title","is_active":true}
```

```json
{"detail":"Authentication credentials were not provided."}
```

```json
{"detail":"You do not have permission to perform this action."}
```

```json
{"field_name":["This field is required."]}
```

## Source of Truth

This reference was rebuilt from the active URL resolver, ViewSet actions, APIView methods, serializers, and permission declarations. Django URL configuration remains authoritative.
