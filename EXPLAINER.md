# EXPLAINER.md

## 1. The Tree: Nested Comments Model

### Database Model

I used the **Adjacency List** model with a self-referential foreign key for nested comments:

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

Each comment has:
- `post`: The post it belongs to
- `parent`: Reference to parent comment (NULL for root-level comments)
- `replies`: Reverse relation to child comments

### Avoiding N+1 Queries

The key to avoiding N+1 queries is fetching ALL comments for a post in a **single query**, then building the tree structure in memory:

```python
# In views.py - retrieve method
def retrieve(self, request, pk=None):
    post = self.get_object()
    
    # ONE query to get ALL comments for this post
    comments = list(
        Comment.objects.filter(post=post)
        .select_related('author')  # Joins author in same query
        .annotate(like_count=Count('likes'))  # Aggregates likes
        .order_by('created_at')
    )
    
    # Build tree in-memory (O(n) time complexity)
    comment_tree = build_comment_tree(comments)

def build_comment_tree(comments):
    """Build tree from flat list - groups comments by parent_id"""
    tree = {}
    for comment in comments:
        parent_id = comment.parent_id
        if parent_id not in tree:
            tree[parent_id] = []
        tree[parent_id].append(comment)
    return tree
```

This approach:
- Uses only **2-3 SQL queries total** regardless of comment count
- Builds nested structure in Python (fast, O(n))
- Uses `select_related` to avoid separate author queries
- Uses `annotate` to count likes without additional queries

---

## 2. The Math: 24-Hour Leaderboard Query

The leaderboard calculates karma dynamically from `PostLike` and `CommentLike` timestamps, NOT from a stored field.

### The QuerySet/SQL

```python
# In views.py - leaderboard function
from django.utils import timezone
from datetime import timedelta

def leaderboard(request):
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
    
    # Combine karma from both sources in Python
    user_karma = {}
    for entry in post_karma:
        user_id = entry['post__author']
        user_karma[user_id] = user_karma.get(user_id, 0) + entry['karma']
    
    for entry in comment_karma:
        user_id = entry['comment__author']
        user_karma[user_id] = user_karma.get(user_id, 0) + entry['karma']
    
    # Sort and get top 5
    sorted_users = sorted(user_karma.items(), key=lambda x: x[1], reverse=True)[:5]
```

### Equivalent SQL

```sql
-- Post karma (5 per like)
SELECT post.author_id, COUNT(*) * 5 as karma
FROM feed_postlike
JOIN feed_post post ON feed_postlike.post_id = post.id
WHERE feed_postlike.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY post.author_id;

-- Comment karma (1 per like)
SELECT comment.author_id, COUNT(*) as karma
FROM feed_commentlike
JOIN feed_comment comment ON feed_commentlike.comment_id = comment.id
WHERE feed_commentlike.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY comment.author_id;
```

This approach:
- Calculates karma dynamically from like timestamps
- Does NOT store daily karma on User model
- Uses database aggregation for efficiency
- Filters by `created_at >= last_24h` for time window

---

## 3. The AI Audit

### Bug: Race Condition in Like Logic

**Initial AI-generated code:**

```python
def like(self, request, pk=None):
    post = self.get_object()
    # AI wrote this - vulnerable to race conditions!
    if PostLike.objects.filter(user=request.user, post=post).exists():
        return Response({'detail': 'Already liked'}, status=400)
    PostLike.objects.create(user=request.user, post=post)
    return Response({'detail': 'Liked'})
```

**The Problem:**
This code has a TOCTOU (Time-of-Check to Time-of-Use) race condition. Two concurrent requests could both pass the `exists()` check before either creates the like, resulting in duplicate likes.

**My Fix:**

```python
def like(self, request, pk=None):
    post = self.get_object()
    try:
        with transaction.atomic():
            # Use get_or_create - atomic operation that relies on DB constraint
            _, created = PostLike.objects.get_or_create(user=user, post=post)
            if not created:
                return Response(
                    {'detail': 'Already liked this post'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response({'detail': 'Post liked successfully'})
    except IntegrityError:
        # Catches constraint violation if race condition occurs
        return Response(
            {'detail': 'Already liked this post'},
            status=status.HTTP_400_BAD_REQUEST
        )
```

**Plus database constraint in model:**

```python
class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like')
        ]
```

**Why this works:**
1. `get_or_create` is atomic at the database level
2. `UniqueConstraint` prevents duplicates even if race condition occurs
3. `IntegrityError` catch handles edge cases
4. No karma inflation possible via rapid clicking

---

## Technical Decisions Summary

| Constraint | Solution |
|------------|----------|
| N+1 Comments | Single query + in-memory tree building |
| 24h Leaderboard | Aggregate from Like timestamps, not stored field |
| Double-Like Prevention | DB constraint + atomic get_or_create |
| Race Conditions | transaction.atomic + IntegrityError handling |
