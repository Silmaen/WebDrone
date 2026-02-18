# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebDrone is a Django 3.1 web application for drone management — tracking articles/news, components, configurations, and flights. The UI and codebase (model fields, comments, templates) are in French. Production host: `drone.argawaen.net`.

## Development Commands

```bash
# Docker (production-like)
docker compose up --build            # Build and start
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py import_from_mysql  # Import data from MySQL source

# Local development
python manage.py runserver
python manage.py test
python manage.py test drone
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py import_from_mysql   # Requires MYSQL_* env vars
```

Dependencies are declared in `requirements.txt`: `django>=3.1,<4`, `django-markdownx`, `markdown`, `Pillow`, `mysqlclient`, `gunicorn`, `whitenoise`.

There is no linting, formatting, or CI/CD configuration.

## Docker Setup

The project is containerised with Docker Compose. Configuration is in `Dockerfile`, `docker-compose.yml`, and `entrypoint.sh`.

- **Image**: `python:3.9-slim` with MySQL client libraries (for `import_from_mysql`).
- **Entrypoint**: Runs `migrate` and `collectstatic` automatically before starting gunicorn on port 8000.
- **Volumes** (configurable via `.env`):
  - `${PATH_DATABASE:-./docker_data/db/}` → `/app/db/` (SQLite database)
  - `${PATH_MEDIA:-./docker_data/media/}` → `/app/data/media/` (uploaded files)
- **Environment**: All secrets and settings read from `.env` (see `.env.sample` for the template).

## Configuration & Secrets

All secrets and runtime settings are read from environment variables (`os.environ`) in `drone_project/settings.py`:

- `SECRET_KEY`, `DEBUG` (default `0`), `ALLOWED_HOSTS`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`
- `PORT`, `PATH_DATABASE`, `PATH_MEDIA` (Docker Compose only)
- `MYSQL_*` variables (used only by `import_from_mysql` command)

The `.env` file is git-ignored. Copy `.env.sample` and fill in real values.

## Architecture

### App Structure

- **`drone_project/`** — Django project settings and root URL configuration. Routes: `''` → `drone.urls`, `'profile/'` → `connector.urls`, `'admin/'` → Django admin, `'markdownx/'` → markdownx.
- **`common/`** — Shared base layer. Provides `SiteArticle` and `SiteArticleComment` base models, admin classes, and user group utilities (`user_is_validated`, `user_is_developper`, `user_is_moderator`).
- **`drone/`** — Primary domain app. Contains all drone-specific models, views, forms, templates, and the `import_from_mysql` management command.
- **`connector/`** — User authentication and profile management (registration, login, profile editing, password reset). Extends Django `User` with `UserProfile` (avatar, birthDate) via signals.
- **`data/`** — All templates (`data/templates/`), static assets (`data/static/`), and uploaded media (`data/media/`).

### Key Design Patterns

**Multi-table inheritance from `common`:** All drone entity models (`DroneArticle`, `DroneComponent`, `DroneConfiguration`, `DroneFlight`) inherit from `SiteArticle` (a concrete model in `common`), sharing its fields via OneToOne links. Each entity type has its own Comment subclass inheriting from `SiteArticleComment`.

**Proxy import modules:** `drone/base_models.py`, `drone/base_admin.py`, and `drone/user_utils.py` re-export from `common`. This exists to enable future extraction of the `drone` app as a standalone project.

**Article visibility:** `SiteArticle` has `private`, `superprivate`, `staff`, and `developper` boolean flags with cascading logic in `save()` — setting `superprivate` implies `private`, etc.

**Comment moderation:** Comments default to `active=False` and require approval, unless posted by a user in the "moderator" group.

**Markdown content:** All article and comment content uses `MarkdownxField`, rendered via `markdownify()` with `extra` and `codehilite` extensions.

**App-level settings:** Each app has its own `settings.py` defining a `base_info` dict that is spread into template context for per-app customization (favicon, title, etc.).

**Custom template tags** (`drone/templatetags/template_drone_extra.py`): `getunit` tag (spec name → unit symbol) and `has_group` filter (user group membership check).

### Template Hierarchy

`common/common_base.html` (Bootstrap 4.5.3 + MDI via CDN) → `drone/base.html` (drone navbar) → individual page templates. Registration templates extend `registration/base_registration.html`.

### Database

SQLite backend (`django.db.backends.sqlite3`), stored at `BASE_DIR / 'db' / 'db.sqlite3'`. In Docker, this directory is mounted as a volume for persistence. Data can be imported from the original MySQL source using `python manage.py import_from_mysql`.

### Static Files

Static files are served via WhiteNoise middleware in production. `collectstatic` gathers files into `staticfiles/` at container startup. Source assets are in `data/static/` (CSS and images for drone and profile apps).

## Notes

- This is a traditional server-rendered Django app — no REST API, no JS framework.
- The frontend uses Bootstrap 4.5.3, jQuery 3.5.1, and Material Design Icons 5.4.55, all from CDN.
- Test coverage is minimal: a single test in `drone/tests.py` checks the index page returns HTTP 200.
- Language is `fr`, timezone is `Europe/Paris`.
