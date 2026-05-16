from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from todo.models import Task

from .paginations import DefaultPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import TaskSerializer


class TaskModelViewSet(viewsets.ModelViewSet):
    """ViewSet for tasks scoped to the authenticated user."""

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "priority": ["exact", "in"],
        "due_date": ["exact"],
        "completed": ["exact"],
    }
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "id", "priority"]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Task.objects.filter(author__user=self.request.user).select_related(
            "author", "author__user"
        )
