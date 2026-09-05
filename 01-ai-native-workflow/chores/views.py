from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ChoreForm, PersonForm
from .models import Chore, Person


@require_GET
def chore_list(request):
    if request.session.get("person_id") is None:
        return redirect(reverse("chores:who_am_i"))

    hide_done_param = request.GET.get("hide_done")
    if hide_done_param in ("0", "1"):
        request.session["hide_done"] = hide_done_param == "1"
    hide_done = bool(request.session.get("hide_done"))

    chores = (
        Chore.objects
        .select_related("assigned_to")
        .order_by("title")
    )
    if hide_done:
        chores = chores.filter(last_done_at__isnull=True)

    completed_count = Chore.objects.filter(last_done_at__isnull=False).count()

    current_person = Person.objects.get(pk=request.session["person_id"])
    return render(
        request,
        "chores/chore_list.html",
        {
            "chores": chores,
            "current_person": current_person,
            "hide_done": hide_done,
            "completed_count": completed_count,
        },
    )


@require_http_methods(["GET", "POST"])
def who_am_i(request):
    if not Person.objects.exists():
        return redirect(reverse("chores:people_create"))
    if request.method == "POST":
        try:
            person_id = int(request.POST.get("person_id", ""))
            Person.objects.get(pk=person_id)
        except (TypeError, ValueError, Person.DoesNotExist):
            people = Person.objects.all()
            return render(request, "chores/who_am_i.html", {"people": people})
        request.session["person_id"] = person_id
        return redirect(reverse("chores:index"))

    people = Person.objects.all()
    return render(request, "chores/who_am_i.html", {"people": people})


@require_POST
def mark_done(request, chore_id):
    chore = get_object_or_404(Chore, pk=chore_id)
    chore.last_done_at = timezone.now()
    chore.save(update_fields=["last_done_at"])
    return redirect(reverse("chores:index"))


@require_POST
def chore_delete(request, chore_id):
    chore = get_object_or_404(Chore, pk=chore_id)
    title = chore.title
    chore.delete()
    messages.success(request, f"Deleted chore '{title}'.")
    return redirect(reverse("chores:index"))


@require_POST
def chores_delete_completed(request):
    deleted_count, _ = Chore.objects.filter(last_done_at__isnull=False).delete()
    if deleted_count:
        messages.success(request, f"Deleted {deleted_count} completed chore{'s' if deleted_count != 1 else ''}.")
    else:
        messages.info(request, "No completed chores to delete.")
    return redirect(reverse("chores:index"))


@require_http_methods(["GET", "POST"])
def chore_create(request):
    person_id = request.session.get("person_id")
    if person_id is None:
        return redirect(reverse("chores:who_am_i"))
    if not Person.objects.exists():
        return redirect(reverse("chores:people_create"))
    current_person = Person.objects.get(pk=person_id)
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("chores:index"))
    else:
        form = ChoreForm(initial={"assigned_to": current_person})
    return render(
        request,
        "chores/chore_create.html",
        {"form": form, "current_person": current_person},
    )


@require_GET
def people_list(request):
    people = Person.objects.all()
    return render(request, "chores/people_list.html", {"people": people})


@require_http_methods(["GET", "POST"])
def people_create(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            messages.success(request, f"Added {person.name}.")
            return redirect(reverse("chores:people_list"))
    else:
        form = PersonForm()
    return render(request, "chores/people_create.html", {"form": form})


@require_POST
def person_delete(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    name = person.name
    person.delete()
    messages.success(request, f"Deleted {name} and all their chores.")
    return redirect(reverse("chores:people_list"))
