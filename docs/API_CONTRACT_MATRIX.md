# Shahm Frontend ↔ Backend API Contract Matrix

Generated from all active frontend request call sites, `src/api/routes.js`, and Django’s live URL resolver. Dynamic/database-driven values remain governed by serializers and runtime configuration. A test prevents active source from embedding API paths outside the route registry.

- Frontend request call sites: 219 (171 domain API functions and 48 centralized component call sites), represented by 168 deduplicated method/path contract rows
- Backend URL patterns: 179
- MATCH: 219
- MISMATCH: 0
- UNCERTAIN: 0

## Frontend Requests

| Module / function | Method | Frontend path | Backend implementation | Auth / permission | Content | Fields consumed | Result |
|---|---|---|---|---|---|---|---|
| `aboutApi.js::createIcon` | POST | `/cms/admin/about/icons/` | `apps.cms.views.AdminAboutIconListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::createPartner` | POST | `/cms/admin/about/partners/` | `apps.cms.views.AdminAboutPartnerListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::createPost` | POST | `/cms/admin/about/posts/` | `apps.cms.views.AdminAboutPostListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::createSection` | POST | `/cms/admin/about/sections/` | `apps.cms.views.AdminAboutSectionListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::createStat` | POST | `/cms/admin/about/stats/` | `apps.cms.views.AdminAboutStatListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::deleteIcon` | DELETE | `/cms/admin/about/icons/{id}/` | `apps.cms.views.AdminAboutIconDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::deletePartner` | DELETE | `/cms/admin/about/partners/{id}/` | `apps.cms.views.AdminAboutPartnerDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::deletePost` | DELETE | `/cms/admin/about/posts/{id}/` | `apps.cms.views.AdminAboutPostDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::deleteSection` | DELETE | `/cms/admin/about/sections/{id}/` | `apps.cms.views.AdminAboutSectionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::deleteStat` | DELETE | `/cms/admin/about/stats/{id}/` | `apps.cms.views.AdminAboutStatDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::getAdminAbout` | GET | `/cms/admin/about/` | `apps.cms.views.AdminAboutView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `aboutApi.js::getPublicAbout` | GET | `/cms/public/about/` | `apps.cms.views.PublicAboutView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `aboutApi.js::updateAdminAbout` | PATCH | `/cms/admin/about/` | `apps.cms.views.AdminAboutView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::updateIcon` | PATCH | `/cms/admin/about/icons/{id}/` | `apps.cms.views.AdminAboutIconDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::updatePartner` | PATCH | `/cms/admin/about/partners/{id}/` | `apps.cms.views.AdminAboutPartnerDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::updatePost` | PATCH | `/cms/admin/about/posts/{id}/` | `apps.cms.views.AdminAboutPostDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::updateSection` | PATCH | `/cms/admin/about/sections/{id}/` | `apps.cms.views.AdminAboutSectionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `aboutApi.js::updateStat` | PATCH | `/cms/admin/about/stats/{id}/` | `apps.cms.views.AdminAboutStatDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `appointmentsApi.js::deleteSlot` | DELETE | `/services/admin/appointments/slots/{id}/` | `apps.services.appointments.admin_views.AdminAppointmentSlotDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `appointmentsApi.js::generateSlots` | POST | `/services/admin/appointments/slots/generate/` | `apps.services.appointments.admin_views.AdminGenerateSlotsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `appointmentsApi.js::getAdminAppointmentPage` | GET | `/services/admin/appointments/page/` | `apps.services.appointments.admin_views.AdminAppointmentPageView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `appointmentsApi.js::getAdminAppointmentSettings` | GET | `/services/admin/appointments/settings/` | `apps.services.appointments.admin_views.AdminAppointmentSettingsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `appointmentsApi.js::getAdminBookings` | GET | `/services/admin/appointments/bookings/` | `apps.services.appointments.admin_views.AdminAppointmentBookingsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `appointmentsApi.js::getAdminSlots` | GET | `/services/admin/appointments/slots/` | `apps.services.appointments.admin_views.AdminAppointmentSlotsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `appointmentsApi.js::getAvailableSlots` | GET | `/services/public/appointments/slots/` | `apps.services.appointments.public_views.PublicAvailableSlotsView` | JWTAuthentication, AllowAny | none | results | **MATCH** |
| `appointmentsApi.js::updateAdminAppointmentPage` | PATCH | `/services/admin/appointments/page/` | `apps.services.appointments.admin_views.AdminAppointmentPageView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `appointmentsApi.js::updateAdminAppointmentSettings` | PATCH | `/services/admin/appointments/settings/` | `apps.services.appointments.admin_views.AdminAppointmentSettingsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `appointmentsApi.js::updateBookingStatus` | PATCH | `/services/admin/appointments/bookings/{id}/status/` | `apps.services.appointments.admin_views.AdminUpdateBookingStatusView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `appointmentsApi.js::updateSlot` | PATCH | `/services/admin/appointments/slots/{id}/` | `apps.services.appointments.admin_views.AdminAppointmentSlotDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `authApi.js::createUser` | POST | `/accounts/users/create/` | `apps.accounts.views.CreateUserView` | JWTAuthentication, IsAdminOrSuper | application/json | response.data | **MATCH** |
| `authApi.js::deleteUser` | DELETE | `/accounts/users/{id}/` | `apps.accounts.views.UserDetailView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `authApi.js::getUsers` | GET | `/accounts/users/` | `apps.accounts.views.UsersListView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `authApi.js::login` | POST | `/accounts/login/` | `apps.accounts.views.LoginView` | JWTAuthentication, AllowAny | application/json | response.data | **MATCH** |
| `authApi.js::updateUser` | PATCH | `/accounts/users/{id}/` | `apps.accounts.views.UserDetailView` | JWTAuthentication, IsAdminOrSuper | application/json | response.data | **MATCH** |
| `blogApi.js::createCategory` | POST | `/blog/admin/categories/` | `apps.blog.views.CategoryListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | response.data | **MATCH** |
| `blogApi.js::createPost` | POST | `/blog/admin/posts/` | `apps.blog.views.BlogListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | response.data | **MATCH** |
| `blogApi.js::createTag` | POST | `/blog/admin/tags/` | `apps.blog.views.TagListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `blogApi.js::deleteCategory` | DELETE | `/blog/admin/categories/{id}/` | `apps.blog.views.CategoryDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::deletePost` | DELETE | `/blog/admin/posts/{id}/` | `apps.blog.views.BlogDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::deleteTag` | DELETE | `/blog/admin/tags/{id}/` | `apps.blog.views.TagDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::getCategories` | GET | `/blog/admin/categories/` | `apps.blog.views.CategoryListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::getPosts` | GET | `/blog/admin/posts/` | `apps.blog.views.BlogListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::getTags` | GET | `/blog/admin/tags/` | `apps.blog.views.TagListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `blogApi.js::updateCategory` | PATCH | `/blog/admin/categories/{id}/` | `apps.blog.views.CategoryDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | response.data | **MATCH** |
| `blogApi.js::updatePost` | PATCH | `/blog/admin/posts/{id}/` | `apps.blog.views.BlogDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | response.data | **MATCH** |
| `blogApi.js::updateTag` | PATCH | `/blog/admin/tags/{id}/` | `apps.blog.views.TagDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `careersApi.js::createJob` | POST | `/services/admin/careers/jobs/` | `apps.services.views.AdminCareerJobsViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `careersApi.js::deleteJob` | DELETE | `/services/admin/careers/jobs/{id}/` | `apps.services.views.AdminCareerJobsViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `careersApi.js::getAdminJobs` | GET | `/services/admin/careers/jobs/` | `apps.services.views.AdminCareerJobsViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `careersApi.js::getApplications` | GET | `/services/admin/careers/applications/` | `apps.services.views.AdminCareerApplicationsViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `careersApi.js::updateJob` | PATCH | `/services/admin/careers/jobs/{id}/` | `apps.services.views.AdminCareerJobsViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `cmsApi.js::adminCreateFaq` | POST | `/cms/admin/faq/` | `apps.cms.views.FAQListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | map | **MATCH** |
| `cmsApi.js::adminCreateFaqCategory` | POST | `/cms/admin/faq-categories/` | `apps.cms.views.FAQCategoryListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | map | **MATCH** |
| `cmsApi.js::adminCreateHero` | POST | `/cms/admin/heroes/` | `apps.cms.views.HeroListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminCreateHeroMedia` | POST | `/cms/admin/hero-media/{heroId}/` | `apps.cms.views.HeroMediaListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminCreatePage` | POST | `/cms/admin/pages/` | `apps.cms.views.PageListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminDeleteFaq` | DELETE | `/cms/admin/faq/{id}/` | `apps.cms.views.FAQDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | map | **MATCH** |
| `cmsApi.js::adminDeleteFaqCategory` | DELETE | `/cms/admin/faq-categories/{id}/` | `apps.cms.views.FAQCategoryDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | map | **MATCH** |
| `cmsApi.js::adminDeleteHero` | DELETE | `/cms/admin/heroes/{id}/` | `apps.cms.views.HeroDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminDeleteHeroMedia` | DELETE | `/cms/admin/hero-media/item/{id}/` | `apps.cms.views.HeroMediaDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminDeletePage` | DELETE | `/cms/admin/pages/{id}/` | `apps.cms.views.PageDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminEditFaq` | PATCH | `/cms/admin/faq/{id}/` | `apps.cms.views.FAQDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | map | **MATCH** |
| `cmsApi.js::adminEditFaqCategory` | PATCH | `/cms/admin/faq-categories/{id}/` | `apps.cms.views.FAQCategoryDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | map | **MATCH** |
| `cmsApi.js::adminEditHero` | PATCH | `/cms/admin/heroes/{id}/` | `apps.cms.views.HeroDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminEditHeroMedia` | PATCH | `/cms/admin/hero-media/item/{id}/` | `apps.cms.views.HeroMediaDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminEditPage` | PATCH | `/cms/admin/pages/{id}/` | `apps.cms.views.PageDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminFaq` | GET | `/cms/admin/faq/` | `apps.cms.views.FAQListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | map | **MATCH** |
| `cmsApi.js::adminFaqCategories` | GET | `/cms/admin/faq-categories/` | `apps.cms.views.FAQCategoryListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | map | **MATCH** |
| `cmsApi.js::adminGetHeroMedia` | GET | `/cms/admin/hero-media/{heroId}/` | `apps.cms.views.HeroMediaListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminHeroes` | GET | `/cms/admin/heroes/` | `apps.cms.views.HeroListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `cmsApi.js::adminPages` | GET | `/cms/admin/pages/` | `apps.cms.views.PageListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | footer_columns, hero | **MATCH** |
| `contactApi.js::getPublicContactPage` | GET | `/cms/public/contact-page/` | `apps.cms.views.PublicContactPageView` | JWTAuthentication, AllowAny | none | cards, description_ar, description_en, faq_preview, title_ar, title_en | **MATCH** |
| `dashboardApi.js::getDashboardStats` | GET | `/public/admin/dashboard-stats/` | `apps.core.views_public.DashboardStatsView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | none | response.data | **MATCH** |
| `emailApi.js::getEmailSettings` | GET | `/settings/email/` | `apps.settings_app.views.EmailSettingsView` | JWTAuthentication, IsAdminOrSuper | none | error | **MATCH** |
| `emailApi.js::getEmailTemplates` | GET | `/messaging/admin/email-templates/` | `apps.messaging.views.EmailTemplateView` | JWTAuthentication, IsAdminOrSuper | none | forEach | **MATCH** |
| `emailApi.js::updateEmailSettings` | PUT | `/settings/email/` | `apps.settings_app.views.EmailSettingsView` | JWTAuthentication, IsAdminOrSuper | application/json | error | **MATCH** |
| `emailApi.js::updateEmailTemplate` | POST | `/messaging/admin/email-templates/` | `apps.messaging.views.EmailTemplateView` | JWTAuthentication, IsAdminOrSuper | application/json | forEach | **MATCH** |
| `formBuilderApi.js::createAdminForm` | POST | `/admin/forms/` | `apps.form_builder.views.AdminFormTemplateListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `formBuilderApi.js::createSuccessResponse` | POST | `/admin/success-responses/` | `apps.form_builder.views.AdminSuccessResponseListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `formBuilderApi.js::deleteAdminForm` | DELETE | `/admin/forms/{id}/` | `apps.form_builder.views.AdminFormTemplateDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::deleteSuccessResponse` | DELETE | `/admin/success-responses/{id}/` | `apps.form_builder.views.AdminSuccessResponseDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::getAdminForm` | GET | `/admin/forms/{id}/` | `apps.form_builder.views.AdminFormTemplateDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::getAdminForms` | GET | `/admin/forms/` | `apps.form_builder.views.AdminFormTemplateListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::getFormSubmissions` | GET | `/admin/form-submissions/` | `apps.form_builder.views.AdminFormSubmissionListView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::getPublicForm` | GET | `/public/forms/{slug}/` | `apps.form_builder.views.PublicFormDetailView` | JWTAuthentication, AllowAny | none | initial_values, success_response | **MATCH** |
| `formBuilderApi.js::getSuccessResponse` | GET | `/admin/success-responses/{id}/` | `apps.form_builder.views.AdminSuccessResponseDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::getSuccessResponses` | GET | `/admin/success-responses/` | `apps.form_builder.views.AdminSuccessResponseListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `formBuilderApi.js::submitPublicForm` | POST | `/public/forms/{slug}/submit/` | `apps.form_builder.views.PublicFormSubmitView` | JWTAuthentication, AllowAny | application/json | initial_values, success_response | **MATCH** |
| `formBuilderApi.js::updateAdminForm` | PATCH | `/admin/forms/{id}/` | `apps.form_builder.views.AdminFormTemplateDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `formBuilderApi.js::updateSuccessResponse` | PATCH | `/admin/success-responses/{id}/` | `apps.form_builder.views.AdminSuccessResponseDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `formBuilderSectionApi.js::createField` | POST | `/admin/forms/{formId}/fields/` | `apps.form_builder.views.AdminFormFieldListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `formBuilderSectionApi.js::createOption` | POST | `/admin/forms/fields/{fieldId}/options/` | `apps.form_builder.views.AdminFormFieldOptionListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `formBuilderSectionApi.js::createSection` | POST | `/admin/forms/{formId}/sections/` | `apps.form_builder.views.AdminFormSectionListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `formBuilderSectionApi.js::deleteField` | DELETE | `/admin/forms/fields/{id}/` | `apps.form_builder.views.AdminFormFieldDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `formBuilderSectionApi.js::deleteOption` | DELETE | `/admin/forms/options/{id}/` | `apps.form_builder.views.AdminFormFieldOptionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `formBuilderSectionApi.js::deleteSection` | DELETE | `/admin/forms/sections/{id}/` | `apps.form_builder.views.AdminFormSectionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `formBuilderSectionApi.js::updateField` | PATCH | `/admin/forms/fields/{id}/` | `apps.form_builder.views.AdminFormFieldDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `formBuilderSectionApi.js::updateOption` | PATCH | `/admin/forms/options/{id}/` | `apps.form_builder.views.AdminFormFieldOptionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `formBuilderSectionApi.js::updateSection` | PATCH | `/admin/forms/sections/{id}/` | `apps.form_builder.views.AdminFormSectionDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `legalApi.js::adminLegalCreate` | POST | `/legal/admin/pages/` | `apps.legal.views.LegalPageListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `legalApi.js::adminLegalDelete` | DELETE | `/legal/admin/pages/{id}/` | `apps.legal.views.LegalPageDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `legalApi.js::adminLegalEdit` | PATCH | `/legal/admin/pages/{id}/` | `apps.legal.views.LegalPageDetailView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `legalApi.js::adminLegalList` | GET | `/legal/admin/pages/` | `apps.legal.views.LegalPageListCreateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `legalApi.js::getPublicLegal` | GET | `/legal/page/{slug}/` | `apps.legal.views.PublicLegalPageView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `messagesApi.js::adminBroadcast` | POST | `/messaging/admin/broadcast/` | `apps.messaging.views.BroadcastEmailView` | JWTAuthentication, IsAdminOrSuper | application/json | response.data | **MATCH** |
| `messagesApi.js::adminDeleteSubscriber` | DELETE | `/messaging/admin/subscribers/{id}/` | `apps.messaging.views.SubscriberDeleteView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminExportSubscribers` | GET | `/messaging/admin/subscribers/export/` | `apps.messaging.views.ExportSubscribersCSV` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminGetBroadcastLogs` | GET | `/messaging/admin/broadcast/logs/` | `apps.messaging.views.BroadcastLogsListView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminGetMessages` | GET | `/messaging/admin/messages/` | `apps.messaging.views.AdminMessagesView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminGetSingleMessage` | GET | `/messaging/admin/messages/{id}/` | `apps.messaging.views.AdminSingleMessageView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminGetSubscribers` | GET | `/messaging/admin/subscribers/` | `apps.messaging.views.SubscribersListView` | JWTAuthentication, IsAdminOrSuper | none | response.data | **MATCH** |
| `messagesApi.js::adminUpdateMessage` | PATCH | `/messaging/admin/messages/{id}/` | `apps.messaging.views.AdminSingleMessageView` | JWTAuthentication, IsAdminOrSuper | application/json | response.data | **MATCH** |
| `messagesApi.js::sendContact` | POST | `/messaging/contact/` | `apps.messaging.views.ContactMessageView` | JWTAuthentication, AllowAny | application/json | cards, description_ar, description_en, faq_preview, title_ar, title_en | **MATCH** |
| `publicApi.js::getPublicBlogSettings` | GET | `/blog/settings/` | `apps.blog.views.PublicBlogSettingsView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicCategories` | GET | `/blog/categories/` | `apps.blog.views.PublicCategoryListView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicFAQ` | GET | `/cms/public/faq/` | `apps.cms.views.PublicFAQView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicFooter` | GET | `/public/footer/` | `apps.core.views_public.PublicFooterView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicHeader` | GET | `/public/header/` | `apps.core.views_public.PublicHeaderView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicHome` | GET | `/public/home/` | `apps.cms.views.PublicHomeView` | JWTAuthentication, AllowAny | none | footer_columns, hero | **MATCH** |
| `publicApi.js::getPublicPostDetails` | GET | `/blog/posts/{slug}/` | `apps.blog.views.PublicBlogDetailView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicPosts` | GET | `/blog/posts/` | `apps.blog.views.PublicBlogListView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `publicApi.js::getPublicSettings` | GET | `/public/settings/` | `apps.core.views_public.PublicSiteSettingsView` | JWTAuthentication, AllowAny | none | footer, phone_whatsapp, whatsapp, whatsapp_number | **MATCH** |
| `publicApi.js::searchPublic` | GET | `/cms/public/search/` | `apps.cms.views.public_search` | Public/function view | none | response.data | **MATCH** |
| `seoApi.js::adminAllPages` | GET | `/seo/admin/all-pages/` | `apps.seo.views.AllPagesForSEO` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | none | response.data | **MATCH** |
| `seoApi.js::adminCreateSEO` | POST | `/seo/admin/pages/` | `apps.seo.views.PageSEOListCreateView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | multipart/form-data | response.data | **MATCH** |
| `seoApi.js::adminDeleteSEO` | DELETE | `/seo/admin/pages/{id}/` | `apps.seo.views.PageSEODetailView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | none | response.data | **MATCH** |
| `seoApi.js::adminSEOList` | GET | `/seo/admin/pages/` | `apps.seo.views.PageSEOListCreateView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | none | response.data | **MATCH** |
| `seoApi.js::adminUpdateSEO` | PATCH | `/seo/admin/pages/{id}/` | `apps.seo.views.PageSEODetailView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | multipart/form-data | response.data | **MATCH** |
| `blogApi.js::getBlogSettings` | GET | `/blog/settings/` | `apps.blog.views.PublicBlogSettingsView` | JWTAuthentication, AllowAny | none | response.data | **MATCH** |
| `blogApi.js::updateBlogSettings` | PATCH | `/blog/admin/settings/` | `apps.blog.views.BlogSettingsUpdateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `seoApi.js::adminGetDefaultSEO` | GET | `/seo/admin/default/` | `apps.seo.views.DefaultSEOView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | none | response.data | **MATCH** |
| `seoApi.js::adminUpdateDefaultSEO` | PUT | `/seo/admin/default/` | `apps.seo.views.DefaultSEOView` | JWTAuthentication, IsAuthenticated, IsAdminOrSuper | application/json | response.data | **MATCH** |

