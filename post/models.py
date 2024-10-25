from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reply_on_comments = models.BooleanField(default=False)
    reply_time = models.DurationField(default=timedelta(minutes=5))
    is_blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @property
    def comments(self):
        from comment.models import Comment
        return Comment.objects.filter(post=self)

    def __str__(self):
        return self.title
