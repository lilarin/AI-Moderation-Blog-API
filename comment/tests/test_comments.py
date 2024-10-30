from django.test import (
    TestCase,
    Client
)
from ninja_jwt.tokens import AccessToken
import comment.models as models
from post.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.admin_user = User.objects.create_user(
            username="admin", password="admin", is_staff=True
        )
        self.post = Post.objects.create(
            title="Test Post", text="Test Content", author=self.user
        )
        self.comment = models.Comment.objects.create(
            post=self.post, author=self.user, text="Test Comment"
        )
        self.client = Client()

    def authenticate(self, user=None):
        if not user:
            user = self.user
        access = AccessToken.for_user(user)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    def test_create_comment_authenticated(self):
        self.authenticate()
        payload = {"text": "New Comment"}
        response = self.client.post(
            f"/api/comments/create/{self.post.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "New Comment")
        self.assertTrue(models.Comment.objects.filter(text="New Comment").exists())

    def test_create_comment_unauthenticated(self):
        payload = {"text": "New Comment"}
        response = self.client.post(
            f"/api/comments/create/{self.post.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_edit_comment(self):
        self.authenticate()
        payload = {"text": "Updated Comment"}
        response = self.client.patch(
            f"/api/comments/{self.comment.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, "Updated Comment")

    def test_edit_comment_no_permission(self):
        self.authenticate(self.admin_user)
        payload = {"text": "Updated Comment"}
        response = self.client.patch(
            f"/api/comments/{self.comment.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_comment(self):
        self.authenticate()
        response = self.client.delete(
            f"/api/comments/{self.comment.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            models.Comment.objects.filter(id=self.comment.id).exists()
        )

    def test_delete_other_user_comment_without_permission(self):
        self.authenticate()
        admin_post = Post.objects.create(
            title="Test Admin Post",
            text="Test Admin Content",
            author=self.admin_user
        )
        admin_comment = models.Comment.objects.create(
            post=admin_post, author=self.admin_user, text="Test Admin Comment"
        )

        response = self.client.delete(
            f"/api/comments/{admin_comment.id}"
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_other_user_comment_by_admin(self):
        self.authenticate(self.admin_user)
        payload = {"text": "Updated Comment"}
        response = self.client.patch(
            f"/api/comments/{self.comment.id}",
            payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_by_admin_user(self):
        self.authenticate(self.admin_user)
        response = self.client.delete(
            f"/api/comments/{self.comment.id}"
        )
        self.assertEqual(response.status_code, 200)
