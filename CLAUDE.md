# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebDrone is a Django 5.1 web application for drone management — tracking articles/news, components, configurations, and flights. The UI and codebase (model fields, comments, templates) are in French. Production host: `drone.argawaen.net`.

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

Dependencies are declared in `requirements.txt`: `django>=5.1,<5.2`, `django-markdownx`, `markdown`, `Pillow`, `mysqlclient`, `gunicorn`, `whitenoise`.

That Django pin is what caps the Python version in the `Dockerfile`: 5.1 supports 3.10 to 3.13, so the base image stays on `python:3.13-slim` until Django moves.

There is no linting, formatting, or CI/CD configuration.

## Docker Setup

The project is containerised with Docker Compose. Configuration is in `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `nginx.conf`, `gunicorn.conf.py`, `entrypoint.sh`, and `deploy.sh`.

Two services, each with `restart: unless-stopped` and its own healthcheck, so Docker supervises both processes independently:

- **`web`** — built from `Dockerfile` (`python:3.13-slim` + MySQL client libraries for `import_from_mysql`). Entrypoint runs `migrate` and `collectstatic`, then execs gunicorn on `0.0.0.0:8000`. Not published to the host; reachable only on the compose network. Healthcheck: TCP connect to port 8000.
- **`nginx`** — official `nginx:1.30.4-alpine` (the stable branch, pinned to the patch), publishes `${PORT:-8180}:80`, serves `/static/` and `/media/` directly and reverse-proxies the rest to `web:8000`. Waits on `web` via `depends_on: condition: service_healthy`. Healthcheck: `GET /healthz`, an nginx-level `return 200` that touches neither gunicorn nor Django.
- **Volumes** (configurable via `.env`, all bind mounts relative to the project directory):
  - `${PATH_DATABASE:-./docker_data/db/}` → `/app/db/` (SQLite database, `web` only)
  - `${PATH_MEDIA:-./docker_data/media/}` → `/app/data/media/` (uploaded files; rw on `web`, ro on `nginx`)
  - `${PATH_STATIC:-./docker_data/static/}` → `/app/staticfiles/` (`collectstatic` output; rw on `web`, ro on `nginx`)
- **Environment**: All secrets and settings read from `.env` (see `.env.sample` for the template).

`nginx.conf` proxies via a variable (`set $upstream` + `resolver 127.0.0.11`) rather than a literal upstream name, so nginx re-resolves `web` per request instead of pinning its IP at startup — without this, recreating `web` leaves nginx serving 502s.

`.dockerignore` exists for one reason above the others: the `Dockerfile` ends on `COPY . .`, and `docker_data/` is the runtime state — the SQLite database plus 300+ MB of uploaded media. Without the exclusion every build bakes a snapshot of production into the image, which the bind mount then shadows at run time. `.env` is excluded on the same principle: the container receives the secrets through `env_file`, so a copy inside the image is only a copy that leaks with it.

### Deployment: `deploy.sh`

`deploy.sh` at the repository root is the all-in-one entry point, modelled on the one in
`WebServer` (its user-facing text is in English, unlike the rest of the project). It
checks the tooling and `.env`, pre-creates the three bind-mounted directories with the
right owner, updates the repository, refreshes the images, builds, starts, and waits for
`web` then `nginx` to report healthy.

```bash
./deploy.sh                 # déploiement complet : pull + build + up + attente
./deploy.sh --no-pull       # ne rien récupérer : ni le dépôt, ni les images
                            #   (obligatoire si l'arbre est sale)
