# Backlog — Household Chores (Django)

Source: `_docs/plan.md`. One task = one commit-sized unit. Tests deferred until after manual smoke test.

> **Status:** 2 / 8 complete (Tasks 1, 2).
> Commit convention: `Task N: <description>`.

## Decisions

- Seed mechanism: **data migration** (auto-runs with `migrate`, idempotent via `get_or_create`, version-controlled with the schema).
- Completed one-shot chores: rendered struck-through; chore-list page has a **"Hide completed" / "Show completed"** toggle, persisted in session (matches the "who-am-i" identity-in-session pattern).
- Tests: deferred (no task for them yet).

## Tasks (in order)

- [x] **Task 1 — Define models** (`chores/models.py`)
  - `Person` — `name` (CharField).
  - `Chore` — `title` (CharField); `assigned_to` (FK → `Person`, `on_delete=PROTECT`, `related_name="chores"`); `interval_days` (PositiveIntegerField, `null=True`, `blank=True` — null = one-shot); `last_done_at` (DateTimeField, `null=True`, `blank=True`).
  - `__str__` on both.

- [x] **Task 2 — Generate the schema migration**
  - Run from `01-ai-native-workflow/`:
    ```
    uv run python manage.py makemigrations chores
    ```
  - Produces `chores/migrations/0001_initial.py`. `migrate` deferred to Task 3.

- [ ] **Task 3 — Seed the 3 People via a data migration**
  - Create a `RunPython` data migration (e.g. `chores/migrations/0002_seed_people.py`) that uses `Person.objects.get_or_create(name=...)` for `"mom"`, `"sister"`, `"me"`. Runs as part of the standard `uv run python manage.py migrate` step — no extra command needed by future contributors.

- [ ] **Task 4 — Wire URLs**
  - New `chores/urls.py` with `/`, `/who-am-i`, `/chore/<int:chore_id>/done`.
  - `household/urls.py`: add `path("", include("chores.urls"))`.

- [ ] **Task 5 — Implement views** (`chores/views.py`)
  - `chore_list` (GET `/`) — list chores with due-state (`last_done_at IS NULL OR last_done_at + interval_days <= now()`); render "Mark done" form per chore. If session has no `person_id` → redirect `/who-am-i`. Honor `?hide_done=1` / `?hide_done=0` toggle (session-stored).
  - `who_am_i` (GET `/who-am-i`, POST sets session) — render 3 People; POST stores `person_id`, redirects `/`.
  - `mark_done` (POST `/chore/<int:chore_id>/done`) — sets `last_done_at = now()`, redirects `/`.

- [ ] **Task 6 — Templates** (`chores/templates/chores/`)
  - `base.html` — shared layout.
  - `chore_list.html` — title, assignee, due-state, "Mark done" button per row; completed rows rendered `<s>…</s>`; toggle link "Hide completed" / "Show completed" in the header. `{% csrf_token %}` on each POST form.
  - `who_am_i.html` — radio buttons for the 3 People + submit.

- [ ] **Task 7 — Register admin** (`chores/admin.py`)
  - Register `Person` and `Chore` so they can be created/edited at `/admin/`.

- [ ] **Task 8 — Manual smoke test**
  - For each of the 3 people (use 3 browser profiles / private windows for session isolation): pick self at `/who-am-i`; mark a one-shot chore done (verify it becomes struck-through, and verify "Hide completed" hides it); mark a recurring chore done (verify it's struck-through but reappears after `interval_days` elapses — use Django admin or `manage.py shell` to back-date `last_done_at` to simulate).
