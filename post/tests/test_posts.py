from datetime import timedelta
from django.test import TestCase, Client
from ninja_jwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from post.models import Post

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
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            text="Test Content",
            reply_time=timedelta(hours=1)
        )

    def authenticate(self, user=None):
        if not user:
            user = self.user
        access = AccessToken.for_user(user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    def test_get_posts(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        self.authenticate()
        payload = {
            "title": "New Post",
            "text": "New Post Content",
            "reply_time": "01:00:00"
        }
        response = self.client.post(
            "/api/posts/",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "New Post")

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
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_no_access(self):
        self.authenticate(self.other_user)
        response = self.client.delete(f"/api/posts/{self.post.id}")
        self.assertEqual(response.status_code, 403)
