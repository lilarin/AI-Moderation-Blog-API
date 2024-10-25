from datetime import date, timedelta
from django.test import (
    TestCase,
    Client
)
from ninja_jwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class DailyBreakdownTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.client = Client()

    def authenticate(self):
        access = AccessToken.for_user(self.user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    def test_comments_daily_breakdown(self):
        date_from = date.today() - timedelta(days=1)
        date_to = date.today()
        response = self.client.get(
            f"/api/comments/comments-daily-breakdown/"
            f"?date_from={date_from}&date_to={date_to}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_comments_with_incorrect_daily_breakdown(self):
        date_from = date.today() + timedelta(days=1)
        date_to = date.today()
        response = self.client.get(
            f"/api/comments/comments-daily-breakdown/"
            f"?date_from={date_from}&date_to={date_to}"
        )
        self.assertEqual(response.status_code, 400)

    def test_comments_with_incorrect_data(self):
        date_from = "incorrect data"
        date_to = None
        response = self.client.get(
            f"/api/comments/comments-daily-breakdown/"
            f"?date_from={date_from}&date_to={date_to}"
        )
        self.assertEqual(response.status_code, 422)
