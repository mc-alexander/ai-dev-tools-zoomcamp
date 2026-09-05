# AGENTS.md

Repo for the Datatalks "AI Dev Tools" zoomcamp. Single Django module, no monorepo tooling / CI / lint / formatter beyond Django defaults. Tests run via Django's built-in test runner.

## Layout

- `01-ai-native-workflow/` — the only project. A Django chores app, managed with `uv`.
  - `household/` — Django project (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`).
  - `chores/` — Django app (`models.py`, `views.py`, `forms.py`, `admin.py`, `tests.py`, `migrations/`, `templates/`).
  - `_docs/plan.md` — original design brainstorm. Largely historical.
  - `_docs/backlog.md` — implementation backlog with status checkboxes.
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
uv run python manage.py migrate            # applies migrations
uv run python manage.py runserver         # dev server (URL printed on startup)
uv run python manage.py test chores       # runs the 33-test suite
```

`uv run` is required for every `manage.py` invocation; the project lives in `.venv/`, not on the system Python.

## Status: feature-complete MVP

All 17 backlog tasks + post-backlog polish landed (due_label, board state pill fix, stale-session fix, test coverage). Not production-ready — see "Conventions" for dev-only defaults.

### Models (`chores/models.py`)
- `Person` — name.
- `Chore` — title, `assigned_to` (FK → Person, `on_delete=CASCADE`), `interval_days` (null = one-shot), `last_done_at`.
- `Chore.is_due` (property) — recurrence logic.
- `Chore.due_label` (property) — "Due tomorrow" / "1 day overdue" / "Due in N days" etc.

### Views (`chores/views.py`)
- `chore_list` — list view; `?view=list|board` and `?hide_done=0|1` toggles (session-stored); picks `chore_list.html` or `chore_list_board.html`.
- `who_am_i` — identity picker; redirects to `/people/new/` if no people exist.
- `mark_done` — POST-only; sets `last_done_at`.
- `chore_delete`, `chores_delete_completed` — single + bulk delete.
- `chore_create` — in-app chore form; assignee defaults to current user.
- `people_list`, `people_create`, `person_delete` — Person CRUD.
- All mutating endpoints require POST (`@require_POST` / `@require_http_methods(["GET", "POST"])`).

### Templates
- `chores/templates/chores/`: `base.html` (shared layout + inline minimalist CSS), `chore_list.html` (cards), `chore_list_board.html` (kanban), plus form pages.
- State pill colors: DUE = amber `#fef3c7`, DONE = teal `var(--accent)`.
- Recurring chores in board view show context-aware "due in N days" / overdue label.

### Tests (`chores/tests.py`)
- 33 tests across 9 classes: model logic (`is_due`, `due_label`), view redirects/session, mutations (mark_done / delete / bulk / cascade), feature toggles, form validation.
- Run with `uv run python manage.py test chores`.
- Time control is manual (`timezone.now() - timedelta(...)`) — no freezegun.

## Conventions / non-defaults worth knowing

- `DEBUG = True`, `ALLOWED_HOSTS = []`, hard-coded `SECRET_KEY` — all dev defaults. Don't "fix" for production; project explicitly out-of-scope (see `_docs/plan.md` §"Cut").
- No login system: identity via "pick who you are" page stored in the Django session. People are user-managed (in-app CRUD); no seed.
- `Chore.assigned_to` uses `on_delete=CASCADE`. Deleting a Person deletes all their Chores (deliberate change from original `PROTECT` plan, see backlog Task 14).
- Stale sessions (when the logged-in Person was deleted) redirect to `/who-am-i/` and clear the session — see `chore_list` / `chore_create` views.
- `db.sqlite3` is gitignored. Safe to delete and re-migrate; only `0001_initial` runs after the seed migration was dropped.
- Tests live in `chores/tests.py`. Django `TestCase` only — no pytest config, no conftest.

## Out of scope (do not implement unless asked)

Accounts/auth, points, leaderboards, notifications, comments, activity history, multi-tenant, mobile app. See `_docs/plan.md` §"Cut".
