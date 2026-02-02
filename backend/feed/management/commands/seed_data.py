"""Management command to seed demo data."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from feed.models import Post, Comment, PostLike, CommentLike


class Command(BaseCommand):
    help = 'Seeds the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create users
        users = []
        usernames = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank']
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        self.stdout.write(f'Created {len(users)} users')
        
        # Create posts
        post_contents = [
            "Just deployed my first Django REST API! The documentation was super helpful.",
            "Has anyone tried the new React 19 features? The compiler looks promising.",
            "Working on a community feed project. Nested comments are tricky!",
            "Pro tip: Always use select_related and prefetch_related to avoid N+1 queries.",
            "TIL about database constraints for preventing race conditions. Game changer!",
        ]
        
        posts = []
        for i, content in enumerate(post_contents):
            post, _ = Post.objects.get_or_create(
                author=users[i % len(users)],
                content=content
            )
            posts.append(post)
        
        self.stdout.write(f'Created {len(posts)} posts')
        
        # Create comments with nesting
        comments = []
        comment_texts = [
            "Great post! Thanks for sharing.",
            "I had the same experience, very useful info.",
            "Could you explain more about this?",
            "This is exactly what I was looking for!",
            "Interesting perspective, thanks!",
        ]
        
        for post in posts:
            # Root comments
            for i in range(2):
                comment = Comment.objects.create(
                    post=post,
                    author=users[(i + 1) % len(users)],
                    content=random.choice(comment_texts)
                )
                comments.append(comment)
                
                # Nested replies
                reply = Comment.objects.create(
                    post=post,
                    author=users[(i + 2) % len(users)],
                    parent=comment,
                    content="Thanks for your reply!"
                )
                comments.append(reply)
                
                # Second level nesting
                Comment.objects.create(
                    post=post,
                    author=users[(i + 3) % len(users)],
                    parent=reply,
                    content="No problem, happy to help!"
                )
        
        self.stdout.write(f'Created {Comment.objects.count()} comments')
        
        # Create likes (within last 24 hours for leaderboard)
        now = timezone.now()
        
        for post in posts:
            # Each post gets 2-4 random likes
            likers = random.sample(users, k=min(random.randint(2, 4), len(users)))
            for user in likers:
                if user != post.author:
                    PostLike.objects.get_or_create(
                        user=user,
                        post=post,
                        defaults={'created_at': now - timedelta(hours=random.randint(1, 20))}
                    )
        
        for comment in comments[:10]:
            # Some comments get likes
            likers = random.sample(users, k=min(random.randint(1, 3), len(users)))
            for user in likers:
                if user != comment.author:
                    CommentLike.objects.get_or_create(
                        user=user,
                        comment=comment,
                        defaults={'created_at': now - timedelta(hours=random.randint(1, 20))}
                    )
        
        self.stdout.write(f'Created {PostLike.objects.count()} post likes')
        self.stdout.write(f'Created {CommentLike.objects.count()} comment likes')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
