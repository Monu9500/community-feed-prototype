'use client';

import { useState, useEffect } from 'react';
import { getPosts, getLeaderboard, createPost, likePost, unlikePost } from './api';
import PostCard from './components/PostCard';
import Leaderboard from './components/Leaderboard';
import PostDetail from './components/PostDetail';

function App() {
  const [posts, setPosts] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [selectedPostId, setSelectedPostId] = useState(null);
  const [newPostContent, setNewPostContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [postsData, leaderboardData] = await Promise.all([
        getPosts(),
        getLeaderboard(),
      ]);
      setPosts(postsData.results || postsData);
      setLeaderboard(leaderboardData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreatePost(e) {
    e.preventDefault();
    if (!newPostContent.trim()) return;
    
    try {
      await createPost(newPostContent);
      setNewPostContent('');
      loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleLikePost(postId, hasLiked) {
    try {
      if (hasLiked) {
        await unlikePost(postId);
      } else {
        await likePost(postId);
      }
      loadData();
    } catch (err) {
      // Ignore "already liked" errors
      if (!err.message.includes('Already')) {
        setError(err.message);
      }
    }
  }

  if (selectedPostId) {
    return (
      <PostDetail 
        postId={selectedPostId} 
        onBack={() => {
          setSelectedPostId(null);
          loadData();
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Community Feed</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Main Feed */}
          <div className="flex-1">
            {/* Create Post Form */}
            <form onSubmit={handleCreatePost} className="bg-white rounded-lg shadow p-6 mb-6">
              <textarea
                value={newPostContent}
                onChange={(e) => setNewPostContent(e.target.value)}
                placeholder="What's on your mind?"
                className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
              />
              <div className="mt-3 flex justify-end">
                <button
                  type="submit"
                  disabled={!newPostContent.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Post
                </button>
              </div>
            </form>

            {/* Error Message */}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                {error}
                <button onClick={() => setError(null)} className="float-right font-bold">&times;</button>
              </div>
            )}

            {/* Posts */}
            {loading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
                <p className="mt-2 text-gray-600">Loading posts...</p>
              </div>
            ) : posts.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                No posts yet. Be the first to post!
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <PostCard
                    key={post.id}
                    post={post}
                    onLike={() => handleLikePost(post.id, post.user_has_liked)}
                    onClick={() => setSelectedPostId(post.id)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Sidebar - Leaderboard */}
          <div className="w-80 flex-shrink-0">
            <Leaderboard users={leaderboard} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
