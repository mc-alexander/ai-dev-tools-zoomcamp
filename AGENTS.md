# AGENTS.md

Repo for the Datatalks "AI Dev Tools" zoomcamp. The workspace contains a single module — there is no monorepo tooling, CI, lint, formatter, or test config beyond Django defaults.

## Layout

- `01-ai-native-workflow/` — the only project. A Django chores app, managed with `uv`.
  - `household/` — Django project (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`).
  - `chores/` — Django app (`models.py`, `views.py`, `admin.py`, `tests.py`, `migrations/`).
  - `_docs/plan.md` — source-of-truth design doc (data model, pages, scope). Read before changing scope.
  - `manage.py`, `pyproject.toml`, `uv.lock`, `db.sqlite3` (gitignored), `.venv/` (gitignored).
- Root `README.md` is just a title; the real README is `01-ai-native-workflow/README.md`.

All `uv`/`python manage.py ...` commands must be run from `01-ai-native-workflow/`.

## Stack (exact versions)

- Python `>=3.13` (declared in `pyproject.toml`)
- Django `6.1.1` (declared in `uv.lock`) — patterns from Django 4.x/5.x may not apply; check current docs.
- SQLite only (default DB in `household/settings.py`).
- `uv` is the only supported dependency manager. Do not add `pip`/`poetry`/`pdm`/`pipenv` artifacts.

## Setup & run

```bash
cd 01-ai-native-workflow
uv sync                                   # installs deps into .venv
uv run python manage.py migrate
uv run python manage.py runserver
```

`uv run` is required for every `manage.py` invocation; the project lives in `.venv/`, not on the system Python.

## Current status: scaffolding

The project was just generated; **nothing has been implemented yet** beyond Django's defaults:

- `chores/models.py`, `views.py`, `admin.py`, `tests.py` are empty stubs.
- `chores/migrations/` contains only `__init__.py` — no migrations generated.
- `household/urls.py` only has `/admin/`; `chores.urls` is not wired in.
- 3 seed `Person` rows (mom / sister / me) need to be created.

Follow `_docs/plan.md` when implementing. After defining models, the first command is `uv run python manage.py makemigrations chores` (not just `migrate`).

## Conventions / non-defaults worth knowing

- `DEBUG = True`, `ALLOWED_HOSTS = []`, hard-coded `SECRET_KEY` — all dev defaults from `django-admin startproject`. Don't "fix" these for production here; the project explicitly out-of-scope accounts/auth/prod deploy (see plan §"Cut").
- No login system: identity is a "pick who you are" page stored in the Django session (`/who-am-i` per plan).
- No test/lint/typecheck tooling configured. If you add it, keep it inside `01-ai-native-workflow/` (it has its own `pyproject.toml`); do not create repo-root config that implies cross-module coordination.
- `db.sqlite3` is gitignored but already present locally — fine to delete and re-migrate.

## Out of scope (do not implement unless asked)

Accounts/auth, points, leaderboards, notifications, comments, activity history, multi-tenant, mobile app. See `_docs/plan.md` §"Cut".
