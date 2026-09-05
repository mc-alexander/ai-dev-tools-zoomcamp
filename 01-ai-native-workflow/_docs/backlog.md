# Backlog — Household Chores (Django)

Source: `_docs/plan.md`. One task = one commit-sized unit. Tests deferred until after manual smoke test.

> **Status:** 16 / 17 complete (Tasks 1–7, 9–17). Task 8 (manual smoke test) pending.
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

- [x] **Task 3 — Seed the 3 People via a data migration**
  - Create a `RunPython` data migration (e.g. `chores/migrations/0002_seed_people.py`) that uses `Person.objects.get_or_create(name=...)` for `"mom"`, `"sister"`, `"me"`. Runs as part of the standard `uv run python manage.py migrate` step — no extra command needed by future contributors.

- [x] **Task 4 — Wire URLs**
  - New `chores/urls.py` with `/`, `/who-am-i`, `/chore/<int:chore_id>/done`.
  - `household/urls.py`: add `path("", include("chores.urls"))`.

- [x] **Task 5 — Implement views** (`chores/views.py`)
  - `chore_list` (GET `/`) — list chores with due-state (`last_done_at IS NULL OR last_done_at + interval_days <= now()`); render "Mark done" form per chore. If session has no `person_id` → redirect `/who-am-i`. Honor `?hide_done=1` / `?hide_done=0` toggle (session-stored).
  - `who_am_i` (GET `/who-am-i`, POST sets session) — render 3 People; POST stores `person_id`, redirects `/`.
  - `mark_done` (POST `/chore/<int:chore_id>/done`) — sets `last_done_at = now()`, redirects `/`.

- [x] **Task 6 — Templates** (`chores/templates/chores/`)
  - `base.html` — shared layout.
  - `chore_list.html` — title, assignee, due-state, "Mark done" button per row; completed rows rendered `<s>…</s>`; toggle link "Hide completed" / "Show completed" in the header. `{% csrf_token %}` on each POST form.
  - `who_am_i.html` — radio buttons for the 3 People + submit.

- [x] **Task 7 — Register admin** (`chores/admin.py`)
  - Register `Person` and `Chore` so they can be created/edited at `/admin/`.

