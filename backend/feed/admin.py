"""Admin configuration for feed app."""
from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['created_at']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'comment', 'created_at']
    list_filter = ['created_at']
