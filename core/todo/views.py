from django.contrib.auth.decorators import login_required
from django.db.models import Case, When
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, View
from django.views.generic.edit import FormMixin

from accounts.mixins import VerifiedUserRequiredMixin
from accounts.models import Profile
from todo.forms import NewTaskForm
from todo.models import Task


class TodoListView(VerifiedUserRequiredMixin, ListView, FormMixin):
    template_name = "todo.html"
    context_object_name = "completedtasks"
    model = Task
    form_class = NewTaskForm

    def get_queryset(self):
        return (
            Task.objects.filter(author__user=self.request.user, completed=True)
            .select_related("author", "author__user")
            .order_by("-due_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = (
            Task.objects.filter(author__user=self.request.user, completed=False)
            .select_related("author", "author__user")
            .annotate(
                priority_order=Case(
                    When(priority="high", then=1),
                    When(priority="medium", then=2),
                    When(priority="low", then=3),
                    default=4,
                )
            )
            .order_by("priority_order")
        )
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.instance.author = Profile.objects.get(user=request.user)
            form.save()
            return redirect(reverse_lazy("todo:todo"))


class TasksEditView(VerifiedUserRequiredMixin, UpdateView):
    model = Task
    form_class = NewTaskForm
    success_url = "/"
    template_name = "edit-task.html"

    def get_queryset(self):
        return Task.objects.filter(author__user=self.request.user).select_related(
            "author", "author__user"
        )


class TasksDeleteView(VerifiedUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"], author__user=request.user)
        task.delete()
        return redirect("todo:todo")


@login_required
def TasksCompleted(request, pk):
    if not request.user.is_verified:
        return redirect("accounts:login")
    Task.objects.filter(pk=pk, author__user=request.user).update(completed=True)
    return redirect("todo:todo")


@login_required
def TasksNotCompleted(request, pk):
    if not request.user.is_verified:
        return redirect("accounts:login")
    Task.objects.filter(pk=pk, author__user=request.user).update(completed=False)
    return redirect("todo:todo")
