from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ChoreForm
from .models import Chore, Person


class PersonModelTests(TestCase):
    def test_str_returns_name(self):
        p = Person.objects.create(name="mom")
        self.assertEqual(str(p), "mom")

    def test_ordering_by_name(self):
        Person.objects.create(name="sister")
        Person.objects.create(name="mom")
        Person.objects.create(name="me")
        self.assertEqual(
            list(Person.objects.values_list("name", flat=True)),
            ["me", "mom", "sister"],
        )

    def test_verbose_name_plural_is_people(self):
        self.assertEqual(str(Person._meta.verbose_name_plural), "people")


class ChoreModelTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")

    def test_str_returns_title(self):
        c = Chore.objects.create(title="Wash dishes", assigned_to=self.mom)
        self.assertEqual(str(c), "Wash dishes")

    def test_is_due_one_shot_never_done_is_true(self):
        c = Chore.objects.create(title="x", assigned_to=self.mom)
        self.assertTrue(c.is_due)

    def test_is_due_one_shot_done_is_false(self):
        c = Chore.objects.create(
            title="x", assigned_to=self.mom, last_done_at=timezone.now()
        )
        self.assertFalse(c.is_due)

    def test_is_due_recurring_within_interval_is_false(self):
        c = Chore.objects.create(
            title="x",
            assigned_to=self.mom,
            interval_days=3,
            last_done_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(c.is_due)

    def test_is_due_recurring_past_interval_is_true(self):
        c = Chore.objects.create(
            title="x",
            assigned_to=self.mom,
            interval_days=3,
            last_done_at=timezone.now() - timedelta(days=5),
        )
        self.assertTrue(c.is_due)

    def test_due_label_one_shot_returns_empty_string(self):
        c = Chore.objects.create(title="x", assigned_to=self.mom)
        self.assertEqual(c.due_label, "")

    def test_due_label_recurring_never_done(self):
        c = Chore.objects.create(title="x", assigned_to=self.mom, interval_days=3)
        self.assertEqual(c.due_label, "Due now")

    def test_due_label_recurring_due_today(self):
        c = Chore.objects.create(
            title="x",
            assigned_to=self.mom,
            interval_days=3,
            last_done_at=timezone.now() - timedelta(days=2),
        )
        self.assertEqual(c.due_label, "Due today")

    def test_due_label_recurring_one_day_overdue(self):
        c = Chore.objects.create(
            title="x",
            assigned_to=self.mom,
            interval_days=3,
            last_done_at=timezone.now() - timedelta(days=4),
        )
        self.assertEqual(c.due_label, "1 day overdue")

    def test_due_label_recurring_n_days_overdue(self):
        c = Chore.objects.create(
            title="x",
            assigned_to=self.mom,
            interval_days=3,
            last_done_at=timezone.now() - timedelta(days=5),
        )
        self.assertEqual(c.due_label, "2 days overdue")


class WhoAmIViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")
        self.sister = Person.objects.create(name="sister")

    def test_redirects_to_people_create_when_no_people(self):
        Person.objects.all().delete()
        resp = self.client.get(reverse("chores:who_am_i"))
        self.assertRedirects(resp, reverse("chores:people_create"))

    def test_get_renders_picker(self):
        resp = self.client.get(reverse("chores:who_am_i"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "mom")
        self.assertContains(resp, "sister")

    def test_post_valid_person_sets_session_and_redirects(self):
        resp = self.client.post(
            reverse("chores:who_am_i"), {"person_id": self.mom.pk}
        )
        self.assertRedirects(resp, reverse("chores:index"))
        self.assertEqual(self.client.session.get("person_id"), self.mom.pk)

    def test_post_invalid_person_rerenders(self):
        resp = self.client.post(reverse("chores:who_am_i"), {"person_id": 9999})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("person_id", self.client.session)


class ChoreListViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")
        self.sister = Person.objects.create(name="sister")

    def _login_as(self, person):
        session = self.client.session
        session["person_id"] = person.pk
        session.save()

    def test_redirects_when_no_session(self):
        resp = self.client.get(reverse("chores:index"))
        self.assertRedirects(resp, reverse("chores:who_am_i"))

    def test_redirects_when_session_person_deleted(self):
        self._login_as(self.mom)
        self.mom.delete()
        resp = self.client.get(reverse("chores:index"))
        self.assertRedirects(resp, reverse("chores:who_am_i"))

    def test_clears_stale_person_id_from_session(self):
        self._login_as(self.mom)
        self.mom.delete()
        self.client.get(reverse("chores:index"))
        self.assertNotIn("person_id", self.client.session)

    def test_hide_done_query_param_filters_completed_chores(self):
        self._login_as(self.mom)
        Chore.objects.create(
            title="Done chore", assigned_to=self.mom, last_done_at=timezone.now()
        )
        Chore.objects.create(title="Pending chore", assigned_to=self.mom)
        resp = self.client.get(reverse("chores:index") + "?hide_done=1")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Pending chore")
        self.assertNotContains(resp, "Done chore")

    def test_view_toggle_persists_in_session(self):
        self._login_as(self.mom)
        self.client.get(reverse("chores:index") + "?view=board")
        self.assertEqual(self.client.session.get("view"), "board")

    def test_board_view_renders_kanban_template(self):
        self._login_as(self.mom)
        session = self.client.session
        session["view"] = "board"
        session.save()
        resp = self.client.get(reverse("chores:index"))
        self.assertTemplateUsed(resp, "chores/chore_list_board.html")
        self.assertContains(resp, 'class="kanban"')

    def test_completed_count_in_context(self):
        self._login_as(self.mom)
        Chore.objects.create(
            title="A", assigned_to=self.mom, last_done_at=timezone.now()
        )
        Chore.objects.create(
            title="B", assigned_to=self.mom, last_done_at=timezone.now()
        )
        Chore.objects.create(title="C", assigned_to=self.mom)
        resp = self.client.get(reverse("chores:index"))
        self.assertEqual(resp.context["completed_count"], 2)


class MarkDoneViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")
        self.chore = Chore.objects.create(title="x", assigned_to=self.mom)

    def test_marks_done_and_redirects(self):
        resp = self.client.post(reverse("chores:mark_done", args=[self.chore.pk]))
        self.assertRedirects(
            resp, reverse("chores:index"), fetch_redirect_response=False
        )
        self.chore.refresh_from_db()
        self.assertIsNotNone(self.chore.last_done_at)

    def test_get_returns_405(self):
        resp = self.client.get(reverse("chores:mark_done", args=[self.chore.pk]))
        self.assertEqual(resp.status_code, 405)


class ChoreDeleteViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")
        self.chore = Chore.objects.create(title="x", assigned_to=self.mom)

    def test_deletes_chore_and_redirects(self):
        resp = self.client.post(reverse("chores:chore_delete", args=[self.chore.pk]))
        self.assertRedirects(
            resp, reverse("chores:index"), fetch_redirect_response=False
        )
        self.assertFalse(Chore.objects.filter(pk=self.chore.pk).exists())

    def test_get_returns_405(self):
        resp = self.client.get(reverse("chores:chore_delete", args=[self.chore.pk]))
        self.assertEqual(resp.status_code, 405)


class ChoresDeleteCompletedViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")

    def test_deletes_only_completed(self):
        c_done_a = Chore.objects.create(
            title="Done A", assigned_to=self.mom, last_done_at=timezone.now()
        )
        c_done_b = Chore.objects.create(
            title="Done B", assigned_to=self.mom, last_done_at=timezone.now()
        )
        c_pending = Chore.objects.create(title="Pending", assigned_to=self.mom)
        resp = self.client.post(reverse("chores:chores_delete_completed"))
        self.assertRedirects(
            resp, reverse("chores:index"), fetch_redirect_response=False
        )
        self.assertFalse(Chore.objects.filter(pk__in=[c_done_a.pk, c_done_b.pk]).exists())
        self.assertTrue(Chore.objects.filter(pk=c_pending.pk).exists())

    def test_no_completed_renders_info_message(self):
        Chore.objects.create(title="Pending", assigned_to=self.mom)
        resp = self.client.post(
            reverse("chores:chores_delete_completed"), follow=True
        )
        self.assertEqual(Chore.objects.count(), 1)
        messages = [str(m) for m in resp.context["messages"]]
        self.assertTrue(any("No completed chores" in m for m in messages))


class PersonDeleteViewTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")
        self.sister = Person.objects.create(name="sister")

    def test_cascades_to_assigned_chores(self):
        Chore.objects.create(title="mom chore 1", assigned_to=self.mom)
        Chore.objects.create(title="mom chore 2", assigned_to=self.mom)
        Chore.objects.create(title="sister chore", assigned_to=self.sister)
        self.client.post(reverse("chores:person_delete", args=[self.mom.pk]))
        self.assertEqual(Chore.objects.count(), 1)
        self.assertEqual(Chore.objects.first().assigned_to, self.sister)


class ChoreFormTests(TestCase):
    def setUp(self):
        self.mom = Person.objects.create(name="mom")

    def test_title_and_assignee_required(self):
        form = ChoreForm(data={"title": "", "assigned_to": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("assigned_to", form.errors)

    def test_interval_days_optional_blank_means_one_shot(self):
        form = ChoreForm(
            data={"title": "x", "assigned_to": self.mom.pk, "interval_days": ""}
        )
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data["interval_days"])
