from unittest.mock import call, patch

from django.test import TestCase
from rest_framework.test import APIClient

from apps.messaging.models import ContactMessage, Subscriber
from apps.settings_app.models import SiteSettings


class MessagingEmailContractTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        SiteSettings.objects.create(
            site_name_ar="Shahm",
            contact_receiver_email="admin@example.test",
            auto_reply_email="no-reply@example.test",
        )

    @patch("apps.messaging.views.DynamicEmailService.send_email")
    @patch("apps.messaging.views.render_email_template")
    def test_contact_selects_admin_alert_and_auto_reply_without_real_smtp(
        self, render_template, send_email
    ):
        render_template.side_effect = [
            ("Admin alert", "<p>alert</p>"),
            ("Auto reply", "<p>reply</p>"),
        ]

        response = self.client.post(
            "/api/messaging/contact/",
            {
                "name": "Client",
                "email": "client@example.test",
                "phone": "+966500000000",
                "subject": "Question",
                "message": "Please contact me.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(
            [item.args[0] for item in render_template.call_args_list],
            ["admin_alert", "auto_reply"],
        )
        self.assertEqual(send_email.call_count, 2)

    @patch("apps.messaging.views.DynamicEmailService.send_email")
    @patch("apps.messaging.views.render_email_template", return_value=("Welcome", "<p>Hi</p>"))
    def test_subscription_welcome_is_sent_once_for_a_new_address(
        self, render_template, send_email
    ):
        first = self.client.post(
            "/api/messaging/subscribe/", {"email": "reader@example.test"}, format="json"
        )
        duplicate = self.client.post(
            "/api/messaging/subscribe/", {"email": "reader@example.test"}, format="json"
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 1)
        render_template.assert_called_once_with(
            "subscription_welcome",
            {"email": "reader@example.test", "site_name": "Shahm"},
        )
        send_email.assert_called_once()

    def test_admin_message_list_requires_authentication(self):
        response = self.client.get("/api/messaging/admin/messages/")

        self.assertEqual(response.status_code, 401)
