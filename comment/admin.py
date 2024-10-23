from django.contrib import admin
from comment.models import Comment

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_blocked')
    search_fields = ('author__username', 'post__title')
    list_filter = ('is_blocked', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Comment, CommentAdmin)