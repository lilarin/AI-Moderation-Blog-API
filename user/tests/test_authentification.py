from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ninja_jwt.tokens import AccessToken

User = get_user_model()


class UserAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="old_password"
        )
        self.client = Client()

    def authenticate(self):
        access = AccessToken.for_user(self.user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    def test_get_user(self):
        self.authenticate()
        response = self.client.get("/api/user/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                "id": self.user.id,
                "is_staff": False,
                "username": "testuser"
            }
        )

    def test_update_password(self):
        self.authenticate()

        response = self.client.patch(
            "/api/user/",
            {"old_password": "old_password", "new_password": "new_password"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password"))

        failure_cases = [
            (
                {"old_password": "wrong_password", "new_password": "new_password"},
                400,
                "Current password is incorrect.",
            ),
            (
                {"old_password": "old_password", "new_password": "old_password"},
                400,
                "Current password is incorrect.",
            )
        ]

        for data, status_code, detail in failure_cases:
            response = self.client.patch(
                "/api/user/", data, content_type="application/json"
            )
            self.assertEqual(response.status_code, status_code)
            self.assertIn(detail, response.json()["detail"])

    def test_register_user(self):
        response = self.client.post(
            "/api/user/register",
            {"username": "newuser", "password": "new_password"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

        failure_cases = [
            (
                {"username": "testuser", "password": "new_password"},
                400,
                "Username is already taken.",
            ),
            (
                {"username": "newuser2", "password": "short"},
                400,
                "This password is too short.",
            ),
            ({"password": "valid_password"}, 422, None),
            ({"username": "newuser3"}, 422, None),
        ]

        for data, status_code, detail in failure_cases:
            response = self.client.post(
                "/api/user/register", data, content_type="application/json"
            )
            self.assertEqual(response.status_code, status_code)
            if detail:
                self.assertIn(detail, response.json()["detail"])

    def test_get_user_unauthenticated(self):
        response = self.client.get("/api/user/")
        self.assertEqual(response.status_code, 401)

    def test_update_password_unauthenticated(self):
        response = self.client.patch(
            "/api/user/",
            {"old_password": "old_password", "new_password": "new_password"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
