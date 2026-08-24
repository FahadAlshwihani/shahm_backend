from django.urls import path

from .views import (
    ContactMessageView,
    SubscriberView,
    AdminMessagesView,
    AdminSingleMessageView,
    SubscribersListView,
    BroadcastEmailView,
    SubscriberDeleteView,
    ExportSubscribersCSV,
    BroadcastLogsListView,
    EmailTemplateView,
)


urlpatterns = [
    # Public
    path("contact/", ContactMessageView.as_view()),
    path("subscribe/", SubscriberView.as_view()),

    # Admin - Messages
    path("admin/messages/", AdminMessagesView.as_view()),
    path("admin/messages/<int:pk>/", AdminSingleMessageView.as_view()),

    # Admin - Subscribers
    path("admin/subscribers/", SubscribersListView.as_view()),
    path("admin/subscribers/<int:pk>/", SubscriberDeleteView.as_view()),
    path("admin/subscribers/export/", ExportSubscribersCSV.as_view()),

    # Admin - Broadcast
    path("admin/broadcast/", BroadcastEmailView.as_view()),
    path("admin/broadcast/logs/", BroadcastLogsListView.as_view()),

    # email templates
    path("admin/email-templates/", EmailTemplateView.as_view()),

]