The 48 component-level calls are restricted to the large header/footer/contact CMS screens and the public footer. They use `API_PATHS` exclusively and resolve to routes already represented in the backend inventory below.
| `servicesApi.js::createMainService` | POST | `/services/admin/main-services/` | `apps.services.views.AdminMainServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::createService` | POST | `/services/admin/services/` | `apps.services.views.AdminServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::createServiceRequestAccessLink` | POST | `/services/admin/service-advisory-requests/{id}/access-links/create/` | `apps.services.access.views.AdminCreateAccessLinkView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | detail, non_field_errors | **MATCH** |
| `servicesApi.js::createServiceSection` | POST | `/services/admin/service-sections/` | `apps.services.views.AdminServiceSectionViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `servicesApi.js::createServicesPageCMS` | POST | `/services/admin/services-page/` | `apps.services.views.AdminServicePageCMSViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::deleteMainService` | DELETE | `/services/admin/main-services/{id}/` | `apps.services.views.AdminMainServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::deleteService` | DELETE | `/services/admin/services/{id}/` | `apps.services.views.AdminServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::deleteServiceAdvisoryRequest` | DELETE | `/services/admin/service-advisory-requests/{id}/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::deleteServiceRequest` | DELETE | `/services/admin/service-advisory-requests/{id}/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::deleteServiceSection` | DELETE | `/services/admin/service-sections/{id}/` | `apps.services.views.AdminServiceSectionViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::getEditableRequestSnapshot` | GET | `/services/public/request-access/{key}/` | `apps.services.access.views.EditableSubmissionSnapshotView` | JWTAuthentication, AllowAny | none | access_token, cooldown_seconds, detail, masked_destination, message, remaining_seconds | **MATCH** |
| `servicesApi.js::getMainServices` | GET | `/services/admin/main-services/` | `apps.services.views.AdminMainServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::getPublicCareers` | GET | `/services/public/careers/jobs/` | `apps.services.views.PublicCareerJobsViewSet` | JWTAuthentication, AllowAny | none | results | **MATCH** |
| `servicesApi.js::getPublicMainServices` | GET | `/services/public/main-services/` | `apps.services.views.PublicMainServiceViewSet` | JWTAuthentication, AllowAny | none | results | **MATCH** |
| `servicesApi.js::getPublicServices` | GET | `/services/public/services/` | `apps.services.views.PublicServiceViewSet` | JWTAuthentication, AllowAny | none | results | **MATCH** |
| `servicesApi.js::getPublicServicesPage` | GET | `/services/public/services-page/` | `apps.services.views.PublicServicePageCMSViewSet` | JWTAuthentication, AllowAny | none | results | **MATCH** |
| `servicesApi.js::getRequestAccessLogs` | GET | `/services/admin/service-advisory-requests/{id}/logs/` | `apps.services.access.views.AdminAccessActivityLogsView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::getServiceAdvisoryRequest` | GET | `/services/admin/service-advisory-requests/{id}/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::getServiceAdvisoryRequests` | GET | `/services/admin/service-advisory-requests/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::getServiceRequestAccessLinks` | GET | `/services/admin/service-advisory-requests/{id}/access-links/` | `apps.services.access.views.AdminRequestAccessLinksView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | detail, non_field_errors | **MATCH** |
| `servicesApi.js::getServiceRequests` | GET | `/services/admin/service-advisory-requests/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::getServiceSections` | GET | `/services/admin/service-sections/` | `apps.services.views.AdminServiceSectionViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::getServices` | GET | `/services/admin/services/` | `apps.services.views.AdminServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::getServicesPageCMS` | GET | `/services/admin/services-page/` | `apps.services.views.AdminServicePageCMSViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | results | **MATCH** |
| `servicesApi.js::getSubmissionEditHistory` | GET | `/services/admin/submissions/{id}/history/` | `apps.services.access.views.AdminSubmissionEditHistoryView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | none | response.data | **MATCH** |
| `servicesApi.js::importServicesExcel` | POST | `/services/admin/import-services/` | `apps.services.views.AdminImportServicesView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | detail, error | **MATCH** |
| `servicesApi.js::regenerateServiceRequestAccessLink` | POST | `/services/admin/request-access-links/{id}/regenerate/` | `apps.services.access.views.AdminRegenerateAccessLinkView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | detail, non_field_errors | **MATCH** |
| `servicesApi.js::revokeServiceRequestAccessLink` | POST | `/services/admin/request-access-links/{id}/revoke/` | `apps.services.access.views.AdminRevokeAccessLinkView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | detail, non_field_errors | **MATCH** |
| `servicesApi.js::sendRequestOTP` | POST | `/services/public/request-access/send-otp/` | `apps.services.access.views.SendOTPView` | JWTAuthentication, AllowAny | application/json | access_token, cooldown_seconds, detail, masked_destination, message, remaining_seconds | **MATCH** |
| `servicesApi.js::updateAdminSubmission` | PATCH | `/services/admin/submissions/{id}/update/` | `apps.services.access.views.AdminEditableSubmissionUpdateView` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | detail | **MATCH** |
| `servicesApi.js::updateEditableRequest` | PATCH | `/services/public/request-access/{key}/update/` | `apps.services.access.views.EditableSubmissionUpdateView` | JWTAuthentication, AllowAny | application/json | access_token, cooldown_seconds, detail, masked_destination, message, remaining_seconds | **MATCH** |
| `servicesApi.js::updateMainService` | PATCH | `/services/admin/main-services/{id}/` | `apps.services.views.AdminMainServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::updateService` | PATCH | `/services/admin/services/{id}/` | `apps.services.views.AdminServiceViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::updateServiceAdvisoryRequest` | PATCH | `/services/admin/service-advisory-requests/{id}/` | `apps.services.views.AdminServiceAdvisoryRequestViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | response.data | **MATCH** |
| `servicesApi.js::updateServiceSection` | PATCH | `/services/admin/service-sections/{id}/` | `apps.services.views.AdminServiceSectionViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | application/json | results | **MATCH** |
| `servicesApi.js::updateServicesPageCMS` | PATCH | `/services/admin/services-page/{id}/` | `apps.services.views.AdminServicePageCMSViewSet` | JWTAuthentication, IsAuthenticated, IsEditorOrAbove | multipart/form-data | results | **MATCH** |
| `servicesApi.js::verifyRequestOTP` | POST | `/services/public/request-access/verify-otp/` | `apps.services.access.views.VerifyOTPView` | JWTAuthentication, AllowAny | application/json | access_token, cooldown_seconds, detail, masked_destination, message, remaining_seconds | **MATCH** |
| `settingsApi.js::getSettings` | GET | `/settings/` | `apps.settings_app.views.SiteSettingsView` | JWTAuthentication, IsAdminOrSuper | none | detail | **MATCH** |
| `settingsApi.js::updateSettings` | PUT | `/settings/` | `apps.settings_app.views.SiteSettingsView` | JWTAuthentication, IsAdminOrSuper | multipart/form-data | detail | **MATCH** |

## Non-MATCH Contracts

None.

## Interpretation

- `MATCH` means the centralized frontend method/path resolves to a backend view supporting that method.
- Request fields marked `caller-provided payload` are serializer-driven objects assembled by the listed consumer.
- Response fields are conservative static observations; database-driven dynamic form fields cannot be exhaustively enumerated statically.
- Backend-only routes may be public, external, framework-generated, or dynamically invoked and remain documented in the public/dashboard references.
