"""
Models for Community Feed.

Nested comments are modeled using MPTT (Modified Preorder Tree Traversal) pattern
with parent reference for efficient tree queries without N+1 problems.
"""
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """A text post in the community feed."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    """
    A comment on a post or reply to another comment.
    Uses parent reference for nested threading (adjacency list model).
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username}"


class PostLike(models.Model):
    """
    Like on a post. Unique constraint prevents double-liking.
    Each like gives 5 karma to the post author.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent double-liking at database level
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like')
        ]

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


class CommentLike(models.Model):
    """
    Like on a comment. Unique constraint prevents double-liking.
    Each like gives 1 karma to the comment author.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent double-liking at database level
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_like')
        ]

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"
