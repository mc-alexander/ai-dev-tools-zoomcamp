from django.db import models


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
        on_delete=models.PROTECT,
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