- [ ] **Task 8 — Manual smoke test**
  - For each of the 3 people (use 3 browser profiles / private windows for session isolation): pick self at `/who-am-i`; mark a one-shot chore done (verify it becomes struck-through, and verify "Hide completed" hides it); mark a recurring chore done (verify it's struck-through but reappears after `interval_days` elapses — use Django admin or `manage.py shell` to back-date `last_done_at` to simulate).

- [x] **Task 9 — In-app chore creation**
  - `ChoreForm` (`chores/forms.py`): `ModelForm` with `title`, `assigned_to`, `interval_days`. Excludes `last_done_at` (auto-set by `mark_done`).
  - `chore_create` view (GET/POST `/chore/new/`): requires session identity; on GET, pre-fills `assigned_to` with current person; on POST, validates and saves; redirects to `/`. Errors re-render the form with messages.
  - URL: `path("chore/new/", views.chore_create, name="chore_create")` in `chores/urls.py`.
  - Template `chores/templates/chores/chore_create.html`: extends base; vertical stacked form, teal submit, secondary cancel link back to `/`.
  - `chore_list.html`: add "+ Add chore" link in the toolbar; empty state gains a primary CTA to the same URL.

- [x] **Task 10 — Visual polish (minimalist redesign)**
  - `base.html`: replace inline `<style>` with a teal (`#0d9488`) minimalist palette — light gray background, white surface cards with subtle border + 8px radius, system font stack, focus rings in teal.
  - `chore_list.html`: card-based layout (`<ul class="chore-list">` of `<li class="chore">` cards) instead of `<table>`. Each card shows title (struck-through when completed), assignee, "DUE"/"DONE" state pill, inline `.btn.secondary` "Mark done" form.
  - `who_am_i.html`: wrap radio list in `form.stack` with teal "Continue" button.
  - `chore_create.html` (from Task 9): styled with `form.stack`.

- [x] **Task 11 — Switch user ghost button**
  - `base.html`: add `.header-extra { display: flex; gap: 0.75rem; align-items: center; }`.
  - `chore_list.html`: wrap greeting and `Switch` `.btn.secondary` in `<div class="header-extra">`.

- [x] **Task 12 — Person CRUD + drop the seed**
  - Delete `chores/migrations/0002_seed_people.py` and `db.sqlite3`; re-run `migrate` (only `0001_initial` runs). New clones start with an empty `Person` table.
  - `PersonForm` (in `chores/forms.py`): `ModelForm` for `Person.name` only.
  - `people_list` view (GET `/people/`): list all people; per-row "Delete" POST form; "Add person" link; error banner when deletion fails due to `ProtectedError`.
  - `people_create` view (GET/POST `/people/new/`): `PersonForm`; redirect to `/people/` on success.
  - `person_delete` view (POST `/people/<int:person_id>/delete/`): catches `ProtectedError` (from `Chore.assigned_to on_delete=PROTECT`) and re-renders the list with an error message instead of a 500.
  - URLs: `people_list`, `people_create`, `person_delete` in `chores/urls.py`.
  - Templates: `people_list.html`, `people_create.html` extending base with the existing card / form patterns.
  - Empty-state handling: `who_am_i` and `chore_create` show a banner pointing to `/people/new/` when no people exist.
  - `chore_list.html`: add a small "People" link in the toolbar.

- [x] **Task 13 — Chore deletion**
  - `chore_delete` view (POST `/chore/<int:chore_id>/delete/`): single-click delete; redirects to `/` with success message via Django messages.
  - `chores_delete_completed` view (POST `/chores/delete-completed/`): bulk-delete `Chore.objects.filter(last_done_at__isnull=False)`; success message shows count.
  - URLs: `chore_delete`, `chores_delete_completed` in `chores/urls.py`.
  - `chore_list.html`: per-row "Delete" button (paired with "Mark done" in an `.actions` flex container); toolbar gains "Delete N completed" button shown only when `completed_count > 0`.
  - `base.html`: add `.btn.danger` (white bg, red text/border, hover red wash) and `.actions { display: flex; gap: 0.375rem; }`.

- [x] **Task 14 — User deletion: CASCADE**
  - `chores/models.py`: change `Chore.assigned_to` `on_delete=PROTECT` → `on_delete=CASCADE`.
  - New migration via `makemigrations` (auto-named `0002_alter_chore_assigned_to.py`).
  - `chores/views.py`: simplify `person_delete` — drop `ProtectedError` handling; success message becomes "Deleted {name} and all their chores."
  - DB reset (`db.sqlite3`) + `migrate` to confirm clean state on the empty table.

- [x] **Task 15 — View toggle (list vs board)**
  - `chore_list` view: read `?view=` from query (accepts `"list"`/`"board"`), persist to `request.session["view"]`, default `"list"`. Pass `view` to context.
  - `chore_list.html` toolbar: `[List] · [Board]` links with the active view in bold.
  - `base.html`: `.toolbar a.active { font-weight: 600; color: var(--text); }`.

- [x] **Task 16 — Kanban board template**
  - New `chores/templates/chores/chore_list_board.html`: CSS Grid, one column per Person, with the person's chores stacked as compact cards. Empty columns render "No chores".
  - Reuses `.chore-card` styling; each card shows title, optional recurrence, state pill, Mark done + Delete buttons.
  - `chore_list` view: prefetch `Person.objects.prefetch_related("chores")`; pass `people` to context; pick template by `view` (`board` → `chore_list_board.html`, else `chore_list.html`).
  - `base.html`: `.kanban`, `.column`, `.board-card` CSS — column width via inline `grid-template-columns: repeat({{ people|length }}, minmax(0, 1fr))`.

- [x] **Task 17 — Color coding (DUE/DONE swap)**
  - `base.html` CSS swap:
    - `.chore .state` (DONE) → teal background `var(--accent)`, white text.
    - `.chore .state.due` → amber background `#fef3c7`, amber text `#92400e`.
