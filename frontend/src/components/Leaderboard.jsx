function Leaderboard({ users }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 sticky top-8">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Top 5 Users
        <span className="block text-sm font-normal text-gray-500">Last 24 hours</span>
      </h2>

      {users.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No karma earned yet today</p>
      ) : (
        <div className="space-y-3">
          {users.map((user, index) => (
            <div
              key={user.id}
              className="flex items-center gap-3 p-3 rounded-lg bg-gray-50"
            >
              {/* Rank */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  index === 0
                    ? 'bg-yellow-400 text-yellow-900'
                    : index === 1
                    ? 'bg-gray-300 text-gray-700'
                    : index === 2
                    ? 'bg-amber-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {index + 1}
              </div>

              {/* User Info */}
              <div className="flex-1">
                <p className="font-semibold text-gray-900">{user.username}</p>
              </div>

              {/* Karma */}
              <div className="text-right">
                <p className="font-bold text-blue-600">{user.karma_24h}</p>
                <p className="text-xs text-gray-500">karma</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
        <p>Post likes: +5 karma</p>
        <p>Comment likes: +1 karma</p>
      </div>
    </div>
  );
}

export default Leaderboard;
