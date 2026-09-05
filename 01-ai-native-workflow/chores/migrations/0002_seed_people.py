from django.db import migrations


PEOPLE = ["mom", "sister", "me"]


def seed_people(apps, schema_editor):
    Person = apps.get_model("chores", "Person")
    for name in PEOPLE:
        Person.objects.get_or_create(name=name)


def unseed_people(apps, schema_editor):
    Person = apps.get_model("chores", "Person")
    Person.objects.filter(name__in=PEOPLE).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("chores", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_people, reverse_code=unseed_people),
    ]
