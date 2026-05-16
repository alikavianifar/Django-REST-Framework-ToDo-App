from django.contrib import admin
from todo.models import Task

# Register your models here.


class TaskAdmin(admin.ModelAdmin):
    list_display = ["author", "title", "due_date", "priority", "completed"]


admin.site.register(Task, TaskAdmin)
