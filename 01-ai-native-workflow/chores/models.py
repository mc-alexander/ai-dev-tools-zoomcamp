from datetime import timedelta

from django.db import models
from django.utils import timezone


class Person(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "people"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Chore(models.Model):
    title = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="chores",
    )
    interval_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Recurrence interval in days. Leave blank for one-shot chores.",
    )
    last_done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_due(self) -> bool:
        if self.last_done_at is None:
            return True
        if self.interval_days is None:
            return False
        return self.last_done_at + timedelta(days=self.interval_days) <= timezone.now()
