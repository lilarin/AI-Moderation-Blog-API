from celery import shared_task
from comment.models import Comment
from integrations.gemini import response_to_comment

@shared_task
def auto_reply_to_comment(comment_id: int):
    try:
        comment = Comment.objects.get(id=comment_id)
        post = comment.post
        if post.reply_on_comments:
            reply = response_to_comment(post.text, comment.text)
            new_comment = Comment(
                post=post,
                author=post.author,
                text=reply,
                parent=comment
            )
            new_comment.save()
    except Comment.DoesNotExist:
        pass