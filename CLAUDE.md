# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create and apply a new migration after model changes
python manage.py makemigrations && python manage.py migrate

# Run all tests
python manage.py test

# Run tests for a single app
python manage.py test reviews
python manage.py test content
python manage.py test accounts

# Run a single test case
python manage.py test reviews.tests.MyTestCase

# Collect static files (production)
python manage.py collectstatic --noinput

# Create a superuser
python manage.py createsuperuser
```

## Environment

Copy `.env.example` to `.env` and fill in values. Key variables:

- `DATABASE_URL` — omit to use SQLite locally; set to a Postgres URL in production
- `TMDB_API_KEY` — required for film search (get one at developer.themoviedb.org)
- `INVITE_CODE` — gate for new registrations (default: `friends2025`)
- `SECRET_KEY` — must be set in production

## Architecture

### Apps

**`accounts`** — custom `User` model (extends `AbstractUser` with `bio` and `avatar`). Invite-code-gated registration: `InviteRegistrationForm` validates the code against `settings.INVITE_CODE`.

**`content`** — `Film` and `Book` models. These are the reviewable works. Films are sourced from TMDB; books from OpenLibrary. Both generate unique slugs on save. Views are all read-only (list + detail); content is created implicitly when a user selects a search result during review creation.

**`reviews`** — `Review`, `Comment`, and `Like` models. A `Review` belongs to exactly one `Film` **or** one `Book` (enforced by a `CheckConstraint`). One review per user per work (enforced by `UniqueConstraint`). Rating is 1–10 integers, rendered as half-star glyphs via `HALF_STARS` dict and `rating_display` property.

### Review creation flow

1. User hits `/reviews/new/` → picks film or book type
2. HTMX live-search calls `/reviews/search/films/` (TMDB) or `/reviews/search/books/` (OpenLibrary) and swaps in partial results
3. User selects a result → GET to `/reviews/select/film/` or `/reviews/select/book/` → creates the `Film`/`Book` if it doesn't exist, redirects to `/reviews/<work_type>/<slug>/`
4. User submits `ReviewForm` → `Review` saved with `author`, `film`/`book`, `rating`, `text`

### HTMX partials

HTMX is used for:
- Live search dropdowns during review creation (`reviews/partials/tmdb_results.html`, `reviews/partials/book_results.html`)
- Lazy-loading comments on detail pages (`reviews/partials/comments.html`)
- Like toggle (`reviews/partials/like_button.html`) — `POST` to `/reviews/<id>/like/`, returns updated button HTML

The `django-htmx` package is installed and its middleware runs; use `request.htmx` to detect HTMX requests if you need to differentiate responses.

### Templates

All templates extend `templates/base.html`. The base pulls Tailwind CSS and HTMX from CDN (no build step). Dark theme (`bg-gray-950`), brand green `#00b020`. Global templates live in `templates/`; app templates live in `templates/<app>/`. Partials are in `templates/reviews/partials/`.

`film_detail.html` and `book_detail.html` both extend `templates/content/work_detail.html` (shared detail layout).

### Database

SQLite locally, Postgres on Railway (via `DATABASE_URL`). Railway's `startCommand` runs `migrate` before gunicorn on every deploy.

### Static files

WhiteNoise serves static files in production (`CompressedManifestStaticFilesStorage`). No CDN; files collected to `staticfiles/`.

### Auth

All views require login (`@login_required`). `LOGIN_URL = /accounts/login/`. The custom `User` model is set via `AUTH_USER_MODEL = "accounts.User"`.
