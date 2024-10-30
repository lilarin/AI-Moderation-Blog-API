from datetime import timedelta
from django.test import (
    TestCase,
    Client
)
from django.contrib.auth import get_user_model
import post.models as models
from ninja_jwt.tokens import AccessToken

User = get_user_model()


class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="password"
        )
        self.client = Client()
        self.post = models.Post.objects.create(
            author=self.user,
            title="Test Post",
            text="Test Content"
        )

    def authenticate(self, user=None):
        if not user:
            user = self.user
        access = AccessToken.for_user(user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    def test_get_posts(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, 200)

    def test_create_post_without_auto_replay(self):
        self.authenticate()
        time = timedelta(hours=1)
        payload = {
            "title": "New Post",
            "text": "New Post Content",
            "reply_time": time
        }
        response = self.client.post(
            "/api/posts/",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply_time"], "P0DT01H00M00S")

    def test_create_post_with_auto_replay_default_time(self):
        self.authenticate()
        payload = {
            "title": "New Post",
            "text": "New Post Content",
            "reply_on_comments": True
        }
        response = self.client.post(
            "/api/posts/",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply_time"], "P0DT00H05M00S")

    def test_create_post_with_auto_replay_specified_time(self):
        self.authenticate()
        time = timedelta(minutes=10)
        payload = {
            "title": "New Post",
            "text": "New Post Content",
            "reply_on_comments": True,
            "reply_time": time
        }
        response = self.client.post(
            "/api/posts/",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply_time"], "P0DT00H10M00S")

    def test_toggle_auto_replay(self):
        self.authenticate()
        response = self.client.patch(
            f"/api/posts/{self.post.id}/toggle",
            {}, content_type="application/json"
        )
        self.assertNotEqual(
            response.json()["reply_on_comments"], self.post.reply_on_comments
        )

    def test_get_post(self):
        response = self.client.get(f"/api/posts/{self.post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.post.title)

    def test_edit_post(self):
        self.authenticate()
        payload = {
            "title": "Updated Post",
            "text": "Updated Content"
        }
        response = self.client.patch(
            f"/api/posts/{self.post.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")

    def test_edit_post_no_access(self):
        self.authenticate(self.other_user)
        payload = {
            "title": "Updated Post",
            "text": "Updated Content"
        }
        response = self.client.patch(
            f"/api/posts/{self.post.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_post(self):
        self.authenticate()
        response = self.client.delete(f"/api/posts/{self.post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_no_access(self):
        self.authenticate(self.other_user)
        response = self.client.delete(f"/api/posts/{self.post.id}")
        self.assertEqual(response.status_code, 403)
