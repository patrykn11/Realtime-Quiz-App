# Realtime Quiz App

A real-time quiz application. The project includes a Django/Channels backend, a React frontend, and PostgreSQL and Redis services managed with Docker Compose.

## Main Features

- create and join quiz rooms,
- real-time gameplay over WebSocket with Redis,
- user authentication,
- quiz history and score ranking,
- lobby view with room participants.

## Tech Stack

- Backend: Django, Django REST Framework, Channels
- Frontend: React, Vite
- Database: PostgreSQL
- Realtime/cache: Redis
- Environment: Docker Compose

## Backend Structure

The Django backend is split into small domain applications directly under
`backend`, next to the `config` package:

- `users` — registration, JWT endpoints, and WebSocket authentication,
- `quizzes` — quizzes, questions, and answer choices,
- `histories` — played-game history,
- `rooms` — lobby API, Redis service, and room consumer,
- `games` — gameplay service and game consumer,
- `common` — shared infrastructure such as Redis clients.

Project-wide settings, URL configuration, and ASGI/WSGI entry points live in
`backend/config`.

## Game Screenshots

<p>
  <img src="img/lobby_room.png" alt="Quiz room lobby">
  <img src="img/quiz_answer2.png" alt="Answering a quiz question 2">
  <img src="img/quiz_answer.png" alt="Answering a quiz question">
  <img src="img/quiz_result.png" alt="Quiz results">
</p>

## Getting Started

```bash
docker compose up --build
```

After startup, the application is available at:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

## Adding a Quiz

After a fresh clone, the database is empty. To add the sample quiz, run:

```bash
docker compose exec backend python manage.py seed_quiz
```

You can also create quizzes through the backend API:

```text
POST http://localhost:8000/api/create_quiz/
```

Stop the containers:

```bash
docker compose down
```

## Tests

```bash
docker compose run --rm --build test
```

## Authentication API

The authentication flow uses a custom `users.User` model and rotating JWTs:

- `POST /api/register/` — `username`, `email`, `password`, `password_confirm`,
- `POST /api/login/` — `username`, `password`,
- `POST /api/token/refresh/` — rotates a refresh token,
- `GET /api/me/` — returns the authenticated user,
- `POST /api/logout/` — blacklists the supplied refresh token.

When upgrading a database created before the custom user model was introduced,
preserve the existing `auth_user` table and mark the compatibility migration as
already represented by that table before starting the updated backend:

```bash
docker compose exec -T db psql -U postgres -d postgres -c \
  "INSERT INTO django_migrations (app, name, applied) SELECT 'users', '0001_initial', NOW() WHERE to_regclass('public.auth_user') IS NOT NULL AND NOT EXISTS (SELECT 1 FROM django_migrations WHERE app = 'users' AND name = '0001_initial');"
docker compose run --rm --entrypoint python backend manage.py migrate
```

The next migration preserves user IDs, assigns reserved placeholder addresses to
legacy accounts without e-mail, and then enforces unique e-mail addresses.
