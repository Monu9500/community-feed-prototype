'use client';

function CommentTree({
  comments,
  onLike,
  onReply,
  replyingTo,
  replyContent,
  onReplyContentChange,
  onSubmitReply,
  onCancelReply,
  depth = 0,
}) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Limit nesting depth for UI clarity
  const maxDepth = 4;
  const actualDepth = Math.min(depth, maxDepth);

  return (
    <div className={depth > 0 ? 'ml-6 border-l-2 border-gray-200 pl-4' : ''}>
      {comments.map((comment) => (
        <div key={comment.id} className="mb-4">
          {/* Comment */}
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
              {comment.author.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900 text-sm">
                    {comment.author.username}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(comment.created_at)}
                  </span>
                </div>
                <p className="text-gray-800 text-sm">{comment.content}</p>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-4 mt-2 text-sm">
                <button
                  onClick={() => onLike(comment.id, comment.user_has_liked)}
                  className={`flex items-center gap-1 hover:text-red-500 transition-colors ${
                    comment.user_has_liked ? 'text-red-500' : 'text-gray-500'
                  }`}
                >
                  <svg
                    className="w-4 h-4"
                    fill={comment.user_has_liked ? 'currentColor' : 'none'}
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
                  <span>{comment.like_count}</span>
                </button>

                {actualDepth < maxDepth && (
                  <button
                    onClick={() => onReply(comment.id)}
                    className="text-gray-500 hover:text-blue-500 transition-colors"
                  >
                    Reply
                  </button>
                )}
              </div>

              {/* Reply Form */}
              {replyingTo === comment.id && (
                <div className="mt-3 bg-white border border-gray-200 rounded-lg p-3">
                  <textarea
                    value={replyContent}
                    onChange={(e) => onReplyContentChange(e.target.value)}
                    placeholder="Write your reply..."
                    className="w-full p-2 border border-gray-300 rounded resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    rows={2}
                    autoFocus
                  />
                  <div className="mt-2 flex justify-end gap-2">
                    <button
                      onClick={onCancelReply}
                      className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => onSubmitReply(comment.id)}
                      disabled={!replyContent.trim()}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Reply
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Nested Replies */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-3">
              <CommentTree
                comments={comment.replies}
                onLike={onLike}
                onReply={onReply}
                replyingTo={replyingTo}
                replyContent={replyContent}
                onReplyContentChange={onReplyContentChange}
                onSubmitReply={onSubmitReply}
                onCancelReply={onCancelReply}
                depth={depth + 1}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default CommentTree;
