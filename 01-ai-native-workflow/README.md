# Shared Household Chores

A tiny Django app for a family to coordinate chores. Mark chores done, see what's due per person, manage people in-app. No accounts — pick who you are on first visit, remembered via session.

## Stack
- Python 3.13
- Django 6.1
- SQLite (default)
- HTML templates (Django, no JS framework)
- uv (dependency management)

## Features
- Chore list with assignee (any number of people)
- "Mark done" button; no history beyond `last_done_at`
- Recurring chores: auto-reset N days after completion (e.g. every 3 days, weekly)
- One-shot chores: stay done forever after first completion
- View modes: list (cards) or kanban board (one column per person)
- Per-chore "Delete" + bulk "Delete completed"
- In-app Person CRUD (add / remove people freely)
- "Hide completed" toggle, session-stored
- Identity picker (`/who-am-i/`) with a "Switch" button in the header

## Project layout
- `household/` — Django project (settings, urls, wsgi)
- `chores/` — Django app (models, views, forms, admin, tests, templates)
- `_docs/` — design doc (`plan.md`) and implementation backlog (`backlog.md`)

## Run

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                # install deps into .venv
uv run python manage.py migrate        # apply migrations
uv run python manage.py runserver      # dev server (URL printed on startup)
```

## Test

```bash
uv run python manage.py test chores    # 33 tests, ~0.1s
```

## First-time flow

1. Run `uv run python manage.py runserver` and open the URL it prints — you'll be redirected to `/who-am-i/`.
2. No people yet → redirected to `/people/new/` — add your first person.
3. Add more people via `/people/`.
4. Pick yourself at `/who-am-i/` → land on the chore list.
5. Use `+ Add chore` to create your first chore (assignee defaults to you).
6. Toggle view via `[List] · [Board]` in the toolbar.

## Scope (out)

Accounts / auth, points / leaderboards, notifications, comments, activity history, multi-tenant, mobile app. See `_docs/plan.md` §"Cut".

## Status

Feature-complete MVP. All 17 backlog tasks landed plus post-backlog polish (recurring due labels, board view, in-app Person CRUD, test coverage). See `_docs/backlog.md` for the task history.
