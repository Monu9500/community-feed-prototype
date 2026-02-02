export default function Page() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Community Feed Project
          </h1>
          <p className="text-gray-600 mb-6">
            This is a Django + React project built for the Playto Engineering Challenge.
            It cannot run in the v0 preview because Django requires a Python backend.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-blue-900 mb-3">
              How to Run Locally
            </h2>
            <div className="space-y-4 text-sm">
              <div>
                <h3 className="font-semibold text-blue-800">1. Backend (Django)</h3>
                <pre className="bg-gray-900 text-green-400 p-3 rounded mt-2 overflow-x-auto">
{`cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data  # Optional: adds demo data
python manage.py runserver`}
                </pre>
              </div>
              <div>
                <h3 className="font-semibold text-blue-800">2. Frontend (React)</h3>
                <pre className="bg-gray-900 text-green-400 p-3 rounded mt-2 overflow-x-auto">
{`cd frontend
npm install
npm run dev`}
                </pre>
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Features</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Feed with text posts</li>
                <li>Threaded comments (nested like Reddit)</li>
                <li>Like system with karma</li>
                <li>24-hour leaderboard</li>
              </ul>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Tech Stack</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Backend: Django + DRF</li>
                <li>Frontend: React + Tailwind</li>
                <li>Database: SQLite</li>
              </ul>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-amber-800 mb-2">Deployment</h3>
            <p className="text-sm text-amber-700">
              <strong>Backend:</strong> Deploy to Railway or Render<br />
              <strong>Frontend:</strong> Deploy to Vercel (set VITE_API_URL env var)
            </p>
          </div>

          <div className="border-t pt-6">
            <h3 className="font-semibold text-gray-900 mb-3">Project Files</h3>
            <div className="grid gap-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="bg-gray-200 px-2 py-1 rounded font-mono">backend/</span>
                <span className="text-gray-600">Django REST API</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="bg-gray-200 px-2 py-1 rounded font-mono">frontend/</span>
                <span className="text-gray-600">React + Vite app</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="bg-gray-200 px-2 py-1 rounded font-mono">README.md</span>
                <span className="text-gray-600">Setup instructions</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="bg-gray-200 px-2 py-1 rounded font-mono">EXPLAINER.md</span>
                <span className="text-gray-600">Technical documentation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
