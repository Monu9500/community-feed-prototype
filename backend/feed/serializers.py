"""
Serializers for Community Feed API.

Comment tree serialization is done in-memory after a single prefetched query
to avoid N+1 problems.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, PostLike, CommentLike


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""
    class Meta:
        model = User
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer with nested replies.
    The 'replies' field is populated manually to avoid N+1 queries.
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    replies = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'created_at', 'like_count', 'replies', 'user_has_liked']
        read_only_fields = ['id', 'author', 'created_at', 'like_count']

    def get_replies(self, obj):
        """Get nested replies from context (pre-built tree)."""
        comment_tree = self.context.get('comment_tree', {})
        replies = comment_tree.get(obj.id, [])
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_user_has_liked(self, obj):
        """Check if current user has liked this comment."""
        user = self.context.get('request')
        if user and hasattr(user, 'user') and user.user.is_authenticated:
            liked_comment_ids = self.context.get('liked_comment_ids', set())
            return obj.id in liked_comment_ids
        return False


class PostSerializer(serializers.ModelSerializer):
    """Post serializer with author and like count."""
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count', 'user_has_liked']
        read_only_fields = ['id', 'author', 'created_at', 'like_count', 'comment_count']

    def get_user_has_liked(self, obj):
        """Check if current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked_post_ids = self.context.get('liked_post_ids', set())
            return obj.id in liked_post_ids
        return False


class PostDetailSerializer(PostSerializer):
    """Post serializer with nested comment tree."""
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        """Get top-level comments with nested replies."""
        comment_tree = self.context.get('comment_tree', {})
        # Get root comments (those without parent)
        root_comments = comment_tree.get(None, [])
        return CommentSerializer(root_comments, many=True, context=self.context).data


class LeaderboardUserSerializer(serializers.Serializer):
    """Serializer for leaderboard entries."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    karma_24h = serializers.IntegerField()
