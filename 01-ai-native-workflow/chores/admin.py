from django.contrib import admin

from .models import Chore, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "interval_days", "last_done_at", "is_due")
    list_filter = ("interval_days",)
    search_fields = ("title",)
    autocomplete_fields = ("assigned_to",)
    ordering = ("title",)
