from django import forms
from .models import Task


class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date", "priority", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update(
            {"class": "form-control", "id": "title"}
        )
        self.fields["due_date"].widget = forms.DateTimeInput(
            attrs={
                "class": "form-control",
                "id": "due_date",
                "type": "datetime-local",
            }
        )
        self.fields["priority"].widget.attrs.update(
            {"class": "form-select", "id": "priority"}
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "id": "description", "rows": "5"}
        )
