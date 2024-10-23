# posts/admin.py

from django.contrib import admin
from .models import Post
from comment.models import Comment  # Импортируем модель Comment для использования в админке

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1  # Количество пустых комментариев, которые будут отображаться по умолчанию

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_blocked')  # Поля, которые будут отображаться в списке
    search_fields = ('title', 'author__username', 'text')  # Поиск по заголовку и автору
    list_filter = ('is_blocked', 'created_at')  # Фильтры
    inlines = [CommentInline]  # Встраиваем комментарии в админку

    def comments(self, obj):
        """Свойство для отображения количества комментариев в списке."""
        return obj.comments.count()

    comments.short_description = 'Comments'  # Название для столбца

