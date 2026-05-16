from django.db import models
from django.urls import reverse


class Task(models.Model):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    PRIORITY_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]

    author = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(
        max_length=6,
        choices=PRIORITY_CHOICES,
        default=LOW,
    )
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title

    def get_snippet(self):
        return self.title[:10]

    def get_absolute_api_url(self):
        return reverse("todo:api-v1:todo-detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["due_date"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
