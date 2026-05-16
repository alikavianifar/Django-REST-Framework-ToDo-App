from django.urls import path, include
from todo.views import (
    TodoListView,
    TasksEditView,
    TasksDeleteView,
    TasksCompleted,
    TasksNotCompleted,
)

app_name = "todo"

urlpatterns = [
    path("", TodoListView.as_view(), name="todo"),
    path("edit/<int:pk>", TasksEditView.as_view(), name="edit"),
    path("delete/<int:pk>", TasksDeleteView.as_view(), name="delete"),
    path("completed/<int:pk>", TasksCompleted, name="completed"),
    path("not-completed/<int:pk>", TasksNotCompleted, name="not-completed"),
    path("api/v1/", include("todo.api.v1.urls")),
]
