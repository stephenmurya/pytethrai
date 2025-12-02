# TethrAI - Vue + Django + SQLite

A modern AI chat application built with Vue.js, Django, and SQLite.

## Stack

- **Frontend**: Vue 3 + TypeScript + Vite + Tailwind CSS v4
- **Backend**: Django 5 + Django REST Framework + SQLite
- **AI**: OpenRouter API
- **Deployment**: Docker + Nginx

## Quick Start (Docker)

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd tethrai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.docker.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - Django Admin: http://localhost/admin (after creating superuser)

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Features

- ✅ User authentication (Register, Login, Logout)
- ✅ Chat with AI (OpenRouter integration)
- ✅ Chat history
- ✅ Session-based authentication
- ✅ SQLite database
- ✅ Docker deployment

## API Endpoints

- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/register/` - Register
- `GET /api/auth/me/` - Get current user
- `POST /api/chat/send/` - Send message
- `GET /api/chat/history/` - Get chat history
- `GET /api/chat/<uuid>/` - Get specific chat

## Environment Variables

Create a `.env` file in the project root with:

```
OPENROUTER_API_KEY=your_openrouter_api_key
DJANGO_SECRET_KEY=your_django_secret_key
```

## License

MIT
