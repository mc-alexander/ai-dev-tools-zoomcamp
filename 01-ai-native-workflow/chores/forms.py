from django import forms

from .models import Chore, Person


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["title", "assigned_to", "interval_days"]


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["name"]