./deploy.sh --tests         # lance la suite de tests avant de démarrer
./deploy.sh --dry-run       # affiche le plan sans rien exécuter
./deploy.sh check           # vérifie seulement s'il y a une mise à jour, ne change rien
./deploy.sh status | logs | stop | restart
./deploy.sh tests [app]     # tests dans un conteneur jetable
./deploy.sh superuser       # créer un admin
./deploy.sh shell           # shell Django
```

`./deploy.sh check` (alias `--check`) ne fait qu'un `git fetch` et compare à l'upstream :
il ne construit rien, ne démarre rien, et n'écrit que les refs de suivi. Ses codes de
retour sont faits pour être scriptés (cron, supervision) : **0** à jour, **10** mise à
jour en attente, **1** impossible de conclure (pas un dépôt, pas d'upstream, fetch
échoué).

`prepare_directories()` crée `db/`, `media/` et `static/` avant le premier `up`, parce que
Docker crée lui-même une source de bind mount manquante — en root, et le propriétaire ne
peut alors plus ni nettoyer ni sauvegarder ce qu'il y a dedans.

`pull_images()` existe parce qu'un tag épinglé ne bouge jamais tout seul : sans lui,
`nginx:1.30.4-alpine` reste sur l'image tirée au premier déploiement, donc les
reconstructions de ce même tag — là où arrivent les correctifs alpine — n'atterrissent
jamais. Il rafraîchit les services venant d'un registre avec
`docker compose pull --ignore-buildable`, puis le `FROM` du `Dockerfile` séparément (un
service constructible est ignoré par cette commande, et une base périmée est tout aussi
mauvaise), en lisant le tag dans le `Dockerfile` plutôt qu'en le répétant. Un registre
injoignable est un **avertissement, pas une erreur** : les images déjà sur le disque
suffisent à déployer, et abandonner laisserait la mise à jour à moitié faite.

Migrations et `collectstatic` sont lancés par `entrypoint.sh` au démarrage du conteneur
`web` : ni `deploy.sh` ni toi n'avez à les rejouer à la main.

**La forme sans argument est un contrat.** La console de la flotte (`WebServer`, page
Stacks) propose un bouton « Mettre à jour » par stack, et ce qu'elle actionne est ce
fichier : `homelab-probe` déclare un stack déployable quand un `deploy.sh` posé à côté du
compose est exécutable **et suivi par git**, puis `homelab-wake-agent` le lance sans
argument, sans TTY, stdin sur `/dev/null`, en tant que propriétaire du checkout. D'où
trois contraintes à préserver : les arguments ne font qu'ajouter à ce que fait l'appel nu,
les couleurs se coupent quand stdout n'est pas un terminal, et rien ici ne lit stdin.

### Suivi des versions d'images (wud)

`wud` (What's Up Docker, sur `selene`) surveille tous les conteneurs du lab et répond à
« lesquels de mes tags épinglés sont en retard ? ». Sans contrainte il retient le tag « le
plus grand » du dépôt, ce qui produisait du bruit sur ce stack (il était nommément cité
comme tel dans `home-server-stacks/selene/monitoring/README.md`). Chaque service porte donc
son label :

- **`web`** → `wud.watch: 'false'`. Construite ici, l'image n'existe dans aucun registre :
  wud cherchait `library/webdrone-web:latest` sur Docker Hub et remontait un 401 à chaque
  scan. Ce que cette image suit réellement est le `FROM` du `Dockerfile`, que `deploy.sh`
  tire à chaque déploiement.
- **`nginx`** → `wud.tag.include: '^\d+\.\d*[02468]\.\d+-alpine$$'` + `wud.watch.digest: 'true'`.
  nginx numérote ses branches par parité : mineurs pairs (1.28, 1.30, 1.32) = stable,
  impairs (1.29, 1.31) = mainline. D'où `\d*[02468]` sur le mineur au lieu du `\d+` que la
  forme du tag suggérerait : 1.30.5 et la prochaine stable restent une nouvelle, 1.31.x
  devient du bruit. Le digest est un **second signal, pas le même** : le tag dit « un nginx
  plus récent existe » et demande un commit ici, le digest dit « ce tag-là a été
  reconstruit » (une CVE alpine, en général) et ne demande que le `pull` que `deploy.sh`
  fait déjà.

Deux pièges, tous deux silencieux :

- `$$` et non `$` — compose interpole la valeur, le conteneur doit recevoir un seul `$`.
  Vérifiable : `docker inspect webdrone-nginx-1 --format '{{index .Config.Labels "wud.tag.include"}}'`.
- une regex qui **exclut le tag en cours d'exécution** ne laisse rien à comparer à wud, qui
  répond alors « à jour » pour toujours. Vérifier les deux sens en la modifiant : bumper le
  tag de l'image, c'est bumper cette regex dans le même mouvement — et c'est précisément le
  moment où la question mérite d'être posée.

**Un label n'atteint wud qu'à la recréation du conteneur** : les labels sont figés à la
création, donc c'est `docker compose up -d` (ou `./deploy.sh`) qui les rend effectifs.

## Configuration & Secrets

All secrets and runtime settings are read from environment variables (`os.environ`) in `drone_project/settings.py`:

- `SECRET_KEY`, `DEBUG` (default `0`), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
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

Under Docker, static files are served by the `nginx` service straight from the shared `staticfiles/` volume — requests never reach Django. WhiteNoise is still in `MIDDLEWARE` and remains the fallback outside Docker (e.g. `runserver`). `collectstatic` gathers files into `staticfiles/` at `web` startup. Source assets are in `data/static/` (CSS and images for drone and profile apps).

## Notes

- This is a traditional server-rendered Django app — no REST API, no JS framework.
- The frontend uses Bootstrap 5.3.3 and Material Design Icons 7.4.47, all from CDN (no jQuery).
- Test coverage is minimal: a single test in `drone/tests.py` checks the index page returns HTTP 200.
- Language is `fr`, timezone is `Europe/Paris`.
