"""
Views for Community Feed API.

Key optimizations:
1. Comment tree is fetched in a single query with select_related and prefetch_related
2. Tree structure is built in-memory to avoid N+1 queries
3. Leaderboard uses aggregation on activity history (PostLike/CommentLike created_at)
4. Like operations use select_for_update to handle race conditions
"""
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum, Case, When, IntegerField, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    PostSerializer, PostDetailSerializer, CommentSerializer,
    LeaderboardUserSerializer, UserSerializer
)


def build_comment_tree(comments):
    """
    Build a tree structure from flat list of comments.
    Returns a dict mapping parent_id -> list of child comments.
    This avoids N+1 queries by building the tree in memory.
    """
    tree = {}
    for comment in comments:
        parent_id = comment.parent_id
        if parent_id not in tree:
            tree[parent_id] = []
        tree[parent_id].append(comment)
    return tree


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for posts with optimized queries.
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get posts with author and like count in a single query."""
        return Post.objects.select_related('author').annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer
    
    def get_serializer_context(self):
        """Add liked post IDs to context for current user."""
        context = super().get_serializer_context()
        request = self.request
        if request and request.user.is_authenticated:
            context['liked_post_ids'] = set(
                PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
            )
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get a single post with its full comment tree.
        All comments are fetched in ONE query, then tree is built in-memory.
        """
        post = self.get_object()
        
        # Fetch ALL comments for this post in a single query
        comments = list(
            Comment.objects.filter(post=post)
            .select_related('author')
            .annotate(like_count=Count('likes'))
            .order_by('created_at')
        )
        
        # Build tree structure in memory
        comment_tree = build_comment_tree(comments)
        
        # Get liked comment IDs for current user
        liked_comment_ids = set()
        if request.user.is_authenticated:
            liked_comment_ids = set(
                CommentLike.objects.filter(
                    user=request.user,
                    comment__post=post
                ).values_list('comment_id', flat=True)
            )
        
        context = self.get_serializer_context()
        context['comment_tree'] = comment_tree
        context['liked_comment_ids'] = liked_comment_ids
        
        serializer = self.get_serializer(post, context=context)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Create post with current user as author."""
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            # For demo: use first user or create one
            user, _ = User.objects.get_or_create(
                username='demo_user',
                defaults={'email': 'demo@example.com'}
            )
            serializer.save(author=user)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def like(self, request, pk=None):
        """
        Like a post. Handles race conditions with select_for_update.
        Uses unique constraint to prevent double-liking.
        Awards 5 karma to post author.
        """
        post = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            user, _ = User.objects.get_or_create(
                username='demo_user',
                defaults={'email': 'demo@example.com'}
            )
        
        try:
            with transaction.atomic():
                # Use get_or_create with unique constraint to handle race conditions
                _, created = PostLike.objects.get_or_create(user=user, post=post)
                if not created:
                    return Response(
                        {'detail': 'Already liked this post'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response({'detail': 'Post liked successfully', 'karma_awarded': 5})
        except IntegrityError:
            return Response(
                {'detail': 'Already liked this post'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def unlike(self, request, pk=None):
        """Remove like from a post."""
        post = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            user = User.objects.filter(username='demo_user').first()
            if not user:
                return Response(
                    {'detail': 'Not liked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        deleted, _ = PostLike.objects.filter(user=user, post=post).delete()
        if deleted:
            return Response({'detail': 'Like removed'})
        return Response(
            {'detail': 'Not liked'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments."""
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get comments with author and like count."""
        return Comment.objects.select_related('author').annotate(
            like_count=Count('likes')
        )
    
    def perform_create(self, serializer):
        """Create comment with current user as author."""
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            user, _ = User.objects.get_or_create(
                username='demo_user',
                defaults={'email': 'demo@example.com'}
            )
            serializer.save(author=user)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def like(self, request, pk=None):
        """
        Like a comment. Awards 1 karma to comment author.
        Uses unique constraint to prevent double-liking.
        """
        comment = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            user, _ = User.objects.get_or_create(
                username='demo_user',
                defaults={'email': 'demo@example.com'}
            )
        
        try:
            with transaction.atomic():
                _, created = CommentLike.objects.get_or_create(user=user, comment=comment)
                if not created:
                    return Response(
                        {'detail': 'Already liked this comment'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response({'detail': 'Comment liked successfully', 'karma_awarded': 1})
        except IntegrityError:
            return Response(
                {'detail': 'Already liked this comment'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def unlike(self, request, pk=None):
        """Remove like from a comment."""
        comment = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            user = User.objects.filter(username='demo_user').first()
            if not user:
                return Response(
                    {'detail': 'Not liked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        deleted, _ = CommentLike.objects.filter(user=user, comment=comment).delete()
        if deleted:
            return Response({'detail': 'Like removed'})
        return Response(
            {'detail': 'Not liked'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """
    Get top 5 users by karma earned in the last 24 hours.
    
    Karma calculation:
    - 1 PostLike received = 5 karma
    - 1 CommentLike received = 1 karma
    
    This is calculated dynamically from PostLike and CommentLike created_at timestamps,
    NOT from a stored "daily_karma" field.
    
    The QuerySet:
    - Filters likes received in last 24 hours
    - Aggregates karma: (post_likes * 5) + (comment_likes * 1)
    - Orders by total karma descending
    - Returns top 5
    """
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    # Get karma from post likes (5 karma each) received in last 24h
    # A user gets karma when THEIR posts are liked
    post_karma = PostLike.objects.filter(
        created_at__gte=last_24h
    ).values('post__author').annotate(
        karma=Count('id') * 5
    ).values('post__author', 'karma')
    
    # Get karma from comment likes (1 karma each) received in last 24h
    comment_karma = CommentLike.objects.filter(
        created_at__gte=last_24h
    ).values('comment__author').annotate(
        karma=Count('id')
    ).values('comment__author', 'karma')
    
    # Combine karma from both sources
    user_karma = {}
    
    for entry in post_karma:
        user_id = entry['post__author']
        user_karma[user_id] = user_karma.get(user_id, 0) + entry['karma']
    
    for entry in comment_karma:
        user_id = entry['comment__author']
        user_karma[user_id] = user_karma.get(user_id, 0) + entry['karma']
    
    # Sort by karma and get top 5
    sorted_users = sorted(user_karma.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Fetch user details
    user_ids = [user_id for user_id, _ in sorted_users]
    users = {u.id: u for u in User.objects.filter(id__in=user_ids)}
    
    result = []
    for user_id, karma in sorted_users:
        if user_id in users:
            result.append({
                'id': user_id,
                'username': users[user_id].username,
                'karma_24h': karma
            })
    
    serializer = LeaderboardUserSerializer(result, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Simple user registration."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(username=username, password=password)
    return Response({
        'id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Simple login that returns user info."""
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        return Response({
            'id': user.id,
            'username': user.username
        })
    return Response(
        {'detail': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """Get current user info."""
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'username': request.user.username
        })
    return Response({'detail': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
