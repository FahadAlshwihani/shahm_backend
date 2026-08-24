# Shahm Codebase Map

| Concern | Backend | Frontend |
|---|---|---|
| Project settings/deployment | `config/`, `config/settings/` | `.env.example`, build-time frontend environment |
| Shared infrastructure | `common/` | n/a |
| Authentication/users | `apps/accounts/`, `common/permissions.py`, `apps/accounts/permissions.py` | `src/api/authApi.js`, `src/store/useAuthStore.js`, `src/pages/auth/`, `src/router/ProtectedRoute.jsx` |
| CMS/home/layout | `apps/cms/`, `apps/core/views_public.py` | `src/api/cmsApi.js`, `src/api/publicApi.js`, public pages/layouts |
| Services | `apps/services/models.py`, `serializers.py`, `views.py` | `src/api/servicesApi.js`, public/dashboard service pages |
| Dynamic forms | `apps/form_builder/` | `src/components/forms/`, `src/api/formBuilderApi.js`, form stores |
| Request access/OTP | root service model modules, `apps/services/access/` | request-access page/store and `servicesApi.js` |
| Appointments | `apps/services/models.py`, `apps/services/appointments/` | `appointmentsApi.js`, `pages/dashboard/appointments/` |
| Careers | service models/views and `apps/form_builder/actions.py` | `careersApi.js`, `pages/dashboard/jobs/` |
| Blog/legal/SEO | `apps/blog/`, `apps/legal/`, `apps/seo/` | corresponding API modules, public pages, `pages/dashboard/cms/` |
| Messaging/email | `apps/messaging/`, `integrations/email/services.py` | message/email APIs and dashboard pages |
| Settings | `apps/settings_app/` | settings API/store and dashboard settings pages |
| Routing | `config/urls.py` and app `urls.py` files | `src/router/` |
| API route contracts | app URL modules and views | `src/api/routes.js`, domain API modules; verified in `docs/API_CONTRACT_MATRIX.json` |
| Configured links | CMS URL fields | `src/utils/safeNavigation.js` |
| Styling | n/a | `src/styles/` by layout/dashboard/forms/common/pages |
| Translations | bilingual model fields | `public/translation/*.json`, `src/i18n.js` |

Search both repositories and persisted database contracts before changing dynamic keys, email types, route paths, form slugs, or access identifiers.

Migration-sensitive service models remain in `apps/services/models.py`, `apps/services/client_files.py`, `apps/services/request_access.py`, and `apps/services/request_otp.py`. Do not relocate them without a dedicated model-state migration analysis.

## Project Attribution

Project source developed by **ENG. FAHAD ALSHWIHANI**. Portfolio: [fyaa.io](https://fyaa.io) · [GitHub](https://github.com/FahadAlshwihani) · [LinkedIn](https://www.linkedin.com/in/fahad-alshwihani/).

Copyright © 2026 ENG. FAHAD ALSHWIHANI.
