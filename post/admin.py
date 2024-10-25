from django.contrib import admin
from .models import Post
from comment.models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "created_at", "reply_on_comments", "is_blocked"
    )
    search_fields = ("title", "author__username", "text")
    list_filter = ("is_blocked", "created_at")
    inlines = [CommentInline]

    def comments(self, obj):
        return obj.comments.count()

    comments.short_description = "Comments"
