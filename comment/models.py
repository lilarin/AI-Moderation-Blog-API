from django.db import models
from django.contrib.auth import get_user_model
from post.models import Post

User = get_user_model()


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="replies"
    )
    is_blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.parent:
            return (
                f"Reply by {self.author} on comment {self.parent.id}"
            )
        return (
            f"Comment by {self.author} with text {self.text}"
        )
