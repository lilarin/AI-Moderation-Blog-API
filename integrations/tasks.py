from celery import shared_task
from comment.models import Comment
from integrations.gemini import response_to_comment


@shared_task
def auto_reply_to_comment(comment_id: int) -> None:
    try:
        comment = Comment.objects.get(id=comment_id)
        reply = response_to_comment(comment.post.text, comment.text)
        new_comment = Comment(
            post=comment.post,
            author=comment.post.author,
            text=reply,
            parent=comment
        )
        new_comment.save()
    except Comment.DoesNotExist:
        pass
