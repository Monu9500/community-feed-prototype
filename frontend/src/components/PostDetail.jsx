'use client';

import { useState, useEffect } from 'react';
import { getPost, likePost, unlikePost, createComment, likeComment, unlikeComment } from '../api';
import CommentTree from './CommentTree';

function PostDetail({ postId, onBack }) {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyContent, setReplyContent] = useState('');

  useEffect(() => {
    loadPost();
  }, [postId]);

  async function loadPost() {
    try {
      setLoading(true);
      const data = await getPost(postId);
      setPost(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleLikePost() {
    try {
      if (post.user_has_liked) {
        await unlikePost(postId);
      } else {
        await likePost(postId);
      }
      loadPost();
    } catch (err) {
      if (!err.message.includes('Already')) {
        setError(err.message);
      }
    }
  }

  async function handleSubmitComment(e) {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await createComment(postId, newComment);
      setNewComment('');
      loadPost();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSubmitReply(parentId) {
    if (!replyContent.trim()) return;

    try {
      await createComment(postId, replyContent, parentId);
      setReplyContent('');
      setReplyingTo(null);
      loadPost();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleLikeComment(commentId, hasLiked) {
    try {
      if (hasLiked) {
        await unlikeComment(commentId);
      } else {
        await likeComment(commentId);
      }
      loadPost();
    } catch (err) {
      if (!err.message.includes('Already')) {
        setError(err.message);
      }
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
          <p className="mt-2 text-gray-600">Loading post...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
          <button
            onClick={onBack}
            className="mt-4 text-blue-600 hover:underline"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Feed
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Post Details</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Post */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-lg">
              {post.author.username.charAt(0).toUpperCase()}
            </div>
            <div className="ml-3">
              <p className="font-semibold text-gray-900">{post.author.username}</p>
              <p className="text-sm text-gray-500">{formatDate(post.created_at)}</p>
            </div>
          </div>

          <p className="text-gray-800 text-lg mb-6">{post.content}</p>

          <div className="flex items-center gap-6 text-gray-500 border-t pt-4">
            <button
              onClick={handleLikePost}
              className={`flex items-center gap-2 hover:text-red-500 transition-colors ${
                post.user_has_liked ? 'text-red-500' : ''
              }`}
            >
              <svg
                className="w-6 h-6"
                fill={post.user_has_liked ? 'currentColor' : 'none'}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
              <span className="font-medium">{post.like_count} Likes</span>
            </button>
            <span className="flex items-center gap-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <span className="font-medium">{post.comments?.length || 0} Comments</span>
            </span>
          </div>
        </div>

        {/* Add Comment Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Add a Comment</h3>
          <form onSubmit={handleSubmitComment}>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write your comment..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
            <div className="mt-3 flex justify-end">
              <button
                type="submit"
                disabled={!newComment.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Comment
              </button>
            </div>
          </form>
        </div>

        {/* Comments */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">
            Comments ({post.comments?.length || 0})
          </h3>

          {post.comments && post.comments.length > 0 ? (
            <CommentTree
              comments={post.comments}
              onLike={handleLikeComment}
              onReply={(commentId) => {
                setReplyingTo(commentId);
                setReplyContent('');
              }}
              replyingTo={replyingTo}
              replyContent={replyContent}
              onReplyContentChange={setReplyContent}
              onSubmitReply={handleSubmitReply}
              onCancelReply={() => setReplyingTo(null)}
            />
          ) : (
            <p className="text-gray-500 text-center py-4">No comments yet. Be the first!</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default PostDetail;
