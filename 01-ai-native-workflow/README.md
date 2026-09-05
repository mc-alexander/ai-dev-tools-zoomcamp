# Shared Household Chores

A small Django app for a family to coordinate chores. Pick who you are once, remembered via session — no accounts.

## Stack
- Python 3.13
- Django 6.1
- SQLite
- uv (dependency management)

## Features
- Chore list with assignee (any number of people)
- "Mark done" button; one-shots stay done forever, recurring chores auto-reset N days after completion
- List and kanban board views (one column per person)
- In-app Person CRUD
- Session-stored identity, view mode, and hide-completed preferences

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

1. Run the server, open the URL it prints → redirected to `/who-am-i/`.
2. No people yet → add your first via `/people/new/`, then pick yourself.
3. Create chores with `+ Add chore`; toggle `[List] · [Board]` for kanban view.

## Decisions and trade-offs

- **No seed data for people.** The original plan called for 3 fixed rows (mom/sister/me). Dropped the seed during the build in favor of in-app Person CRUD, so the app is empty on first run and any number of people can be added.
- **`on_delete=CASCADE` for `Chore.assigned_to`.** The original plan called for `PROTECT`. With in-app Person CRUD, deleting a user with active chores was a real UX problem, so we switched to `CASCADE` — deleting a person wipes their chores. Trade-off: chore history can be lost.
- **Session-stored view and hide-done preferences** instead of URL-only. Sticky across navigation, bookmark-friendly via `?view=board` / `?hide_done=1`.
- **Inline `<style>` in `base.html`** instead of separate CSS files. Single template, zero build step.
- **Manual time control in tests** (`timezone.now() - timedelta(...)`) instead of `freezegun`. Avoids a dep.
- **No auth.** Per the original plan's "Cut" list. Session-based identity only.

## Status

Feature-complete MVP. All 17 backlog tasks + post-backlog polish landed (33 tests). See `_docs/backlog.md` for the task history.
