# Shared Household Chores

A tiny Django app to coordinate chores between mom, sister, and me.

## Stack
- Python 3.13
- Django 6.1
- SQLite (default)
- HTML templates (Django)
- uv (dependency management)

## Project layout
- `household/` — Django project (settings, urls, wsgi)
- `chores/` — Django app (models, views, templates)

## Scope (in)
- Chore list, each assigned to one of 3 people
- "Mark done" button (no history kept)
- Recurring chores: reset automatically after completion (e.g. every 3 days, weekly)
- No login: on first visit, pick who you are; remembered via cookie/session

## Scope (out)
- Accounts, passwords, auth
- Points, leaderboards, rewards
- Notifications / email / push
- Comments or activity history

## Run
Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                  # install deps into .venv
uv run python manage.py migrate
uv run python manage.py runserver
```

## Status
Scaffolding complete. Models, views, templates not yet implemented —
see [_docs/plan.md](_docs/plan.md).
