// API base URL - change this for production
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function fetchApi(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
}

// Posts
export const getPosts = () => fetchApi('/posts/');
export const getPost = (id) => fetchApi(`/posts/${id}/`);
export const createPost = (content) => fetchApi('/posts/', {
  method: 'POST',
  body: JSON.stringify({ content }),
});
export const likePost = (id) => fetchApi(`/posts/${id}/like/`, { method: 'POST' });
export const unlikePost = (id) => fetchApi(`/posts/${id}/unlike/`, { method: 'POST' });

// Comments
export const createComment = (postId, content, parentId = null) => fetchApi('/comments/', {
  method: 'POST',
  body: JSON.stringify({ post: postId, content, parent: parentId }),
});
export const likeComment = (id) => fetchApi(`/comments/${id}/like/`, { method: 'POST' });
export const unlikeComment = (id) => fetchApi(`/comments/${id}/unlike/`, { method: 'POST' });

// Leaderboard
export const getLeaderboard = () => fetchApi('/leaderboard/');

// Auth
export const login = (username, password) => fetchApi('/auth/login/', {
  method: 'POST',
  body: JSON.stringify({ username, password }),
});
export const register = (username, password) => fetchApi('/auth/register/', {
  method: 'POST',
  body: JSON.stringify({ username, password }),
});
