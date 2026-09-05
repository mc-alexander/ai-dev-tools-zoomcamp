from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="index"),
    path("who-am-i/", views.who_am_i, name="who_am_i"),
    path("chore/new/", views.chore_create, name="chore_create"),
    path("chore/<int:chore_id>/done/", views.mark_done, name="mark_done"),
    path("chore/<int:chore_id>/delete/", views.chore_delete, name="chore_delete"),
    path("chores/delete-completed/", views.chores_delete_completed, name="chores_delete_completed"),
    path("people/", views.people_list, name="people_list"),
    path("people/new/", views.people_create, name="people_create"),
    path("people/<int:person_id>/delete/", views.person_delete, name="person_delete"),
]
