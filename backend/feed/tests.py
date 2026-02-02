"""
Tests for Community Feed.

Key test: Leaderboard calculation logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post, Comment, PostLike, CommentLike


class LeaderboardTestCase(APITestCase):
    """Test the leaderboard calculation logic."""
    
    def setUp(self):
        """Create test users and content."""
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'pass123')
        
        # user1 creates a post
        self.post1 = Post.objects.create(author=self.user1, content='Test post 1')
        
        # user1 creates a comment
        self.comment1 = Comment.objects.create(
            post=self.post1,
            author=self.user1,
            content='Test comment'
        )
    
    def test_leaderboard_post_karma(self):
        """Test that post likes give 5 karma each."""
        # user2 likes user1's post (5 karma to user1)
        PostLike.objects.create(user=self.user2, post=self.post1)
        
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'user1')
        self.assertEqual(data[0]['karma_24h'], 5)
    
    def test_leaderboard_comment_karma(self):
        """Test that comment likes give 1 karma each."""
        # user2 likes user1's comment (1 karma to user1)
        CommentLike.objects.create(user=self.user2, comment=self.comment1)
        
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'user1')
        self.assertEqual(data[0]['karma_24h'], 1)
    
    def test_leaderboard_combined_karma(self):
        """Test combined karma from posts and comments."""
        # user2 likes user1's post (5 karma)
        PostLike.objects.create(user=self.user2, post=self.post1)
        # user3 likes user1's comment (1 karma)
        CommentLike.objects.create(user=self.user3, comment=self.comment1)
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        self.assertEqual(data[0]['username'], 'user1')
        self.assertEqual(data[0]['karma_24h'], 6)  # 5 + 1
    
    def test_leaderboard_excludes_old_likes(self):
        """Test that likes older than 24 hours are not counted."""
        # Create a like from 25 hours ago (should not count)
        old_like = PostLike.objects.create(user=self.user2, post=self.post1)
        old_like.created_at = timezone.now() - timedelta(hours=25)
        old_like.save()
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        # Leaderboard should be empty since the only like is old
        self.assertEqual(len(data), 0)
    
    def test_leaderboard_top_5_only(self):
        """Test that leaderboard returns only top 5 users."""
        # Create 6 users with different karma
        users = [User.objects.create_user(f'topuser{i}', f'top{i}@test.com', 'pass') for i in range(6)]
        
        for i, user in enumerate(users):
            post = Post.objects.create(author=user, content=f'Post by {user.username}')
            # Each user gets (i+1) likes on their post
            for j in range(i + 1):
                liker = users[(j + 1) % len(users)]
                if liker != user:
                    PostLike.objects.create(user=liker, post=post)
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        self.assertLessEqual(len(data), 5)


class DoubleLikeTestCase(APITestCase):
    """Test that double-liking is prevented."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.author = User.objects.create_user('author', 'author@test.com', 'pass123')
        self.post = Post.objects.create(author=self.author, content='Test post')
        self.client.force_authenticate(user=self.user)
    
    def test_cannot_double_like_post(self):
        """Test that a user cannot like the same post twice."""
        # First like should succeed
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Second like should fail
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Only one like should exist
        self.assertEqual(PostLike.objects.filter(user=self.user, post=self.post).count(), 1)
