# Plan — Shared Household Chores (Django)

## Brainstorm log

1. **Who is it for?** Family of 3: mom, sister, me.
2. **Where does it run?** Django web app (single backend, browser-based).
3. **Core features?** Keep it simple:
   - Chore list with assignee (one of 3 people).
   - "Mark done" button; no history kept.
   - Recurring chores that auto-reset after completion
     (intervals like every N days, or weekly).
   - No accounts — pick "who you are" once, remembered in session.
4. **Cut (out of scope):** points, leaderboards, notifications,
   comments, activity history, multi-tenant, mobile app.

## Data model (draft)
- `Person` — name (3 fixed rows seeded: mom, sister, me).
- `Chore` — title, assigned_to (FK->Person), interval_days (nullable,
  null = one-shot), last_done_at (nullable).

## Pages / views (draft)
- `GET /` — chore list, "Mark done" button per chore.
- `GET /who-am-i` — pick your person (stored in session).
- `POST /chore/<id>/done` — marks done, sets `last_done_at = now`.

## Next steps after this plan
1. Scaffold Django project + app.
2. Models + migrations + seed 3 people.
3. Templates + views.
4. Manual test with all 3 users.
