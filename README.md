# Community Feed

A community feed prototype with threaded discussions and a dynamic leaderboard built with Django REST Framework and React.

## Features

- **Feed**: Display text posts with author and like count
- **Threaded Comments**: Nested comment replies (like Reddit)
- **Gamification**: 
  - 1 Like on a Post = 5 Karma
  - 1 Like on a Comment = 1 Karma
- **Leaderboard**: Top 5 users by karma earned in the last 24 hours

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Database**: SQLite (can switch to PostgreSQL)

## Project Structure

```
├── backend/           # Django backend
│   ├── core/          # Django project settings
│   ├── feed/          # Main app (models, views, serializers)
│   └── manage.py
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## Running Locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Seed demo data (optional)
python manage.py seed_data

# Start the server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List all posts |
| POST | `/api/posts/` | Create a new post |
| GET | `/api/posts/{id}/` | Get post with comments |
| POST | `/api/posts/{id}/like/` | Like a post |
| POST | `/api/posts/{id}/unlike/` | Unlike a post |
| POST | `/api/comments/` | Create a comment |
| POST | `/api/comments/{id}/like/` | Like a comment |
| POST | `/api/comments/{id}/unlike/` | Unlike a comment |
| GET | `/api/leaderboard/` | Get top 5 users (24h karma) |

## Running Tests

```bash
cd backend
python manage.py test feed
```

## Deployment

### Backend (Railway)

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables:
   - `DJANGO_SECRET_KEY`: Your secret key
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: Your railway domain
4. Railway will auto-detect Django and deploy

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Set root directory to `frontend`
4. Set environment variable:
   - `VITE_API_URL`: Your backend URL (`https://my-app.railway.app/api`)
5. Deploy

## License

MIT
